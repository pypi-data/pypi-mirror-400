"""
Prism Executor - Training Script Execution and Metrics Capture

This module handles the execution of training scripts and captures
metrics from their output. It supports multiple output modes:

- stdout_json: Training script prints JSON metrics to stdout
- file: Training script writes metrics to a file
- exit_code: Only check exit code (0 = success, non-zero = failure)

Usage:
    from prism.executor import Executor
    from prism.project import Project
    
    project = Project.load(".")
    executor = Executor(project)
    
    result = executor.run(config_dict, experiment_name="exp_001")
    print(result.success)
    print(result.metrics)
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import yaml

from .utils import (
    print_info, print_warning, print_error, print_success, print_progress,
    PrintContext
)
from .project import Project, ProjectConfig, MetricsConfig


@dataclass
class ExecutionResult:
    """Result of a training execution."""
    success: bool
    exit_code: int
    metrics: Dict[str, Any] = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    config_path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "metrics": self.metrics,
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "config_path": str(self.config_path) if self.config_path else None,
        }


class MetricsParser:
    """
    Parser for extracting metrics from training output.
    
    Supports multiple formats:
    - JSON object on a single line
    - JSON with METRICS: prefix
    - Key-value pairs (metric_name: value)
    """
    
    # Patterns for finding metrics in output
    JSON_LINE_PATTERN = re.compile(r'^\s*\{.*\}\s*$')
    METRICS_PREFIX_PATTERN = re.compile(r'^METRICS:\s*(\{.*\})\s*$', re.IGNORECASE)
    KEY_VALUE_PATTERN = re.compile(r'^(\w+):\s*([+-]?\d*\.?\d+(?:[eE][+-]?\d+)?)\s*$')
    
    def __init__(self, metrics_config: MetricsConfig):
        self.config = metrics_config
    
    def parse_stdout(self, stdout: str) -> Dict[str, Any]:
        """
        Parse metrics from stdout.
        
        Looks for:
        1. Lines starting with "METRICS:" followed by JSON
        2. Standalone JSON objects
        3. Key-value pairs in format "metric_name: value"
        
        Returns the last found metrics (to handle streaming output).
        """
        metrics = {}
        
        for line in stdout.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Try METRICS: prefix
            match = self.METRICS_PREFIX_PATTERN.match(line)
            if match:
                try:
                    parsed = json.loads(match.group(1))
                    if isinstance(parsed, dict):
                        metrics.update(parsed)
                    continue
                except json.JSONDecodeError:
                    pass
            
            # Try standalone JSON
            if self.JSON_LINE_PATTERN.match(line):
                try:
                    parsed = json.loads(line)
                    if isinstance(parsed, dict):
                        # Check if it looks like metrics (has numeric values)
                        if any(isinstance(v, (int, float)) for v in parsed.values()):
                            metrics.update(parsed)
                    continue
                except json.JSONDecodeError:
                    pass
            
            # Try key-value pattern
            match = self.KEY_VALUE_PATTERN.match(line)
            if match:
                key, value = match.groups()
                try:
                    metrics[key] = float(value)
                except ValueError:
                    pass
        
        return metrics
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse metrics from a JSON file."""
        if not file_path.exists():
            return {}
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, IOError):
            return {}


