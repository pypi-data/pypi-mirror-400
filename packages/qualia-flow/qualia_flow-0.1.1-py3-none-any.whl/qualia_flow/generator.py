"""Jupyter notebook generation module."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class NotebookGenerator:
    """Generate Jupyter notebooks for artifact exploration."""
    
    def __init__(self, tracking_uri: str):
        """Initialize notebook generator.
        
        Args:
            tracking_uri: MLflow tracking URI.
        """
        self.tracking_uri = tracking_uri
        
    def generate_notebook(
        self,
        selected_runs: List[Dict[str, Any]],
        output_path: Path,
        title: str = "MLflow Artifact Exploration"
    ) -> None:
        """Generate a Jupyter notebook for exploring selected runs.
        
        Args:
            selected_runs: List of run dictionaries to include.
            output_path: Path where to save the notebook.
            title: Title for the notebook.
        """
        cells = []
        
        # Title cell
        cells.append(self._create_markdown_cell(f"# {title}\n\n"))
        cells.append(self._create_markdown_cell(
            f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**MLflow Tracking URI:** `{self.tracking_uri}`\n\n"
            f"**Number of runs:** {len(selected_runs)}"
        ))
        
        # Import cell
        cells.append(self._create_markdown_cell("## Setup and Imports"))
        cells.append(self._create_code_cell(self._generate_imports()))
        
        # Configuration cell
        cells.append(self._create_markdown_cell("## Configuration"))
        cells.append(self._create_code_cell(self._generate_config(selected_runs)))
        
        # Load runs cell
        cells.append(self._create_markdown_cell("## Load Selected Runs"))
        cells.append(self._create_code_cell(self._generate_load_runs()))
        
        # Overview cell
        cells.append(self._create_markdown_cell("## Runs Overview"))
        cells.append(self._create_code_cell(self._generate_overview_code()))
        
        # Individual run sections
        for idx, run in enumerate(selected_runs, 1):
            cells.append(self._create_markdown_cell(f"## Run {idx}: `{run['run_id'][:8]}...`"))
            cells.append(self._create_code_cell(self._generate_run_exploration(idx - 1)))
        
        # Comparison section
        if len(selected_runs) > 1:
            cells.append(self._create_markdown_cell("## Compare Runs"))
            cells.append(self._create_code_cell(self._generate_comparison_code()))
        
        # Exploration section
        cells.append(self._create_markdown_cell("## Free-form Exploration\n\nUse this section for your own analysis."))
        cells.append(self._create_code_cell("# Your exploration code here\n"))
        
        # Create notebook structure
        notebook = {
            "cells": cells,
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {"name": "ipython", "version": 3},
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.12.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Save notebook
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
        
        print(f"\n✅ Notebook created: {output_path}")
    
    def _create_markdown_cell(self, content: str) -> Dict[str, Any]:
        """Create a markdown cell."""
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": content.split('\n')
        }
    
    def _create_code_cell(self, content: str) -> Dict[str, Any]:
        """Create a code cell."""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": content.split('\n')
        }
    
    def _generate_imports(self) -> str:
        """Generate import statements."""
        return """import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import json
from pathlib import Path
from datetime import datetime

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)"""
    
    def _generate_config(self, selected_runs: List[Dict[str, Any]]) -> str:
        """Generate configuration code."""
        run_ids = [run['run_id'] for run in selected_runs]
        return f"""# MLflow Configuration
TRACKING_URI = "{self.tracking_uri}"
mlflow.set_tracking_uri(TRACKING_URI)
client = MlflowClient(tracking_uri=TRACKING_URI)

# Selected run IDs
RUN_IDS = {json.dumps(run_ids, indent=4)}

print(f"Tracking URI: {{TRACKING_URI}}")
print(f"Number of runs: {{len(RUN_IDS)}}")"""
    
    def _generate_load_runs(self) -> str:
        """Generate code to load runs."""
        return """# Load all selected runs
runs = []
for run_id in RUN_IDS:
    try:
        run = client.get_run(run_id)
        runs.append({
            'run_id': run.info.run_id,
            'experiment_id': run.info.experiment_id,
            'status': run.info.status,
            'start_time': datetime.fromtimestamp(run.info.start_time / 1000),
            'end_time': datetime.fromtimestamp(run.info.end_time / 1000) if run.info.end_time else None,
            'artifact_uri': run.info.artifact_uri,
            'params': dict(run.data.params),
            'metrics': dict(run.data.metrics),
            'tags': dict(run.data.tags),
        })
        print(f"✓ Loaded run: {run_id[:8]}...")
    except Exception as e:
        print(f"✗ Failed to load run {run_id[:8]}...: {e}")

print(f"\\nSuccessfully loaded {len(runs)} run(s)")"""
    
    def _generate_overview_code(self) -> str:
        """Generate overview display code."""
        return """# Create overview DataFrame
overview_data = []
for run in runs:
    overview_data.append({
        'Run ID (short)': run['run_id'][:8],
        'Status': run['status'],
        'Start Time': run['start_time'].strftime('%Y-%m-%d %H:%M'),
        'Duration (min)': round((run['end_time'] - run['start_time']).total_seconds() / 60, 2) if run['end_time'] else None,
        'Num Params': len(run['params']),
        'Num Metrics': len(run['metrics']),
    })

df_overview = pd.DataFrame(overview_data)
display(df_overview)"""
    
    def _generate_run_exploration(self, run_index: int) -> str:
        """Generate code to explore a specific run."""
        return f"""# Explore run {run_index + 1}
run = runs[{run_index}]

print(f"Run ID: {{run['run_id']}}")
print(f"Status: {{run['status']}}")
print(f"Artifact URI: {{run['artifact_uri']}}")
print()

# Display parameters
print("Parameters:")
params_df = pd.DataFrame(list(run['params'].items()), columns=['Parameter', 'Value'])
display(params_df)

print()

# Display metrics
print("Metrics:")
metrics_df = pd.DataFrame(list(run['metrics'].items()), columns=['Metric', 'Value'])
display(metrics_df)

# List artifacts
print("\\nArtifacts:")
try:
    artifacts = client.list_artifacts(run['run_id'])
    for artifact in artifacts:
        size_str = f"({{artifact.file_size}} bytes)" if not artifact.is_dir else "(directory)"
        print(f"  - {{artifact.path}} {{size_str}}")
except Exception as e:
    print(f"  Could not list artifacts: {{e}}")"""
    
    def _generate_comparison_code(self) -> str:
        """Generate comparison code for multiple runs."""
        return """# Compare parameters across runs
params_comparison = []
for run in runs:
    row = {'run_id': run['run_id'][:8]}
    row.update(run['params'])
    params_comparison.append(row)

df_params = pd.DataFrame(params_comparison)
print("Parameter Comparison:")
display(df_params)

print()

# Compare metrics across runs
metrics_comparison = []
for run in runs:
    row = {'run_id': run['run_id'][:8]}
    row.update(run['metrics'])
    metrics_comparison.append(row)

df_metrics = pd.DataFrame(metrics_comparison)
print("Metrics Comparison:")
display(df_metrics)

# If you want to plot metrics
# import matplotlib.pyplot as plt
# df_metrics.plot(x='run_id', kind='bar', figsize=(12, 6))
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()"""
