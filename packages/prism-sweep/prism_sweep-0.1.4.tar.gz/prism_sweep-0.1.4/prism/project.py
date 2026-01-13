"""
Prism Project - Project Configuration Management

This module handles the prism.project.yaml file which defines project-level
settings including paths to training scripts, schema, and validation rules.

Project YAML Format:

    project:
      name: "my_ml_project"
      version: "1.0"
    
    paths:
      # Training script (called as: python <script> --config <config.yaml>)
      train_script: "scripts/train.py"
      # Custom arguments (optional, {config_path} is replaced with actual path)
      train_args: ["--config", "{config_path}"]
      
      # Directories
      configs_dir: "configs/"
      prism_configs_dir: "configs/prism/"
      output_dir: "outputs/"
    
    # Schema file for config validation (optional)
    schema:
      file: "configs/schema.prism.yaml"
    
    # Validation rules file (optional)
    validation:
      file: "configs/validation.prism.yaml"
    
    # Metrics output settings
    metrics:
      # How training script outputs metrics
      output_mode: "stdout_json"  # or "file"
      output_file: "metrics.json"  # used when output_mode is "file"
"""

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml

from .utils import (
    print_info, print_warning, print_error, print_success, print_file,
    deep_merge
)


class ProjectNotFoundError(Exception):
    """Raised when no prism.project.yaml is found."""
    pass


# Default project file names
PROJECT_FILE_NAMES = [
    "prism.project.yaml",
    "prism.project.yml",
    ".prism.yaml",
    ".prism.yml",
]


@dataclass
class ProjectPaths:
    """Project path configuration."""
    train_script: Optional[Path] = None
    train_args: List[str] = field(default_factory=lambda: ["--config", "{config_path}"])
    configs_dir: Path = Path("configs")
    prism_configs_dir: Path = Path("configs/prism")
    output_dir: Path = Path("outputs")
    
    def resolve(self, project_root: Path) -> "ProjectPaths":
        """Resolve all paths relative to project root."""
        return ProjectPaths(
            train_script=project_root / self.train_script if self.train_script else None,
            train_args=self.train_args,
            configs_dir=project_root / self.configs_dir,
            prism_configs_dir=project_root / self.prism_configs_dir,
            output_dir=project_root / self.output_dir,
        )


@dataclass
class MetricsConfig:
    """Configuration for how metrics are captured from training."""
    output_mode: str = "stdout_json"  # "stdout_json", "file", "exit_code"
    output_file: str = "metrics.json"  # Relative to experiment output dir
    success_key: Optional[str] = None  # JSON key that indicates success
    
    def __post_init__(self):
        valid_modes = {"stdout_json", "file", "exit_code"}
        if self.output_mode not in valid_modes:
            raise ValueError(f"output_mode must be one of {valid_modes}")


