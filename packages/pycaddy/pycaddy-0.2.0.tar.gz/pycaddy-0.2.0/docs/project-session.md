# Project & Session — High-Level Experiment Management

The `Project` and `Session` classes provide a friendly, high-level API for organizing experiments and tracking individual runs.

- **Project**: Organizes output folders and manages the shared `Ledger`
- **Session**: A lightweight handle for one experiment run — builds file paths, updates status, and tracks artifacts

---

## Table of Contents

- [Quick Start](#quick-start)
- [Key Concepts](#key-concepts)
- [API Reference](#api-reference)
  - [Project](#project)
  - [Session](#session)
- [Examples](#examples)
  - [Grid Search with Auto-Resume](#grid-search-with-auto-resume)
  - [Nested Namespaces](#nested-namespaces)
  - [Logging Extra Files](#logging-extra-files)
- [Cheat Sheet](#cheat-sheet)

---

## Quick Start

```python
from pycaddy.project import Project

# Create a project
proj = Project(root="results").ensure_folder()

# Start a new run
run = proj.session("train", params={"lr": 1e-3})
run.start()

# Save your model
save_model(run.path("model.pt"))

# Mark as done
run.done()
```

---

## Key Concepts

| Term                      | What it means                                                                 |
| ------------------------- | ----------------------------------------------------------------------------- |
| **Project**               | A namespace that manages a root folder + relpath + shared Ledger             |
| **Session**               | One experiment run identified by `(identifier, uid)`                          |
| **StorageMode**           | `SUBFOLDER` (default) or `PREFIX` for organizing files                        |
| **ExistingRun Strategy**  | `RESUME` (reuse finished run) or `NEW` (always create fresh)                  |

### Storage Modes

- **`SUBFOLDER`** (default): Each run gets its own folder
  ```
  results/
  └── train/
      ├── 0001/
      │   ├── model.pt
      │   └── log.txt
      └── 0002/
          └── model.pt
  ```

- **`PREFIX`**: Files are prefixed with the run ID
  ```
  results/
  └── train/
      ├── 0001_model.pt
      ├── 0001_log.txt
      └── 0002_model.pt
  ```

### Existing Run Strategies

- **`ExistingRun.RESUME`**: If a run with the same parameters exists and is completed, reuse it
- **`ExistingRun.NEW`**: Always create a new run, even if parameters match existing ones
- **`None`** (default): Create new run but don't enforce any strategy

---

## API Reference

### Project

```python
Project(
    root: str | Path,
    relpath: str | Path = "",
    storage_mode: StorageMode = StorageMode.SUBFOLDER
)
```

#### Methods

- **`ensure_folder() -> Project`**
  Creates the project directory if it doesn't exist. Returns `self` for chaining.

- **`sub(name: str) -> Project`**
  Creates a sub-project with a deeper `relpath`.
  ```python
  root = Project("results")
  imagenet = root.sub("imagenet")  # results/imagenet/
  ```

- **`session(identifier: str, params: dict, existing_run_strategy: ExistingRun | None = None, storage_mode: StorageMode | None = None) -> Session`**
  Creates a new session (experiment run).

### Session

Represents one experiment run.

#### Properties

- **`uid: str`** — Unique run ID (zero-padded, e.g., "0001")
- **`status: Status`** — Current status (PENDING, RUNNING, DONE, ERROR)
- **`folder: Path`** — Auto-created directory for this run
- **`files: dict[str, Path]`** — Dictionary of attached file paths

#### Methods

- **`start() -> Session`**
  Marks the run as RUNNING. Returns `self` for chaining.

- **`done() -> Session`**
  Marks the run as DONE. Returns `self` for chaining.

- **`error() -> Session`**
  Marks the run as ERROR. Returns `self` for chaining.

- **`is_done() -> bool`**
  Returns `True` if status is DONE.

- **`path(filename: str, include_identifier: bool = True) -> Path`**
  Builds a file path within the run's folder.
  ```python
  model_path = session.path("model.pt")
  # results/train/0001/model.pt (SUBFOLDER mode)
  # results/train/0001_model.pt (PREFIX mode)
  ```

- **`attach_files(file_dict: dict[str, Path]) -> Session`**
  Logs additional files to the run's metadata.
  ```python
  session.attach_files({
      "checkpoint": session.path("ckpt.pt"),
      "logs": session.path("train.log")
  })
  ```

---

## Examples

### Grid Search with Auto-Resume

Automatically skip runs that have already completed:

```python
from pycaddy.project import Project, ExistingRun, StorageMode

project = Project("results/grid", storage_mode=StorageMode.PREFIX)

for config in sweep.generate():
    session = project.session(
        "train",
        params=config,
        existing_run_strategy=ExistingRun.RESUME
    )

    if session.is_done():
        print(f"Skipping completed: {config}")
        continue

    session.start()
    train_model(config, checkpoint=session.path("ckpt.pt"))
    session.done()
```

### Nested Namespaces

Organize experiments into hierarchical folders:

```python
from pycaddy.project import Project

root = Project("results")
imagenet = root.sub("imagenet")           # results/imagenet/
randaug = imagenet.sub("randaug")         # results/imagenet/randaug/

session = randaug.session("train", params={"aug_level": 5})
session.start()
# ... training ...
session.done()
```

### Logging Extra Files

Track additional artifacts like logs, configs, or checkpoints:

```python
from pycaddy.project import Project

project = Project("experiments").ensure_folder()
session = project.session("train", params={"lr": 0.001})
session.start()

# Attach files
session.attach_files({
    "log": session.path("train.log", include_identifier=False),
    "config": session.path("config.yaml"),
    "tensorboard": session.path("events.out")
})

session.done()

# Later, retrieve files
print(session.files["log"])  # Path to log file
```

---

## Cheat Sheet

```python
from pycaddy.project import Project, ExistingRun, StorageMode

# Create project
p = Project("results")
p.ensure_folder()

# Create sub-project
sub = p.sub("experiment_name")

# Create session
s = p.session(
    "train",
    params={"lr": 0.001},
    existing_run_strategy=ExistingRun.RESUME,  # optional
    storage_mode=StorageMode.SUBFOLDER          # optional
)

# Session lifecycle
s.start()
s.done()
s.error()

# Check status
if s.is_done():
    print("Already completed!")

# File paths
model_path = s.path("model.pt")
log_path = s.path("log.txt", include_identifier=False)

# Attach files
s.attach_files({
    "checkpoint": s.path("ckpt.pt"),
    "metrics": s.path("metrics.json")
})

# Access files
print(s.files)  # dict[str, Path]

# Access folder
print(s.folder)  # Path to run directory
```

---

## See Also

- [Ledger API](ledger.md) — Low-level run registry
- [Parameter Sweeping](parameter-sweeping.md) — Generate parameter grids
- [Main README](../README.md) — Project overview
