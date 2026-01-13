"""
HTML Extract - Configuration-driven HTML data extraction tool.

This package provides functionality to extract structured data from HTML files
using declarative configuration files (YAML or JSON) or dict objects.
"""

__version__ = "0.7.0"

# Core extraction function
from .extract import extract_data_from_html

# Configuration management
from .config import load_config, create_config_template

# Batch processing
from .batch import batch_extract, process_directory, process_csv, create_csv_template, ProgressInfo

# Output formatting
from .output import save_output

# Logging utilities (optional, for programmatic use)
from .logging import setup_logging, get_logger

__all__ = [
    "extract_data_from_html",
    "load_config",
    "create_config_template",
    "batch_extract",
    "process_directory",
    "process_csv",
    "create_csv_template",
    "save_output",
    "ProgressInfo",
    "setup_logging",
    "get_logger",
]
