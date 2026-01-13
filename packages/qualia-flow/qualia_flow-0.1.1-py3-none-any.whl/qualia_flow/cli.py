"""Command-line interface for interactive notebook generation."""

import random
import sys
from datetime import datetime
from pathlib import Path

import mlflow

from qualia_flow.env_utils import get_mlflow_env
from qualia_flow.explorer import ArtifactExplorer
from qualia_flow.generator import NotebookGenerator


def create_demo_runs(num_runs: int = 3):
    """Create demo MLflow runs for testing.

    Args:
        num_runs: Number of demo runs to create.
        tracking_uri: MLflow tracking URI.
    """
    # Import here to avoid circular dependency and keep mlflow as optional for some uses
    tracking_uri = get_mlflow_env()

    mlflow.set_tracking_uri(tracking_uri)
    experiment_name = "demo-observational-notebook"
    mlflow.set_experiment(experiment_name)

    print(f"Creating {num_runs} demo runs in experiment '{experiment_name}'...")
    print(f"Tracking URI: {tracking_uri}")
    print()

    learning_rates = [1e-4, 5e-4, 1e-3]
    batch_sizes = [16, 32, 64]

    for i in range(num_runs):
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
            with open(artifact_path, "w", encoding="utf-8") as f:
                f.write(f"Demo run {i+1}\n")
                f.write(f"Learning Rate: {lr}\n")
                f.write(f"Batch Size: {batch_size}\n")
                f.write(f"Final Accuracy: {final_accuracy:.4f}\n")

            mlflow.log_artifact(artifact_path)
            artifact_path.unlink()  # Clean up local file

            run_id = mlflow.active_run().info.run_id
            print(f"✅ Created demo run {i+1}/{num_runs}: {run_id[:8]}...")

    print()
    print("✨ Demo runs created successfully!")
    print()
    print("Now you can run:")
    print("  qualia-flow create")
    print()
    print(
        "And select the 'demo-observational-notebook' experiment to explore these runs."
    )


def interactive_selection():
    """Run interactive selection process."""
    print("=" * 70)
    print("MLflow Observational Notebook Generator")
    print("=" * 70)
    print()

    tracking_uri = get_mlflow_env()
    print()
    explorer = ArtifactExplorer(tracking_uri)

    # List experiments
    print("📊 Discovering experiments...")
    experiments = explorer.list_experiments()

    if not experiments:
        print("❌ No experiments found!")
        return

    print(f"\nFound {len(experiments)} experiment(s):")
    for idx, exp in enumerate(experiments, 1):
        print(f"  {idx}. {exp['name']} (ID: {exp['id']})")

    # Select experiments
    print()
    exp_input = input(
        "Select experiment(s) by number (comma-separated, or 'all'): "
    ).strip()

    if exp_input.lower() == "all":
        selected_experiments = experiments
    else:
        try:
            indices = [int(x.strip()) - 1 for x in exp_input.split(",")]
            selected_experiments = [experiments[i] for i in indices]
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
            return

    # List runs
    print()
    print("🔍 Discovering runs...")
    exp_ids = [exp["id"] for exp in selected_experiments]
    runs = explorer.list_runs(exp_ids)

    if not runs:
        print("❌ No runs found in selected experiments!")
        return

    print(f"\nFound {len(runs)} run(s):")
    for idx, run in enumerate(runs, 1):
        status_emoji = (
            "✅"
            if run["status"] == "FINISHED"
            else "⏳" if run["status"] == "RUNNING" else "❌"
        )
        print(
            f"  {idx}. {status_emoji} {run['run_id'][:8]}... - Started: {run['start_time'].strftime('%Y-%m-%d %H:%M')}"
        )
        print(f"      Params: {len(run['params'])} | Metrics: {len(run['metrics'])}")

    # Select runs
    print()
    run_input = input("Select run(s) by number (comma-separated, or 'all'): ").strip()

    if run_input.lower() == "all":
        selected_runs = runs
    else:
        try:
            indices = [int(x.strip()) - 1 for x in run_input.split(",")]
            selected_runs = [runs[i] for i in indices]
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
            return

    # Get notebook details
    print()
    default_name = f"observation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ipynb"
    notebook_name = input(f"Notebook name (default: {default_name}): ").strip()
    if not notebook_name:
        notebook_name = default_name

    if not notebook_name.endswith(".ipynb"):
        notebook_name += ".ipynb"

    notebook_path = Path("notebooks") / notebook_name

    title = input("Notebook title (default: MLflow Artifact Exploration): ").strip()
    if not title:
        title = "MLflow Artifact Exploration"

    # Generate notebook
    print()
    print("📝 Generating notebook...")
    generator = NotebookGenerator(tracking_uri)
    generator.generate_notebook(selected_runs, notebook_path, title)

    print()
    print("✨ Done! You can now open the notebook and start exploring.")
    print(f"   jupyter notebook {notebook_path}")


def main():
    """Main entry point."""
    try:
        # Parse command-line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == "create":
                interactive_selection()
            elif command == "demo":
                num_runs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
                tracking_uri = sys.argv[3] if len(sys.argv) > 3 else "./mlruns"
                create_demo_runs(num_runs=num_runs)
            elif command in ("-h", "--help", "help"):
                print("Qualia Flow - MLflow Observational Notebook Generator")
                print()
                print("Usage:")
                print(
                    "  qualia-flow create                    Generate observational notebook"
                )
                print(
                    "  qualia-flow demo [N] [tracking_uri]   Create N demo runs (default: 3)"
                )
                print("  qualia-flow help                      Show this help message")
                print()
                print("Examples:")
                print("  qualia-flow create")
                print("  qualia-flow demo 5")
                print("  qualia-flow demo 3 ./mlruns")
            else:
                print(f"Unknown command: {command}")
                print("Run 'qualia-flow help' for usage information")
        else:
            # Default: run interactive selection
            interactive_selection()
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
