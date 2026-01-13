# bombsquad

**Isolate OOM-prone functions in a separate process, raise exceptions on SIGKILL or segfault.**

Methods that cause out-of-memory errors (OOM) or segfaults are killed by the OS immediately, crashing the interpreter without raising an exception.

To solve this problem, the `bombsquad` package provides the `@bombsquad` decorator. This runs the decorated function in a separate, isolated process. If that process is terminated by the OS (e.g. `SIGKILL`), `bombsquad` catches the exit code and raises a `NonzeroExitcode` exception in your main process.

Normal Python exceptions raised within the function are propagated back to the parent process transparently.

## Installation

```bash
pip install bombsquad
```
## Quick Start

### 1. Trapping a Crash

Protect your main application from dangerous functions.

```Python
import os
import signal
from bombsquad import bombsquad, NonzeroExitcode

@bombsquad
def risky_business():
    print("Running risky code...")
    # Simulate a hard crash (like an OOM killer)
    os.kill(os.getpid(), signal.SIGKILL)

try:
    risky_business()
except NonzeroExitcode as e:
    print(f"Caught crash! Process exited with code {e.exitcode}")
```

### 2. Propagating Exceptions

Standard exceptions work exactly as expected.

```Python
@bombsquad
def divide(a, b):
    return a / b

try:
    divide(10, 0)
except ZeroDivisionError:
    print("Caught division by zero from child process.")
```

## Advanced Configuration

The decorator accepts arguments to tune performance and safety.
```Python
@bombsquad(start_method="spawn", backend="file")
def massive_processing(data):
    ...
```

### Parameters

| Argument | Options | Default | Description |
| :--- | :--- | :--- | :--- |
| **`start_method`** | `"spawn"`, `"fork"` | `"spawn"` | How the child process is created. |
| **`backend`** | `"file"`, `"queue"` | `"file"` | How data is returned to the parent. |

### Choosing a `backend`

* **`"file"` (Default, Recommended):**
    * **Mechanism:** Serializes results to a temporary file on disk.
    * **Pros:** Supports **unlimited return sizes** (limited only by disk space).
    * **Cons:** Slower due to disk I/O.
    * **Use for:** Returning large arrays, datasets, or huge strings.

* **`"queue"`:**
    * **Mechanism:** Uses `multiprocessing.Queue` (memory pipes).
    * **Pros:** Faster (in-memory transfer).
    * **Cons:** Limited to **~4GB** payloads (Python pickle limit).
    * **Use for:** Returning small results (status codes, metrics, small dicts).

## License

MIT