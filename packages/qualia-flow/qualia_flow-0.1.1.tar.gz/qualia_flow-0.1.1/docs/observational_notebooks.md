# Observational Notebook Creator

An interactive script that discovers MLflow experiments and runs, then generates Jupyter notebooks for exploring artifacts and results.

## Features

- 🔍 **Automatic Discovery**: Scans MLflow tracking server for experiments and runs
- 🎯 **Interactive Selection**: Choose which experiments and runs to explore
- 📊 **Rich Metadata**: Includes parameters, metrics, and artifact information
- 📝 **Ready-to-Use Notebooks**: Pre-populated with code for immediate exploration
- 🔬 **Comparison Tools**: Built-in comparison code for multiple runs

## Usage

### Command Line

After installation, run:

```bash
create-observation-notebook
```

Or directly with Python:

```bash
python -m qualia_lab.scripts.create_observational_notebook
```

### Interactive Workflow

1. **Set Tracking URI**: Specify your MLflow tracking URI (or use default `./mlruns`)
   
2. **Select Experiments**: Choose one or more experiments to explore
   - Enter numbers comma-separated (e.g., `1,3,5`)
   - Or type `all` to select all experiments

3. **Select Runs**: Choose specific runs from the selected experiments
   - Each run shows status (✅ finished, ⏳ running, ❌ failed)
   - Shows start time, number of parameters and metrics
   - Enter numbers or `all`

4. **Configure Notebook**: 
   - Provide a filename (default: `observation_YYYYMMDD_HHMMSS.ipynb`)
   - Set a title (default: "MLflow Artifact Exploration")

5. **Explore**: The generated notebook is saved in `notebooks/` directory

## Generated Notebook Structure

The created notebook includes:

### 1. Setup and Imports
- All necessary imports (mlflow, pandas, etc.)
- Display configuration

### 2. Configuration
- MLflow tracking URI
- Selected run IDs
- Client initialization

### 3. Load Selected Runs
- Loads all metadata for selected runs
- Handles errors gracefully

### 4. Runs Overview
- DataFrame showing all runs at a glance
- Status, duration, parameter/metric counts

### 5. Individual Run Sections
For each selected run:
- Run ID and status
- Parameters table
- Metrics table
- Artifact listing

### 6. Comparison Section (if multiple runs)
- Side-by-side parameter comparison
- Metrics comparison
- Optional visualization code (commented)

### 7. Free-form Exploration
- Empty cell for your custom analysis

## Example Session

```
======================================================================
MLflow Observational Notebook Generator
======================================================================

Enter MLflow tracking URI (or press Enter for default): 
Using default: /Users/user/project/mlruns

📊 Discovering experiments...

Found 2 experiment(s):
  1. gemma3-finetuning-base (ID: 1)
  2. gemma3-finetuning-v2 (ID: 2)

Select experiment(s) by number (comma-separated, or 'all'): 1

🔍 Discovering runs...

Found 3 run(s):
  1. ✅ a1b2c3d4... - Started: 2026-01-05 14:30
      Params: 8 | Metrics: 5
  2. ✅ e5f6g7h8... - Started: 2026-01-04 09:15
      Params: 8 | Metrics: 5
  3. ❌ i9j0k1l2... - Started: 2026-01-03 16:45
      Params: 8 | Metrics: 2

Select run(s) by number (comma-separated, or 'all'): 1,2

Notebook name (default: observation_20260106_143000.ipynb): gemma3_comparison

Notebook title (default: MLflow Artifact Exploration): Gemma3 Training Comparison

📝 Generating notebook...

✅ Notebook created: notebooks/gemma3_comparison.ipynb

✨ Done! You can now open the notebook and start exploring.
   jupyter notebook notebooks/gemma3_comparison.ipynb
```

## Use Cases

### 1. Post-Training Analysis
After completing training runs, quickly create a notebook to:
- Compare hyperparameters across runs
- Analyze metric trends
- Identify best-performing configurations

### 2. Experiment Documentation
Generate notebooks that serve as documentation:
- Include all run metadata
- Add your own analysis and observations
- Share with team members

### 3. Model Selection
When choosing between multiple model versions:
- Load multiple candidate runs
- Compare metrics side-by-side
- Examine artifacts and outputs

### 4. Debugging Failed Runs
Investigate problematic runs:
- Load failed runs alongside successful ones
- Compare parameters to identify issues
- Examine partial metrics

## Tips

### Working with Large Numbers of Runs
- Use experiment filtering first
- Select specific runs instead of `all`
- Consider time ranges when browsing

### Customizing Generated Notebooks
After generation, you can:
- Add markdown explanations
- Include visualizations
- Load and analyze artifacts
- Add custom metrics calculations

### Artifact Exploration
The notebook includes artifact listing. To load artifacts:

```python
# Example: Download an artifact
artifact_path = "model/checkpoint.pt"
local_path = mlflow.artifacts.download_artifacts(
    run_id=run['run_id'],
    artifact_path=artifact_path
)
```

### Advanced Filtering
Modify the script to add filtering by:
- Date ranges
- Specific parameter values
- Metric thresholds
- Run status

## Requirements

- Python 3.12+
- mlflow
- pandas
- jupyter

All dependencies are included in the project's `pyproject.toml`.

## Architecture

### ArtifactExplorer Class
Handles MLflow API interactions:
- `list_experiments()`: Discover available experiments
- `list_runs()`: Find runs in experiments
- `list_artifacts()`: Enumerate run artifacts
- `get_run_details()`: Fetch comprehensive run info

### NotebookGenerator Class
Creates Jupyter notebooks:
- Generates proper notebook JSON structure
- Creates markdown and code cells
- Populates with run-specific code
- Handles multiple runs and comparisons

### Interactive Flow
- User-friendly prompts
- Input validation
- Error handling
- Progress feedback

## Future Enhancements

Potential additions:
- [ ] Support for filtering runs by date range
- [ ] Automatic visualization generation
- [ ] Template system for custom notebook layouts
- [ ] Integration with dataset artifacts
- [ ] Metric history plots (not just final values)
- [ ] Diff view for parameter changes
- [ ] Export to HTML/PDF for sharing
