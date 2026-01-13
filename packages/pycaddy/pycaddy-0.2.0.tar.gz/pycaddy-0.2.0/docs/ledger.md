# Ledger — Low-Level Run Registry

The `Ledger` is a JSON-backed registry that tracks every experiment run in a single `metadata.json` file. It provides fine-grained control and is the foundation for the higher-level `Project` and `Session` APIs.

**Key features:**
- One file per project (singleton per process)
- Thread/process-safe with file locking
- Deterministic parameter hashing for run deduplication
- Granular run tracking with status updates

---

## Table of Contents

- [Quick Start](#quick-start)
- [Key Concepts](#key-concepts)
- [API Reference](#api-reference)
  - [Initialization](#initialization)
  - [Core Methods](#core-methods)
- [Examples](#examples)
  - [Record Auxiliary Files](#record-auxiliary-files)
  - [Find Previous Run by Parameters](#find-previous-run-by-parameters)
- [Cheat Sheet](#cheat-sheet)

---

## Quick Start

```python
from pycaddy.ledger import Ledger, Status
from multiprocessing import Lock
from pathlib import Path

# Set global lock (one per worker pool)
Ledger.set_global_lock(Lock())

# Create ledger
ledger = Ledger(path=Path("results/metadata.json"))

# Allocate a new run
uid = ledger.allocate("train", relpath=Path("mnist/cnn"))

# Update status
ledger.log("train", uid, status=Status.RUNNING)

# ... training ...

# Mark as done and attach files
ledger.log(
    "train",
    uid,
    status=Status.DONE,
    path_dict={"model": Path("model.pt")}
)
```

---

## Key Concepts

| Concept              | Description                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------- |
| **identifier**       | Groups related runs (e.g., `"train"`, `"eval"`)                                          |
| **relpath/relkey**   | Sub-folder namespace; empty string means project root                                    |
| **uid**              | Zero-padded counter unique within `(identifier, relpath)` (e.g., `"0001"`)               |
| **param_hash**       | Deterministic integer hash of the params dict; enables auto-resume                       |
| **LEDGER_LOCK**      | Single `multiprocessing.Lock` that serializes all writes to `metadata.json`              |

### Run Lifecycle

1. **Allocate**: Reserve a unique ID for a new run
2. **Log**: Update status, attach files, or modify metadata
3. **Query**: Find runs by ID, parameters, or other criteria

---

## API Reference

### Initialization

```python
Ledger(path: Path, lock: Lock | None = None)
```

- **`path`**: Path to `metadata.json` file
- **`lock`**: Optional lock; if `None`, uses global lock set via `Ledger.set_global_lock()`

#### Class Method

```python
Ledger.set_global_lock(lock: Lock)
```

Sets a global lock for all `Ledger` instances. Call this once at the start of your program.

---

### Core Methods

#### `allocate(identifier: str, relpath: Path = Path(""), param_hash: int | None = None) -> str`

Allocates a new unique ID for a run.

```python
uid = ledger.allocate("train", relpath=Path("mnist"), param_hash=12345)
# Returns "0001" (or next available)
```

#### `log(identifier: str, uid: str, status: Status | None = None, path_dict: dict[str, Path] | None = None)`

Updates an existing run's status or attached files.

```python
# Update status
ledger.log("train", "0001", status=Status.RUNNING)

# Attach files
ledger.log("train", "0001", path_dict={"model": Path("model.pt")})

# Both
ledger.log(
    "train",
    "0001",
    status=Status.DONE,
    path_dict={"weights": Path("weights.pt")}
)
```

#### `get_record(identifier: str, uid: str) -> Record | None`

Retrieves the full record for a specific run.

```python
record = ledger.get_record("train", "0001")
if record:
    print(record.status)     # Status.DONE
    print(record.files)      # {"model": Path("model.pt")}
    print(record.param_hash) # 12345
```

#### `get_uid_record_dict(identifier: str, relpath: Path = Path("")) -> dict[str, Record]`

Returns all runs for a given identifier and relpath.

```python
runs = ledger.get_uid_record_dict("train", relpath=Path("mnist"))
for uid, record in runs.items():
    print(f"Run {uid}: {record.status}")
```

#### `find_by_param_hash(identifier: str, param_hash: int, relpath: Path = Path("")) -> tuple[str, Record] | None`

Finds a run by its parameter hash.

```python
hit = ledger.find_by_param_hash("train", param_hash=12345)
if hit:
    uid, record = hit
    print(f"Found run {uid} with matching parameters")
```

#### `load() -> dict`

Returns the raw JSON snapshot of the entire ledger.

```python
data = ledger.load()
print(data)  # {"train": {"mnist/cnn": {"0001": {...}}}}
```

---

## Examples

### Record Auxiliary Files

Track multiple files associated with a run:

```python
from pycaddy.ledger import Ledger, Status
from pathlib import Path

ledger = Ledger(path=Path("results/metadata.json"))
uid = ledger.allocate("train")

ledger.log("train", uid, status=Status.RUNNING)

# Training code here...

# Attach multiple files
ledger.log(
    "train",
    uid,
    status=Status.DONE,
    path_dict={
        "tensorboard": Path("tb/events.out"),
        "notes": Path("notes.yaml"),
        "model": Path("model.pt")
    }
)

# Retrieve later
record = ledger.get_record("train", uid)
print(record.files["model"])  # Path("model.pt")
```

### Find Previous Run by Parameters

Automatically resume training if parameters match:

```python
from pycaddy.ledger import Ledger, Status
from pathlib import Path

ledger = Ledger(path=Path("results/metadata.json"))

params = {"lr": 0.001, "batch_size": 32}
param_hash = hash(frozenset(params.items()))  # Simple hash

# Check if already trained
hit = ledger.find_by_param_hash("train", param_hash=param_hash)
if hit:
    old_uid, record = hit
    print(f"Already trained with these params: {record.files['model']}")
else:
    # New run
    uid = ledger.allocate("train", param_hash=param_hash)
    ledger.log("train", uid, status=Status.RUNNING)
    # ... train ...
    ledger.log(
        "train",
        uid,
        status=Status.DONE,
        path_dict={"model": Path("model.pt")}
    )
```

---

## Cheat Sheet

```python
from pycaddy.ledger import Ledger, Status
from multiprocessing import Lock
from pathlib import Path

# Set global lock (once per program)
Ledger.set_global_lock(Lock())

# Create ledger
ledger = Ledger(path=Path("results/metadata.json"))

# Allocate new run
uid = ledger.allocate(
    identifier="train",
    relpath=Path("subfolder"),
    param_hash=12345  # optional
)

# Update status
ledger.log("train", uid, status=Status.RUNNING)
ledger.log("train", uid, status=Status.DONE)
ledger.log("train", uid, status=Status.ERROR)

# Attach files
ledger.log("train", uid, path_dict={"weights": Path("w.pt")})

# Retrieve record
record = ledger.get_record("train", uid)
print(record.status)      # Status.DONE
print(record.files)       # {"weights": Path("w.pt")}
print(record.param_hash)  # 12345

# Get all runs
runs = ledger.get_uid_record_dict("train", relpath=Path("subfolder"))
for uid, rec in runs.items():
    print(f"{uid}: {rec.status}")

# Find by param hash
hit = ledger.find_by_param_hash("train", param_hash=12345)
if hit:
    uid, record = hit
    print(f"Found: {uid}")

# Load raw data
data = ledger.load()
```

---

## Status Enum

```python
from pycaddy.ledger import Status

Status.PENDING   # Allocated but not started
Status.RUNNING   # Currently running
Status.DONE      # Completed successfully
Status.ERROR     # Failed with error
```

---

## Thread/Process Safety

The `Ledger` uses `filelock.FileLock` to ensure safe concurrent access:

- Multiple processes can share the same `metadata.json`
- All writes are serialized via the global lock
- Set the lock once at program start: `Ledger.set_global_lock(Lock())`

**Example with multiprocessing:**

```python
from pycaddy.ledger import Ledger
from multiprocessing import Pool, Manager

def train_worker(config):
    ledger = Ledger(path=Path("results/metadata.json"))
    uid = ledger.allocate("train")
    ledger.log("train", uid, status=Status.RUNNING)
    # ... train ...
    ledger.log("train", uid, status=Status.DONE)

if __name__ == "__main__":
    manager = Manager()
    Ledger.set_global_lock(manager.Lock())

    with Pool(4) as pool:
        pool.map(train_worker, configs)
```

---

## See Also

- [Project & Session API](project-session.md) — High-level experiment management
- [Parameter Sweeping](parameter-sweeping.md) — Generate parameter grids
- [Main README](../README.md) — Project overview