@dataclass
class ProjectConfig:
    """Complete project configuration."""
    name: str = "unnamed_project"
    version: str = "1.0"
    paths: ProjectPaths = field(default_factory=ProjectPaths)
    validator_module: Optional[Path] = None  # Custom Python validator module
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    
    # Runtime state
    project_root: Path = field(default_factory=Path.cwd)
    project_file: Optional[Path] = None
    _custom_validator_module: Any = field(default=None, repr=False)
    
    def get_custom_validator(self) -> Optional[Any]:
        """
        Get the custom Python validator module if defined.
        
        The validator module must expose either:
        - validate(config_dict: Dict) -> validated_config (dict or dataclass)
        - ConfigValidator class with load_and_validate(path) method
        
        Returns:
            Loaded Python module or None
        """
        if self.validator_module is None:
            return None
        
        if self._custom_validator_module is not None:
            return self._custom_validator_module
        
        # Resolve path
        validator_path = self.validator_module
        if not validator_path.is_absolute():
            validator_path = self.project_root / validator_path
        
        if not validator_path.exists():
            print_warning(f"Validator module not found: {validator_path}")
            return None
        
        # Load the module dynamically
        import importlib.util
        import sys
        
        # Add project root AND validator's parent directory to sys.path
        # This allows both absolute and relative imports in the validator
        project_root_str = str(self.project_root)
        validator_parent_str = str(validator_path.parent)
        
        paths_to_add = []
        if project_root_str not in sys.path:
            paths_to_add.append(project_root_str)
        if validator_parent_str not in sys.path and validator_parent_str != project_root_str:
            paths_to_add.append(validator_parent_str)
        
        for p in paths_to_add:
            sys.path.insert(0, p)
        
        try:
            # Try to import as a submodule of the parent package if possible
            # e.g., configs/validator.py -> configs.validator
            relative_path = validator_path.relative_to(self.project_root)
            module_name = str(relative_path.with_suffix('')).replace('/', '.').replace('\\\\', '.')
            
            # First, ensure parent packages exist as modules
            parts = module_name.split('.')
            if len(parts) > 1:
                # Import parent package first (e.g., 'configs')
                parent_package = parts[0]
                parent_init = self.project_root / parent_package / "__init__.py"
                
                if not parent_init.exists():
                    # Create a temporary __init__.py to make it a package
                    parent_init.touch()
                    created_init = True
                else:
                    created_init = False
                
                try:
                    # Import using the full module path
                    import importlib
                    module = importlib.import_module(module_name)
                    self._custom_validator_module = module
                    print_success(f"Loaded custom validator: {module_name}")
                    return module
                except ImportError:
                    # Fall back to direct file loading
                    pass
                finally:
                    if created_init:
                        parent_init.unlink()
            
            # Fallback: load as standalone module
            spec = importlib.util.spec_from_file_location("custom_validator", validator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._custom_validator_module = module
            print_success(f"Loaded custom validator: {validator_path.name}")
            return module
            
        except Exception as e:
            print_error(f"Failed to load validator module {validator_path}: {e}")
            return None
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a config dict using the custom validator.
        
        Args:
            config: Configuration dictionary
        
        Returns:
            Validated configuration (may be modified with defaults)
        
        Raises:
            ValueError: If validation fails
        """
        validator_module = self.get_custom_validator()
        
        if validator_module is None:
            # No validator configured - return config as-is
            return config
        
        # Try different validator interfaces
        # 1. validate(dict) -> dict function
        if hasattr(validator_module, 'validate'):
            return validator_module.validate(config)
        
        # 2. ConfigValidator class with validate_dict method
        if hasattr(validator_module, 'ConfigValidator'):
            validator_cls = validator_module.ConfigValidator
            validator = validator_cls()
            if hasattr(validator, 'validate_dict'):
                return validator.validate_dict(config)
            if hasattr(validator, 'validate'):
                return validator.validate(config)
        
        print_warning(f"Validator module has no recognized validate function")
        return config
    
    def get_resolved_paths(self) -> ProjectPaths:
        """Get paths resolved relative to project root."""
        return self.paths.resolve(self.project_root)


class Project:
    """
    Manages a Prism project configuration.
    
    Usage:
        # Load existing project
        project = Project.load("path/to/project")
        
        # Or create new
        project = Project.create("path/to/new/project", name="my_project")
        
        # Access configuration
        print(project.config.name)
        print(project.config.paths.train_script)
    """
    
    def __init__(self, config: ProjectConfig):
        self.config = config
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> "Project":
        """
        Load a project from a directory or project file.
        
        Args:
            path: Path to project directory or project file
        
        Returns:
            Project instance
        
        Raises:
            FileNotFoundError: If project file not found
        """
        path = Path(path).resolve()
        
        # If path is a file, use it directly
        if path.is_file():
            project_file = path
            project_root = path.parent
        else:
            # Search for project file
            project_file = None
            for name in PROJECT_FILE_NAMES:
                candidate = path / name
                if candidate.exists():
                    project_file = candidate
                    break
            
            if project_file is None:
                raise FileNotFoundError(
                    f"No project file found in {path}. "
                    f"Expected one of: {PROJECT_FILE_NAMES}"
                )
            project_root = path
        
        # Load project file
        with open(project_file, 'r') as f:
            raw = yaml.safe_load(f) or {}
        
        config = cls._parse_config(raw, project_root, project_file)
        
        print_success(f"Loaded project: {config.name}")
        print_file(str(project_file), "Project file")
        
        return cls(config)
    
    @classmethod
    def create(
        cls,
        path: Union[str, Path],
        name: str = "my_project",
        train_script: Optional[str] = None,
        **kwargs
    ) -> "Project":
        """
        Create a new project.
        
        Args:
            path: Path to project directory
            name: Project name
            train_script: Path to training script (relative to project root)
            **kwargs: Additional project configuration
        
        Returns:
            Project instance
        """
        path = Path(path).resolve()
        path.mkdir(parents=True, exist_ok=True)
        
        project_file = path / "prism.project.yaml"
        
        # Build configuration
        config_dict = {
            "project": {
                "name": name,
                "version": "1.0",
            },
            "paths": {
                "configs_dir": "configs",
                "prism_configs_dir": "configs/prism",
                "output_dir": "outputs",
            },
            "metrics": {
                "output_mode": "stdout_json",
            }
        }
        
        if train_script:
            config_dict["paths"]["train_script"] = train_script
        
        # Merge additional kwargs
        for key, value in kwargs.items():
            if key in config_dict:
                if isinstance(config_dict[key], dict) and isinstance(value, dict):
                    config_dict[key] = deep_merge(config_dict[key], value)
                else:
                    config_dict[key] = value
            else:
                config_dict[key] = value
        
        # Write project file
        with open(project_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
        
        # Create directories
        (path / "configs").mkdir(exist_ok=True)
        (path / "configs" / "prism").mkdir(exist_ok=True)
        (path / "outputs").mkdir(exist_ok=True)
        
        print_success(f"Created project: {name}")
        print_file(str(project_file), "Project file")
        
        config = cls._parse_config(config_dict, path, project_file)
        return cls(config)
    
    @classmethod
    def _parse_config(
        cls,
        raw: Dict[str, Any],
        project_root: Path,
        project_file: Path
    ) -> ProjectConfig:
        """Parse raw config dict into ProjectConfig."""
        
        # Project info
        project_raw = raw.get("project", {})
        name = project_raw.get("name", "unnamed_project")
        version = project_raw.get("version", "1.0")
        
        # Paths
        paths_raw = raw.get("paths", {})
        train_script = paths_raw.get("train_script")
        paths = ProjectPaths(
            train_script=Path(train_script) if train_script else None,
            train_args=paths_raw.get("train_args", ["--config", "{config_path}"]),
            configs_dir=Path(paths_raw.get("configs_dir", "configs")),
            prism_configs_dir=Path(paths_raw.get("prism_configs_dir", "configs/prism")),
            output_dir=Path(paths_raw.get("output_dir", "outputs")),
        )
        
        # Custom validator module (Python file)
        validator_raw = raw.get("validator", {})
        validator_module = validator_raw.get("module") if isinstance(validator_raw, dict) else validator_raw
        
        # Metrics
        metrics_raw = raw.get("metrics", {})
        metrics = MetricsConfig(
            output_mode=metrics_raw.get("output_mode", "stdout_json"),
            output_file=metrics_raw.get("output_file", "metrics.json"),
            success_key=metrics_raw.get("success_key"),
        )
        
        return ProjectConfig(
            name=name,
            version=version,
            paths=paths,
            validator_module=Path(validator_module) if validator_module else None,
            metrics=metrics,
            project_root=project_root,
            project_file=project_file,
        )
    
    def save(self):
        """Save project configuration to file."""
        if self.config.project_file is None:
            raise ValueError("No project file path set")
        
        config_dict = self._config_to_dict()
        
        with open(self.config.project_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
        
        print_success(f"Saved project configuration")
    
    def _config_to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        result = {
            "project": {
                "name": self.config.name,
                "version": self.config.version,
            },
            "paths": {
                "configs_dir": str(self.config.paths.configs_dir),
                "prism_configs_dir": str(self.config.paths.prism_configs_dir),
                "output_dir": str(self.config.paths.output_dir),
            },
            "metrics": {
                "output_mode": self.config.metrics.output_mode,
                "output_file": self.config.metrics.output_file,
            }
        }
        
        if self.config.paths.train_script:
            result["paths"]["train_script"] = str(self.config.paths.train_script)
        
        if self.config.paths.train_args != ["--config", "{config_path}"]:
            result["paths"]["train_args"] = self.config.paths.train_args
        
        if self.config.schema_file:
            result["schema"] = {"file": str(self.config.schema_file)}
        
        if self.config.validation_file:
            result["validation"] = {"file": str(self.config.validation_file)}
        
        if self.config.metrics.success_key:
            result["metrics"]["success_key"] = self.config.metrics.success_key
        
        return result
    
    # Convenience properties for easy access
    @property
    def output_dir(self) -> Path:
        """Get resolved output directory."""
        return self.config.get_resolved_paths().output_dir
    
    @property
    def configs_dir(self) -> Path:
        """Get resolved configs directory."""
        return self.config.get_resolved_paths().configs_dir
    
    @property
    def prism_configs_dir(self) -> Path:
        """Get resolved prism configs directory."""
        return self.config.get_resolved_paths().prism_configs_dir
    
    @property
    def list_configs(self) -> List[Path]:
        """List all configuration files in the configs directory."""
        configs_dir = self.config.project_root / self.config.paths.configs_dir
        if not configs_dir.exists():
            return []
        
        configs = []
        for ext in [".yaml", ".yml"]:
            configs.extend(configs_dir.glob(f"*{ext}"))
        
        # Exclude prism configs
        prism_dir = self.config.project_root / self.config.paths.prism_configs_dir
        configs = [c for c in configs if not c.is_relative_to(prism_dir)]
        
        return sorted(configs)
    
    def list_prism_configs(self) -> List[Path]:
        """List all prism configuration files."""
        prism_dir = self.config.project_root / self.config.paths.prism_configs_dir
        if not prism_dir.exists():
            return []
        
        configs = []
        for ext in [".yaml", ".yml"]:
            configs.extend(prism_dir.glob(f"*.prism{ext}"))
            configs.extend(prism_dir.glob(f"*{ext}"))
        
        return sorted(set(configs))
    
    def list_studies(self) -> List[Path]:
        """List all existing study (.study.json) files in output directory."""
        output_dir = self.config.project_root / self.config.paths.output_dir
        if not output_dir.exists():
            return []

        return sorted(output_dir.glob("**/*.study.json"))
    
    def get_train_command(self, config_path: Union[str, Path]) -> List[str]:
        """
        Get the command to run training.
        
        Args:
            config_path: Path to configuration file
        
        Returns:
            Command as list of strings
        """
        paths = self.config.get_resolved_paths()
        
        if paths.train_script is None:
            raise ValueError("No train_script defined in project")
        
        # Build command
        import sys
        cmd = [sys.executable, str(paths.train_script)]
        
        # Add arguments, replacing {config_path}
        config_path = str(config_path)
        for arg in paths.train_args:
            cmd.append(arg.replace("{config_path}", config_path))
        
        return cmd


def find_project(start_path: Optional[Union[str, Path]] = None) -> Project:
    """
    Find and load a project by searching upward from start_path.
    
    Args:
        start_path: Starting directory (defaults to cwd)
    
    Returns:
        Project instance
        
    Raises:
        ProjectNotFoundError: If no project file is found
    """
    path = Path(start_path or os.getcwd()).resolve()
    
    while path != path.parent:
        for name in PROJECT_FILE_NAMES:
            project_file = path / name
            if project_file.exists():
                return Project.load(project_file)
        path = path.parent
    
    raise ProjectNotFoundError(
        f"No prism.project.yaml found in {start_path or os.getcwd()} or parent directories"
    )


def init_project(
    path: Union[str, Path],
    name: str,
    train_script: Optional[str] = None,
    interactive: bool = False,
) -> Project:
    """
    Initialize a new Prism project.
    
    Args:
        path: Project directory
        name: Project name
        train_script: Training script path
        interactive: Whether to prompt for options
    
    Returns:
        Created Project instance
    """
    return Project.create(
        path=path,
        name=name,
        train_script=train_script,
    )