class Executor:
    """
    Executes training scripts and captures metrics.
    
    Usage:
        executor = Executor(project)
        result = executor.run(config_dict)
    """
    
    def __init__(self, project: Project):
        self.project = project
        self.config = project.config
        self._printer = PrintContext("EXECUTOR")
    
    def run(
        self,
        config: Dict[str, Any],
        experiment_name: Optional[str] = None,
        output_dir: Optional[Path] = None,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
        capture_output: bool = True,
        live_output: bool = True,
    ) -> ExecutionResult:
        """
        Run training with the given configuration.
        
        Args:
            config: Configuration dictionary
            experiment_name: Name for this experiment (used in output paths)
            output_dir: Override output directory
            timeout: Maximum execution time in seconds
            env: Additional environment variables
            capture_output: Whether to capture stdout/stderr
            live_output: Whether to print output in real-time
        
        Returns:
            ExecutionResult with metrics and status
        """
        started_at = datetime.now().isoformat()
        start_time = time.time()
        
        # Resolve paths
        paths = self.config.get_resolved_paths()
        
        if paths.train_script is None:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                error_message="No train_script defined in project",
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
            )
        
        if not paths.train_script.exists():
            return ExecutionResult(
                success=False,
                exit_code=-1,
                error_message=f"Training script not found: {paths.train_script}",
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
            )
        
        # Determine output directory
        if output_dir is None:
            output_dir = paths.output_dir
            if experiment_name:
                output_dir = output_dir / experiment_name
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate config using custom validator if available
        try:
            validated_config = self.config.validate_config(config)
            # If validator returns a dataclass, convert to dict for YAML serialization
            if hasattr(validated_config, '__dataclass_fields__'):
                validated_config = self._dataclass_to_dict(validated_config)
            elif not isinstance(validated_config, dict):
                # Try to convert to dict if it has a to_dict method
                if hasattr(validated_config, 'to_dict'):
                    validated_config = validated_config.to_dict()
                elif hasattr(validated_config, '__dict__'):
                    validated_config = vars(validated_config)
                else:
                    self._printer.warning(f"Validator returned non-dict type: {type(validated_config)}, using original config")
                    validated_config = config
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                error_message=f"Config validation failed: {e}",
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
            )
        
        # Write validated config to file
        config_path = output_dir / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(validated_config, f, default_flow_style=False)
        
        # Build command
        cmd = self.project.get_train_command(config_path)

        # Ensure we use the same Python interpreter that launched Prism.
        # This guarantees training runs inside the active environment (CLI/TUI).
        if cmd:
            first = str(cmd[0]).strip().lower()
            if first in {"python", "python3"}:
                cmd[0] = sys.executable
        
        self._printer.progress(f"Running: {' '.join(cmd)}")
        
        # Prepare environment
        run_env = os.environ.copy()
        # Force unbuffered output to prevent hangs during data loading
        run_env["PYTHONUNBUFFERED"] = "1"
        # Preserve colors in subprocess output
        run_env["FORCE_COLOR"] = "1"
        run_env["TERM"] = run_env.get("TERM", "xterm-256color")
        if env:
            run_env.update(env)
        
        # Run training
        try:
            if live_output and capture_output:
                result = self._run_with_live_capture(
                    cmd, 
                    cwd=self.config.project_root,
                    env=run_env,
                    timeout=timeout,
                )
            else:
                result = subprocess.run(
                    cmd,
                    cwd=self.config.project_root,
                    capture_output=capture_output,
                    text=True,
                    env=run_env,
                    timeout=timeout,
                )
                result = {
                    "returncode": result.returncode,
                    "stdout": result.stdout if capture_output else "",
                    "stderr": result.stderr if capture_output else "",
                }
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                error_message=f"Training timed out after {timeout} seconds",
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
                duration_seconds=time.time() - start_time,
                config_path=config_path,
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                exit_code=-1,
                error_message=str(e),
                started_at=started_at,
                completed_at=datetime.now().isoformat(),
                duration_seconds=time.time() - start_time,
                config_path=config_path,
            )
        
        completed_at = datetime.now().isoformat()
        duration = time.time() - start_time
        
        # Parse metrics
        metrics = self._extract_metrics(
            result.get("stdout", ""),
            output_dir,
        )
        
        # Determine success
        exit_code = result.get("returncode", -1)
        success = exit_code == 0
        
        # Check success_key if defined
        if success and self.config.metrics.success_key:
            if self.config.metrics.success_key not in metrics:
                success = False
        
        error_message = None
        if not success:
            stderr = result.get("stderr", "")
            if stderr:
                # Get last few lines of stderr
                error_lines = stderr.strip().split('\n')[-5:]
                error_message = '\n'.join(error_lines)
        
        return ExecutionResult(
            success=success,
            exit_code=exit_code,
            metrics=metrics,
            stdout=result.get("stdout", ""),
            stderr=result.get("stderr", ""),
            duration_seconds=duration,
            started_at=started_at,
            completed_at=completed_at,
            error_message=error_message,
            config_path=config_path,
        )
    
    def _run_with_live_capture(
        self,
        cmd: List[str],
        cwd: Path,
        env: Dict[str, str],
        timeout: Optional[int],
    ) -> Dict[str, Any]:
        """Run command with live output while still capturing it."""
        import io
        import threading
        import queue
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
        )
        
        # Use threads to read stdout and stderr without blocking
        # This works on both Windows and Unix
        def read_stream(stream, capture, print_func):
            """Read from stream and capture/print in a thread."""
            try:
                for line in iter(stream.readline, ''):
                    if line:
                        print_func(line, end='')
                        capture.write(line)
            except Exception:
                pass
            finally:
                stream.close()
        
        stdout_thread = threading.Thread(
            target=read_stream,
            args=(process.stdout, stdout_capture, print),
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=read_stream,
            args=(process.stderr, stderr_capture, lambda x, **kw: print(x, file=sys.stderr, **kw)),
            daemon=True
        )
        
        stdout_thread.start()
        stderr_thread.start()
        
        try:
            # Wait for process with timeout
            process.wait(timeout=timeout)
            
            # Wait for threads to finish reading
            stdout_thread.join(timeout=1.0)
            stderr_thread.join(timeout=1.0)
            
        except subprocess.TimeoutExpired:
            process.kill()
            raise
        except KeyboardInterrupt:
            process.kill()
            raise
        
        return {
            "returncode": process.returncode,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
        }
    
    def _dataclass_to_dict(self, obj: Any) -> Dict[str, Any]:
        """Recursively convert a dataclass to a dictionary."""
        from dataclasses import fields, is_dataclass
        from enum import Enum
        from pathlib import Path
        
        if is_dataclass(obj) and not isinstance(obj, type):
            result = {}
            for f in fields(obj):
                value = getattr(obj, f.name)
                result[f.name] = self._dataclass_to_dict(value)
            return result
        elif isinstance(obj, dict):
            return {k: self._dataclass_to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._dataclass_to_dict(item) for item in obj]
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, Path):
            return str(obj)
        else:
            return obj
    
    def _extract_metrics(
        self,
        stdout: str,
        output_dir: Path,
    ) -> Dict[str, Any]:
        """Extract metrics based on configured output mode."""
        parser = MetricsParser(self.config.metrics)
        
        if self.config.metrics.output_mode == "stdout_json":
            return parser.parse_stdout(stdout)
        
        elif self.config.metrics.output_mode == "file":
            metrics_file = output_dir / self.config.metrics.output_file
            return parser.parse_file(metrics_file)
        
        elif self.config.metrics.output_mode == "exit_code":
            return {}
        
        return {}
    
    def run_config_file(
        self,
        config_path: Union[str, Path],
        experiment_name: Optional[str] = None,
        **kwargs
    ) -> ExecutionResult:
        """
        Run training with a configuration file.
        
        Args:
            config_path: Path to configuration YAML file
            experiment_name: Name for this experiment
            **kwargs: Additional arguments passed to run()
        
        Returns:
            ExecutionResult
        """
        config_path = Path(config_path)
        
        # Load and optionally validate config
        validator = self.project.get_validator()
        if validator:
            config = validator.load_and_validate(config_path)
        else:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        
        return self.run(config, experiment_name=experiment_name, **kwargs)


class DryRunExecutor(Executor):
    """
    Executor that simulates training without actually running it.
    
    Useful for testing configuration expansion and validation.
    """
    
    def run(
        self,
        config: Dict[str, Any],
        experiment_name: Optional[str] = None,
        **kwargs
    ) -> ExecutionResult:
        """Simulate a training run."""
        self._printer.info(f"[DRY RUN] Would execute training for: {experiment_name}")
        self._printer.info(f"  Config keys: {list(config.keys())}")
        
        # Simulate some metrics
        import random
        metrics = {
            "loss": random.uniform(0.1, 1.0),
            "accuracy": random.uniform(0.7, 0.99),
            "val_loss": random.uniform(0.1, 1.0),
            "val_accuracy": random.uniform(0.7, 0.99),
        }
        
        return ExecutionResult(
            success=True,
            exit_code=0,
            metrics=metrics,
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            duration_seconds=0.1,
        )
