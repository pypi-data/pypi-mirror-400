"""
Prism - Standalone Experiment Parameter Sweep Manager

A self-contained module for generating, managing, and executing parameter sweeps
across experiments using configuration inheritance and overrides.

This module is designed to be:
- Standalone: No external dependencies on specific project structures
- Project-agnostic: Works with any training script via prism.project.yaml
- Flexible: YAML-based schema and validation rules

## Quick Start

### 1. Initialize a project

    prism init

This creates a `prism.project.yaml` file defining:
- Training script path and arguments
- Config/output directories
- Metrics capture configuration

### 2. Create a study

    from prism import Project, PrismManager
    
    project = Project.load("prism.project.yaml")
    
    manager = PrismManager(
        base_config_path="configs/base.yaml",
        prism_config_path=["studies/sweep.yaml"],
        study_name="my_experiment",
        output_dir=project.output_dir
    )
    manager.expand_configs()

### 3. Execute experiments

    from prism import Executor
    
    executor = Executor(
        train_command=project.get_train_command("{config_path}"),
        working_dir=project.config.project_root
    )
    
    manager.execute_all(executor=executor)

### 4. Or use the interactive TUI

    prism tui

## Modules

- `manager`: Core sweep manager and state management
- `project`: Project configuration and discovery
- `executor`: Training execution and metrics capture
- `config_validator`: YAML-based config validation
- `schema_parser`: Schema definition parsing
- `rules_engine`: Validation rules engine
- `tui`: Interactive terminal interface
- `cli`: Command-line interface
- `utils`: Internal utilities
"""

# Core components
from .manager import PrismManager, ExperimentStatus, ExperimentRecord, PrismState

# Project management
from .project import Project, ProjectConfig, find_project, ProjectNotFoundError

# Execution
from .executor import Executor, ExecutionResult, DryRunExecutor

# Utils
from .utils import (
    PrintContext,
    deep_get,
    deep_set,
    deep_merge,
)

# CLI entry point
from .cli import main as cli_main

__all__ = [
    # Manager
    "PrismManager",
    "ExperimentStatus",
    "ExperimentRecord",
    "PrismState",
    
    # Project
    "Project",
    "ProjectConfig",
    "find_project",
    "ProjectNotFoundError",
    
    # Executor
    "Executor",
    "ExecutionResult",
    "DryRunExecutor",
    
    # Utils
    "PrintContext",
    "deep_get",
    "deep_set",
    "deep_merge",
    
    # CLI
    "cli_main",
]

__version__ = "0.1.4"
