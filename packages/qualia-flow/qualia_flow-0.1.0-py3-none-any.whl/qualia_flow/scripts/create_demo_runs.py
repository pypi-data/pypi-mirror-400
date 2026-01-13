#!/usr/bin/env python3
"""Demo script to create sample MLflow runs for testing the observational notebook creator."""

import mlflow
from pathlib import Path
import random


def create_demo_runs(mlflow_tracking_uri: str = "./mlruns", num_demo_runs: int = 3):
    """Create sample MLflow runs for demonstration.
    
    Args:
        mlflow_tracking_uri: MLflow tracking URI.
        num_demo_runs: Number of demo runs to create.
    """
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    experiment_name = "demo-observational-notebook"
    mlflow.set_experiment(experiment_name)
    
    print(f"Creating {num_demo_runs} demo runs in experiment '{experiment_name}'...")
    print(f"Tracking URI: {mlflow_tracking_uri}")
    print()
    
    learning_rates = [1e-4, 5e-4, 1e-3]
    batch_sizes = [16, 32, 64]
    
    for i in range(num_demo_runs):
        with mlflow.start_run(run_name=f"demo_run_{i+1}"):
            # Log parameters
            lr = random.choice(learning_rates)
            batch_size = random.choice(batch_sizes)
            max_steps = random.randint(1000, 5000)
            
            mlflow.log_param("learning_rate", lr)
            mlflow.log_param("batch_size", batch_size)
            mlflow.log_param("max_steps", max_steps)
            mlflow.log_param("optimizer", "adamw")
            mlflow.log_param("warmup_steps", 100)
            
            # Log metrics (simulated training)
            for step in range(0, max_steps, 100):
                # Simulate improving metrics
                train_loss = 2.0 * (1 - step / max_steps) + random.uniform(0, 0.1)
                val_loss = train_loss + random.uniform(0, 0.3)
                accuracy = 0.5 + 0.45 * (step / max_steps) + random.uniform(-0.05, 0.05)
                
                mlflow.log_metric("train_loss", train_loss, step=step)
                mlflow.log_metric("val_loss", val_loss, step=step)
                mlflow.log_metric("accuracy", accuracy, step=step)
            
            # Log final metrics
            final_train_loss = 0.15 + random.uniform(-0.05, 0.05)
            final_val_loss = 0.25 + random.uniform(-0.05, 0.05)
            final_accuracy = 0.90 + random.uniform(-0.05, 0.05)
            
            mlflow.log_metric("final_train_loss", final_train_loss)
            mlflow.log_metric("final_val_loss", final_val_loss)
            mlflow.log_metric("final_accuracy", final_accuracy)
            
            # Log tags
            mlflow.set_tag("model_type", "gemma3-1b")
            mlflow.set_tag("dataset", "demo_dataset")
            mlflow.set_tag("purpose", "demo")
            
            # Create a simple artifact
            artifact_path = Path("demo_artifact.txt")
            with open(artifact_path, 'w', encoding='utf-8') as f:
                f.write(f"Demo run {i+1}\n")
                f.write(f"Learning Rate: {lr}\n")
                f.write(f"Batch Size: {batch_size}\n")
                f.write(f"Final Accuracy: {final_accuracy:.4f}\n")
            
            mlflow.log_artifact(artifact_path)
            artifact_path.unlink()  # Clean up local file
            
            run_id = mlflow.active_run().info.run_id
            print(f"✅ Created demo run {i+1}/{num_demo_runs}: {run_id[:8]}...")
    
    print()
    print("✨ Demo runs created successfully!")
    print()
    print("Now you can run:")
    print("  create-observation-notebook")
    print()
    print("And select the 'demo-observational-notebook' experiment to explore these runs.")


if __name__ == "__main__":
    import sys
    
    num_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    tracking_uri = sys.argv[2] if len(sys.argv) > 2 else "./mlruns"
    
    create_demo_runs(mlflow_tracking_uri=tracking_uri, num_demo_runs=num_runs)
