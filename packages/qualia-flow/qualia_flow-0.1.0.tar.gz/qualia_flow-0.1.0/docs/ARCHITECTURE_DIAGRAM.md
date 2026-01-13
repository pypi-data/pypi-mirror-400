# Observational Notebook System - Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    OBSERVATIONAL NOTEBOOK SYSTEM                        │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────┐
│  User Interface │
└────────┬────────┘
         │
         ├─────────────────────────────────────────────────────┐
         │                                                     │
         ▼                                                     ▼
┌─────────────────────┐                          ┌──────────────────────┐
│  Interactive CLI    │                          │  Programmatic API    │
│                     │                          │                      │
│  • Prompts          │                          │  • Python imports    │
│  • Input validation │                          │  • Direct calls      │
│  • Progress display │                          │  • Batch operations  │
│  • Error handling   │                          │  • Custom filters    │
└──────────┬──────────┘                          └──────────┬───────────┘
           │                                                │
           │                                                │
           └────────────────┬───────────────────────────────┘
                            │
                            ▼
                ┌─────────────────────┐
                │  ArtifactExplorer   │
                │                     │
                │  Methods:           │
                │  • list_experiments │
                │  • list_runs        │
                │  • list_artifacts   │
                │  • get_run_details  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  MLflow Client      │
                │                     │
                │  • Search ops       │
                │  • Query metadata   │
                │  • List artifacts   │
                └──────────┬──────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │       MLflow Tracking Server         │
        │                                      │
        │  ┌────────────┐  ┌────────────┐    │
        │  │Experiment 1│  │Experiment 2│    │
        │  │            │  │            │    │
        │  │ • Run 1    │  │ • Run 4    │    │
        │  │ • Run 2    │  │ • Run 5    │    │
        │  │ • Run 3    │  │ • Run 6    │    │
        │  └────────────┘  └────────────┘    │
        └──────────────────────────────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Selected Runs      │
                │  [run1, run2, ...]  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  NotebookGenerator  │
                │                     │
                │  • generate_notebook│
                │  • create cells     │
                │  • format JSON      │
                └──────────┬──────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │      Generated Jupyter Notebook      │
        │                                      │
        │  ┌────────────────────────────┐     │
        │  │  # Title                   │     │
        │  ├────────────────────────────┤     │
        │  │  ## Setup and Imports      │     │
        │  │  [code cell]               │     │
        │  ├────────────────────────────┤     │
        │  │  ## Configuration          │     │
        │  │  [code cell]               │     │
        │  ├────────────────────────────┤     │
        │  │  ## Load Selected Runs     │     │
        │  │  [code cell]               │     │
        │  ├────────────────────────────┤     │
        │  │  ## Runs Overview          │     │
        │  │  [code cell]               │     │
        │  ├────────────────────────────┤     │
        │  │  ## Run 1: details         │     │
        │  │  [code cell]               │     │
        │  ├────────────────────────────┤     │
        │  │  ## Run 2: details         │     │
        │  │  [code cell]               │     │
        │  ├────────────────────────────┤     │
        │  │  ## Compare Runs           │     │
        │  │  [code cell]               │     │
        │  ├────────────────────────────┤     │
        │  │  ## Free Exploration       │     │
        │  │  [empty code cell]         │     │
        │  └────────────────────────────┘     │
        └──────────────────────────────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  Jupyter Notebook   │
                │                     │
                │  • Run cells        │
                │  • View results     │
                │  • Add analysis     │
                │  • Save findings    │
                └─────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                              DATA FLOW
═══════════════════════════════════════════════════════════════════════════

User Input
    ↓
[ Select Experiments ] → Query tracking server → Get experiment list
    ↓
[ Select Runs ] → Query experiments → Get run list with metadata
    ↓
[ Configure Notebook ] → Set filename, title
    ↓
[ Generate ] → Create JSON structure with cells
    ↓
