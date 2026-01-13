#!/usr/bin/env python3
"""
Prism TUI - Text User Interface for PRISM Experiment Management

This module provides an interactive terminal interface for managing PRISM experiments.
It is project-centric: the user first selects/creates a project (defined by prism.project.yaml),
then manages studies within that project.

Usage:
    prism_tui
    prism tui
"""

import sys
import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from matplotlib.pyplot import prism

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.syntax import Syntax
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    print("⚠️  'rich' package not found. Install it with: pip install rich")
    sys.exit(1)

from .manager import (
    PrismManager,
    ExperimentStatus,
    list_studies as list_studies_state,
    study_exists,
    delete_study,
)
from .project import Project, find_project, ProjectNotFoundError
from .executor import Executor


# ============================================================================
# Persistence: Save/load last opened project
# ============================================================================

def _get_prism_config_dir() -> Path:
    """Get the prism config directory (~/.config/prism or platform equivalent)."""
    if sys.platform == "win32":
        config_dir = Path(os.environ.get("APPDATA", Path.home())) / "prism"
    else:
        config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "prism"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def _load_last_project() -> Optional[Path]:
    """Load the path of the last opened project."""
    config_file = _get_prism_config_dir() / "last_project.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                data = json.load(f)
            path = Path(data.get("last_project", ""))
            if path.exists():
                return path
        except Exception:
            pass
    return None


def _save_last_project(project_path: Path) -> None:
    """Save the path of the current project as last opened."""
    config_file = _get_prism_config_dir() / "last_project.json"
    try:
        # Also save recent projects list
        recent = _load_recent_projects()
        recent_str = str(project_path.resolve())
        if recent_str in recent:
            recent.remove(recent_str)
        recent.insert(0, recent_str)
        recent = recent[:10]  # Keep last 10
        
        with open(config_file, "w") as f:
            json.dump({
                "last_project": str(project_path.resolve()),
                "recent_projects": recent
            }, f, indent=2)
    except Exception:
        pass


def _load_recent_projects() -> List[str]:
    """Load list of recently opened projects."""
    config_file = _get_prism_config_dir() / "last_project.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                data = json.load(f)
            return data.get("recent_projects", [])
        except Exception:
            pass
    return []


class MenuAction(Enum):
    """Available menu actions."""
    # Project-level actions
    SELECT_PROJECT = "select_project"
    CREATE_PROJECT = "create_project"
    
    # Study-level actions
    LIST_STUDIES = "list_studies"
    SELECT_STUDY = "select_study"
    CREATE_STUDY = "create_study"
    DELETE_STUDY = "delete_study"
    
    # Experiment-level actions
    VIEW_STATUS = "view_status"
    EXECUTE_NEXT = "execute_next"
    EXECUTE_ALL = "execute_all"
    EXECUTE_KEY = "execute_key"
    RETRY_FAILED = "retry_failed"
    SHOW_CONFIG = "show_config"
    DIFF_CONFIGS = "diff_configs"
    MARK_DONE = "mark_done"
    MARK_FAILED = "mark_failed"
    RESET_STUDY = "reset_study"
    EXPORT_CONFIG = "export_config"
    
    # Navigation
    BACK = "back"
    QUIT = "quit"


@dataclass
class StudyInfo:
    """Information about a PRISM study."""
    name: str
    path: Path
    total: int
    pending: int
    done: int
    failed: int
    running: int
    base_config: str
    prism_configs: List[str]
    updated_at: str


