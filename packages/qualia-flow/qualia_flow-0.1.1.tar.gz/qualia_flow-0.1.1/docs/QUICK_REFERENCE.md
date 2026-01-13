# Observational Notebook System - Quick Reference

## 🚀 Getting Started

```bash
# 1. Create demo runs (optional - for testing)
python -m qualia_lab.scripts.create_demo_runs 3

# 2. Generate an observational notebook
create-observation-notebook

# 3. Open and explore
jupyter notebook notebooks/your_notebook.ipynb
```

## 📁 File Structure

```
qualia-lab/
├── qualia_lab/
│   └── scripts/
│       ├── create_observational_notebook.py  # Main interactive script
│       └── create_demo_runs.py               # Demo data generator
├── examples/
│   └── programmatic_usage.py                 # Code examples
├── notebooks/
│   ├── README.md                             # Notebooks directory guide
│   └── [generated notebooks].ipynb           # Your generated notebooks
├── docs/
│   ├── observational_notebooks.md            # Full documentation
│   ├── quick_start_observational_notebooks.md # Tutorial
│   └── IMPLEMENTATION_OBSERVATIONAL_NOTEBOOKS.md # Technical details
└── pyproject.toml                             # Added script entry points
```

## 🎯 Commands

### Command Line Interface

| Command | Description |
|---------|-------------|
| `create-observation-notebook` | Launch interactive notebook generator |
| `create-demo-runs` | Create sample MLflow runs for testing |
| `python -m qualia_lab.scripts.create_demo_runs 5` | Create 5 demo runs |

### Programmatic API

```python
from qualia_lab.scripts.create_observational_notebook import (
    ArtifactExplorer,
    NotebookGenerator
)

# Explore artifacts
explorer = ArtifactExplorer(tracking_uri="./mlruns")
experiments = explorer.list_experiments()
runs = explorer.list_runs([exp['id'] for exp in experiments])

# Generate notebook
generator = NotebookGenerator(tracking_uri="./mlruns")
generator.generate_notebook(
    selected_runs=runs,
    output_path=Path("notebooks/my_analysis.ipynb"),
    title="My Analysis"
)
```

## 🔍 Interactive Flow

```
┌─────────────────────────────────────────┐
│  create-observation-notebook            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Enter MLflow Tracking URI              │
│  (default: ./mlruns)                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  📊 Discovering experiments...          │
│                                         │
│  Found 2 experiment(s):                 │
│    1. gemma3-finetuning-base           │
│    2. demo-observational-notebook      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Select experiment(s)                   │
│  (numbers, comma-separated, or 'all')   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  🔍 Discovering runs...                 │
│                                         │
│  Found 3 run(s):                        │
│    1. ✅ a1b2c3d4... (Params: 5)       │
│    2. ✅ e5f6g7h8... (Params: 5)       │
│    3. ❌ i9j0k1l2... (Params: 5)       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Select run(s)                          │
│  (numbers, comma-separated, or 'all')   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Configure Notebook                     │
│  - Filename (default: auto-generated)   │
│  - Title (default: generic)             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  📝 Generating notebook...              │
│  ✅ Notebook created!                   │
└─────────────────────────────────────────┘
```

## 📓 Generated Notebook Structure

```
┌───────────────────────────────────────────────────┐
│ # [Your Custom Title]                             │
│                                                   │
│ Generated: 2026-01-06 14:30:00                   │
│ Tracking URI: ./mlruns                           │
│ Number of runs: 3                                │
├───────────────────────────────────────────────────┤
│ ## Setup and Imports                             │
│ [code] import mlflow, pandas, etc.               │
├───────────────────────────────────────────────────┤
│ ## Configuration                                 │
│ [code] Set tracking URI, run IDs                 │
├───────────────────────────────────────────────────┤
│ ## Load Selected Runs                            │
│ [code] Load all run metadata                     │
├───────────────────────────────────────────────────┤
│ ## Runs Overview                                 │
│ [code] Display summary DataFrame                 │
├───────────────────────────────────────────────────┤
│ ## Run 1: a1b2c3d4...                           │
│ [code] Show params, metrics, artifacts           │
├───────────────────────────────────────────────────┤
│ ## Run 2: e5f6g7h8...                           │
│ [code] Show params, metrics, artifacts           │
├───────────────────────────────────────────────────┤
│ ## Run 3: i9j0k1l2...                           │
│ [code] Show params, metrics, artifacts           │
├───────────────────────────────────────────────────┤
│ ## Compare Runs                                  │
│ [code] Side-by-side comparison tables            │
├───────────────────────────────────────────────────┤
│ ## Free-form Exploration                         │
│ [code] Empty cell for custom analysis            │
└───────────────────────────────────────────────────┘
```

