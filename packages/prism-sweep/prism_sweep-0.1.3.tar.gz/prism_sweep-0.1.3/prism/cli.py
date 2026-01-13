"""
Prism CLI - Command Line Interface for Parameter Sweep Management

This module provides the CLI for the Prism experiment multiplexer.
It is designed to be standalone and project-agnostic.

Usage:
    # Initialize a new project
    prism init
    
    # List all existing studies
    prism list
    
    # Show status of an existing study
    prism status my_sweep
    
    # Resume an existing study (execute next pending)
    prism run --study my_sweep --next
    
    # Create a NEW study from configs
    prism create --name my_sweep --config base.yaml --prism sweep.yaml
    
    # Execute experiments
    prism run --study my_sweep --next          # Run first pending
    prism run --study my_sweep --key conf_A    # Run specific key
    prism run --study my_sweep --all           # Run all pending
    
    # Reset study
    prism reset my_sweep
    
    # Retry only failed experiments
    prism retry my_sweep
    
    # Show config for specific experiment
    prism show-config my_sweep conf_A
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from .utils import PrintContext
from .manager import (
    PrismManager,
    ExperimentStatus,
    list_studies as list_studies_state,
    load_study_by_name as load_study_by_name_state,
    study_exists,
    delete_study,
)
from .project import Project, find_project, ProjectNotFoundError
from .executor import Executor


# Create package-level printer with PRISM context
_printer = PrintContext("PRISM")
print_error = _printer.error
print_warning = _printer.warning
print_success = _printer.success
print_progress = _printer.progress
print_info = _printer.info
print_file = _printer.file


def print_progress_bar(done: int, total: int, width: int = 30) -> str:
    """Create a text-based progress bar."""
    if total == 0:
        return "[" + "─" * width + "] 0%"
    
    filled = int(width * done / total)
    bar = "█" * filled + "░" * (width - filled)
    percentage = int(100 * done / total)
    return f"[{bar}] {percentage}%"


def list_existing_studies(output_dir: Path) -> List[Dict[str, Any]]:
    """List studies (delegates to manager as source of truth)."""
    return list_studies_state(output_dir)


def print_studies_list(studies: List[Dict[str, Any]]):
    """Print a formatted list of studies."""
    if not studies:
        print_warning("No existing studies found.")
        print_info("Create a new study with: prism create --name <name> --config <base.yaml> --prism <sweep.yaml>")
        return

    print_info(f"\n{'='*80}")
    print_info("EXISTING PRISM STUDIES")
    print_info(f"{'='*80}\n")

    for i, study in enumerate(studies, 1):
        done = int(study.get("done", 0))
        total = int(study.get("total", 0))
        pending = int(study.get("pending", 0))
        failed = int(study.get("failed", 0))
        running = int(study.get("running", 0))

        progress_bar = print_progress_bar(done, total)
        status_emoji = "✅" if pending == 0 and failed == 0 else "⏳" if pending > 0 else "❌"

        print_info(f"{i}. {status_emoji} {study.get('name', '')}")
        print_info(f"   {progress_bar}  ({done}/{total} done)")
        if pending > 0:
            print_info(f"   ⏳ {pending} pending")
        if failed > 0:
            print_warning(f"   ❌ {failed} failed")
        if running > 0:
            print_info(f"   🔄 {running} running")

        path = study.get("path", "")
        if path:
            print_file(f"   📁 {path}")
        print_info(f"   🕐 Last updated: {study.get('updated_at', '')}")
        print_info("")

    print_info(f"{'='*80}")
    print_info("Quick commands:")
    print_info("  Resume:      prism run --study <name> --next")
    print_info("  Status:      prism status <name>")
    print_info("  Reset:       prism reset <name>")
    print_info("  Retry fails: prism retry <name>")
    print_info(f"{'='*80}\n")


def show_config_diff(config1: Dict[str, Any], config2: Dict[str, Any], key1: str, key2: str):
    """Show differences between two configurations."""
    def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    flat1 = flatten_dict(config1)
    flat2 = flatten_dict(config2)
    
    all_keys = set(flat1.keys()) | set(flat2.keys())
    
    print_info(f"\n{'='*60}")
    print_info(f"Config Diff: {key1} vs {key2}")
    print_info(f"{'='*60}")
    
    differences = []
    for key in sorted(all_keys):
        val1 = flat1.get(key, "<missing>")
        val2 = flat2.get(key, "<missing>")
        if val1 != val2:
            differences.append((key, val1, val2))
    
    if not differences:
        print_success("Configurations are identical!")
    else:
        print_warning(f"Found {len(differences)} difference(s):\n")
        for key, val1, val2 in differences:
            print_info(f"  {key}:")
            print_error(f"    - {key1}: {val1}")
            print_success(f"    + {key2}: {val2}")
    
    print_info(f"{'='*60}\n")


def cmd_init(args):
    """Initialize a new prism project."""
    target_dir = Path(args.directory).resolve()
    
    # Check if project already exists
    project_file = target_dir / "prism.project.yaml"
    if project_file.exists() and not args.force:
        print_error(f"Project file already exists: {project_file}")
        print_info("Use --force to overwrite")
        sys.exit(1)
    
    # Prompt for configuration
    name = args.name or input("Project name: ").strip() or "my-project"
    train_script = args.train_script or input("Train script path [train.py]: ").strip() or "train.py"
    
    # Prompt for schema and validation files (optional)
    schema_file = args.schema or input("Schema file path (optional, press Enter to skip): ").strip() or None
    validation_file = args.validation or input("Validation rules file path (optional, press Enter to skip): ").strip() or None
    
    # Build extra kwargs
    extra_kwargs = {}
    if schema_file:
        extra_kwargs["schema"] = {"file": schema_file}
    if validation_file:
        extra_kwargs["validation"] = {"file": validation_file}
    
    # Use Project.create() to generate correct format
    project = Project.create(
        path=target_dir,
        name=name,
        train_script=train_script,
        **extra_kwargs
    )
    
    print_info(f"  configs/  - Base configuration files")
    print_info(f"  studies/  - Prism sweep definitions")
    print_info(f"  outputs/  - Experiment results")


def cmd_list(args, project: Project):
    """List all existing studies."""
    studies = list_existing_studies(project.output_dir)
    print_studies_list(studies)


def cmd_status(args, project: Project):
    """Show status of a study."""
    study_name = args.study

    try:
        manager = load_study_by_name_state(study_name, project.output_dir)
    except FileNotFoundError:
        print_error(f"Study '{study_name}' not found")
        print_info("Use 'prism list' to see available studies")
        sys.exit(1)

    manager.print_summary()


def cmd_create(args, project: Project):
    """Create a new study."""
    study_name = args.name
    base_config = Path(args.config).expanduser()
    prism_configs = [Path(p).expanduser() for p in (args.prism or [])]
    
    # Resolve relative paths
    if not base_config.is_absolute():
        # Try relative to project configs dir
        if (project.configs_dir / base_config).exists():
            base_config = project.configs_dir / base_config
        elif not base_config.exists():
            print_error(f"Config not found: {base_config}")
            sys.exit(1)
    
    resolved_prism = []
    for pc in prism_configs:
        if not pc.is_absolute():
            if (project.prism_configs_dir / pc).exists():
                pc = project.prism_configs_dir / pc
            elif not pc.exists():
                print_error(f"Prism config not found: {pc}")
                sys.exit(1)
        resolved_prism.append(pc)
    
    # Check if study exists
    if study_exists(study_name, project.output_dir):
        if not args.force:
            print_error(f"Study '{study_name}' already exists")
            print_info("Use --force to overwrite")
            sys.exit(1)
        delete_study(study_name=study_name, output_dir=project.output_dir)
    
    # Create manager
    print_progress(f"✨ Creating study: {study_name}")
    
    manager = PrismManager(
        base_config_path=base_config,
        prism_config_path=resolved_prism,
        study_name=study_name,
        output_dir=project.output_dir,
    )
    
    # Expand configs
    available_keys = manager.get_available_keys()
    if args.keys:
        prism_keys = args.keys
    else:
        prism_keys = available_keys
    
    manager.expand_configs(
        prism_keys=prism_keys,
        linking_mode=args.linking or "zip"
    )
    
    print_success(f"✅ Created '{study_name}' with {len(manager.state.experiments)} experiments")
    manager.print_summary()


def cmd_run(args, project: Project, executor: Executor):
    """Run experiments."""
    study_name = args.study

    try:
        manager = load_study_by_name_state(study_name, project.output_dir)
    except FileNotFoundError:
        print_error(f"Study '{study_name}' not found")
        sys.exit(1)
    
    # Handle dry run - just show what would happen
    if args.dry_run:
        print_info("=== DRY RUN - No experiments will be executed ===")
        if args.next:
            next_key = manager.get_next_pending()
            if next_key:
                print_info(f"Would execute: {next_key}")
                exp = manager.get_experiment(next_key)
                if exp and exp.config:
                    print_info(f"Config keys: {list(exp.config.keys())}")
            else:
                print_info("No pending experiments")
        elif args.key:
            print_info(f"Would execute: {args.key}")
            exp = manager.get_experiment(args.key)
            if exp and exp.config:
                print_info(f"Config keys: {list(exp.config.keys())}")
        elif args.all:
            pending = manager.get_pending_experiments()
            print_info(f"Would execute {len(pending)} experiments:")
            for key in pending[:10]:
                print_info(f"  - {key}")
            if len(pending) > 10:
                print_info(f"  ... and {len(pending) - 10} more")
        manager.print_summary()
        return
    
    # Execute based on mode
    if args.next:
        print_progress("Running next pending experiment...")
        manager.execute_next(executor=executor)
    elif args.key:
        print_progress(f"Running experiment: {args.key}")
        manager.execute_key(args.key, executor=executor, restart=args.restart)
    elif args.all:
        pending = sum(1 for e in manager.state.experiments.values() 
                     if e.status == ExperimentStatus.PENDING)
        print_progress(f"Running {pending} pending experiments...")
        manager.execute_all(executor=executor, stop_on_failure=args.stop_on_failure)
    else:
        print_error("Specify --next, --key, or --all")
        sys.exit(1)
    
    manager.print_summary()


def cmd_reset(args, project: Project):
    """Reset a study."""
    study_name = args.study
    try:
        manager = load_study_by_name_state(study_name, project.output_dir)
    except FileNotFoundError:
        print_error(f"Study '{study_name}' not found")
        sys.exit(1)

    print_warning(f"🔄 Resetting study: {study_name}")
    try:
        manager = manager.rebuild(project_root=project.config.project_root, linking_mode="zip")
    except Exception as e:
        print_error(str(e))
        sys.exit(1)

    print_success(f"✅ Reset '{study_name}' with {len(manager.state.experiments)} experiments")


def cmd_reload(args, project: Project):
    """Reload study configuration."""
    study_name = args.study
    try:
        manager = load_study_by_name_state(study_name, project.output_dir)
    except FileNotFoundError:
        print_error(f"Study '{study_name}' not found")
        sys.exit(1)

    print_progress(f"🔄 Reloading configuration for study: {study_name}")
    try:
        manager.reload_configs()
    except Exception as e:
        print_error(str(e))
        sys.exit(1)


def cmd_retry(args, project: Project, executor: Executor):
    """Retry failed experiments."""
    study_name = args.study

    try:
        manager = load_study_by_name_state(study_name, project.output_dir)
    except FileNotFoundError:
        print_error(f"Study '{study_name}' not found")
        sys.exit(1)
    
    failed_keys = manager.get_failed_experiments()
    
    if not failed_keys:
        print_success("No failed experiments to retry!")
        return
    
    print_progress(f"🔄 Retrying {len(failed_keys)} failed experiment(s)")
    
    # Reset and execute
    for key in failed_keys:
        if args.dry_run:
            print_info(f"Would retry: {key}")
            continue
        manager.reset_experiment(key)
        manager.execute_key(key, executor=executor)
    
    manager.print_summary()


def cmd_show_config(args, project: Project):
    """Show config for an experiment."""
    study_name = args.study
    exp_key = args.key
    
    try:
        manager = load_study_by_name_state(study_name, project.output_dir)
    except FileNotFoundError:
        print_error(f"Study '{study_name}' not found")
        sys.exit(1)
    
    if exp_key not in manager.state.experiments:
        print_error(f"Experiment '{exp_key}' not found")
        print_info(f"Available: {list(manager.state.experiments.keys())}")
        sys.exit(1)
    
    import yaml
    config = manager.state.experiments[exp_key].config
    print_info(f"\n{'='*60}")
    print_info(f"Configuration for: {exp_key}")
    print_info(f"{'='*60}")
    print(yaml.dump(config, default_flow_style=False, sort_keys=False))


def cmd_diff(args, project: Project):
    """Show diff between two experiments."""
    study_name = args.study
    key1, key2 = args.keys
    
    try:
        manager = load_study_by_name_state(study_name, project.output_dir)
    except FileNotFoundError:
        print_error(f"Study '{study_name}' not found")
        sys.exit(1)
    
    if key1 not in manager.state.experiments:
        print_error(f"Experiment '{key1}' not found")
        sys.exit(1)
    if key2 not in manager.state.experiments:
        print_error(f"Experiment '{key2}' not found")
        sys.exit(1)
    
    show_config_diff(
        manager.state.experiments[key1].config,
        manager.state.experiments[key2].config,
        key1, key2
    )


def cmd_mark(args, project: Project):
    """Mark an experiment as done or failed."""
    study_name = args.study
    exp_key = args.key
    status = args.status
    
    try:
        manager = load_study_by_name_state(study_name, project.output_dir)
    except FileNotFoundError:
        print_error(f"Study '{study_name}' not found")
        sys.exit(1)
    
    if exp_key not in manager.state.experiments:
        print_error(f"Experiment '{exp_key}' not found")
        sys.exit(1)
    
    if status == "done":
        manager.mark_done(exp_key)
        print_success(f"✅ Marked '{exp_key}' as DONE")
    else:
        manager.mark_failed(exp_key, error_message="Manually marked as failed")
        print_warning(f"❌ Marked '{exp_key}' as FAILED")


def cmd_delete(args, project: Project):
    """Delete a study."""
    study_name = args.study

    if not study_exists(study_name, project.output_dir):
        print_error(f"Study '{study_name}' not found")
        sys.exit(1)
    
    if not args.force:
        confirm = input(f"Delete study '{study_name}'? [y/N]: ").strip().lower()
        if confirm not in ('y', 'yes'):
            print_info("Aborted")
            return
    
    deleted = delete_study(
        study_name=study_name,
        output_dir=project.output_dir,
        delete_artifacts_dir=bool(args.artifacts),
    )
    if not deleted:
        print_warning("Nothing deleted")
    else:
        for p in deleted:
            print_success(f"Deleted: {p}")


def cmd_tui(args, project: Optional[Project]):
    """Launch the interactive TUI."""
    from .tui import PrismTUI
    
    if project:
        tui = PrismTUI(project_path=project.config.project_root / "prism.project.yaml")
    else:
        tui = PrismTUI()
    
    tui.run()


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for Prism CLI."""
    parser = argparse.ArgumentParser(
        prog="prism",
        description="Prism - Experiment Parameter Sweep Manager"
    )
    
    parser.add_argument(
        "--project", "-p",
        type=str,
        help="Path to prism.project.yaml or project directory"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # init
    init_parser = subparsers.add_parser("init", help="Initialize a new prism project")
    init_parser.add_argument("directory", nargs="?", default=".", help="Project directory")
    init_parser.add_argument("--name", type=str, help="Project name")
    init_parser.add_argument("--train-script", type=str, help="Training script path")
    init_parser.add_argument("--config-arg", type=str, help="Config argument name")
    init_parser.add_argument("--schema", type=str, help="Schema file path for config validation")
    init_parser.add_argument("--validation", type=str, help="Validation rules file path")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing project")
    
    # list
    subparsers.add_parser("list", help="List all existing studies")
    
    # status
    status_parser = subparsers.add_parser("status", help="Show study status")
    status_parser.add_argument("study", type=str, help="Study name")
    
    # create
    create_parser = subparsers.add_parser("create", help="Create a new study")
    create_parser.add_argument("--name", "-n", required=True, type=str, help="Study name")
    create_parser.add_argument("--config", "-c", required=True, type=str, help="Base config path")
    create_parser.add_argument("--prism", nargs="+", help="Prism config path(s)")
    create_parser.add_argument("--keys", nargs="+", help="Specific keys to generate")
    create_parser.add_argument("--linking", choices=["zip", "product"], default="zip")
    create_parser.add_argument("--force", action="store_true", help="Overwrite existing study")
    
    # run
    run_parser = subparsers.add_parser("run", help="Run experiments")
    run_parser.add_argument("--study", "-s", required=True, type=str, help="Study name")
    run_group = run_parser.add_mutually_exclusive_group(required=True)
    run_group.add_argument("--next", action="store_true", help="Run next pending")
    run_group.add_argument("--key", type=str, help="Run specific experiment")
    run_group.add_argument("--all", action="store_true", help="Run all pending")
    run_parser.add_argument("--restart", action="store_true", help="Reset before running")
    run_parser.add_argument("--dry-run", action="store_true", help="Print without executing")
    run_parser.add_argument("--stop-on-failure", action="store_true", help="Stop on first failure")
    
    # reset
    reset_parser = subparsers.add_parser("reset", help="Reset a study")
    reset_parser.add_argument("study", type=str, help="Study name")
    
    # reload
    reload_parser = subparsers.add_parser("reload", help="Reload study configuration")
    reload_parser.add_argument("study", type=str, help="Study name")
    
    # retry
    retry_parser = subparsers.add_parser("retry", help="Retry failed experiments")
    retry_parser.add_argument("study", type=str, help="Study name")
    retry_parser.add_argument("--dry-run", action="store_true")
    
    # show-config
    show_parser = subparsers.add_parser("show-config", help="Show experiment config")
    show_parser.add_argument("study", type=str, help="Study name")
    show_parser.add_argument("key", type=str, help="Experiment key")
    
    # diff
    diff_parser = subparsers.add_parser("diff", help="Compare two experiment configs")
    diff_parser.add_argument("study", type=str, help="Study name")
    diff_parser.add_argument("keys", nargs=2, help="Two experiment keys to compare")
    
    # mark
    mark_parser = subparsers.add_parser("mark", help="Mark experiment status")
    mark_parser.add_argument("study", type=str, help="Study name")
    mark_parser.add_argument("key", type=str, help="Experiment key")
    mark_parser.add_argument("status", choices=["done", "failed"], help="New status")
    
    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete a study")
    delete_parser.add_argument("study", type=str, help="Study name")
    delete_parser.add_argument("--artifacts", action="store_true", help="Also delete artifacts")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    
    # tui
    subparsers.add_parser("tui", help="Launch interactive TUI")
    
    return parser


def main(args: Optional[List[str]] = None):
    """Main entry point for Prism CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Try to find/load project
    project = None
    executor = None
    
    if parsed_args.project:
        try:
            project = Project.load(Path(parsed_args.project))
        except Exception as e:
            print_error(f"Failed to load project: {e}")
            sys.exit(1)
    else:
        try:
            project = find_project()
        except ProjectNotFoundError:
            # Only fail if command requires project
            pass
    
    # Create executor if project is loaded
    executor = None
    if project:
        try:
            executor = Executor(project)
        except Exception as e:
            print_warning(f"Could not create executor: {e}")
    
    # Handle commands
    if parsed_args.command == "init":
        cmd_init(parsed_args)
    
    elif parsed_args.command == "list":
        if not project:
            print_error("No project found. Run 'prism init' first or specify --project")
            sys.exit(1)
        cmd_list(parsed_args, project)
    
    elif parsed_args.command == "status":
        if not project:
            print_error("No project found")
            sys.exit(1)
        cmd_status(parsed_args, project)
    
    elif parsed_args.command == "create":
        if not project:
            print_error("No project found")
            sys.exit(1)
        cmd_create(parsed_args, project)
    
    elif parsed_args.command == "run":
        if not project:
            print_error("No project found")
            sys.exit(1)
        if not executor:
            print_error("No executor available")
            sys.exit(1)
        cmd_run(parsed_args, project, executor)
    
    elif parsed_args.command == "reset":
        if not project:
            print_error("No project found")
            sys.exit(1)
        cmd_reset(parsed_args, project)
    
    elif parsed_args.command == "reload":
        if not project:
            print_error("No project found")
            sys.exit(1)
        cmd_reload(parsed_args, project)
    
    elif parsed_args.command == "retry":
        if not project:
            print_error("No project found")
            sys.exit(1)
        if not executor:
            print_error("No executor available")
            sys.exit(1)
        cmd_retry(parsed_args, project, executor)
    
    elif parsed_args.command == "show-config":
        if not project:
            print_error("No project found")
            sys.exit(1)
        cmd_show_config(parsed_args, project)
    
    elif parsed_args.command == "diff":
        if not project:
            print_error("No project found")
            sys.exit(1)
        cmd_diff(parsed_args, project)
    
    elif parsed_args.command == "mark":
        if not project:
            print_error("No project found")
            sys.exit(1)
        cmd_mark(parsed_args, project)
    
    elif parsed_args.command == "delete":
        if not project:
            print_error("No project found")
            sys.exit(1)
        cmd_delete(parsed_args, project)
    
    elif parsed_args.command == "tui":
        cmd_tui(parsed_args, project)
    
    else:
        # Default: show help or launch TUI
        if project:
            cmd_tui(parsed_args, project)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