class PrismTUI:
    """Interactive TUI for PRISM experiment management."""
    
    def __init__(self, project_path: Optional[Path] = None):
        """
        Initialize the TUI.
        
        Args:
            project_path: Optional path to a prism.project.yaml file or directory.
                         If None, will try to load last opened project.
        """
        self.console = Console()
        self.project: Optional[Project] = None
        self.current_study: Optional[StudyInfo] = None
        self.current_manager: Optional[PrismManager] = None
        self.executor: Optional[Executor] = None
        
        # Try to load project
        if project_path:
            self._try_load_project(project_path)
        else:
            # Try last opened project
            last_project = _load_last_project()
            if last_project:
                self._try_load_project(last_project, silent=True)
    
    def _try_load_project(self, path: Path, silent: bool = False) -> bool:
        """Try to load a project from path."""
        try:
            self.project = Project.load(path)
            self._create_executor()
            _save_last_project(path)
            return True
        except Exception as e:
            if not silent:
                self.console.print(f"[yellow]Warning: Could not load project: {e}[/yellow]")
            return False
        
    def _create_executor(self) -> None:
        """Create an executor from the current project."""
        if self.project:
            try:
                self.executor = Executor(self.project)
            except ValueError as e:
                # train_script not defined
                self.console.print(f"[yellow]Warning: Could not create executor: {e}[/yellow]")
                self.executor = None
            except Exception as e:
                self.console.print(f"[yellow]Warning: Executor creation failed: {e}[/yellow]")
                self.executor = None
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self, subtitle: str = ""):
        """Print the PRISM TUI header."""
        header_text = Text()
        header_text.append("╔══════════════════════════════════════════════════════════════╗\n", style="cyan bold")
        header_text.append("║", style="cyan bold")
        header_text.append("          🔬 PRISM - Parameter Research & Investigation        ", style="white bold")
        header_text.append("║\n", style="cyan bold")
        header_text.append("║", style="cyan bold")
        header_text.append("              Sweep Manager - Interactive TUI                  ", style="dim white")
        header_text.append("║\n", style="cyan bold")
        header_text.append("╚══════════════════════════════════════════════════════════════╝", style="cyan bold")
        
        self.console.print(header_text)
        
        # Show project info if loaded
        if self.project:
            project_info = f"📁 Project: {self.project.config.name} @ {self.project.config.project_root}"
            self.console.print(f"[dim]{project_info}[/dim]")
        
        if subtitle:
            self.console.print(f"\n[yellow]📍 {subtitle}[/yellow]")
        self.console.print()
        
    def get_studies(self) -> List[StudyInfo]:
        """Get list of all existing PRISM studies."""
        if not self.project:
            return []

        output_dir = self.project.config.get_resolved_paths().output_dir
        rows = list_studies_state(output_dir)

        studies: List[StudyInfo] = []
        for row in rows:
            studies.append(
                StudyInfo(
                    name=row.get("name", ""),
                    path=Path(row.get("path", "")),
                    total=int(row.get("total", 0)),
                    pending=int(row.get("pending", 0)),
                    done=int(row.get("done", 0)),
                    failed=int(row.get("failed", 0)),
                    running=int(row.get("running", 0)),
                    base_config=row.get("base_config", ""),
                    prism_configs=list(row.get("prism_configs", []) or []),
                    updated_at=row.get("updated_at", ""),
                )
            )

        return studies
    
    def get_prism_config_files(self) -> List[Path]:
        """Get list of available prism config files."""
        if not self.project:
            return []
            
        configs = []
        prism_configs_dir = self.project.config.get_resolved_paths().prism_configs_dir
        print(prism_configs_dir)
        if prism_configs_dir.exists():
            configs.extend(prism_configs_dir.glob("*.prism.yaml"))
        return sorted(configs)
    
    def get_base_config_files(self) -> List[Path]:
        """Get list of available base config files."""
        if not self.project:
            return []
            
        configs = []
        configs_dir = self.project.config.get_resolved_paths().configs_dir
        if configs_dir.exists():
            for f in configs_dir.glob("*.yaml"):
                # Exclude prism configs
                if "prism" not in f.name.lower() and f.is_file():
                    configs.append(f)
        return sorted(configs)
    
    def print_menu(self, options: List[Tuple[str, str, str]], title: str = "Menu") -> str:
        """
        Print a numbered menu and get user selection.
        
        Args:
            options: List of (key, label, description) tuples
            title: Menu title
            
        Returns:
            Selected option key
        """
        table = Table(title=title, box=box.ROUNDED, show_header=False, padding=(0, 2))
        table.add_column("No.", style="cyan bold", width=4, justify="right", no_wrap=True)
        table.add_column("Option", style="white bold", width=25, no_wrap=True)
        table.add_column("Description", style="dim", width=55, no_wrap=True)
        
        for i, (key, label, desc) in enumerate(options, 1):
            table.add_row(f"[{i}]", label, desc)
        
        self.console.print(table)
        self.console.print()
        
        while True:
            try:
                choice = Prompt.ask(
                    "[cyan]Enter choice[/cyan]",
                    default="q" if any(k == "quit" for k, _, _ in options) else "1"
                )
                
                # Handle quit shortcuts
                if choice.lower() in ('q', 'quit', 'exit'):
                    return "quit"
                if choice.lower() in ('b', 'back'):
                    return "back"
                
                # Be tolerant to accidental pastes
                import re
                m = re.match(r"^([+-]?\d+)", str(choice).strip())
                if not m:
                    raise ValueError("No leading integer")
                idx = int(m.group(1)) - 1
                if 0 <= idx < len(options):
                    return options[idx][0]
                else:
                    self.console.print("[red]Invalid choice. Please try again.[/red]")
            except ValueError:
                self.console.print("[red]Please enter a number.[/red]")
    
    def print_studies_table(self, studies: List[StudyInfo]) -> None:
        """Print a table of studies."""
        if not studies:
            self.console.print(Panel(
                "[yellow]No studies found.[/yellow]\n\n"
                "Create a new study from the main menu.",
                title="📚 Studies",
                border_style="yellow"
            ))
            return
        
        table = Table(title="📚 Existing Studies", box=box.ROUNDED)
        table.add_column("No.", style="cyan", justify="right", width=4)
        table.add_column("Status", justify="center", width=3)
        table.add_column("Name", style="white bold", max_width=30)
        table.add_column("Progress", justify="center", width=20)
        table.add_column("Pending", justify="right", style="yellow")
        table.add_column("Done", justify="right", style="green")
        table.add_column("Failed", justify="right", style="red")
        table.add_column("Last Updated", style="dim", max_width=20)
        
        for i, study in enumerate(studies, 1):
            # Status emoji
            if study.pending == 0 and study.failed == 0:
                status = "✅"
            elif study.failed > 0:
                status = "❌"
            elif study.running > 0:
                status = "🔄"
            else:
                status = "⏳"
            
            # Progress bar
            if study.total > 0:
                pct = int(100 * study.done / study.total)
                filled = int(15 * study.done / study.total)
                bar = "█" * filled + "░" * (15 - filled)
                progress = f"{bar} {pct}%"
            else:
                progress = "N/A"
            
            # Format date
            updated = study.updated_at[:16].replace("T", " ") if study.updated_at else "N/A"
            
            table.add_row(
                str(i),
                status,
                study.name,
                progress,
                str(study.pending),
                str(study.done),
                str(study.failed),
                updated
            )
        
        self.console.print(table)
    
    def print_study_status(self, study: StudyInfo, manager: PrismManager) -> None:
        """Print detailed status for a study."""
        # Summary panel
        summary_text = Text()
        summary_text.append(f"📁 Path: ", style="dim")
        summary_text.append(f"{study.path}\n", style="white")
        summary_text.append(f"📝 Base Config: ", style="dim")
        summary_text.append(f"{Path(study.base_config).name}\n", style="white")
        summary_text.append(f"🔧 Prism Configs: ", style="dim")
        prism_names = [Path(p).name for p in study.prism_configs]
        summary_text.append(f"{', '.join(prism_names)}\n", style="white")
        summary_text.append(f"🕐 Last Updated: ", style="dim")
        if study.updated_at:
            summary_text.append(f"{study.updated_at[:19].replace('T', ' ')}", style="white")
        else:
            summary_text.append("N/A", style="white")
        
        self.console.print(Panel(summary_text, title=f"📊 Study: {study.name}", border_style="cyan"))
        
        # Experiments table
        exp_table = Table(title="🧪 Experiments", box=box.ROUNDED)
        exp_table.add_column("No.", style="cyan", justify="right", width=4)
        exp_table.add_column("Key", style="white bold", max_width=40)
        exp_table.add_column("Status", justify="center", width=10)
        exp_table.add_column("Metrics", style="dim", max_width=30)
        exp_table.add_column("Started", style="dim", max_width=18)
        exp_table.add_column("Completed", style="dim", max_width=18)
        
        experiments = manager.state.experiments
        for i, (key, exp) in enumerate(experiments.items(), 1):
            status_str = exp.status.value if isinstance(exp.status, ExperimentStatus) else exp.status
            
            if status_str == "DONE":
                status_display = "[green]✅ DONE[/green]"
            elif status_str == "FAILED":
                status_display = "[red]❌ FAILED[/red]"
            elif status_str == "RUNNING":
                status_display = "[yellow]🔄 RUNNING[/yellow]"
            else:
                status_display = "[dim]⏳ PENDING[/dim]"
            
            started = (exp.started_at[:16].replace("T", " ") if exp.started_at else "-")
            completed = (exp.completed_at[:16].replace("T", " ") if exp.completed_at else "-")
            
            # Format metrics summary
            metrics_str = "-"
            if exp.metrics:
                metrics_items = [f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}" 
                               for k, v in list(exp.metrics.items())[:3]]
                metrics_str = ", ".join(metrics_items)
                if len(exp.metrics) > 3:
                    metrics_str += "..."
            
            exp_table.add_row(str(i), key, status_display, metrics_str, started, completed)
        
        self.console.print(exp_table)
        
        # Progress summary
        total = len(experiments)
        done = sum(1 for e in experiments.values() if e.status == ExperimentStatus.DONE)
        failed = sum(1 for e in experiments.values() if e.status == ExperimentStatus.FAILED)
        pending = sum(1 for e in experiments.values() if e.status == ExperimentStatus.PENDING)
        running = sum(1 for e in experiments.values() if e.status == ExperimentStatus.RUNNING)
        
        pct = int(100 * done / total) if total > 0 else 0
        
        self.console.print()
        self.console.print(Panel(
            f"[green]✅ Done: {done}[/green]  |  "
            f"[yellow]⏳ Pending: {pending}[/yellow]  |  "
            f"[red]❌ Failed: {failed}[/red]  |  "
            f"[blue]🔄 Running: {running}[/blue]  |  "
            f"[cyan]📊 Progress: {pct}%[/cyan]",
            title="Summary",
            border_style="blue"
        ))
    
    def select_experiment(self, manager: PrismManager, 
                          filter_status: Optional[ExperimentStatus] = None,
                          negative_filter: Optional[ExperimentStatus] = None) -> Optional[str]:
                        
        """Let user select an experiment from the current study."""
        experiments = manager.state.experiments
        
        if filter_status:
            filtered = {k: v for k, v in experiments.items() if v.status == filter_status}
        else:
            filtered = experiments

        if negative_filter:
            filtered = {k: v for k, v in filtered.items() if v.status != negative_filter}
        
        if not filtered:
            status_name = filter_status.value if filter_status else "any"
            self.console.print(f"[yellow]No experiments with status '{status_name}' found.[/yellow]")
            return None
        
        options = [(k, k, f"Status: {v.status.value}") for k, v in filtered.items()]
        options.append(("back", "", "Return to study menu"))
        
        key = self.print_menu(options, title="Select Experiment")
        return key if key not in ("back", "quit") else None
    
    def show_config_viewer(self, manager: PrismManager, exp_key: str) -> None:
        """Display the configuration for an experiment."""
        if exp_key not in manager.state.experiments:
            self.console.print(f"[red]Experiment '{exp_key}' not found.[/red]")
            return
        
        import yaml
        config = manager.state.experiments[exp_key].config
        yaml_str = yaml.dump(config, default_flow_style=False, sort_keys=False)
        
        syntax = Syntax(yaml_str, "yaml", theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title=f"📝 Config: {exp_key}", border_style="green"))
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def show_config_diff(self, manager: PrismManager) -> None:
        """Show diff between two experiment configurations."""
        experiments = list(manager.state.experiments.keys())
        
        if len(experiments) < 2:
            self.console.print("[yellow]Need at least 2 experiments to compare.[/yellow]")
            return
        
        # Select first experiment
        self.console.print("[cyan]Select first experiment:[/cyan]")
        key1 = self.select_experiment(manager)
        if not key1:
            return
        
        # Select second experiment
        self.console.print("[cyan]Select second experiment:[/cyan]")
        key2 = self.select_experiment(manager)
        if not key2:
            return
        
        if key1 == key2:
            self.console.print("[yellow]Selected the same experiment twice.[/yellow]")
            return
        
        # Flatten configs for comparison
        def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        config1 = manager.state.experiments[key1].config
        config2 = manager.state.experiments[key2].config
        
        flat1 = flatten_dict(config1)
        flat2 = flatten_dict(config2)
        
        all_keys = sorted(set(flat1.keys()) | set(flat2.keys()))
        
        # Build diff table
        diff_table = Table(title=f"🔍 Diff: {key1} vs {key2}", box=box.ROUNDED)
        diff_table.add_column("Parameter", style="cyan", max_width=40)
        diff_table.add_column(key1, style="red", max_width=30)
        diff_table.add_column(key2, style="green", max_width=30)
        
        diff_count = 0
        for key in all_keys:
            val1 = flat1.get(key, "<missing>")
            val2 = flat2.get(key, "<missing>")
            if val1 != val2:
                diff_table.add_row(key, str(val1), str(val2))
                diff_count += 1
        
        if diff_count == 0:
            self.console.print("[green]✅ Configurations are identical![/green]")
        else:
            self.console.print(diff_table)
            self.console.print(f"\n[yellow]Found {diff_count} difference(s).[/yellow]")
        
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def create_study_wizard(self) -> Optional[Tuple[str, Path, List[Path]]]:
        """Interactive wizard to create a new study."""
        if not self.project:
            self.console.print("[red]No project loaded. Please load a project first.[/red]")
            return None
            
        self.clear_screen()
        self.print_header("Create New Study")
        
        # Step 1: Study name
        self.console.print(Panel(
            "Choose a name for your study.\n"
            "This will be used for the .study.json file.",
            title="Step 1/3: Study Name",
            border_style="cyan"
        ))
        
        study_name = Prompt.ask("[cyan]Study name[/cyan]")
        if not study_name:
            self.console.print("[red]Study name cannot be empty.[/red]")
            return None
        
        # Check if exists
        output_dir = self.project.config.get_resolved_paths().output_dir
        if study_exists(study_name, output_dir):
            if not Confirm.ask(f"[yellow]Study '{study_name}' already exists. Overwrite?[/yellow]"):
                return None
            delete_study(study_name=study_name, output_dir=output_dir)
        
        # Step 2: Base config
        self.console.print()
        self.console.print(Panel(
            "Select the base configuration file.\n"
            "This contains default settings for all experiments.",
            title="Step 2/3: Base Config",
            border_style="cyan"
        ))
        
        base_configs = self.get_base_config_files()
        if not base_configs:
            self.console.print("[red]No base config files found.[/red]")
            self.console.print(f"[dim]Expected in: {self.project.config.get_resolved_paths().configs_dir}[/dim]")
            return None
        
        options = [(str(i), c.name, str(c.relative_to(self.project.config.project_root))) 
                   for i, c in enumerate(base_configs)]
        options.append(("custom", "📝 Custom path", "Enter a custom path"))
        options.append(("back", "", "Cancel"))
        
        choice = self.print_menu(options, title="Available Base Configs")
        
        if choice == "back":
            return None
        elif choice == "custom":
            custom_path = Prompt.ask("[cyan]Enter base config path[/cyan]")
            base_config = Path(custom_path).expanduser()
            if not base_config.exists():
                self.console.print(f"[red]File not found: {custom_path}[/red]")
                return None
        else:
            base_config = base_configs[int(choice)]
        
        # Step 3: Prism configs
        self.console.print()
        self.console.print(Panel(
            "Select one or more prism configuration files.\n"
            "Multiple files will create a cartesian product of parameters.\n"
            "If you want a single run, you can skip prism selection.",
            title="Step 3/3: Prism Configs",
            border_style="cyan"
        ))
        
        prism_configs = self.get_prism_config_files()
        
        if not prism_configs:
            prism_configs_dir = self.project.config.get_resolved_paths().prism_configs_dir
            self.console.print(f"[yellow]⚠️  No .prism.yaml files found in {prism_configs_dir}[/yellow]")
            self.console.print(f"[dim]You can create one later or skip to run a single experiment.[/dim]")
        
        selected_prism: List[Path] = []
        skipped = False
        
        while True:
            self.console.print(f"\n[green]Selected: {[p.name for p in selected_prism] if selected_prism else 'None'}[/green]")
            
            options = [(str(i), c.name, "✓ Selected" if c in selected_prism else "") 
                      for i, c in enumerate(prism_configs)]
            options.append(("skip", "⏭️  Skip", "No prism sweep (single experiment from base config)"))
            options.append(("done", "✅ Done", "Finish selection"))
            options.append(("custom", "📝 Custom path", "Enter a custom path"))
            options.append(("back", "", "Cancel"))
            
            choice = self.print_menu(options, title="Available Prism Configs")
            
            if choice == "back":
                return None
            elif choice == "skip":
                selected_prism = []
                skipped = True
                break
            elif choice == "done":
                if not prism_configs and not selected_prism:
                    skipped = True
                    break
                if not selected_prism:
                    self.console.print("[red]Please select at least one prism config, or choose Skip for a single run.[/red]")
                    continue
                break
            elif choice == "custom":
                custom_path = Prompt.ask("[cyan]Enter prism config path[/cyan]")
                custom = Path(custom_path).expanduser()
                if custom.exists():
                    if custom not in selected_prism:
                        selected_prism.append(custom)
                        skipped = False
                else:
                    self.console.print(f"[red]File not found: {custom_path}[/red]")
            else:
                idx = int(choice)
                config = prism_configs[idx]
                if config in selected_prism:
                    selected_prism.remove(config)
                else:
                    selected_prism.append(config)
                skipped = False
        
        # Confirmation
        self.console.print()
        prism_summary = "(none - single experiment)" if skipped or not selected_prism else ", ".join(p.name for p in selected_prism)
        self.console.print(Panel(
            f"[white]Study Name:[/white] {study_name}\n"
            f"[white]Base Config:[/white] {base_config.name}\n"
            f"[white]Prism Configs:[/white] {prism_summary}",
            title="📋 Summary",
            border_style="green"
        ))
        
        if Confirm.ask("[cyan]Create this study?[/cyan]"):
            return study_name, base_config, selected_prism
        
        return None
    
    def execute_experiment(self, manager: PrismManager, exp_key: Optional[str] = None, 
                          mode: str = "next") -> None:
        """Execute experiment(s)."""
        if not self.executor:
            self.console.print("[red]No executor available. Check project configuration.[/red]")
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            return
            
        if mode == "all":
            pending = [k for k, v in manager.state.experiments.items()
                      if v.status == ExperimentStatus.PENDING]
            self.console.print(f"[cyan]Running {len(pending)} experiments...[/cyan]")

            for key in pending:
                self.console.print(f"[cyan]Running: {key}[/cyan]")
                try:
                    manager.execute_key(key, executor=self.executor)
                except Exception as e:
                    self.console.print(f"[red]❌ {key} failed: {e}[/red]")

        elif mode == "next":
            self.console.print("[cyan]Finding next pending...[/cyan]")
            try:
                manager.execute_next(executor=self.executor)
            except Exception as e:
                self.console.print(f"[red]❌ Execution failed: {e}[/red]")

        elif mode == "key" and exp_key:
            self.console.print(f"[cyan]Running: {exp_key}[/cyan]")
            try:
                manager.execute_key(exp_key, executor=self.executor)
            except Exception as e:
                self.console.print(f"[red]❌ {exp_key} failed: {e}[/red]")

        elif mode == "failed":
            failed = [k for k, v in manager.state.experiments.items()
                     if v.status == ExperimentStatus.FAILED]
            if not failed:
                self.console.print("[green]✅ No failed experiments to retry![/green]")
                return

            self.console.print(f"[cyan]Retrying {len(failed)} failed...[/cyan]")
            for key in failed:
                self.console.print(f"[cyan]Retrying: {key}[/cyan]")
                manager.reset_experiment(key)
                try:
                    manager.execute_key(key, executor=self.executor)
                except Exception as e:
                    self.console.print(f"[red]❌ {key} failed again: {e}[/red]")
        
        self.console.print("[green]✅ Execution complete![/green]")
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def study_menu(self) -> None:
        """Display and handle the study menu."""
        while True:
            self.clear_screen()
            self.print_header(f"Study: {self.current_study.name}")
            
            # Show quick status
            self.print_study_status(self.current_study, self.current_manager)
            
            options = [
                ("execute_next", "🎬 Execute Next", "Run the first pending experiment"),
                ("execute_all", "🎬 Execute All", "Run all pending experiments"),
                ("execute_key", "🎯 Execute Specific", "Run a specific experiment by key"),
                ("retry_failed", "❎ Retry Failed", "Reset and re-run failed experiments"),
                ("show_config", "👀 View Config", "Display config for an experiment"),
                ("diff_configs", "🔍 Compare Configs", "Show diff between two experiments"),
                ("mark_done", "✅ Mark Done", "Manually mark experiment as done"),
                ("mark_failed", "❌ Mark Failed", "Manually mark experiment as failed"),
                ("reload_config", "🔄 Reload Config", "Reload configuration without resetting studies"),
                ("reset_study", "🔃 Reset Study", "Reloads all configs and resets experiments to pending"),
                ("export_config", "💾 Export Config", "Export experiment config to file"),
                ("back", "​", "Return to main menu"),
            ]
            
            action = self.print_menu(options, title="Study Actions")
            
            if action == "back" or action == "quit":
                break
            
            elif action == "execute_next":
                self.execute_experiment(self.current_manager, mode="next")
                
            elif action == "execute_all":
                pending_count = sum(1 for e in self.current_manager.state.experiments.values() 
                                   if e.status == ExperimentStatus.PENDING)
                if pending_count == 0:
                    self.console.print("[yellow]No pending experiments to run.[/yellow]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                elif Confirm.ask(f"[yellow]Run {pending_count} pending experiments?[/yellow]"):
                    self.execute_experiment(self.current_manager, mode="all")
                    
            elif action == "execute_key":
                exp_key = self.select_experiment(self.current_manager)
                if exp_key:
                    self.execute_experiment(self.current_manager, exp_key=exp_key, mode="key")
                    
            elif action == "retry_failed":
                failed_count = sum(1 for e in self.current_manager.state.experiments.values() 
                                  if e.status == ExperimentStatus.FAILED)
                if failed_count == 0:
                    self.console.print("[green]✅ No failed experiments![/green]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                elif Confirm.ask(f"[yellow]Retry {failed_count} failed experiments?[/yellow]"):
                    self.execute_experiment(self.current_manager, mode="failed")
                    
            elif action == "show_config":
                exp_key = self.select_experiment(self.current_manager)
                if exp_key:
                    self.show_config_viewer(self.current_manager, exp_key)
                    
            elif action == "diff_configs":
                self.show_config_diff(self.current_manager)
                
            elif action == "mark_done":
                exp_key = self.select_experiment(self.current_manager, negative_filter=ExperimentStatus.DONE)
                if exp_key:
                    self.current_manager.mark_done(exp_key)
                    self.console.print(f"[green]✅ Marked '{exp_key}' as DONE[/green]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                    
            elif action == "mark_failed":
                exp_key = self.select_experiment(self.current_manager, negative_filter=ExperimentStatus.FAILED)
                if exp_key:
                    self.current_manager.mark_failed(exp_key, error_message="Manually marked as failed")
                    self.console.print(f"[yellow]❌ Marked '{exp_key}' as FAILED[/yellow]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            
            elif action == "reload_config":
                try:
                    self.current_manager.reload_configs()
                    self.console.print(f"[green]✅ Configuration reloaded for study '{self.current_manager.study_name}'[/green]")
                except Exception as e:
                    self.console.print(f"[red]❌ Failed to reload config: {e}[/red]")
                Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                                     
            elif action == "reset_study":
                if Confirm.ask("[red]⚠️  Reset the study completely? This will delete and recreate the experiment.[/red]"):
                    try:
                        project_root = self.project.config.project_root if self.project else Path.cwd()
                        self.current_manager = self.current_manager.rebuild(project_root=project_root, linking_mode="zip")
                        
                        # Update current_study reference to reflect the new state
                        studies = self.get_studies()
                        for s in studies:
                            if s.name == self.current_manager.study_name:
                                self.current_study = s
                                break
                        
                        self.console.print(
                            f"[green]✅ Study '{self.current_manager.study_name}' reset and rebuilt with {len(self.current_manager.state.experiments)} experiments[/green]"
                        )
                    except Exception as e:
                        self.console.print(f"[red]❌ Failed to reset study: {e}[/red]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            
            elif action == "export_config":
                exp_key = self.select_experiment(self.current_manager)
                if exp_key:
                    default_path = self.project.config.get_resolved_paths().output_dir / f"{exp_key}_config.yaml"
                    export_path = Prompt.ask("[cyan]Export path[/cyan]", default=str(default_path))
                    self.current_manager.export_config(exp_key, Path(export_path))
                    self.console.print(f"[green]✅ Config exported to: {export_path}[/green]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            
            # Refresh study info
            studies = self.get_studies()
            for s in studies:
                if s.name == self.current_study.name:
                    self.current_study = s
                    break
    
    def load_study(self, study: StudyInfo) -> bool:
        """Load a study and create its manager."""
        try:
            self.current_manager = PrismManager(
                base_config_path=Path(study.base_config),
                prism_config_path=[Path(p) for p in study.prism_configs],
                study_name=study.name,
                output_dir=study.path.parent,
            )
            self.current_study = study
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to load study: {e}[/red]")
            return False
    
    def project_wizard(self) -> Optional[Project]:
        """Interactive wizard to create or find a project."""
        self.clear_screen()
        self.print_header("Project Setup")
        
        # Show recent projects if available
        recent = _load_recent_projects()
        valid_recent = []
        for p in recent:
            path = Path(p)
            if path.exists():
                valid_recent.append(path)
        
        if valid_recent:
            self.console.print(Panel(
                "\n".join([f"  {i+1}. {p}" for i, p in enumerate(valid_recent[:5])]),
                title="📚 Recent Projects",
                border_style="dim"
            ))
            self.console.print()
        
        options = [
            ("find", "🔍 Find Project", "Search for prism.project.yaml in current directory or parents"),
            ("create", "✨ Create Project", "Create a new prism.project.yaml"),
            ("path", "� Open Path", "Open a specific project by path"),
        ]
        
        # Add recent projects as options
        for i, p in enumerate(valid_recent[:5]):
            options.append((f"recent_{i}", f"📂 {Path(p).name}", str(p)))
        
        options.append(("quit", "", "Exit"))
        
        action = self.print_menu(options, title="Project Setup")
        
        if action == "quit":
            return None
        
        # Handle recent project selection
        if action.startswith("recent_"):
            idx = int(action.split("_")[1])
            path = valid_recent[idx]
            try:
                project = Project(path)
                _save_last_project(path)
                self.console.print(f"[green]✅ Loaded project: {project.config.name}[/green]")
                Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                return project
            except Exception as e:
                self.console.print(f"[red]Failed to load project: {e}[/red]")
                Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                return self.project_wizard()
            
        elif action == "find":
            try:
                project = find_project()
                _save_last_project(project.config.project_root / "prism.project.yaml")
                self.console.print(f"[green]✅ Found project: {project.config.name}[/green]")
                self.console.print(f"[dim]   at: {project.config.project_root}[/dim]")
                Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                return project
            except ProjectNotFoundError:
                self.console.print("[yellow]No project found in current directory or parents.[/yellow]")
                Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                return self.project_wizard()
                
        elif action == "create":
            return self._create_project_wizard()
            
        elif action == "path":
            path_str = Prompt.ask("[cyan]Enter project path[/cyan]", default=".")
            path = Path(path_str).expanduser().resolve()
            try:
                project = Project.load(path)
                _save_last_project(path)
                self.console.print(f"[green]✅ Loaded project: {project.config.name}[/green]")
                Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                return project
            except Exception as e:
                self.console.print(f"[red]Failed to load project: {e}[/red]")
                Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                return self.project_wizard()
        
        return None
    
    def _create_project_wizard(self) -> Optional[Project]:
        """Create a new project interactively."""
        self.clear_screen()
        self.print_header("Create New Project")
        
        # Project name
        name = Prompt.ask("[cyan]Project name[/cyan]", default="my-project")
        
        # Project root
        root_str = Prompt.ask("[cyan]Project root directory[/cyan]", default=".")
        root = Path(root_str).expanduser().resolve()
        
        # Train script
        train_script = Prompt.ask(
            "[cyan]Train script path (relative to project root)[/cyan]",
            default="train.py"
        )
        
        # Config argument
        config_arg = Prompt.ask(
            "[cyan]Config argument name[/cyan]",
            default="--config"
        )
        
        # Directories
        configs_dir = Prompt.ask("[cyan]Configs directory[/cyan]", default="configs")
        output_dir = Prompt.ask("[cyan]Output directory[/cyan]", default="outputs")
        
        # Prism configs are always inside configs/prism
        prism_configs_dir = f"{configs_dir}/prism"
        
        # Create the project config
        project_yaml = f"""# PRISM Project Configuration
project:
  name: "{name}"
  version: "1.0.0"

paths:
  train_script: "{train_script}"
  configs_dir: "{configs_dir}"
  prism_configs_dir: "{prism_configs_dir}"
  output_dir: "{output_dir}"

metrics:
  output_mode: "stdout_json"
  output_file: "metrics.json"
"""
        
        # Summary
        self.console.print()
        self.console.print(Panel(
            f"[white]Name:[/white] {name}\n"
            f"[white]Root:[/white] {root}\n"
            f"[white]Train:[/white] {train_script} {config_arg} <config>\n"
            f"[white]Configs:[/white] {configs_dir}/\n"
            f"[white]Prism Configs:[/white] {prism_configs_dir}/\n"
            f"[white]Output:[/white] {output_dir}/",
            title="📋 Project Summary",
            border_style="green"
        ))
        
        if not Confirm.ask("[cyan]Create this project?[/cyan]"):
            return None
        
        try:
            # Create directories
            root.mkdir(parents=True, exist_ok=True)
            (root / configs_dir).mkdir(parents=True, exist_ok=True)
            (root / prism_configs_dir).mkdir(parents=True, exist_ok=True)
            (root / output_dir).mkdir(parents=True, exist_ok=True)
            
            # Write project file
            project_file = root / "prism.project.yaml"
            project_file.write_text(project_yaml)
            
            self.console.print(f"[green]✅ Created project at: {project_file}[/green]")
            
            project = Project.load(project_file)
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            return project
            
        except Exception as e:
            self.console.print(f"[red]Failed to create project: {e}[/red]")
            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
            return None
    
    def main_menu(self) -> None:
        """Display and handle the main menu."""
        while True:
            self.clear_screen()
            self.print_header()
            
            # Show studies overview
            studies = self.get_studies()
            self.print_studies_table(studies)
            
            self.console.print()
            
            options = [
                ("select", "📂 Select Study", "Open an existing study"),
                ("create", "✨ Create Study", "Create a new parameter sweep"),
                ("delete", "❌ Delete Study", "Remove a study file"),
                ("refresh", "🔄 Refresh", "Refresh the studies list"),
                ("project", "📁 Change Project", "Load a different project"),
                ("quit", "", "Exit the TUI"),
            ]
            
            action = self.print_menu(options, title="Main Menu")
            
            if action == "quit":
                self.console.print("\n[cyan]👋 Goodbye![/cyan]\n")
                break
                
            elif action == "refresh":
                continue
                
            elif action == "project":
                new_project = self.project_wizard()
                if new_project:
                    self.project = new_project
                    self._create_executor()
                continue
                
            elif action == "select":
                if not studies:
                    self.console.print("[yellow]No studies available. Create one first![/yellow]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                    continue
                
                try:
                    choice = IntPrompt.ask(
                        f"[cyan]Enter study number (1-{len(studies)})[/cyan]",
                        default=1
                    )
                    if 1 <= choice <= len(studies):
                        if self.load_study(studies[choice - 1]):
                            self.study_menu()
                    else:
                        self.console.print("[red]Invalid choice.[/red]")
                        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                except Exception:
                    pass
                    
            elif action == "create":
                result = self.create_study_wizard()
                if result:
                    study_name, base_config, prism_configs = result
                    
                    try:
                        with self.console.status(f"[cyan]Creating study '{study_name}'...[/cyan]"):
                            manager = PrismManager(
                                base_config_path=base_config,
                                prism_config_path=prism_configs,
                                study_name=study_name,
                                output_dir=self.project.config.get_resolved_paths().output_dir,
                            )

                            # Get available keys and expand
                            available_keys = manager.get_available_keys()
                            manager.expand_configs(prism_keys=available_keys, linking_mode="zip")

                        self.console.print(f"\n[green]✅ Created study '{study_name}' with {len(manager.state.experiments)} experiments[/green]")

                        # Load the study
                        studies = self.get_studies()
                        for s in studies:
                            if s.name == study_name:
                                if self.load_study(s):
                                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                                    self.study_menu()
                                break

                    except Exception as e:
                        import traceback
                        self.console.print(f"[red]❌ Failed to create study: {e}[/red]")
                        self.console.print(f"[dim]{traceback.format_exc()}[/dim]")
                        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                else:
                    self.console.print("[yellow]Study creation cancelled or failed.[/yellow]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                            
            elif action == "delete":
                if not studies:
                    self.console.print("[yellow]No studies to delete.[/yellow]")
                    Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                    continue
                
                try:
                    choice = IntPrompt.ask(
                        f"[cyan]Enter study number to delete (1-{len(studies)})[/cyan]"
                    )
                    if 1 <= choice <= len(studies):
                        study = studies[choice - 1]
                        if Confirm.ask(f"[red]⚠️  Delete study '{study.name}'?[/red]"):
                            delete_artifacts = Confirm.ask(f"[yellow]Also delete artifacts directory?[/yellow]")
                            deleted = delete_study(
                                study_name=study.name,
                                output_dir=study.path.parent,
                                delete_artifacts_dir=delete_artifacts,
                            )
                            for p in deleted:
                                self.console.print(f"[green]✅ Deleted: {p}[/green]")
                            
                            Prompt.ask("\n[dim]Press Enter to continue[/dim]")
                except Exception:
                    pass
    
    def run(self):
        """Run the TUI application."""
        try:
            # If no project loaded, show project wizard
            if not self.project:
                self.project = self.project_wizard()
                if not self.project:
                    return
                self._create_executor()
            
            self.main_menu()
        except KeyboardInterrupt:
            self.console.print("\n\n[cyan]👋 Interrupted. Goodbye![/cyan]\n")
        except Exception as e:
            self.console.print(f"\n[red]❌ Error: {e}[/red]")
            raise


def main():
    """Entry point for the TUI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PRISM TUI - Interactive experiment management")
    parser.add_argument(
        "--project", "-p",
        type=str,
        help="Path to prism.project.yaml or project directory"
    )
    
    args = parser.parse_args()
    
    project_path = Path(args.project) if args.project else None
    tui = PrismTUI(project_path=project_path)
    tui.run()


if __name__ == "__main__":
    main()
