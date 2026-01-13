"""MLflow artifact exploration module."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import mlflow
from mlflow.tracking import MlflowClient


class ArtifactExplorer:
    """Explore and select MLflow artifacts interactively."""

    def __init__(self, tracking_uri: Optional[str] = None):
        """Initialize the artifact explorer.
        
        Args:
            tracking_uri: MLflow tracking URI. If None, uses environment or defaults.
        """
        self.tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI", 
            str(Path(__file__).parent.parent.parent / "mlruns")
        )
        mlflow.set_tracking_uri(self.tracking_uri)
        self.client = MlflowClient(tracking_uri=self.tracking_uri)
        
    def list_experiments(self) -> List[Dict[str, Any]]:
        """List all available experiments.
        
        Returns:
            List of experiment dictionaries with id, name, and artifact location.
        """
        experiments = self.client.search_experiments()
        return [
            {
                "id": exp.experiment_id,
                "name": exp.name,
                "artifact_location": exp.artifact_location,
                "lifecycle_stage": exp.lifecycle_stage,
            }
            for exp in experiments
            if exp.lifecycle_stage == "active"
        ]
    
    def list_runs(self, experiment_ids: List[str]) -> List[Dict[str, Any]]:
        """List all runs for given experiments.
        
        Args:
            experiment_ids: List of experiment IDs to search.
            
        Returns:
            List of run dictionaries with relevant metadata.
        """
        runs = []
        for exp_id in experiment_ids:
            exp_runs = self.client.search_runs(
                experiment_ids=[exp_id],
                order_by=["start_time DESC"]
            )
            for run in exp_runs:
                runs.append({
                    "run_id": run.info.run_id,
                    "experiment_id": run.info.experiment_id,
                    "status": run.info.status,
                    "start_time": datetime.fromtimestamp(run.info.start_time / 1000),
                    "end_time": datetime.fromtimestamp(run.info.end_time / 1000) if run.info.end_time else None,
                    "artifact_uri": run.info.artifact_uri,
                    "params": run.data.params,
                    "metrics": run.data.metrics,
                    "tags": run.data.tags,
                })
        return runs
    
    def list_artifacts(self, run_id: str, path: str = "") -> List[Dict[str, Any]]:
        """List artifacts for a specific run.
        
        Args:
            run_id: MLflow run ID.
            path: Subpath within artifacts to list.
            
        Returns:
            List of artifact dictionaries with path, size, and type info.
        """
        artifacts = []
        try:
            for artifact in self.client.list_artifacts(run_id, path):
                artifacts.append({
                    "path": artifact.path,
                    "is_dir": artifact.is_dir,
                    "file_size": artifact.file_size if not artifact.is_dir else None,
                })
        except (mlflow.exceptions.MlflowException, IOError) as e:
            print(f"Warning: Could not list artifacts for run {run_id}: {e}")
        return artifacts
    
    def get_run_details(self, run_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific run.
        
        Args:
            run_id: MLflow run ID.
            
        Returns:
            Dictionary with comprehensive run information.
        """
        run = self.client.get_run(run_id)
        return {
            "run_id": run.info.run_id,
            "experiment_id": run.info.experiment_id,
            "status": run.info.status,
            "start_time": datetime.fromtimestamp(run.info.start_time / 1000),
            "end_time": datetime.fromtimestamp(run.info.end_time / 1000) if run.info.end_time else None,
            "artifact_uri": run.info.artifact_uri,
            "params": dict(run.data.params),
            "metrics": dict(run.data.metrics),
            "tags": dict(run.data.tags),
            "artifacts": self.list_artifacts(run_id),
        }
