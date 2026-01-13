# Parameter Sweeping — Grid Search & Hyperparameter Generation

The `sweeper` module provides tools for generating parameter combinations for hyperparameter tuning, grid searches, and experiment automation.

**Key features:**
- Multiple sweeping strategies (product, zip)
- Chain multiple sweepers together
- Support for constants and nested parameters
- Lightweight and composable

---

## Table of Contents

- [Quick Start](#quick-start)
- [Core Classes](#core-classes)
  - [DictSweep](#dictsweep)
  - [ChainSweep](#chainsweep)
- [Strategies](#strategies)
- [Examples](#examples)
  - [Basic Grid Search](#basic-grid-search)
  - [Constants](#constants)
  - [Zip Strategy](#zip-strategy)
  - [Chained Sweeps](#chained-sweeps)
  - [Integration with Project](#integration-with-project)
- [Cheat Sheet](#cheat-sheet)

---

## Quick Start

```python
from pycaddy.sweeper import DictSweep, StrategyName

# Define parameter space
params = {
    'learning_rate': [0.01, 0.001, 0.0001],
    'batch_size': [16, 32, 64]
}

# Generate all combinations (Cartesian product)
sweep = DictSweep(parameters=params, strategy=StrategyName.PRODUCT)

for config in sweep.generate():
    print(config)
    # {'learning_rate': 0.01, 'batch_size': 16}
    # {'learning_rate': 0.01, 'batch_size': 32}
    # ... 9 combinations total
```

---

## Core Classes

### DictSweep

Generates parameter combinations from a dictionary of parameter lists.

```python
DictSweep(
    parameters: dict = {},
    constants: dict = {},
    strategy: StrategyName = StrategyName.PRODUCT
)
```

**Parameters:**
- **`parameters`**: Dictionary where values are lists of options to sweep over
- **`constants`**: Dictionary of fixed values included in every configuration
- **`strategy`**: Strategy for combining parameters (PRODUCT or ZIP)

**Methods:**
- **`generate() -> Iterable[dict]`**: Yields parameter configurations

---

### ChainSweep

Combines multiple `DictSweep` instances into a single sweep, merging their outputs.

```python
ChainSweep(sweepers: list[DictSweep])
```

**Parameters:**
- **`sweepers`**: List of `DictSweep` instances to chain together

**Methods:**
- **`generate() -> Iterable[dict]`**: Yields merged parameter configurations

---

## Strategies

### PRODUCT (Cartesian Product)

Generates all possible combinations (Cartesian product) of parameter values.

```python
from pycaddy.sweeper import DictSweep, StrategyName

params = {
    'lr': [0.01, 0.001],
    'dropout': [0.1, 0.2]
}

sweep = DictSweep(parameters=params, strategy=StrategyName.PRODUCT)
for config in sweep.generate():
    print(config)

# Output:
# {'lr': 0.01, 'dropout': 0.1}
# {'lr': 0.01, 'dropout': 0.2}
# {'lr': 0.001, 'dropout': 0.1}
# {'lr': 0.001, 'dropout': 0.2}
```

**Use case:** Full grid search across all parameter combinations.

---

### ZIP (Paired Values)

Zips parameter lists together element-wise. All parameter lists must have the same length.

```python
from pycaddy.sweeper import DictSweep, StrategyName

params = {
    'model': ['resnet18', 'resnet50', 'vgg16'],
    'batch_size': [64, 32, 16]
}

sweep = DictSweep(parameters=params, strategy=StrategyName.ZIP)
for config in sweep.generate():
    print(config)

# Output:
# {'model': 'resnet18', 'batch_size': 64}
# {'model': 'resnet50', 'batch_size': 32}
# {'model': 'vgg16', 'batch_size': 16}
```

**Use case:** Paired experiments where parameters are correlated.

---

## Examples

### Basic Grid Search

```python
from pycaddy.sweeper import DictSweep, StrategyName

params = {
    'learning_rate': [0.01, 0.001],
    'batch_size': [16, 32, 64],
    'optimizer': ['adam', 'sgd']
}

sweep = DictSweep(parameters=params, strategy=StrategyName.PRODUCT)

# Total: 2 × 3 × 2 = 12 combinations
for i, config in enumerate(sweep.generate(), 1):
    print(f"Experiment {i}: {config}")
```

---

### Constants

Use constants to include fixed values in every configuration:

```python
from pycaddy.sweeper import DictSweep, StrategyName

params = {
    'learning_rate': [0.01, 0.001],
    'dropout': [0.1, 0.3]
}

constants = {
    'epochs': 100,
    'seed': 42,
    'model': 'resnet18'
}

sweep = DictSweep(
    parameters=params,
    constants=constants,
    strategy=StrategyName.PRODUCT
)

for config in sweep.generate():
    print(config)
    # {'learning_rate': 0.01, 'dropout': 0.1, 'epochs': 100, 'seed': 42, 'model': 'resnet18'}
    # ... etc
```

---

### Zip Strategy

Pair parameters together instead of full Cartesian product:

```python
from pycaddy.sweeper import DictSweep, StrategyName

# Test different model sizes with appropriate batch sizes
params = {
    'model': ['tiny', 'small', 'base', 'large'],
    'batch_size': [128, 64, 32, 16],
    'learning_rate': [0.001, 0.001, 0.0005, 0.0001]
}

sweep = DictSweep(parameters=params, strategy=StrategyName.ZIP)

# Only 4 combinations (one per model)
for config in sweep.generate():
    print(config)
    # {'model': 'tiny', 'batch_size': 128, 'learning_rate': 0.001}
    # {'model': 'small', 'batch_size': 64, 'learning_rate': 0.001}
    # ... etc
```

---

### Chained Sweeps

Combine multiple sweepers for complex search spaces:

```python
from pycaddy.sweeper import DictSweep, ChainSweep, StrategyName

# Sweep 1: Model architecture
arch_sweep = DictSweep(
    parameters={'arch': ['resnet', 'vgg']},
    constants={'type': 'cnn'}
)

# Sweep 2: Optimizer settings
optim_sweep = DictSweep(
    parameters={
        'optimizer': ['adam', 'sgd'],
        'learning_rate': [0.01, 0.001]
    },
    strategy=StrategyName.PRODUCT
)

# Chain them together
chain = ChainSweep(sweepers=[arch_sweep, optim_sweep])

# Generates all combinations across both sweeps
for config in chain.generate():
    print(config)
    # {'arch': 'resnet', 'type': 'cnn', 'optimizer': 'adam', 'learning_rate': 0.01}
    # {'arch': 'resnet', 'type': 'cnn', 'optimizer': 'adam', 'learning_rate': 0.001}
    # ... 8 combinations total (2 arch × 2 optim × 2 lr)
```

---

### Integration with Project

Combine sweepers with the Project API for automatic experiment tracking:

```python
from pycaddy.project import Project, ExistingRun
from pycaddy.sweeper import DictSweep, StrategyName

# Define parameter grid
params = {
    'learning_rate': [0.01, 0.001, 0.0001],
    'batch_size': [16, 32, 64],
    'dropout': [0.1, 0.3, 0.5]
}

sweep = DictSweep(parameters=params, strategy=StrategyName.PRODUCT)
project = Project(root="experiments/grid_search").ensure_folder()

# Run grid search with auto-resume
for config in sweep.generate():
    session = project.session(
        "train",
        params=config,
        existing_run_strategy=ExistingRun.RESUME
    )

    if session.is_done():
        print(f"Skipping completed: {config}")
        continue

    print(f"Running: {config}")
    session.start()

    # Your training code here
    # train_model(config, checkpoint=session.path("model.pt"))

    session.done()
```

---

## Cheat Sheet

```python
from pycaddy.sweeper import DictSweep, ChainSweep, StrategyName

# Basic sweep (Cartesian product)
sweep = DictSweep(
    parameters={'lr': [0.01, 0.001], 'bs': [16, 32]},
    strategy=StrategyName.PRODUCT
)
for config in sweep.generate():
    print(config)

# With constants
sweep = DictSweep(
    parameters={'lr': [0.01, 0.001]},
    constants={'epochs': 100, 'seed': 42}
)

# Zip strategy (paired)
sweep = DictSweep(
    parameters={'model': ['small', 'large'], 'bs': [64, 32]},
    strategy=StrategyName.ZIP
)

# Chain multiple sweeps
sweep1 = DictSweep(parameters={'a': [1, 2]})
sweep2 = DictSweep(parameters={'b': [3, 4]})
chain = ChainSweep(sweepers=[sweep1, sweep2])
for config in chain.generate():
    print(config)  # Merges both sweeps

# Count combinations
params = {'lr': [0.01, 0.001], 'bs': [16, 32, 64]}
sweep = DictSweep(parameters=params, strategy=StrategyName.PRODUCT)
total = len(params['lr']) * len(params['bs'])  # 2 × 3 = 6
```

---

## Advanced: Nested Parameters

The sweeper supports nested parameter dictionaries using dot notation:

```python
from pycaddy.sweeper import DictSweep, StrategyName

params = {
    'model.layers': [3, 5],
    'model.hidden_size': [128, 256],
    'optimizer.lr': [0.01, 0.001]
}

sweep = DictSweep(parameters=params, strategy=StrategyName.PRODUCT)

for config in sweep.generate():
    print(config)
    # {
    #   'model': {'layers': 3, 'hidden_size': 128},
    #   'optimizer': {'lr': 0.01}
    # }
```

---

## See Also

- [Project & Session API](project-session.md) — High-level experiment management
- [Ledger API](ledger.md) — Low-level run registry
- [Main README](../README.md) — Project overview