## 💡 Use Cases

| Scenario | What to Do |
|----------|------------|
| **After Training** | Select recent runs → Compare metrics → Document best config |
| **Model Selection** | Filter by metric → Compare top N → Choose winner |
| **Debugging** | Select failed run + successful run → Compare params |
| **Documentation** | Select all runs from experiment → Generate report |
| **Exploration** | Select all → Browse in notebook → Add custom analysis |

## 🎨 Customization Examples

### Filter Runs by Metric
```python
from examples.programmatic_usage import example_compare_best_runs
example_compare_best_runs()  # Creates notebook with top 5 runs
```

### Filter Runs by Parameter
```python
from examples.programmatic_usage import example_filtered_runs
example_filtered_runs()  # Filters by learning_rate parameter
```

### Get Run Details
```python
from examples.programmatic_usage import example_get_run_details
example_get_run_details()  # Prints comprehensive run information
```

## 🔧 Advanced Usage

### Custom Tracking URI
```python
explorer = ArtifactExplorer(tracking_uri="sqlite:///custom.db")
```

### Remote MLflow Server
```python
explorer = ArtifactExplorer(tracking_uri="http://mlflow-server:5000")
```

### Batch Generation
```python
for experiment in experiments:
    runs = explorer.list_runs([experiment['id']])
    generator.generate_notebook(
        selected_runs=runs,
        output_path=Path(f"notebooks/{experiment['name']}.ipynb"),
        title=f"Analysis: {experiment['name']}"
    )
```

## 📚 Documentation Links

- **Quick Start:** `docs/quick_start_observational_notebooks.md`
- **Full Guide:** `docs/observational_notebooks.md`
- **Implementation:** `docs/IMPLEMENTATION_OBSERVATIONAL_NOTEBOOKS.md`
- **Examples:** `examples/programmatic_usage.py`

## ⚙️ Technical Details

### Classes

**ArtifactExplorer**
- `list_experiments()` → List[Dict]
- `list_runs(experiment_ids)` → List[Dict]
- `list_artifacts(run_id, path)` → List[Dict]
- `get_run_details(run_id)` → Dict

**NotebookGenerator**
- `generate_notebook(selected_runs, output_path, title)` → None

### Dependencies
- `mlflow` - Tracking client
- `pandas` - Data manipulation
- `jupyter` - Running notebooks
- Standard library: `json`, `pathlib`, `datetime`

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No experiments found" | Check tracking URI, ensure runs exist |
| "Cannot import mlflow" | Install dependencies: `uv sync` |
| "Permission denied" | Check write permissions on notebooks/ |
| Script not found | Reinstall: `pip install -e .` |

## 🚦 Status Indicators

- ✅ **FINISHED** - Run completed successfully
- ⏳ **RUNNING** - Run is currently executing
- ❌ **FAILED** - Run failed or was terminated

## 📊 Example Output

```
======================================================================
MLflow Observational Notebook Generator
======================================================================

Enter MLflow tracking URI (or press Enter for default): 
Using default: /Users/user/project/mlruns

📊 Discovering experiments...

Found 1 experiment(s):
  1. demo-observational-notebook (ID: 1)

Select experiment(s) by number (comma-separated, or 'all'): 1

🔍 Discovering runs...

Found 3 run(s):
  1. ✅ a1b2c3d4... - Started: 2026-01-06 14:30
      Params: 5 | Metrics: 6
  2. ✅ e5f6g7h8... - Started: 2026-01-06 14:30
      Params: 5 | Metrics: 6
  3. ✅ i9j0k1l2... - Started: 2026-01-06 14:30
      Params: 5 | Metrics: 6

Select run(s) by number (comma-separated, or 'all'): all

Notebook name (default: observation_20260106_143000.ipynb): demo

Notebook title (default: MLflow Artifact Exploration): Demo Analysis

📝 Generating notebook...

✅ Notebook created: notebooks/demo.ipynb

✨ Done! You can now open the notebook and start exploring.
   jupyter notebook notebooks/demo.ipynb
```
