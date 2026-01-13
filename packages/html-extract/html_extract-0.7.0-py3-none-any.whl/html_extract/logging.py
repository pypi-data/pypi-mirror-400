"""
Logging module for HTML Extract.

Provides structured logging functionality to track file processing, outcomes,
and errors throughout the extraction process.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# Module-level logger instance
_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """
    Get the module logger instance.
    
    Returns:
        Configured logger instance
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger('html_extract')
        # Set default level to INFO if not already configured
        if not _logger.handlers:
            _logger.setLevel(logging.INFO)
    return _logger


def setup_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    verbose: bool = False
) -> None:
    """
    Configure logging for the html_extract module.
    
    Args:
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Optional path to log file. If None, logs to stderr.
        verbose: If True, use DEBUG level regardless of log_level setting
    """
    logger = get_logger()
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Determine effective log level
    if verbose:
        effective_level = logging.DEBUG
    else:
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        effective_level = level_map.get(log_level.upper(), logging.INFO)
    
    logger.setLevel(effective_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create handler(s)
    if log_file:
        # File handler
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(effective_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Always add stderr handler (for console output)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(effective_level)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)


def log_file_start(file_path: str, category: Optional[str] = None) -> None:
    """
    Log that file processing has started.
    
    Args:
        file_path: Path to the HTML file being processed
        category: Optional category name
    """
    logger = get_logger()
    if category:
        logger.info(f"Processing: {file_path} (category: {category})")
    else:
        logger.info(f"Processing: {file_path}")


def log_file_success(
    file_path: str,
    item_count: int,
    skipped_count: int = 0
) -> None:
    """
    Log successful file processing.
    
    Args:
        file_path: Path to the HTML file that was processed
        item_count: Number of items successfully extracted
        skipped_count: Number of items skipped due to missing required attributes
    """
    logger = get_logger()
    if skipped_count > 0:
        logger.info(
            f"Success: {file_path} - Extracted {item_count} items "
            f"({skipped_count} skipped due to missing required attributes)"
        )
    else:
        logger.info(f"Success: {file_path} - Extracted {item_count} items")


def log_file_empty(file_path: str) -> None:
    """
    Log that a file produced no items.
    
    Args:
        file_path: Path to the HTML file that produced no items
    """
    logger = get_logger()
    logger.warning(f"Empty result: {file_path} - No items found")


def log_file_error(file_path: str, error: Exception) -> None:
    """
    Log that file processing failed with an error.
    
    Args:
        file_path: Path to the HTML file that failed
        error: Exception that occurred
    """
    logger = get_logger()
    logger.error(f"Failed: {file_path} - {type(error).__name__}: {error}")


def log_missing_required_attribute(
    file_path: str,
    attribute_name: str
) -> None:
    """
    Log that an item was skipped due to missing required attribute.
    
    Args:
        file_path: Path to the HTML file being processed
        attribute_name: Name of the missing required attribute
    """
    logger = get_logger()
    logger.warning(
        f"Skipped item in {file_path} - Missing required attribute: '{attribute_name}'"
    )


def log_batch_summary(
    total_files: int,
    successful_files: int,
    failed_files: int,
    total_items: int,
    total_skipped_items: int = 0
) -> None:
    """
    Log summary of batch processing operation.
    
    Args:
        total_files: Total number of files processed
        successful_files: Number of files processed successfully
        failed_files: Number of files that failed
        total_items: Total number of items extracted across all files
        total_skipped_items: Total number of items skipped due to missing required attributes
    """
    logger = get_logger()
    if total_skipped_items > 0:
        logger.info(
            f"Summary: Processed {total_files} files, {successful_files} successful, "
            f"{failed_files} failed, {total_items} total items, {total_skipped_items} items skipped"
        )
    else:
        logger.info(
            f"Summary: Processed {total_files} files, {successful_files} successful, "
            f"{failed_files} failed, {total_items} total items"
        )
