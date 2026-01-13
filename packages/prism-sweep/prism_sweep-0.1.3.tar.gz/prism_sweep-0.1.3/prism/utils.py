"""
Prism Utils - Internal utilities for the Prism package.

This module provides print utilities and helper functions used across Prism,
making the package self-contained without external dependencies.
"""

import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Standard colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


def _supports_color() -> bool:
    """Check if the terminal supports color output."""
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


def _colorize(text: str, color: str) -> str:
    """Apply color to text if terminal supports it."""
    if _supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


class PrintContext:
    """
    Context-aware printer for Prism modules.
    
    Provides formatted output with consistent styling and context tags.
    
    Usage:
        printer = PrintContext("PRISM")
        printer.info("Loading configuration...")
        printer.success("Configuration loaded!")
        printer.warning("Deprecated option used")
        printer.error("Failed to load file")
    """
    
    def __init__(self, context: str = "PRISM"):
        self.context = context
        self._show_timestamp = False
    
    def _format_prefix(self, symbol: str, color: str) -> str:
        """Format the prefix with context and symbol."""
        prefix = f"[{self.context}]"
        if self._show_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            prefix = f"[{timestamp}] {prefix}"
        return _colorize(f"{prefix} {symbol}", color)
    
    def info(self, message: str, end: str = "\n"):
        """Print an info message."""
        prefix = self._format_prefix("ℹ", Colors.BLUE)
        print(f"{prefix} {message}", end=end)
    
    def success(self, message: str, end: str = "\n"):
        """Print a success message."""
        prefix = self._format_prefix("✓", Colors.GREEN)
        print(f"{prefix} {message}", end=end)
    
    def warning(self, message: str, end: str = "\n"):
        """Print a warning message."""
        prefix = self._format_prefix("⚠", Colors.YELLOW)
        print(f"{prefix} {message}", end=end)
    
    def error(self, message: str, end: str = "\n"):
        """Print an error message."""
        prefix = self._format_prefix("✗", Colors.RED)
        print(f"{prefix} {message}", end=end, file=sys.stderr)
    
    def progress(self, message: str, end: str = "\n"):
        """Print a progress message."""
        prefix = self._format_prefix("→", Colors.CYAN)
        print(f"{prefix} {message}", end=end)
    
    def debug(self, message: str, end: str = "\n"):
        """Print a debug message (dimmed)."""
        prefix = self._format_prefix("•", Colors.DIM)
        print(f"{prefix} {_colorize(message, Colors.DIM)}", end=end)
    
    def file(self, filepath: str, label: Optional[str] = None):
        """Print a file path with optional label."""
        prefix = self._format_prefix("📄", Colors.MAGENTA)
        if label:
            print(f"{prefix} {label}: {_colorize(filepath, Colors.BRIGHT_CYAN)}")
        else:
            print(f"{prefix} {_colorize(filepath, Colors.BRIGHT_CYAN)}")
    
    def header(self, title: str, char: str = "=", width: int = 60):
        """Print a section header."""
        line = char * width
        print(_colorize(line, Colors.BRIGHT_BLUE))
        print(_colorize(f" {title}", Colors.BOLD + Colors.BRIGHT_BLUE))
        print(_colorize(line, Colors.BRIGHT_BLUE))
    
    def subheader(self, title: str, char: str = "-", width: int = 40):
        """Print a subsection header."""
        line = char * width
        print(_colorize(f"\n{line}", Colors.BLUE))
        print(_colorize(f" {title}", Colors.BLUE))
        print(_colorize(line, Colors.BLUE))


# Default printer instance for the package
_default_printer = PrintContext("PRISM")

# Convenience functions using the default printer
def print_info(message: str, end: str = "\n"):
    """Print an info message."""
    _default_printer.info(message, end)

def print_success(message: str, end: str = "\n"):
    """Print a success message."""
    _default_printer.success(message, end)

def print_warning(message: str, end: str = "\n"):
    """Print a warning message."""
    _default_printer.warning(message, end)

def print_error(message: str, end: str = "\n"):
    """Print an error message."""
    _default_printer.error(message, end)

def print_progress(message: str, end: str = "\n"):
    """Print a progress message."""
    _default_printer.progress(message, end)

def print_debug(message: str, end: str = "\n"):
    """Print a debug message."""
    _default_printer.debug(message, end)

def print_file(filepath: str, label: Optional[str] = None):
    """Print a file path."""
    _default_printer.file(filepath, label)

def print_header(title: str, char: str = "=", width: int = 60):
    """Print a section header."""
    _default_printer.header(title, char, width)

def print_subheader(title: str, char: str = "-", width: int = 40):
    """Print a subsection header."""
    _default_printer.subheader(title, char, width)


# Utility functions

def deep_get(d: dict, path: str, default=None):
    """
    Get a nested value from a dictionary using dot notation.
    
    Args:
        d: Dictionary to search
        path: Dot-separated path (e.g., "model.backbone.type")
        default: Default value if path not found
    
    Returns:
        Value at path or default
    """
    keys = path.split(".")
    current = d
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def deep_set(d: dict, path: str, value) -> dict:
    """
    Set a nested value in a dictionary using dot notation.
    
    Args:
        d: Dictionary to modify (will be copied)
        path: Dot-separated path (e.g., "model.backbone.type")
        value: Value to set
    
    Returns:
        Modified dictionary (copy)
    """
    import copy
    result = copy.deepcopy(d)
    keys = path.split(".")
    current = result
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    return result


def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep merge two dictionaries. Override values take precedence.
    
    Args:
        base: Base dictionary
        override: Override dictionary
    
    Returns:
        Merged dictionary (new object)
    """
    import copy
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result
