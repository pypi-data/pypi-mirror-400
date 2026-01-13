# Qualia Flow

MLflow experiment exploration and notebook generation toolkit.

## Overview

Qualia Flow provides tools for discovering, exploring, and documenting MLflow experiments through automatically generated Jupyter notebooks.

## Features

- 🔍 **Automatic Discovery** - Scans MLflow tracking server for experiments and runs
- 🎯 **Interactive Selection** - User-friendly CLI for choosing what to explore
- 📓 **Notebook Generation** - Creates ready-to-use Jupyter notebooks
- 📊 **Comparison Tools** - Built-in parameter and metric comparison
- 💻 **Programmatic API** - Use in your own scripts

## Installation

From the main project:

```bash
pip install -e .
```

Or install qualia_flow as a standalone package:

```bash
cd packages/qualia_flow
pip install -e .
```

## Quick Start

### Interactive CLI

```bash
# Generate an observational notebook
qualia-flow create

# Or with demo data
qualia-flow demo 3  # Create 3 demo runs
qualia-flow create
```

### Programmatic Usage

```python
from qualia_flow import ArtifactExplorer, NotebookGenerator

# Explore artifacts
explorer = ArtifactExplorer(tracking_uri="./mlruns")
experiments = explorer.list_experiments()
runs = explorer.list_runs([exp['id'] for exp in experiments])

# Generate notebook
generator = NotebookGenerator(tracking_uri="./mlruns")
generator.generate_notebook(
    selected_runs=runs,
    output_path="my_analysis.ipynb",
    title="My Analysis"
)
```

## Documentation

- [Quick Start Guide](docs/quick_start_observational_notebooks.md)
- [Full Documentation](docs/observational_notebooks.md)
- [API Reference](docs/QUICK_REFERENCE.md)
- [Architecture](docs/ARCHITECTURE_DIAGRAM.md)

## Examples

See [examples/](examples/) for usage patterns:
- Basic notebook generation
- Filtering runs by criteria
- Comparing best runs by metric
- Getting run details
- Custom notebook structures

## Project Structure

```
qualia_flow/
├── __init__.py           # Package exports
├── cli.py                # Command-line interface
├── explorer.py           # MLflow artifact exploration
├── generator.py          # Notebook generation
├── scripts/              # Standalone scripts
├── examples/             # Usage examples
└── docs/                 # Documentation
```

## Commands

- `qualia-flow create` - Interactive notebook generator
- `qualia-flow demo [N]` - Create N demo MLflow runs

## License

Part of the Qualia Lab project.
