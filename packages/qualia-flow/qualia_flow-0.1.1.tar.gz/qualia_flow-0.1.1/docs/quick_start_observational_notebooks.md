# Quick Start: Observational Notebooks

## Installation

Make sure the project is installed:

```bash
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

## Try it Out

### 1. Create Demo MLflow Runs

First, create some sample runs to explore:

```bash
python -m qualia_lab.scripts.create_demo_runs
```

This creates 3 demo runs with random parameters and metrics in a new experiment called `demo-observational-notebook`.

You can specify the number of runs:

```bash
python -m qualia_lab.scripts.create_demo_runs 5
```

### 2. Run the Interactive Notebook Generator

```bash
create-observation-notebook
```

Or:

```bash
python -m qualia_lab.scripts.create_observational_notebook
```

### 3. Follow the Prompts

**Tracking URI:**
```
Enter MLflow tracking URI (or press Enter for default): 
# Press Enter to use ./mlruns
```

**Select Experiment:**
```
Found 1 experiment(s):
  1. demo-observational-notebook (ID: 1)

Select experiment(s) by number (comma-separated, or 'all'): 1
```

**Select Runs:**
```
Found 3 run(s):
  1. ✅ a1b2c3d4... - Started: 2026-01-06 14:30
      Params: 5 | Metrics: 6
  2. ✅ e5f6g7h8... - Started: 2026-01-06 14:30
      Params: 5 | Metrics: 6
  3. ✅ i9j0k1l2... - Started: 2026-01-06 14:30
      Params: 5 | Metrics: 6

Select run(s) by number (comma-separated, or 'all'): all
```

**Configure Notebook:**
```
Notebook name (default: observation_20260106_143000.ipynb): demo_exploration

Notebook title (default: MLflow Artifact Exploration): My First Observational Notebook
```

### 4. Open the Generated Notebook

```bash
jupyter notebook notebooks/demo_exploration.ipynb
```

Or just navigate to it in VS Code!

## What You'll See

The generated notebook includes:

1. **Imports and Setup** - Ready to run
2. **Configuration** - Your selected runs
3. **Data Loading** - Loads all run metadata
4. **Overview Table** - Quick summary of all runs
5. **Individual Run Details** - Deep dive into each run
6. **Comparison** - Side-by-side analysis (if multiple runs)
7. **Free Exploration** - Your own analysis space

## Working with Real Experiments

To use with your actual training runs:

1. Run your training pipeline (it logs to MLflow)
2. Use `create-observation-notebook` 
3. Select your experiment (e.g., "gemma3-finetuning-base")
4. Choose the runs you want to analyze
5. Explore!

## Tips

### Multiple Experiments

Select multiple experiments at once:
```
Select experiment(s) by number (comma-separated, or 'all'): 1,2,3
```

### Specific Runs

Pick just the runs you care about:
```
Select run(s) by number (comma-separated, or 'all'): 1,3,5
```

### Different Tracking URIs

Point to different MLflow servers:
```
Enter MLflow tracking URI: ./data/mlflow/mlflow.db
```

Or:
```
Enter MLflow tracking URI: http://localhost:5000
```

### Notebook Organization

Notebooks are saved in `notebooks/` directory by default. You can organize them:

```
notebooks/
  gemma3_comparison.ipynb
  experiment_v2_analysis.ipynb
  best_runs_2026.ipynb
```

## Example Workflow

```bash
# 1. Create some demo data
python -m qualia_lab.scripts.create_demo_runs 5

# 2. Generate observation notebook
create-observation-notebook
# (follow prompts)

# 3. Open and explore
jupyter notebook notebooks/my_notebook.ipynb
```

## Next Steps

- Read the full documentation: `docs/observational_notebooks.md`
- Customize the generated notebooks
- Add your own visualizations
- Share notebooks with your team
