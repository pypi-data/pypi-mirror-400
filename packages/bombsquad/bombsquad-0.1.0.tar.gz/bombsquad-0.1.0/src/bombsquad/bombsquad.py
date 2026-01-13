from typing import Literal
import multiprocessing as mp
from functools import wraps, partial
import traceback
import sys
import os
import tempfile
from queue import Empty
import dill


# --- Custom Exceptions ---
class NonzeroExitcode(Exception):
    def __init__(self, exitcode: int, params: dict):
        self.exitcode = exitcode
        self.params = params
        super().__init__(f"Process terminated with exit code {exitcode}")

class ZeroExitcodeWithoutPayload(Exception):
    def __init__(self, params: dict):
        self.params = params
        super().__init__("Process exited successfully (0) but returned no data.")

# --- Worker Strategies ---

def _worker_file(output_path: str, payload_bytes: bytes) -> None:
    """Strategy: Serialize result to a temporary file (Safe for large data)."""
    try:
        worker, args, kwargs = dill.loads(payload_bytes)
        result = worker(*args, **kwargs)
        with open(output_path, "wb") as f:
            dill.dump((True, result), f)
    except Exception as e:
        tb = traceback.format_exc()
        try:
            with open(output_path, "wb") as f:
                dill.dump((False, (e, tb)), f)
        except Exception:
            sys.exit(1)

def _worker_queue(queue: mp.Queue, payload_bytes: bytes) -> None:
    """Strategy: Push result to a Pipe/Queue (Fast, but limited to ~64KB)."""
    try:
        worker, args, kwargs = dill.loads(payload_bytes)
        result = worker(*args, **kwargs)
        queue.put((True, result))
    except Exception as e:
        tb = traceback.format_exc()
        queue.put((False, (e, tb)))

# --- Core Logic ---

def _bombsquad_wrapper_logic(worker, start_method, backend, args, kwargs):
    # 1. Serialize Input (Parent side)
    try:
        payload_bytes = dill.dumps((worker, args, kwargs))
    except Exception as e:
        raise RuntimeError(f"Failed to serialize arguments with dill: {e}") from e

    ctx = mp.get_context(start_method)
    
    # --- QUEUE BACKEND ---
    if backend == "queue":
        queue = ctx.Queue()
        process = ctx.Process(
            target=_worker_queue,
            kwargs={"queue": queue, "payload_bytes": payload_bytes}
        )
        process.start()
        success, payload = False, None
        data_received = False

        while True:
            try:
                # 1. Try to read (with short timeout to allow liveness checks)
                success, payload = queue.get(timeout=0.05)

                # No timeout exception - we received result. Done.
                data_received = True
                break
            except Empty:
                # 2. No data yet. Is the process still running?
                if not process.is_alive():
                    # Process died. Check queue one last time.
                    try:
                        success, payload = queue.get_nowait()
                        data_received = True
                    except Empty:
                        pass # Truly dead and empty
                    break
                # Process is alive, just thinking or working. Loop again.
                continue

        process.join()

    # --- FILE BACKEND ---
    elif backend == "file":
        fd, path = tempfile.mkstemp()
        os.close(fd)
        try:
            process = ctx.Process(
                target=_worker_file,
                kwargs={"output_path": path, "payload_bytes": payload_bytes}
            )
            process.start()
            process.join()

            if os.path.exists(path) and os.path.getsize(path) > 0:
                with open(path, "rb") as f:
                    try:
                        success, payload = dill.load(f)
                        data_received = True
                    except Exception:
                        data_received = False
            else:
                data_received = False
        finally:
            if os.path.exists(path): os.remove(path)
            
    else:
        raise ValueError(f"Unknown backend: {backend}")

    # --- FINAL ERROR HANDLING ---
    
    if data_received:
        if success:
            return payload
        else:
            # Payload is (Exception, Traceback)
            exc, tb = payload
            print(f"--- Traceback from {start_method} child ---\n{tb}", file=sys.stderr)
            raise exc
    else:
        # No data received -> Hard Crash
        params = {"exitcode": process.exitcode, "args": args, "kwargs": kwargs}
        if process.exitcode != 0:
            raise NonzeroExitcode(process.exitcode, params)
        else:
            raise ZeroExitcodeWithoutPayload(params)

# --- The Decorator API ---

def bombsquad(worker: callable = None, 
           *, 
           start_method: Literal["spawn", "fork"] = "spawn", 
           backend: Literal["file", "queue"] = "file"):
    """
    Decorator to isolate a function risking SIGKILL in a separate process and raise an exception on a nonzero exit code.
    
    Usage:
        @bombsquad
        def my_func(): ...

        @bombsquad(backend="queue", start_method="fork")
        def my_func(): ...
        
    Args:
        start_method: 'spawn' (safer, default) or 'fork' (faster on Linux, not compatible with some libraries).
        backend: 'file' (safe for large data, default) or 'queue' (faster, <4GB limit).
    """
    
    # Case 1: Called as @bombsquad(backend="queue") -> worker is None
    if worker is None:
        return partial(bombsquad, start_method=start_method, backend=backend)

    # Case 2: Called as @bombsquad -> worker is the function
    @wraps(worker)
    def wrapper(*args, **kwargs):
        return _bombsquad_wrapper_logic(worker, start_method, backend, args, kwargs)
    
    return wrapper

# --- Demo ---

@bombsquad
def default_div(a, b):
    return a / b

@bombsquad(start_method="fork", backend="queue")
def fast_div(a, b):
    return a / b

if __name__ == "__main__":
    
    print("--- 1. Default (Spawn + File) ---")

    print(f"10 / 2 = {default_div(10, 2)}")

    print("\n--- 2. Configured (Fork + Queue) ---")

    print(f"100 / 2 = {fast_div(100, 2)}")

    print("\n--- 3. Error Handling ---")
    try:
        default_div(1, 0)
    except ZeroDivisionError:
        print("Caught expected ZeroDivisionError!")