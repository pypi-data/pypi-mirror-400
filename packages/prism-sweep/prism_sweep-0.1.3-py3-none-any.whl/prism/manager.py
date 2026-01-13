"""
Prism Manager - Core Logic for Parameter Sweep Management

This module provides the PrismManager class that handles:
- Configuration expansion from base + prism configs
- State file (.study.json) management
- Named experiments ($-notation), positional sweeps (list), and sweep definitions (_type/_*)
- Experiment naming and tracking
"""

import json
import yaml
import copy
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import itertools

from .utils import (
    print_info, print_success, print_warning, print_error, 
    print_progress, print_file, deep_merge, deep_get, deep_set
)

if TYPE_CHECKING:
    from .project import Project
    from .executor import Executor


STUDY_STATE_EXTENSION = ".study.json"


class ExperimentStatus(str, Enum):
    """Status of an experiment run."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class ExperimentRecord:
    """Record of a single experiment configuration and its state."""
    status: ExperimentStatus = ExperimentStatus.PENDING
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status.value if isinstance(self.status, ExperimentStatus) else self.status,
            "config": self.config,
            "metrics": self.metrics,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "duration_seconds": self.duration_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentRecord":
        """Create from dictionary."""
        status = data.get("status", "PENDING")
        if isinstance(status, str):
            status = ExperimentStatus(status)
        return cls(
            status=status,
            config=data.get("config", {}),
            metrics=data.get("metrics", {}),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
            duration_seconds=data.get("duration_seconds"),
        )


@dataclass 
class PrismState:
    """State file content for a Prism study."""
    study_name: str
    base_config_path: str
    prism_config_paths: List[str]
    base_config_content: Dict[str, Any] = field(default_factory=dict)
    prism_configs_content: List[Dict[str, Any]] = field(default_factory=list)
    experiments: Dict[str, ExperimentRecord] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "study_name": self.study_name,
            "base_config_path": self.base_config_path,
            "prism_config_paths": self.prism_config_paths,
            "prism_configs_content": self.prism_configs_content,
            "base_config_content": self.base_config_content,
            "experiments": {k: v.to_dict() for k, v in self.experiments.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrismState":
        """Create from dictionary."""
        experiments = {}
        for k, v in data.get("experiments", {}).items():
            experiments[k] = ExperimentRecord.from_dict(v)

        if "prism_config_paths" not in data or "prism_configs_content" not in data:
            raise ValueError("Invalid study state file format")

        prism_config_paths = data["prism_config_paths"]
        prism_configs_content = data["prism_configs_content"]

        return cls(
            study_name=data["study_name"],
            base_config_path=data["base_config_path"],
            prism_config_paths=prism_config_paths,
            base_config_content=data.get("base_config_content", {}),
            prism_configs_content=prism_configs_content,
            experiments=experiments,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )


class PrismManager:
    """
    Manager for parameter sweep experiments.
    
    Handles the combination of a base config and prism configs to generate,
    manage, and execute multiple experiment configurations.
    
    Prism Config Format:
    --------------------
        Prism configs can contain three types of parameter specifications:
    
        1. Named experiments ($-notation): Named configurations
       ```yaml
       training:
         optimizer:
                     lr: {"$low_lr": 0.0001, "$high_lr": 0.01}
       ```
             Creates experiments named by their keys (low_lr, high_lr).
             The same $name can be reused on multiple parameters to build a single experiment.
       
    2. Positional Linking (List): Sequential configurations  
       ```yaml
       data:
         seed: [42, 123, 456]
       ```
       Creates experiments run_0, run_1, run_2, etc.

        3. Sweep definitions (_type/_*): Advanced generators
             ```yaml
             optimizer:
                 lr:
                     _type: choice
                     _values: [0.001, 0.01]
             ```
    
    Usage:
    ------
    ```python
    manager = PrismManager(
        base_config_path="configs/base.yaml",
        prism_config_path="configs/sweep.prism.yaml", 
        study_name="my_sweep",
        output_dir="outputs"
    )
    
    # Generate experiment configurations
    manager.expand_configs()
    
    # Execute with custom executor
    from prism.executor import Executor
    executor = Executor(project)
    manager.execute_all(executor)
    ```
    """
    
    def __init__(
        self,
        base_config_path: Union[str, Path],
        prism_config_path: Union[str, Path, List[Union[str, Path]], None] = None,
        study_name: str = "study",
        output_dir: Union[str, Path] = "outputs",
        state_file_path: Optional[Union[str, Path]] = None,
        load_state: bool = True,
    ):
        """
        Initialize PrismManager.
        
        Args:
            base_config_path: Path to the base configuration YAML file
            prism_config_path: Path(s) to prism config file(s). Can be:
                              - Single path
                              - List of paths (cartesian product)
                              - None (single experiment = base config only)
            study_name: Name of the study (used for .study.json state file)
            output_dir: Directory for outputs and state file
            state_file_path: Optional explicit state file path override
            load_state: If False, do not load/create state in __init__ (used internally)
        """
        self.base_config_path = Path(base_config_path)
        
        # Handle prism config paths
        if prism_config_path is None:
            self.prism_config_paths = []
        elif isinstance(prism_config_path, (str, Path)):
            self.prism_config_paths = [Path(prism_config_path)]
        else:
            self.prism_config_paths = [Path(p) for p in prism_config_path]
        
        self.study_name = study_name
        self.output_dir = Path(output_dir)
        
        # State file path (canonical)
        if state_file_path is not None:
            self.state_file_path = Path(state_file_path)
        else:
            self.state_file_path = self.output_dir / f"{study_name}{STUDY_STATE_EXTENSION}"

        # Load or create state
        if load_state:
            self.state: PrismState = self._load_or_create_state()
        else:
            # Placeholder; caller is expected to assign a real state
            self.state = PrismState(
                study_name=self.study_name,
                base_config_path=str(self.base_config_path),
                prism_config_paths=[str(p) for p in self.prism_config_paths],
            )
    
    # =========================================================================
    # File I/O
    # =========================================================================
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load a YAML file with inheritance support."""
        with open(path, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # Handle inheritance
        if 'inherit_from' in config:
            base_path = path.parent / config['inherit_from']
            if base_path.exists():
                base_config = self._load_yaml(base_path)
                config = deep_merge(base_config, config)
                config.pop('inherit_from', None)
        
        return config
    
    def _save_yaml(self, path: Path, data: Dict[str, Any]):
        """Save data to a YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load a JSON file."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _save_json(self, path: Path, data: Dict[str, Any]):
        """Save data to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    # =========================================================================
    # State Management
    # =========================================================================
    
    def _load_or_create_state(self) -> PrismState:
        """Load existing state file or create a new one."""
        if self.state_file_path.exists():
            print_file(str(self.state_file_path), "Loading state")
            data = self._load_json(self.state_file_path)
            state = PrismState.from_dict(data)
            
            # Reset any RUNNING experiments to PENDING
            # (they were interrupted if we're loading from disk)
            running_count = 0
            for exp in state.experiments.values():
                if exp.status == ExperimentStatus.RUNNING:
                    exp.status = ExperimentStatus.PENDING
                    exp.started_at = None
                    running_count += 1
            
            if running_count > 0:
                print_warning(f"Reset {running_count} interrupted experiments from RUNNING to PENDING")
                # Save the corrected state
                self._save_state(state)
            
            return state
        
        # Create new state
        print_progress(f"Creating new study: {self.study_name}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load base config
        if not self.base_config_path.exists():
            raise FileNotFoundError(f"Base config not found: {self.base_config_path}")
        base_config = self._load_yaml(self.base_config_path)
        
        # Load all prism configs
        prism_configs = []
        for prism_path in self.prism_config_paths:
            if not prism_path.exists():
                raise FileNotFoundError(f"Prism config not found: {prism_path}")
            prism_configs.append(self._load_yaml(prism_path))
            print_file(str(prism_path), "Loaded prism config")
        
        state = PrismState(
            study_name=self.study_name,
            base_config_path=str(self.base_config_path),
            prism_config_paths=[str(p) for p in self.prism_config_paths],
            base_config_content=base_config,
            prism_configs_content=prism_configs
        )
        
        self._save_state(state)
        return state
    
    def _save_state(self, state: Optional[PrismState] = None):
        """Save current state to the .study.json file."""
        if state is None:
            state = self.state
        state.updated_at = datetime.now().isoformat()
        self._save_json(self.state_file_path, state.to_dict())
    
    def reload_configs(self):
        """Reload base and prism configs from disk and update experiments."""
        self.state.base_config_content = self._load_yaml(self.base_config_path)
        self.state.prism_configs_content = [
            self._load_yaml(Path(p)) for p in self.state.prism_config_paths
        ]
        self.expand_configs()
        self._save_state()
        print_success("Reloaded configurations from disk")
    
    # =========================================================================
    # Parameter Analysis
    # =========================================================================
    
    def _set_nested_value(self, config: Dict, key_path: str, value: Any):
        """Set a value in a nested dictionary using dot notation."""
        keys = key_path.split(".")
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _get_nested_value(self, config: Dict, key_path: str, default: Any = None) -> Any:
        """Get a value from a nested dictionary using dot notation."""
        return deep_get(config, key_path, default)

    def _assert_path_exists_in_base(self, base_config: Dict[str, Any], key_path: str):
        """Ensure an override path exists in base config to avoid silent typos."""
        sentinel = object()
        if deep_get(base_config, key_path, sentinel) is sentinel:
            raise ValueError(
                f"Prism override refers to '{key_path}', but that path does not exist in base config. "
                "Add it to the base config first (or fix the typo)."
            )
    
    def _is_sweep_definition(self, value: Any) -> bool:
        """
        Check if a value is a sweep definition (e.g., _type: choice, _values: [...]).
        
        Supported formats:
        - {_type: "choice", _values: [...]}
        - {_type: "range", _min: ..., _max: ..., _step: ...}
        - {_type: "linspace", _min: ..., _max: ..., _num: ...}
        """
        if not isinstance(value, dict):
            return False
        return "_type" in value and ("_values" in value or "_min" in value)
    
    def _expand_sweep_definition(self, sweep_def: Dict[str, Any]) -> List[Any]:
        """
        Expand a sweep definition into a list of values.
        
        Args:
            sweep_def: Dict with _type and _values or _min/_max/_step
        
        Returns:
            List of expanded values
        """
        sweep_type = sweep_def.get("_type", "choice")
        
        if sweep_type == "choice":
            return sweep_def.get("_values", [])
        
        elif sweep_type == "range":
            start = sweep_def.get("_min", 0)
            stop = sweep_def.get("_max", 1)
            step = sweep_def.get("_step", 1)
            if step == 0:
                raise ValueError("range sweep requires _step != 0")

            values: List[Any] = []
            current = start
            # Inclusive stop with tolerance for floats
            eps = 1e-12
            if step > 0:
                while current <= stop + eps:
                    values.append(current)
                    current = current + step
            else:
                while current >= stop - eps:
                    values.append(current)
                    current = current + step
            return values
        
        elif sweep_type == "linspace":
            start = sweep_def.get("_min", 0)
            stop = sweep_def.get("_max", 1)
            num = int(sweep_def.get("_num", 10))
            if num <= 0:
                return []
            if num == 1:
                return [start]
            step = (stop - start) / (num - 1)
            return [start + i * step for i in range(num)]
        
        else:
            # Unknown type, return values if present
            return sweep_def.get("_values", [sweep_def])
    
    def _is_dollar_experiment_map(self, value: Dict[str, Any]) -> bool:
        """Return True if dict is a $experiment-name map (all keys start with '$')."""
        if not isinstance(value, dict) or not value:
            return False
        return all(isinstance(k, str) and k.startswith("$") for k in value.keys())
    
    def _extract_parameter_types(self, prism_config: Dict[str, Any]) -> tuple:
        """
        Extract nominal (dict), positional (list), and scalar parameters.
        
        Returns:
            Tuple of (nominal_params, positional_params, scalar_params)
        """
        nominal_params = {}
        positional_params = {}
        scalar_params = {}
        
        def extract_recursive(config: Dict, prefix: str = ""):
            for key, value in config.items():
                # Skip the special _linking_mode key
                if key == "_linking_mode":
                    continue
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    # Check for sweep definition first (_type/_values syntax)
                    if self._is_sweep_definition(value):
                        expanded = self._expand_sweep_definition(value)
                        if len(expanded) > 1:
                            positional_params[full_key] = expanded
                        elif len(expanded) == 1:
                            scalar_params[full_key] = expanded[0]
                    elif self._is_dollar_experiment_map(value):
                        mapped: Dict[str, Any] = {}
                        for exp_key, exp_value in value.items():
                            exp_name = exp_key[1:]
                            if not exp_name:
                                raise ValueError(f"Invalid experiment name '{exp_key}' under '{full_key}'")
                            if exp_name in mapped:
                                raise ValueError(f"Duplicate experiment key '${exp_name}' under '{full_key}'")
                            mapped[exp_name] = exp_value
                        nominal_params[full_key] = mapped
                    else:
                        extract_recursive(value, full_key)
                elif isinstance(value, list):
                    # List-of-values sweep only if items are scalar (no dict/list)
                    if all(not isinstance(item, (dict, list)) for item in value) and len(value) > 1:
                        positional_params[full_key] = value
                    else:
                        scalar_params[full_key] = value
                else:
                    scalar_params[full_key] = value
        
        extract_recursive(prism_config)
        return nominal_params, positional_params, scalar_params
    
    def _get_nominal_keys(self, nominal_params: Dict[str, Dict]) -> List[str]:
        """Extract all unique nominal keys from nominal parameters."""
        all_keys = set()
        for param_values in nominal_params.values():
            all_keys.update(param_values.keys())
        return sorted(list(all_keys))
    
    def _get_keys_per_file(self) -> List[List[str]]:
        """Get the list of keys for each prism file separately."""
        prism_configs = self.state.prism_configs_content
        keys_per_file = []
        
        for prism_config in prism_configs:
            nominal_params, positional_params, _ = self._extract_parameter_types(prism_config)

            if nominal_params and positional_params:
                raise ValueError(
                    "A single .prism.yaml file cannot mix $-named experiments and positional sweeps. "
                    "Split them into multiple prism files if you need both."
                )
            
            file_keys = []
            if nominal_params:
                file_keys = self._get_nominal_keys(nominal_params)
            elif positional_params:
                lengths = [len(v) for v in positional_params.values()]
                if len(set(lengths)) != 1:
                    raise ValueError(f"Positional parameters have different lengths: {lengths}")
                file_keys = [f"run_{j}" for j in range(lengths[0])]
            
            if file_keys:
                keys_per_file.append(file_keys)
        
        return keys_per_file
    
    def get_available_keys(self) -> List[str]:
        """
        Get all available experiment keys.
        
        When multiple prism files are provided, returns cartesian product.
        """
        if not self.state.prism_configs_content:
            return ["default"]
        
        keys_per_file = self._get_keys_per_file()
        
        if not keys_per_file:
            return ["default"]
        
        if len(keys_per_file) == 1:
            return keys_per_file[0]
        
        # Cartesian product
        product_keys = []
        for combo in itertools.product(*keys_per_file):
            product_keys.append("_".join(combo))
        
        return product_keys
    
    # =========================================================================
    # Config Expansion
    # =========================================================================
    
    def expand_configs(
        self,
        prism_keys: Optional[List[str]] = None,
        linking_mode: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Expand the base config with prism overrides to generate experiment configs.
        
        Args:
            prism_keys: Optional list of specific keys to generate
            linking_mode: "zip" (strict) or "product" (cartesian). If None, reads from prism file or defaults to "zip"
        
        Returns:
            Dict of {experiment_key: merged_config}
        """
        prism_configs = self.state.prism_configs_content
        base_config = self.state.base_config_content

        # No prism configs -> single experiment
        if not prism_configs:
            experiments = {"default": copy.deepcopy(base_config)}
            self._update_state_experiments(experiments)
            print_success("Generated 1 experiment configuration (no prism sweep)")
            return experiments
        
        # Check for multiple prism files
        keys_per_file = self._get_keys_per_file()
        if len(keys_per_file) > 1:
            return self._expand_configs_cartesian(prism_keys)
        
        # Single file mode
        prism_config = self.state.prism_configs_content[0]
        
        # Extract linking_mode from prism file if not provided as argument
        if linking_mode is None:
            linking_mode = prism_config.get("_linking_mode", "zip")
        
        # Validate linking_mode
        if linking_mode not in ["zip", "product"]:
            raise ValueError(f"Invalid linking_mode '{linking_mode}'. Must be 'zip' or 'product'")
        
        nominal_params, positional_params, scalar_params = self._extract_parameter_types(prism_config)

        if nominal_params and positional_params:
            raise ValueError(
                "A single .prism.yaml file cannot mix $-named experiments and positional sweeps. "
                "Split them into multiple prism files if you need both."
            )
        
        print_info(f"Found {len(nominal_params)} nominal, {len(positional_params)} positional, {len(scalar_params)} scalar params")
        
        # Print linking mode info for positional params
        if positional_params:
            print_info(f"Linking mode: {linking_mode}")
        
        experiments = {}
        
        # Handle nominal parameters
        if nominal_params:
            all_nominal_keys = self._get_nominal_keys(nominal_params)
            keys_to_generate = all_nominal_keys if prism_keys is None else [k for k in prism_keys if k in all_nominal_keys]
            
            for config_key in keys_to_generate:
                merged = copy.deepcopy(base_config)
                
                for param_path, value in scalar_params.items():
                    self._assert_path_exists_in_base(base_config, param_path)
                    self._set_nested_value(merged, param_path, value)
                
                for param_path, param_values in nominal_params.items():
                    if config_key in param_values:
                        self._assert_path_exists_in_base(base_config, param_path)
                        self._set_nested_value(merged, param_path, param_values[config_key])
                
                experiments[config_key] = merged
        
        # Handle positional parameters
        elif positional_params:
            list_lengths = [len(v) for v in positional_params.values()]
            
            if linking_mode == "zip":
                if len(set(list_lengths)) > 1:
                    raise ValueError(f"Positional parameters have different lengths: {list_lengths}")
                
                num_runs = list_lengths[0] if list_lengths else 0
                
                for run_idx in range(num_runs):
                    run_key = f"run_{run_idx}"
                    merged = copy.deepcopy(base_config)
                    
                    for param_path, value in scalar_params.items():
                        self._assert_path_exists_in_base(base_config, param_path)
                        self._set_nested_value(merged, param_path, value)
                    
                    for param_path, param_values in positional_params.items():
                        self._assert_path_exists_in_base(base_config, param_path)
                        self._set_nested_value(merged, param_path, param_values[run_idx])
                    
                    experiments[run_key] = merged
            
            elif linking_mode == "product":
                param_paths = list(positional_params.keys())
                param_values = list(positional_params.values())
                
                for run_idx, combo in enumerate(itertools.product(*param_values)):
                    run_key = f"run_{run_idx}"
                    merged = copy.deepcopy(base_config)
                    
                    for param_path, value in scalar_params.items():
                        self._assert_path_exists_in_base(base_config, param_path)
                        self._set_nested_value(merged, param_path, value)
                    
                    for param_path, value in zip(param_paths, combo):
                        self._assert_path_exists_in_base(base_config, param_path)
                        self._set_nested_value(merged, param_path, value)
                    
                    experiments[run_key] = merged
        
        # Only scalar overrides
        elif scalar_params:
            merged = copy.deepcopy(base_config)
            for param_path, value in scalar_params.items():
                self._assert_path_exists_in_base(base_config, param_path)
                self._set_nested_value(merged, param_path, value)
            experiments["default"] = merged
        
        else:
            experiments["default"] = copy.deepcopy(base_config)
        
        self._update_state_experiments(experiments)
        print_success(f"Generated {len(experiments)} experiment configurations")
        
        return experiments
    
    def _expand_configs_cartesian(
        self,
        prism_keys: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Expand configs using cartesian product of keys from multiple prism files."""
        prism_configs = self.state.prism_configs_content
        base_config = self.state.base_config_content
        
        keys_per_file = self._get_keys_per_file()
        params_per_file = [self._extract_parameter_types(cfg) for cfg in prism_configs]
        
        # Build mapping from keys_per_file index to actual file index
        # Files with only scalars don't appear in keys_per_file
        keys_file_indices = []
        for file_idx, prism_config in enumerate(prism_configs):
            nominal_params, positional_params, _ = self._extract_parameter_types(prism_config)
            if nominal_params or positional_params:
                keys_file_indices.append(file_idx)
        
        print_info(f"Multi-file mode: {len(prism_configs)} files, cartesian product")
        
        all_combos = list(itertools.product(*keys_per_file))
        
        if prism_keys:
            all_combos = [c for c in all_combos if "_".join(c) in prism_keys]
        
        experiments = {}
        
        for combo in all_combos:
            compound_key = "_".join(combo)
            merged = copy.deepcopy(base_config)
            
            # First, apply scalars from ALL files (including scalar-only files)
            for file_idx, (nominal_params, positional_params, scalar_params) in enumerate(params_per_file):
                for param_path, value in scalar_params.items():
                    self._assert_path_exists_in_base(base_config, param_path)
                    self._set_nested_value(merged, param_path, value)
            
            # Then, apply nominal/positional params from files that contribute to the combo
            for combo_idx, key_for_file in enumerate(combo):
                file_idx = keys_file_indices[combo_idx]
                nominal_params, positional_params, scalar_params = params_per_file[file_idx]

                if nominal_params and positional_params:
                    raise ValueError(
                        "A single .prism.yaml file cannot mix $-named experiments and positional sweeps. "
                        "Split them into multiple prism files if you need both."
                    )
                
                if nominal_params:
                    for param_path, param_values in nominal_params.items():
                        if key_for_file in param_values:
                            self._assert_path_exists_in_base(base_config, param_path)
                            self._set_nested_value(merged, param_path, param_values[key_for_file])
                elif positional_params:
                    if not key_for_file.startswith("run_"):
                        raise ValueError(f"Invalid positional key '{key_for_file}'")
                    run_idx = int(key_for_file.split("_", 1)[1])
                    lengths = [len(v) for v in positional_params.values()]
                    if len(set(lengths)) != 1:
                        raise ValueError(f"Positional parameters have different lengths: {lengths}")
                    if run_idx < 0 or run_idx >= lengths[0]:
                        raise ValueError(f"Positional key '{key_for_file}' out of range (0..{lengths[0]-1})")
                    for param_path, param_values in positional_params.items():
                        self._assert_path_exists_in_base(base_config, param_path)
                        self._set_nested_value(merged, param_path, param_values[run_idx])
            
            experiments[compound_key] = merged
        
        self._update_state_experiments(experiments)
        print_success(f"Generated {len(experiments)} experiment configurations (cartesian)")
        
        return experiments
    
    def _update_state_experiments(self, experiments: Dict[str, Dict[str, Any]]):
        """Update state with generated experiments."""
        for exp_key, exp_config in experiments.items():
            if exp_key not in self.state.experiments:
                self.state.experiments[exp_key] = ExperimentRecord(
                    status=ExperimentStatus.PENDING,
                    config=exp_config
                )
            else:
                self.state.experiments[exp_key].config = exp_config
        self._save_state()
    
    # =========================================================================
    # Experiment Access
    # =========================================================================
    
    def get_experiment(self, key: str) -> Optional[ExperimentRecord]:
        """Get an experiment record by key."""
        return self.state.experiments.get(key)
    
    def get_experiments_by_status(self, status: ExperimentStatus) -> List[str]:
        """Get experiment keys with a specific status."""
        return [k for k, v in self.state.experiments.items() if v.status == status]
    
    def get_pending_experiments(self) -> List[str]:
        """Get list of pending experiment keys."""
        return self.get_experiments_by_status(ExperimentStatus.PENDING)
    
    def get_failed_experiments(self) -> List[str]:
        """Get list of failed experiment keys."""
        return self.get_experiments_by_status(ExperimentStatus.FAILED)
    
    def get_completed_experiments(self) -> List[str]:
        """Get list of completed experiment keys."""
        return self.get_experiments_by_status(ExperimentStatus.DONE)
    
    def get_next_pending(self) -> Optional[str]:
        """Get the first pending experiment key."""
        pending = self.get_pending_experiments()
        return pending[0] if pending else None
    
    # =========================================================================
    # Status Management
    # =========================================================================

    def _resolve_source_config_paths(
        self,
        project_root: Optional[Union[str, Path]] = None,
    ) -> tuple[Path, List[Path]]:
        """Resolve base/prism config paths stored in state.

        Stored paths may be absolute or relative to the project root.
        """
        root = Path(project_root) if project_root is not None else Path.cwd()

        base_config_path = Path(self.state.base_config_path)
        if not base_config_path.is_absolute():
            base_config_path = root / base_config_path

        prism_config_paths: List[Path] = []
        for p in (self.state.prism_config_paths or []):
            if not p:
                continue
            ppath = Path(p)
            if not ppath.is_absolute():
                ppath = root / ppath
            prism_config_paths.append(ppath)

        return base_config_path, prism_config_paths
    
    def reset_experiment(self, key: str):
        """Reset an experiment to PENDING status."""
        if key in self.state.experiments:
            exp = self.state.experiments[key]
            exp.status = ExperimentStatus.PENDING
            exp.metrics = {}
            exp.started_at = None
            exp.completed_at = None
            exp.error_message = None
            exp.duration_seconds = None
            self._save_state()
            print_progress(f"Reset '{key}' to PENDING")
    
    def reset_all(self):
        """Reset all experiments to PENDING status."""
        for key in self.state.experiments.keys():
            self.reset_experiment(key)

    def restart_study(self):
        """Reset all experiments to PENDING, preserving metrics.

        This matches the TUI's "restart" semantics: clear timing/error info,
        but do not wipe metrics.
        """
        for exp in self.state.experiments.values():
            exp.status = ExperimentStatus.PENDING
            exp.started_at = None
            exp.completed_at = None
            exp.error_message = None
        self._save_state()
    
    def reset_failed(self):
        """Reset only failed experiments to PENDING."""
        for key in self.get_failed_experiments():
            self.reset_experiment(key)
    
    def mark_done(self, key: str, metrics: Optional[Dict[str, Any]] = None):
        """Mark an experiment as done."""
        if key in self.state.experiments:
            exp = self.state.experiments[key]
            exp.status = ExperimentStatus.DONE
            exp.completed_at = datetime.now().isoformat()
            if metrics:
                exp.metrics = metrics
            self._save_state()
    
    def mark_failed(self, key: str, error_message: Optional[str] = None):
        """Mark an experiment as failed."""
        if key in self.state.experiments:
            exp = self.state.experiments[key]
            exp.status = ExperimentStatus.FAILED
            exp.completed_at = datetime.now().isoformat()
            if error_message:
                exp.error_message = error_message
            self._save_state()
    
    def mark_running(self, key: str):
        """Mark an experiment as running."""
        if key in self.state.experiments:
            exp = self.state.experiments[key]
            exp.status = ExperimentStatus.RUNNING
            exp.started_at = datetime.now().isoformat()
            self._save_state()

    def rebuild(self, project_root: Optional[Union[str, Path]] = None, linking_mode: str = "zip") -> "PrismManager":
        """Delete and recreate the study from the original configs.

        This re-expands the sweep using the base/prism config paths stored in state,
        and writes the new canonical state file (.study.json).
        """
        base_config_path, prism_config_paths = self._resolve_source_config_paths(project_root=project_root)

        # Validate configs still exist
        if not base_config_path.exists():
            raise FileNotFoundError(f"Original base config not found: {base_config_path}")
        for p in prism_config_paths:
            if not p.exists():
                raise FileNotFoundError(f"Original prism config not found: {p}")

        # Delete existing study state
        delete_study(
            study_name=self.study_name,
            output_dir=self.output_dir,
            delete_artifacts_dir=False,
        )

        # Recreate manager + expand all keys
        new_manager = PrismManager(
            base_config_path=base_config_path,
            prism_config_path=prism_config_paths or None,
            study_name=self.study_name,
            output_dir=self.output_dir,
        )
        available_keys = new_manager.get_available_keys()
        new_manager.expand_configs(prism_keys=available_keys, linking_mode=linking_mode)
        return new_manager
    
    # =========================================================================
    # Execution
    # =========================================================================
    
    def execute_key(
        self,
        key: str,
        executor: "Executor",
        restart: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a specific experiment.
        
        Args:
            key: The experiment key
            executor: Executor instance to run the training
            restart: If True, reset to PENDING before running
        
        Returns:
            Metrics dictionary if successful, None otherwise
        """
        if key not in self.state.experiments:
            print_error(f"Experiment '{key}' not found")
            return None
        
        if restart:
            self.reset_experiment(key)
        
        experiment = self.state.experiments[key]
        
        if experiment.status != ExperimentStatus.PENDING:
            print_warning(f"Experiment '{key}' is not PENDING (status: {experiment.status.value})")
            return None
        
        # Mark as running
        self.mark_running(key)
        
        print_progress(f"Starting experiment: {key}")
        
        # Execute
        exp_output_dir = self.output_dir / self.study_name / key
        result = executor.run(
            config=experiment.config,
            experiment_name=f"{self.study_name}_{key}",
            output_dir=exp_output_dir,
        )
        
        # Update state based on result
        experiment.duration_seconds = result.duration_seconds
        
        if result.success:
            experiment.status = ExperimentStatus.DONE
            experiment.metrics = result.metrics
            print_success(f"Experiment '{key}' completed")
        else:
            experiment.status = ExperimentStatus.FAILED
            experiment.error_message = result.error_message
            print_error(f"Experiment '{key}' failed: {result.error_message}")
        
        experiment.completed_at = datetime.now().isoformat()
        self._save_state()
        
        return result.metrics if result.success else None
    
    def execute_next(
        self,
        executor: "Executor",
    ) -> Optional[Dict[str, Any]]:
        """Execute the first pending experiment."""
        next_key = self.get_next_pending()
        if next_key is None:
            print_info("No pending experiments")
            return None
        return self.execute_key(next_key, executor)
    
    def execute_all(
        self,
        executor: "Executor",
        stop_on_failure: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute all pending experiments.
        
        Args:
            executor: Executor instance
            stop_on_failure: If True, stop on first failure
        
        Returns:
            Dict of {key: metrics} for successful experiments
        """
        results = {}
        pending = self.get_pending_experiments()
        
        print_progress(f"Executing {len(pending)} pending experiments")
        
        for i, key in enumerate(pending):
            print_info(f"\n=== [{i+1}/{len(pending)}] {key} ===")
            
            metrics = self.execute_key(key, executor)
            
            if metrics is not None:
                results[key] = metrics
            elif stop_on_failure:
                print_warning("Stopping due to failure")
                break
        
        self.print_summary()
        return results
    
    # =========================================================================
    # Reporting
    # =========================================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the study state."""
        status_counts = {s.value: 0 for s in ExperimentStatus}
        for exp in self.state.experiments.values():
            status_counts[exp.status.value] += 1
        
        return {
            "study_name": self.study_name,
            "state_file": str(self.state_file_path),
            "total_experiments": len(self.state.experiments),
            "status_counts": status_counts,
            "experiments": {k: v.status.value for k, v in self.state.experiments.items()}
        }
    
    def print_summary(self):
        """Print a formatted summary of the study."""
        summary = self.get_summary()
        
        print_info(f"\n{'='*60}")
        print_info(f"Study: {summary['study_name']}")
        print_info(f"{'='*60}")
        print_file(summary['state_file'], "State file")
        print_info(f"Total: {summary['total_experiments']} experiments")
        
        for status, count in summary['status_counts'].items():
            if count > 0:
                print_info(f"  {status}: {count}")
        
        print_info(f"{'='*60}\n")
    
    def export_config(self, key: str, output_path: Union[str, Path]):
        """Export a specific experiment config to a YAML file."""
        if key not in self.state.experiments:
            raise ValueError(f"Experiment '{key}' not found")
        
        config = self.state.experiments[key].config
        output_path = Path(output_path)
        self._save_yaml(output_path, config)
        print_file(str(output_path), f"Exported '{key}'")
    
    def get_config_diff(self, key1: str, key2: str) -> Dict[str, tuple]:
        """
        Get the differences between two experiment configs.
        
        Returns:
            Dict of {param_path: (value1, value2)} for differing values
        """
        if key1 not in self.state.experiments:
            raise ValueError(f"Experiment '{key1}' not found")
        if key2 not in self.state.experiments:
            raise ValueError(f"Experiment '{key2}' not found")
        
        config1 = self.state.experiments[key1].config
        config2 = self.state.experiments[key2].config
        
        diffs = {}
        
        def compare_recursive(c1: Any, c2: Any, path: str = ""):
            if isinstance(c1, dict) and isinstance(c2, dict):
                all_keys = set(c1.keys()) | set(c2.keys())
                for key in all_keys:
                    new_path = f"{path}.{key}" if path else key
                    v1 = c1.get(key)
                    v2 = c2.get(key)
                    compare_recursive(v1, v2, new_path)
            elif c1 != c2:
                diffs[path] = (c1, c2)
        
        compare_recursive(config1, config2)
        return diffs


# =========================================================================
# Convenience Functions
# =========================================================================

def _canonical_study_state_path(output_dir: Union[str, Path], study_name: str) -> Path:
    return Path(output_dir) / f"{study_name}{STUDY_STATE_EXTENSION}"


def find_study_state_file(study_name: str, output_dir: Union[str, Path]) -> Optional[Path]:
    """Find a study state file by study name (canonical: .study.json only)."""
    output_dir = Path(output_dir)
    if not output_dir.exists():
        return None

    # Direct match
    canonical = _canonical_study_state_path(output_dir, study_name)
    if canonical.exists():
        return canonical

    # Search in subdirectories
    for p in output_dir.glob(f"**/{study_name}{STUDY_STATE_EXTENSION}"):
        return p

    # Partial match (last resort)
    for p in output_dir.glob(f"**/*{study_name}*{STUDY_STATE_EXTENSION}"):
        return p

    return None


def study_exists(study_name: str, output_dir: Union[str, Path]) -> bool:
    return find_study_state_file(study_name=study_name, output_dir=output_dir) is not None


def delete_study(
    study_name: str,
    output_dir: Union[str, Path],
    delete_artifacts_dir: bool = False,
) -> List[Path]:
    """Delete a study state file (and optionally its artifacts directory).

    Returns a list of deleted paths.
    """
    output_dir = Path(output_dir)
    deleted: List[Path] = []

    canonical = _canonical_study_state_path(output_dir, study_name)
    for p in [canonical]:
        try:
            if p.exists() and p.is_file():
                p.unlink()
                deleted.append(p)
        except Exception:
            continue

    if delete_artifacts_dir:
        artifacts_dir = output_dir / study_name
        if artifacts_dir.exists() and artifacts_dir.is_dir():
            import shutil
            shutil.rmtree(artifacts_dir)
            deleted.append(artifacts_dir)

    return deleted

def load_study(state_file: Union[str, Path]) -> PrismManager:
    """
    Load an existing study from a study state file (canonical: .study.json).
    
    Args:
        state_file: Path to the state file
    
    Returns:
        PrismManager instance
    """
    state_file = Path(state_file)
    if not state_file.exists():
        raise FileNotFoundError(f"State file not found: {state_file}")
    
    with open(state_file, 'r') as f:
        data = json.load(f)
    
    state = PrismState.from_dict(data)
    
    canonical_path = _canonical_study_state_path(state_file.parent, state.study_name)

    manager = PrismManager(
        base_config_path=state.base_config_path,
        prism_config_path=state.prism_config_paths or None,
        study_name=state.study_name,
        output_dir=state_file.parent,
        state_file_path=canonical_path,
        load_state=False,
    )
    manager.state = state

    # Reset any RUNNING experiments to PENDING (interrupted runs)
    running_count = 0
    for exp in manager.state.experiments.values():
        if exp.status == ExperimentStatus.RUNNING:
            exp.status = ExperimentStatus.PENDING
            exp.started_at = None
            running_count += 1
    if running_count > 0:
        manager._save_state(manager.state)

    return manager


def load_study_by_name(study_name: str, output_dir: Union[str, Path]) -> PrismManager:
    """Load a study by name from an output directory."""
    state_file = find_study_state_file(study_name=study_name, output_dir=output_dir)
    if state_file is None:
        raise FileNotFoundError(f"Study '{study_name}' not found in {output_dir}")
    return load_study(state_file)


def list_studies(output_dir: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    List all studies in an output directory.
    
    Args:
        output_dir: Directory to search for .study.json files
    
    Returns:
        List of study info dictionaries
    """
    output_dir = Path(output_dir)
    studies = []
    
    if not output_dir.exists():
        return studies
    
    files: List[Path] = list(output_dir.glob(f"**/*{STUDY_STATE_EXTENSION}"))

    # De-duplicate
    seen: set[str] = set()
    unique_files: List[Path] = []
    for f in files:
        fp = str(f.resolve())
        if fp not in seen:
            seen.add(fp)
            unique_files.append(f)

    for prism_file in unique_files:
        try:
            with open(prism_file) as f:
                data = json.load(f)
            
            experiments = data.get("experiments", {})
            status_counts = {"PENDING": 0, "RUNNING": 0, "DONE": 0, "FAILED": 0}
            for exp in experiments.values():
                status = exp.get("status", "PENDING")
                status_counts[status] = status_counts.get(status, 0) + 1

            studies.append({
                "name": data.get("study_name", prism_file.name.split(".study")[0]),
                "path": str(prism_file),
                "total": len(experiments),
                "pending": status_counts["PENDING"],
                "running": status_counts["RUNNING"],
                "done": status_counts["DONE"],
                "failed": status_counts["FAILED"],
                "base_config": data.get("base_config_path", ""),
                "prism_configs": data.get("prism_config_paths", []),
                "updated_at": data.get("updated_at", ""),
            })
        except Exception:
            continue

    studies.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return studies
