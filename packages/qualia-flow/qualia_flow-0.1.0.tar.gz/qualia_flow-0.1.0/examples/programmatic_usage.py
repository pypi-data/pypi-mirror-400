"""Example: Using the Observational Notebook System Programmatically

This script demonstrates how to use the ArtifactExplorer and NotebookGenerator
classes directly in your own code, without the interactive CLI.
"""

from pathlib import Path

from qualia_flow import ArtifactExplorer, NotebookGenerator


def example_basic_usage():
    """Basic example: Generate a notebook for all runs in an experiment."""

    # Initialize explorer
    explorer = ArtifactExplorer(tracking_uri="./mlruns")

    # Get experiments
    experiments = explorer.list_experiments()
    if not experiments:
        print("No experiments found!")
        return

    print(f"Found {len(experiments)} experiments")

    # Get all runs from the first experiment
    first_exp = experiments[0]
    runs = explorer.list_runs([first_exp["id"]])

    if not runs:
        print("No runs found!")
        return

    print(f"Found {len(runs)} runs in '{first_exp['name']}'")

    # Generate notebook
    generator = NotebookGenerator(tracking_uri="./mlruns")
    output_path = Path("notebooks/programmatic_example.ipynb")

    generator.generate_notebook(
        selected_runs=runs,
        output_path=output_path,
        title=f"Analysis of {first_exp['name']}",
    )

    print(f"✅ Notebook created: {output_path}")


def example_filtered_runs():
    """Advanced example: Filter runs by status and parameters."""

    explorer = ArtifactExplorer(tracking_uri="./mlruns")

    # Get experiments
    experiments = explorer.list_experiments()
    if not experiments:
        print("No experiments found!")
        return

    # Get runs from all experiments
    exp_ids = [exp["id"] for exp in experiments]
    all_runs = explorer.list_runs(exp_ids)

    # Filter: only finished runs
    finished_runs = [run for run in all_runs if run["status"] == "FINISHED"]

    print(f"Found {len(finished_runs)} finished runs out of {len(all_runs)} total")

    # Further filter: runs with specific parameter value
    # (This is just an example - adapt to your needs)
    filtered_runs = [
        run
        for run in finished_runs
        if run["params"].get("learning_rate")
        == "0.0005"  # MLflow stores params as strings
    ]

    print(f"Found {len(filtered_runs)} runs with learning_rate=0.0005")

    if not filtered_runs:
        print("No runs matched the criteria!")
        return

    # Generate notebook for filtered runs
    generator = NotebookGenerator(tracking_uri="./mlruns")
    output_path = Path("notebooks/filtered_runs.ipynb")

    generator.generate_notebook(
        selected_runs=filtered_runs,
        output_path=output_path,
        title="Filtered Runs Analysis (lr=0.0005)",
    )

    print(f"✅ Notebook created: {output_path}")


def example_compare_best_runs():
    """Example: Create notebook comparing top N runs by a metric."""

    explorer = ArtifactExplorer(tracking_uri="./mlruns")

    # Get all runs
    experiments = explorer.list_experiments()
    if not experiments:
        print("No experiments found!")
        return

    exp_ids = [exp["id"] for exp in experiments]
    all_runs = explorer.list_runs(exp_ids)

    # Filter finished runs that have the metric we care about
    metric_name = "final_accuracy"
    runs_with_metric = [
        run
        for run in all_runs
        if run["status"] == "FINISHED" and metric_name in run["metrics"]
    ]

    if not runs_with_metric:
        print(f"No finished runs with '{metric_name}' metric found!")
        return

    # Sort by metric (descending - higher is better)
    sorted_runs = sorted(
        runs_with_metric, key=lambda x: x["metrics"][metric_name], reverse=True
    )

    # Take top 5
    top_n = 5
    best_runs = sorted_runs[:top_n]

    print(f"Top {len(best_runs)} runs by {metric_name}:")
    for i, run in enumerate(best_runs, 1):
        score = run["metrics"][metric_name]
        run_id_short = run["run_id"][:8]
        print(f"  {i}. {run_id_short}... - {metric_name}: {score:.4f}")

    # Generate comparison notebook
    generator = NotebookGenerator(tracking_uri="./mlruns")
    output_path = Path(f"notebooks/top_{top_n}_runs_{metric_name}.ipynb")

    generator.generate_notebook(
        selected_runs=best_runs,
        output_path=output_path,
        title=f"Top {top_n} Runs by {metric_name}",
    )

    print(f"✅ Notebook created: {output_path}")


def example_get_run_details():
    """Example: Get detailed information about specific runs."""

    explorer = ArtifactExplorer(tracking_uri="./mlruns")

    # You would typically know these run IDs from somewhere
    # For demo, we'll just get the first available run
    experiments = explorer.list_experiments()
    if not experiments:
        print("No experiments found!")
        return

    runs = explorer.list_runs([experiments[0]["id"]])
    if not runs:
        print("No runs found!")
        return

    run_id = runs[0]["run_id"]

    # Get comprehensive details
    details = explorer.get_run_details(run_id)

    print(f"\nRun ID: {run_id}")
    print(f"Status: {details['status']}")
    print(f"Start: {details['start_time']}")
    print(f"\nParameters ({len(details['params'])}):")
    for key, value in details["params"].items():
        print(f"  {key}: {value}")

    print(f"\nMetrics ({len(details['metrics'])}):")
    for key, value in details["metrics"].items():
        print(f"  {key}: {value}")

    print(f"\nArtifacts ({len(details['artifacts'])}):")
    for artifact in details["artifacts"]:
        size_str = (
            f"({artifact['file_size']} bytes)" if artifact["file_size"] else "(dir)"
        )
        print(f"  {artifact['path']} {size_str}")


def example_custom_notebook_structure():
    """Example: Build a custom notebook with additional cells."""

    # This demonstrates how you might extend the NotebookGenerator
    # for custom notebook layouts

    explorer = ArtifactExplorer(tracking_uri="./mlruns")
    experiments = explorer.list_experiments()

    if not experiments:
        print("No experiments found!")
        return

    runs = explorer.list_runs([experiments[0]["id"]])[:3]  # Just first 3 runs

    if not runs:
        print("No runs found!")
        return

    generator = NotebookGenerator(tracking_uri="./mlruns")

    # Generate the standard notebook first
    output_path = Path("notebooks/custom_example.ipynb")
    generator.generate_notebook(
        selected_runs=runs, output_path=output_path, title="Custom Analysis Notebook"
    )

    print(f"✅ Base notebook created: {output_path}")
    print("\nTo customize further, you can:")
    print("1. Open the notebook in Jupyter")
    print("2. Add your own cells for custom analysis")
    print("3. Modify the NotebookGenerator class to add custom cell templates")


if __name__ == "__main__":
    print("Observational Notebook System - Programmatic Examples")
    print("=" * 60)
    print()

    # Uncomment the example you want to run:

    # Example 1: Basic usage
    # example_basic_usage()

    # Example 2: Filter runs by criteria
    # example_filtered_runs()

    # Example 3: Compare best runs by metric
    # example_compare_best_runs()

    # Example 4: Get detailed run information
    # example_get_run_details()

    # Example 5: Custom notebook structure
    # example_custom_notebook_structure()

    print("\nUncomment one of the example functions above to run it!")
    print("You can also import these functions in your own scripts:")
    print()
    print("  from examples.programmatic_usage import example_basic_usage")
    print("  example_basic_usage()")
    print("  example_basic_usage()")