[ Save .ipynb ] → Write to notebooks/ directory
    ↓
[ Open in Jupyter ] → User explores data


═══════════════════════════════════════════════════════════════════════════
                         COMPONENT INTERACTION
═══════════════════════════════════════════════════════════════════════════

┌──────────────────┐
│  create_demo_    │ ──┐
│  runs.py         │   │
└──────────────────┘   │
                       │ Creates test data
                       ▼
                   ┌────────────────┐
                   │  MLflow DB     │
                   │  (mlruns/)     │
                   └───────┬────────┘
                           │
                           │ Queries
                           ▼
┌──────────────────┐   ┌─────────────────────┐
│  create_         │──→│  ArtifactExplorer   │
│  observational_  │   │                     │
│  notebook.py     │   │  Discovers:         │
│                  │   │  - Experiments      │
│  Entry point:    │   │  - Runs             │
│  create-         │   │  - Parameters       │
│  observation-    │   │  - Metrics          │
│  notebook        │   │  - Artifacts        │
└──────────────────┘   └──────────┬──────────┘
                                  │
                                  │ Passes data to
                                  ▼
                       ┌─────────────────────┐
                       │  NotebookGenerator  │
                       │                     │
                       │  Generates:         │
                       │  - Markdown cells   │
                       │  - Code cells       │
                       │  - Notebook JSON    │
                       └──────────┬──────────┘
                                  │
                                  │ Saves to
                                  ▼
                       ┌─────────────────────┐
                       │  notebooks/         │
                       │  *.ipynb            │
                       └──────────┬──────────┘
                                  │
                                  │ Opens with
                                  ▼
                       ┌─────────────────────┐
                       │  Jupyter Notebook   │
                       │  / VS Code          │
                       └─────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                            CLASS STRUCTURE
═══════════════════════════════════════════════════════════════════════════

ArtifactExplorer
├── __init__(tracking_uri)
├── list_experiments() → List[Dict]
│   └── Returns: [{"id", "name", "artifact_location", ...}, ...]
├── list_runs(experiment_ids) → List[Dict]
│   └── Returns: [{"run_id", "params", "metrics", ...}, ...]
├── list_artifacts(run_id, path) → List[Dict]
│   └── Returns: [{"path", "is_dir", "file_size"}, ...]
└── get_run_details(run_id) → Dict
    └── Returns: {"run_id", "params", "metrics", "artifacts", ...}

NotebookGenerator
├── __init__(tracking_uri)
├── generate_notebook(selected_runs, output_path, title)
│   ├── _create_markdown_cell(content)
│   ├── _create_code_cell(content)
│   ├── _generate_imports()
│   ├── _generate_config(selected_runs)
│   ├── _generate_load_runs()
│   ├── _generate_overview_code()
│   ├── _generate_run_exploration(run_index)
│   └── _generate_comparison_code()
└── Outputs: .ipynb file with complete notebook structure


═══════════════════════════════════════════════════════════════════════════
                          FILE ORGANIZATION
═══════════════════════════════════════════════════════════════════════════

qualia-lab/
│
├── qualia_lab/scripts/          [Implementation]
│   ├── create_observational_notebook.py    (578 lines)
│   └── create_demo_runs.py                 (95 lines)
│
├── examples/                     [Usage Examples]
│   ├── __init__.py
│   └── programmatic_usage.py               (5 examples)
│
├── docs/                         [Documentation]
│   ├── observational_notebooks.md          (Full guide)
│   ├── quick_start_observational_notebooks.md
│   ├── IMPLEMENTATION_OBSERVATIONAL_NOTEBOOKS.md
│   ├── QUICK_REFERENCE.md
│   └── PROJECT_COMPLETE.md
│
├── notebooks/                    [Generated Notebooks]
│   ├── README.md
│   └── [*.ipynb files]
│
├── README.md                     [Updated with new section]
└── pyproject.toml                [Updated with entry points]
```
