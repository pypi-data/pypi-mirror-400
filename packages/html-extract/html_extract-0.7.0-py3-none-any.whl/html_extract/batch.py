"""
Batch processing module for HTML Extract.

Provides functionality to process multiple HTML files efficiently with
multiprocessing support for CPU-bound HTML parsing, directory processing, and CSV bulk processing.
"""

import json
import os
import sys
import threading
import time
import traceback
import warnings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed, CancelledError
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Any, Optional, Union, Tuple

import pandas as pd
from tqdm import tqdm

from .extract import extract_data_from_html
from .config import load_config, _get_category_list
from .output import _create_stream_writer, _detect_format
from .logging import (
    get_logger,
    log_file_error,
    log_batch_summary
)

# Try to import BrokenProcessPool - it may not be available in all Python versions
# or may be in a different location. If not available, we'll use runtime type checking.
try:
    from concurrent.futures.process import BrokenProcessPool
except ImportError:
    # BrokenProcessPool not available - we'll check exception type at runtime
    BrokenProcessPool = None


@dataclass
class ProgressInfo:
    """
    Progress information for batch processing operations.
    
    Attributes:
        current: Number of files processed so far
        total: Total number of files to process
        percentage: Completion percentage (0.0 to 100.0)
        rate: Processing rate in files per second
        elapsed_time: Time elapsed in seconds
        current_file: Path of the file currently being processed (or None)
        failed_count: Number of files that returned empty DataFrames (missing required columns)
    """
    current: int
    total: int
    percentage: float
    rate: float
    elapsed_time: float
    current_file: Optional[str]
    failed_count: int


def _calculate_progress(
    current: int,
    total: int,
    start_time: float,
    failed_count: int
) -> ProgressInfo:
    """
    Calculate progress metrics from current state.
    
    Args:
        current: Number of files processed
        total: Total number of files
        start_time: Start time from time.time()
        failed_count: Number of failed files (empty DataFrames)
    
    Returns:
        ProgressInfo with calculated metrics
    """
    elapsed_time = time.time() - start_time
    percentage = (current / total * 100.0) if total > 0 else 0.0
    rate = current / elapsed_time if elapsed_time > 0 else 0.0
    
    return ProgressInfo(
        current=current,
        total=total,
        percentage=percentage,
        rate=rate,
        elapsed_time=elapsed_time,
        current_file=None,
        failed_count=failed_count
    )


def _get_file_diagnostics(file_path: str) -> Dict[str, Any]:
    """
    Gather diagnostic information about a file for error reporting.
    
    Args:
        file_path: Path to the file to diagnose
    
    Returns:
        Dictionary with diagnostic information (size, exists, readable, etc.)
    """
    diagnostics = {
        'path': file_path,
        'exists': False,
        'size_bytes': None,
        'size_mb': None,
        'readable': False
    }
    
    try:
        path = Path(file_path)
        diagnostics['exists'] = path.exists()
        
        if diagnostics['exists']:
            stat = path.stat()
            diagnostics['size_bytes'] = stat.st_size
            diagnostics['size_mb'] = round(stat.st_size / (1024 * 1024), 2)
            diagnostics['readable'] = os.access(file_path, os.R_OK)
    except Exception:
        # If we can't get diagnostics, that's okay - we'll just report what we can
        pass
    
    return diagnostics


def _process_file_worker(
    file_path: str,
    category: str,
    config_dict: Dict[str, Any],
    scrape_date_str: Optional[str]
) -> Tuple[Optional[pd.DataFrame], int]:
    """
    Process a single file and return DataFrame and skipped count, or None and 0 if failed.
    
    This is a module-level function designed to work with multiprocessing.
    For multiprocessing, config_dict must be picklable (dict is fine).
    Module-level functions can be pickled, unlike nested functions.
    
    Args:
        file_path: Path to HTML file to process
        category: Category name to use for extraction
        config_dict: Configuration dictionary (must be picklable)
        scrape_date_str: Optional scrape date in YYYY-MM-DD format
    
    Returns:
        Tuple of (DataFrame or None, skipped_count):
        - DataFrame: Extracted data or None if processing failed
        - skipped_count: Number of items skipped due to missing required attributes (0 if failed)
    """
    try:
        df, skipped_count = extract_data_from_html(
            file_path,
            config_dict,
            scrape_date=scrape_date_str,
            category=category
        )
        return df, skipped_count
    except MemoryError as e:
        # Memory error - likely file too large or insufficient system memory
        diagnostics = _get_file_diagnostics(file_path)
        size_info = f" ({diagnostics['size_mb']} MB)" if diagnostics['size_mb'] is not None else ""
        error_msg = (
            f"MemoryError processing file '{file_path}'{size_info}: {e}. "
            f"Consider reducing max_workers or processing fewer files at once."
        )
        warnings.warn(error_msg, UserWarning)
        return None, 0
    except UnicodeDecodeError as e:
        # Encoding issue - file may have invalid encoding
        diagnostics = _get_file_diagnostics(file_path)
        error_msg = (
            f"UnicodeDecodeError processing file '{file_path}': {e}. "
            f"File may have invalid encoding. Try checking file encoding or re-saving the file."
        )
        warnings.warn(error_msg, UserWarning)
        return None, 0
    except OSError as e:
        # File system error - file may be inaccessible, corrupted, or locked
        diagnostics = _get_file_diagnostics(file_path)
        readable_info = f" (readable: {diagnostics['readable']})" if diagnostics['exists'] else " (file not found)"
        error_msg = (
            f"OSError processing file '{file_path}'{readable_info}: {e}. "
            f"Check file permissions and ensure file is not locked or corrupted."
        )
        warnings.warn(error_msg, UserWarning)
        return None, 0
    except Exception as e:
        # Generic exception - log error and return None
        # extract_data_from_html already logs errors, but we log here too for worker context
        log_file_error(file_path, e)
        return None, 0


def batch_extract(
    files_with_categories: Dict[str, str],
    config: Dict[str, Any],
    scrape_date: Optional[str] = None,
    max_workers: Optional[int] = None,
    use_multiprocessing: bool = True,
    progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
    completion_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    show_progress: bool = False,
    stream_to_file: Optional[Union[str, Path]] = None,
    stream_mode: str = 'overwrite',
    stream_format: Optional[str] = None
) -> pd.DataFrame:
    """
    Core batch processing function that processes multiple HTML files and combines results.
    
    This function processes multiple HTML files in parallel using multiprocessing (for CPU-bound
    HTML parsing) or multithreading (for I/O-bound operations). Results can be either collected
    in memory (returned as DataFrame) or streamed directly to file during processing.
    
    Args:
        files_with_categories: Dictionary mapping file paths (str) to category names (str).
                              Keys are paths to HTML files, values are category names that
                              must match one of the categories in the config.
                              Example: {'path/to/file.html': 'gpu', 'path/to/file2.html': 'laptopy'}
        config: Pre-loaded configuration dictionary (from load_config())
        scrape_date: Optional explicit scrape date in YYYY-MM-DD format. If provided, applies
                     to all files. If None, each file's date is extracted from its path.
        max_workers: Optional maximum number of worker processes/threads for parallel processing.
                     If None, automatically detects optimal worker count:
                     - For multiprocessing: CPU count (optimal for CPU-bound tasks)
                     - For threading: 2x CPU count (optimal for I/O-bound tasks, min 4, max 32)
        use_multiprocessing: If True, use ProcessPoolExecutor for CPU-bound HTML parsing.
                            If False, use ThreadPoolExecutor for I/O-bound operations.
                            Default: True (recommended for HTML parsing which is CPU-intensive).
        progress_callback: Optional callback function that receives ProgressInfo updates.
                          Called after each file is processed. Useful for programmatic progress tracking.
        completion_callback: Optional callback function that receives completion summary.
                            Called once at the end with comprehensive statistics including all processed files.
                            Receives dict with status, summary, processed_files, failed_files, etc.
        show_progress: If True, display tqdm progress bar. Default: False.
        stream_to_file: Optional output file path for streaming. If provided, results are written
                        directly to file during processing instead of collecting in memory.
                        If None, results are collected in memory and returned as DataFrame.
        stream_mode: Streaming mode: 'overwrite' (default) or 'append'. Only used if stream_to_file
                     is provided.
        stream_format: Output format for streaming: 'csv' or 'json'. If None, auto-detected from
                       file extension. Only used if stream_to_file is provided.
    
    Returns:
        If stream_to_file is provided: Empty DataFrame (data already written to file).
        If stream_to_file is None: Combined DataFrame with extracted data from all files.
        Returns empty DataFrame if no data extracted or no files provided.
    
    Raises:
        ValueError: If config is None, files_with_categories is empty, or if any category
                   name doesn't match a category in the config, or if stream_mode/stream_format
                   is invalid
        FileNotFoundError: If any file path in files_with_categories doesn't exist
        OSError: If file write fails during streaming
    
    Example:
        >>> def my_callback(progress: ProgressInfo):
        ...     print(f"Processed {progress.current}/{progress.total} files")
        >>> # Collect in memory
        >>> df = batch_extract(files, config, progress_callback=my_callback, show_progress=True)
        >>> # Stream to file
        >>> df = batch_extract(files, config, stream_to_file='output.csv')
    """
    # Validate inputs
    if config is None:
        raise ValueError("config is required")
    
    if not files_with_categories:
        return pd.DataFrame()
    
    # Validate all file paths exist
    for file_path in files_with_categories.keys():
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
    
    # Validate all category names exist in config
    categories = config.get('categories', [])
    category_list = _get_category_list(categories)
    config_categories = {cat.get('name') for cat in category_list}
    for file_path, category in files_with_categories.items():
        if category not in config_categories:
            raise ValueError(
                f"Category '{category}' not found in configuration for file '{file_path}'. "
                f"Available categories: {sorted(config_categories)}"
            )
    
    # Validate streaming parameters if provided
    if stream_to_file is not None:
        if stream_mode not in ['overwrite', 'append']:
            raise ValueError(f"Invalid stream_mode: {stream_mode}. Must be 'overwrite' or 'append'.")
        
        # Detect format if not provided
        if stream_format is None:
            stream_format = _detect_format(stream_to_file, None)
        
        if stream_format not in ['csv', 'json']:
            raise ValueError(f"Invalid stream_format: {stream_format}. Must be 'csv' or 'json'.")
    
    # Determine max_workers automatically
    if max_workers is None:
        cpu_count = os.cpu_count() or 4
        if use_multiprocessing:
            # For CPU-bound tasks (HTML parsing), use one process per CPU core
            max_workers = cpu_count
        else:
            # For I/O-bound tasks, use more threads than CPU cores
            # Use 2x CPU count for I/O-bound operations, with minimum of 4 and maximum of 32
            max_workers = min(max(cpu_count * 2, 4), 32)
    
    # Set up streaming if enabled
    stream_writer = None
    
    if stream_to_file is not None:
        # Create lock for thread/process safety
        # Note: Even with multiprocessing, writes happen in main process after futures complete,
        # so threading.Lock is sufficient for both multiprocessing and threading scenarios
        stream_lock = threading.Lock()
        
        # Create stream writer
        stream_writer = _create_stream_writer(
            stream_to_file,
            stream_format,
            mode=stream_mode,
            lock=stream_lock
        )
    
    # Process files in parallel
    all_dataframes = []
    failed_files = []
    successful_files = []  # Track successful files with metadata
    failed_count = 0  # Files with empty DataFrames (missing required columns)
    successful_count = 0  # Files processed successfully
    total_items = 0  # Total items extracted across all files
    
    # Initialize progress tracking
    total_files = len(files_with_categories)
    start_time = time.time()
    processed_count = 0
    
    # Create tqdm progress bar if requested
    pbar = None
    if show_progress:
        pbar = tqdm(
            total=total_files,
            desc="Processing files",
            unit="file",
            ncols=100
        )
    
    # Use ProcessPoolExecutor for CPU-bound tasks or ThreadPoolExecutor for I/O-bound tasks
    ExecutorClass = ProcessPoolExecutor if use_multiprocessing else ThreadPoolExecutor
    
    try:
        with ExecutorClass(max_workers=max_workers) as executor:
            # Submit all tasks
            # For multiprocessing, we need to pass config as a parameter (must be picklable)
            # Use module-level function _process_file_worker which can be pickled
            future_to_file = {
                executor.submit(_process_file_worker, file_path, category, config, scrape_date): file_path
                for file_path, category in files_with_categories.items()
            }
            
            # Track if process pool is broken to avoid cascading failures
            executor_broken = False
            broken_pool_file = None
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                # If executor is broken, cancel remaining futures and break
                if executor_broken:
                    future.cancel()
                    continue
                
                file_path = future_to_file[future]
                current_file_name = Path(file_path).name
                
                try:
                    df, skipped_count = future.result()  # Unpack tuple
                    if df is not None and len(df) > 0:
                        # File processed successfully
                        successful_count += 1
                        total_items += len(df)
                        
                        # Track successful file with metadata
                        successful_files.append({
                            "file_path": file_path,
                            "category": files_with_categories[file_path],
                            "item_count": len(df),
                            "missing_required": skipped_count,
                            "status": "success"
                        })
                        
                        if stream_writer is not None:
                            # Stream to file
                            try:
                                stream_writer.write_dataframe(df)
                            except Exception as e:
                                logger = get_logger()
                                logger.error(f"Failed to write DataFrame to stream for file '{file_path}': {e}")
                                # Continue processing other files
                        else:
                            # Collect in memory
                            all_dataframes.append(df)
                    else:
                        # Empty DataFrame - track with skipped_count if items were skipped
                        if skipped_count > 0:
                            # File had items but all were skipped - still track as successful with metadata
                            successful_count += 1
                            successful_files.append({
                                "file_path": file_path,
                                "category": files_with_categories[file_path],
                                "item_count": 0,
                                "missing_required": skipped_count,
                                "status": "success"
                            })
                        else:
                            # Empty DataFrame - likely missing required columns
                            failed_count += 1
                            failed_files.append({
                                "file_path": file_path,
                                "status": "failed"
                            })
                except Exception as e:
                    # Check for specific exception types
                    exception_type_name = type(e).__name__
                    exception_module = type(e).__module__
                    
                    # Check if this is a BrokenProcessPool exception
                    # (check by type name and module since direct import may fail)
                    is_broken_pool = (
                        exception_type_name == 'BrokenProcessPool' or
                        (BrokenProcessPool is not None and isinstance(e, BrokenProcessPool)) or
                        'process pool' in str(e).lower() or
                        'worker process' in str(e).lower() or
                        'terminated abruptly' in str(e).lower()
                    )
                    
                    # Check if this is a TimeoutError
                    is_timeout = (
                        isinstance(e, TimeoutError) or
                        exception_type_name == 'TimeoutError' or
                        'timeout' in str(e).lower()
                    )
                    
                    # Check if this is a CancelledError
                    is_cancelled = isinstance(e, CancelledError) or exception_type_name == 'CancelledError'
                    
                    diagnostics = _get_file_diagnostics(file_path)
                    size_info = f" ({diagnostics['size_mb']} MB)" if diagnostics['size_mb'] is not None else ""
                    tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                    
                    if is_broken_pool:
                        # Process pool corruption - mark executor as broken
                        # This prevents cascading failures from all remaining futures
                        if not executor_broken:
                            executor_broken = True
                            broken_pool_file = file_path
                            # Cancel all remaining futures to prevent cascading failures
                            remaining_futures = [f for f in future_to_file.keys() if not f.done()]
                            for remaining_future in remaining_futures:
                                remaining_future.cancel()
                        
                        # Only show detailed error for the first broken pool exception
                        if broken_pool_file == file_path:
                            error_msg = (
                                f"Process pool error processing file '{file_path}'{size_info}: "
                                f"A worker process terminated abruptly. This may indicate:\n"
                                f"  - Memory issues (try reducing max_workers)\n"
                                f"  - Corrupted or malformed HTML file\n"
                                f"  - Encoding problems\n"
                                f"  - System resource constraints\n"
                                f"Original error: {e}\n"
                                f"Process pool is now broken. Remaining files will be skipped.\n"
                                f"Traceback:\n{tb_str}"
                            )
                            warnings.warn(error_msg, UserWarning)
                        else:
                            # For subsequent broken pool errors, just mark as failed
                            warnings.warn(
                                f"Skipping file '{file_path}' due to broken process pool (initial failure: '{broken_pool_file}')",
                                UserWarning
                            )
                    elif is_timeout:
                        # Timeout error - process took too long
                        error_msg = (
                            f"Timeout processing file '{file_path}'{size_info}: "
                            f"Process exceeded time limit. File may be very large or complex. "
                            f"Consider processing this file separately or increasing timeout.\n"
                            f"Original error: {e}\n"
                            f"Traceback:\n{tb_str}"
                        )
                        warnings.warn(error_msg, UserWarning)
                    elif is_cancelled:
                        # Task was cancelled (may be due to broken pool)
                        if executor_broken:
                            # Don't warn about cancellations if pool is already broken
                            pass
                        else:
                            error_msg = (
                                f"Task cancelled for file '{file_path}': {e}. "
                                f"This may occur if the process pool was shut down unexpectedly.\n"
                                f"Traceback:\n{tb_str}"
                            )
                            warnings.warn(error_msg, UserWarning)
                    else:
                        # Generic exception - log error
                        log_file_error(file_path, e)
                    
                    failed_files.append({
                        "file_path": file_path,
                        "status": "failed"
                    })
                    failed_count += 1
                
                # Update progress
                processed_count += 1
                progress_info = _calculate_progress(
                    processed_count,
                    total_files,
                    start_time,
                    failed_count
                )
                progress_info.current_file = current_file_name
                
                # Update progress bar
                if pbar is not None:
                    pbar.set_description(f"Processing: {current_file_name}")
                    pbar.set_postfix({
                        'failed': failed_count,
                        'rate': f"{progress_info.rate:.1f} files/s"
                    })
                    pbar.update(1)
                
                # Call progress callback if provided
                if progress_callback is not None:
                    try:
                        progress_callback(progress_info)
                    except Exception as e:
                        warnings.warn(
                            f"Progress callback error: {e}",
                            UserWarning
                        )
            
            # If executor was broken, provide summary
            if executor_broken:
                remaining_count = total_files - processed_count
                if remaining_count > 0:
                    warnings.warn(
                        f"Process pool was broken after processing {processed_count}/{total_files} files. "
                        f"{remaining_count} files were skipped. "
                        f"Consider reducing max_workers or processing files in smaller batches.",
                        UserWarning
                    )
    finally:
        # Close progress bar
        if pbar is not None:
            pbar.close()
        
        # Close stream writer if used
        if stream_writer is not None:
            stream_writer.close()
    
    # Calculate total skipped items from successful files
    total_skipped_items = sum(f.get("missing_required", 0) for f in successful_files)
    
    # Log batch summary (before returning)
    log_batch_summary(
        total_files=total_files,
        successful_files=successful_count,
        failed_files=failed_count,
        total_items=total_items,
        total_skipped_items=total_skipped_items
    )
    
    # Call completion callback if provided
    if completion_callback is not None:
        from datetime import datetime
        completion_data = {
            "status": "completed" if failed_count == 0 else "completed_with_errors",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": total_files,
                "successful_files": successful_count,
                "failed_files": failed_count,
                "total_items": total_items,
                "total_skipped_items": total_skipped_items
            },
            "processed_files": successful_files,
            "failed_files": failed_files,
            "output_file": str(stream_to_file) if stream_to_file else None,
            "processing_time_seconds": time.time() - start_time
        }
        try:
            completion_callback(completion_data)
        except Exception as e:
            logger = get_logger()
            logger.warning(f"Completion callback error: {e}")
    
    # Handle return value based on streaming mode
    if stream_writer is not None:
        # Streaming mode: return empty DataFrame (data already written to file)
        return pd.DataFrame()
    else:
        # Collect in memory mode: combine all DataFrames
        if all_dataframes:
            combined_df = pd.concat(all_dataframes, ignore_index=True)
        else:
            # Return empty DataFrame with correct columns if no data extracted
            # Try to get columns from first file (if it exists but had no items)
            if files_with_categories:
                try:
                    # Get a sample DataFrame to determine columns
                    first_file = list(files_with_categories.keys())[0]
                    first_category = files_with_categories[first_file]
                    sample_df, _ = extract_data_from_html(
                        first_file,
                        config,
                        scrape_date=scrape_date,
                        category=first_category
                    )
                    combined_df = pd.DataFrame(columns=sample_df.columns)
                except Exception:
                    # Fallback: empty DataFrame
                    combined_df = pd.DataFrame()
            else:
                combined_df = pd.DataFrame()
        
        return combined_df


def _get_processed_files(
    output_path: Path,
    stream_format: Optional[str],
    show_progress: bool = False
) -> set:
    """
    Get set of already-processed file paths from output file.
    
    Reads the output file (CSV or JSON) and extracts source file information
    from source_path column to determine which files have already been processed.
    Requires source_path column (full file path) for accurate tracking, as source_file
    (filename only) is not sufficient since filenames can be duplicated across directories.
    
    Args:
        output_path: Path to output file (CSV or JSON)
        stream_format: Format of output file ('csv' or 'json'). If None, auto-detected.
        show_progress: If True, display progress when reading large files. Default: False.
    
    Returns:
        Set of file paths (as strings) that have already been processed.
        Returns empty set if output file doesn't exist or doesn't have source_path column.
        In this case, a warning is issued and all files will be processed.
    """
    processed_files = set()
    
    # Check if output file exists
    if not output_path.exists():
        return processed_files
    
    # Detect format if not provided
    if stream_format is None:
        stream_format = _detect_format(output_path, None)
    
    try:
        if stream_format == 'csv':
            # Read CSV file header to check for source tracking columns
            try:
                df_header = pd.read_csv(output_path, encoding='utf-8-sig', nrows=0)
            except UnicodeDecodeError:
                df_header = pd.read_csv(output_path, encoding='utf-8', nrows=0)
            
            # Check for source_path column (required for accurate file tracking)
            # source_file alone is not sufficient as filenames can be duplicated across directories
            has_source_path = 'source_path' in df_header.columns
            
            if has_source_path:
                # Use source_path column (full path is required for unique file identification)
                use_col = 'source_path'
                
                # Estimate total rows for progress bar (if file is not too large)
                total_rows = None
                if show_progress:
                    try:
                        # Quick row count estimation (read first chunk to estimate)
                        with open(output_path, 'rb') as f:
                            # Count newlines as rough estimate (fast)
                            first_chunk = f.read(1024 * 1024)  # Read first 1MB
                            if first_chunk:
                                # Estimate based on first chunk
                                sample_lines = first_chunk.count(b'\n')
                                if sample_lines > 0:
                                    file_size = output_path.stat().st_size
                                    total_rows = int((file_size / len(first_chunk)) * sample_lines)
                    except Exception:
                        # If estimation fails, continue without total
                        pass
                
                # Read only the needed column in chunks for large files
                # This is much faster than reading the entire file (only reads 1 column instead of all)
                chunk_size = 50000  # Larger chunk size for better performance
                try:
                    chunks = pd.read_csv(
                        output_path,
                        encoding='utf-8-sig',
                        usecols=[use_col],
                        chunksize=chunk_size
                    )
                except UnicodeDecodeError:
                    chunks = pd.read_csv(
                        output_path,
                        encoding='utf-8',
                        usecols=[use_col],
                        chunksize=chunk_size
                    )
                except Exception:
                    # If chunking fails, try reading entire column
                    try:
                        chunks = [pd.read_csv(
                            output_path,
                            encoding='utf-8-sig',
                            usecols=[use_col]
                        )]
                    except UnicodeDecodeError:
                        chunks = [pd.read_csv(
                            output_path,
                            encoding='utf-8',
                            usecols=[use_col]
                        )]
                
                # Process each chunk - extract unique values efficiently
                # Use a temporary set for chunk processing to avoid repeated lookups
                chunk_processed = set()
                pbar = None
                if show_progress:
                    pbar = tqdm(
                        desc="Reading processed files",
                        unit="chunk",
                        ncols=100,
                        total=None if total_rows is None else (total_rows // chunk_size + 1)
                    )
                
                try:
                    for df_chunk in chunks:
                        # Filter out NaN, None, and empty strings, then get unique values
                        col_data = df_chunk[use_col]
                        # Drop NaN and filter empty strings efficiently
                        valid_paths = col_data.dropna()
                        if len(valid_paths) > 0:
                            # Filter empty strings and convert to string type
                            valid_paths = valid_paths.astype(str)
                            valid_paths = valid_paths[valid_paths.str.strip() != '']
                            if len(valid_paths) > 0:
                                # Get unique values and add to temporary set
                                chunk_processed.update(valid_paths.unique())
                        
                        if pbar is not None:
                            pbar.update(1)
                            pbar.set_postfix({'unique_files': len(chunk_processed)})
                finally:
                    if pbar is not None:
                        pbar.close()
                
                # Update main set once after processing all chunks
                processed_files.update(chunk_processed)
            else:
                # source_path column not found - cannot reliably determine processed files
                # Warn and return empty set (will process all files)
                warnings.warn(
                    f"Output file '{output_path}' does not have 'source_path' column. "
                    f"Cannot determine already-processed files. Processing all files. "
                    f"To enable skipping already-processed files, ensure 'source_path' metadata "
                    f"is included in your extraction configuration.",
                    UserWarning
                )
                return set()
        
        elif stream_format == 'json':
            # Read JSON file
            with open(output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both list of objects and single object
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and 'items' in data:
                items = data['items']
            else:
                items = [data]
            
            # Extract processed files from source_path field (required)
            # source_file alone is not sufficient as filenames can be duplicated
            has_source_path = False
            for item in items:
                if isinstance(item, dict) and 'source_path' in item:
                    has_source_path = True
                    break
            
            if has_source_path:
                # Extract source_path values
                for item in items:
                    if isinstance(item, dict):
                        if 'source_path' in item and item['source_path']:
                            source_val = str(item['source_path']).strip()
                            if source_val:
                                processed_files.add(source_val)
            else:
                # source_path field not found - cannot reliably determine processed files
                warnings.warn(
                    f"Output file '{output_path}' does not have 'source_path' field. "
                    f"Cannot determine already-processed files. Processing all files. "
                    f"To enable skipping already-processed files, ensure 'source_path' metadata "
                    f"is included in your extraction configuration.",
                    UserWarning
                )
                return set()
    
    except Exception as e:
        # If we can't read the file or extract source info, assume no files processed
        # This allows processing to continue even if output file is malformed
        warnings.warn(
            f"Could not determine processed files from output '{output_path}': {e}. "
            f"Processing all files.",
            UserWarning
        )
        return set()
    
    return processed_files


def _normalize_processed_files(processed_files: set) -> set:
    """
    Pre-normalize all processed file paths for fast lookup.
    
    Converts all processed file paths to normalized POSIX format (lowercase)
    for efficient set-based lookups. This is much faster than normalizing
    paths during comparison.
    
    Args:
        processed_files: Set of file paths (strings) that have been processed
    
    Returns:
        Set of normalized file paths (lowercase POSIX format)
    """
    normalized = set()
    for processed_path in processed_files:
        if not isinstance(processed_path, str) or not processed_path:
            continue
        try:
            # Normalize to POSIX format and lowercase for consistent comparison
            normalized_path = Path(processed_path).as_posix().lower()
            if normalized_path:
                normalized.add(normalized_path)
        except Exception:
            # If path processing fails, try simple string normalization
            try:
                normalized_path = str(processed_path).lower().replace('\\', '/')
                if normalized_path:
                    normalized.add(normalized_path)
            except Exception:
                # Skip invalid paths
                continue
    return normalized


def _is_file_processed(html_file: Path, normalized_processed_files: set) -> bool:
    """
    Check if an HTML file has already been processed (optimized version).
    
    Uses pre-normalized processed files set for O(1) lookup instead of
    iterating through all processed files for each check.
    
    Args:
        html_file: Path to HTML file to check
        normalized_processed_files: Set of normalized file paths (from _normalize_processed_files)
    
    Returns:
        True if file has been processed, False if not.
    """
    if not normalized_processed_files:
        return False
    
    # Normalize the HTML file path for comparison
    try:
        html_file_abs = html_file.resolve()
    except (OSError, RuntimeError):
        # If resolve fails (e.g., file doesn't exist yet), use the original path
        html_file_abs = html_file
    
    # Normalize to POSIX format and lowercase for fast set lookup
    html_file_posix = html_file_abs.as_posix().lower()
    
    # Fast O(1) set lookup
    if html_file_posix in normalized_processed_files:
        return True
    
    # Also check the original path format (in case of path format differences)
    html_file_str = str(html_file_abs).lower().replace('\\', '/')
    if html_file_str in normalized_processed_files:
        return True
    
    # Check if any processed path ends with this file's path (handles relative paths)
    # Only do this if the set is not too large to avoid performance issues
    if len(normalized_processed_files) < 10000:
        for processed_path in normalized_processed_files:
            if processed_path.endswith(html_file_posix) or html_file_posix.endswith(processed_path):
                return True
    
    return False


def _derive_category_from_path(file_path: Path, config: Dict[str, Any]) -> str:
    """
    Derive category name from file path by matching against config categories.
    
    Strategy:
    1. Get all path parts
    2. Check each path segment against category names
    3. For nested categories (e.g., 'domy/najem'), match consecutive segments
    4. Return first matching category (case-sensitive)
    
    Args:
        file_path: Path to HTML file
        config: Configuration dictionary with categories
    
    Returns:
        Category name that matches the path
    
    Raises:
        ValueError: If no category found in path
    """
    # Get all category names from config
    categories = config.get('categories', [])
    category_list = _get_category_list(categories)
    category_names = [cat.get('name') for cat in category_list if cat.get('name')]
    
    if not category_names:
        raise ValueError("No categories found in configuration")
    
    # Get path parts (as strings), normalize to handle Windows paths
    # Convert to list of strings and filter out empty/root parts
    path_parts = [str(part) for part in file_path.parts if part and part not in ('/', '\\')]
    
    # Try to match categories (check longer/more specific first)
    # Sort by length descending to match nested categories first
    sorted_categories = sorted(category_names, key=len, reverse=True)
    
    for category_name in sorted_categories:
        # Split nested category (e.g., 'domy/najem' -> ['domy', 'najem'])
        category_parts = category_name.split('/')
        
        # Check if consecutive path parts match category parts
        for i in range(len(path_parts) - len(category_parts) + 1):
            # Compare path parts slice with category parts
            if path_parts[i:i+len(category_parts)] == category_parts:
                return category_name
    
    # No match found
    available_categories = ', '.join(sorted(category_names))
    raise ValueError(
        f"Could not derive category from path '{file_path}'. "
        f"Available categories: {available_categories}"
    )


def process_directory(
    directory_path: Union[str, Path],
    config: Dict[str, Any],
    scrape_date: Optional[str] = None,
    recursive: bool = True,
    progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
    completion_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    show_progress: bool = False,
    stream_to_file: Optional[Union[str, Path]] = None,
    stream_mode: str = 'overwrite',
    stream_format: Optional[str] = None
) -> pd.DataFrame:
    """
    Process all HTML files in a directory and return combined DataFrame or stream to file.
    
    This function finds all HTML files in the specified directory (recursively by default),
    automatically derives the category from each file's folder path, and processes all
    files using batch_extract().
    
    When stream_mode='append' and the output file exists, the function automatically checks
    for already-processed files by examining the source_path column in the existing output
    file, and skips those files to avoid duplicate processing. The source_path column
    (full file path) is required for accurate file tracking.
    
    Args:
        directory_path: Path to directory containing HTML files (str or Path)
        config: Pre-loaded configuration dictionary (from load_config())
        scrape_date: Optional explicit scrape date in YYYY-MM-DD format. If provided,
                     applies to all files in the directory. If None, each file's date
                     is extracted from its path.
        recursive: If True, process HTML files recursively in subdirectories (default: True)
        progress_callback: Optional callback function that receives ProgressInfo updates.
                          Called after each file is processed.
        completion_callback: Optional callback function that receives completion summary.
                            Called once at the end with comprehensive statistics including all processed files.
        show_progress: If True, display tqdm progress bar. Default: False.
        stream_to_file: Optional output file path for streaming. If provided, results are written
                        directly to file during processing. If None, results are collected in memory.
        stream_mode: Streaming mode: 'overwrite' (default) or 'append'. Only used if stream_to_file
                     is provided. When 'append' and output file exists, automatically skips
                     already-processed files by checking source_file/source_path columns.
        stream_format: Output format for streaming: 'csv' or 'json'. If None, auto-detected from
                       file extension. Only used if stream_to_file is provided.
    
    Returns:
        If stream_to_file is provided: Empty DataFrame (data already written to file).
        If stream_to_file is None: Combined DataFrame with extracted data from all HTML files.
        Returns empty DataFrame if no data extracted or no HTML files found.
    
    Raises:
        FileNotFoundError: If the directory path does not exist
        ValueError: If no HTML files found in the directory, or if stream_mode is invalid
    """
    # Convert to Path object
    dir_path = Path(directory_path)
    
    # Validate directory exists
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory_path}")
    
    # Find all HTML files
    if recursive:
        html_files = list(dir_path.rglob("*.html"))
    else:
        html_files = list(dir_path.glob("*.html"))
    
    if not html_files:
        raise ValueError(f"No HTML files found in directory: {directory_path}")
    
    # Validate stream_mode
    if stream_to_file is not None and stream_mode not in ['overwrite', 'append']:
        raise ValueError(f"Invalid stream_mode: {stream_mode}. Must be 'overwrite' or 'append'.")
    
    # When stream_mode='append' and output file exists, check for already-processed files
    # to avoid duplicate processing
    if stream_mode == 'append' and stream_to_file is not None:
        output_path = Path(stream_to_file)
        if output_path.exists():
            if show_progress:
                print(f"Checking for already-processed files in '{output_path.name}'...")
            try:
                processed_files = _get_processed_files(output_path, stream_format, show_progress=show_progress)
                
                if show_progress:
                    print(f"Found {len(processed_files)} unique processed files. Normalizing paths for fast lookup...")
                
                # Pre-normalize all processed file paths for O(1) lookup
                # This is much faster than normalizing during each comparison
                normalized_processed = _normalize_processed_files(processed_files)
                
                if show_progress:
                    print(f"Checking {len(html_files)} HTML files against {len(normalized_processed)} processed files...")
                
                # Filter HTML files to only include those not yet processed
                original_count = len(html_files)
                
                # Use progress bar for file checking if there are many files
                if show_progress and original_count > 100:
                    filtered_files = []
                    check_pbar = tqdm(
                        html_files,
                        desc="Filtering files",
                        unit="file",
                        ncols=100
                    )
                    for f in check_pbar:
                        if not _is_file_processed(f, normalized_processed):
                            filtered_files.append(f)
                        check_pbar.set_postfix({'remaining': len(filtered_files)})
                    check_pbar.close()
                    html_files = filtered_files
                else:
                    # Fast list comprehension with pre-normalized set
                    html_files = [
                        f for f in html_files
                        if not _is_file_processed(f, normalized_processed)
                    ]
                
                filtered_count = len(html_files)
                
                # Safety check: if we filtered out all files, warn and process all
                if not html_files and original_count > 0:
                    warnings.warn(
                        f"All {original_count} files appear to be already processed. "
                        f"This might indicate a path matching issue. Processing all files to be safe.",
                        UserWarning
                    )
                    # Re-read HTML files since we filtered them all out
                    if recursive:
                        html_files = list(dir_path.rglob("*.html"))
                    else:
                        html_files = list(dir_path.glob("*.html"))
                elif filtered_count < original_count:
                    # Some files were filtered - this is expected
                    if show_progress:
                        print(f"Skipping {original_count - filtered_count} already-processed files. Processing {filtered_count} remaining files.")
                
                if not html_files:
                    # All files already processed (and this is correct)
                    if show_progress:
                        print("All files have already been processed. Nothing to do.")
                    return pd.DataFrame()
            except Exception as e:
                # If there's an error determining processed files, warn and process all
                warnings.warn(
                    f"Error determining processed files for stream_mode='append': {e}. "
                    f"Processing all files to be safe.",
                    UserWarning
                )
                # html_files already contains all files, so we can continue
    
    # Build files_with_categories dictionary by deriving category from each file's path
    # Only process files whose directory paths match defined categories
    files_with_categories = {}
    skipped_count = 0
    
    for html_file in html_files:
        try:
            category = _derive_category_from_path(html_file, config)
            files_with_categories[str(html_file)] = category
        except ValueError as e:
            # Skip files that don't match any category (with warning)
            warnings.warn(
                f"Could not derive category for file '{html_file}': {e}. Skipping file.",
                UserWarning
            )
            skipped_count += 1
            continue
    
    if skipped_count > 0 and show_progress:
        print(f"Skipped {skipped_count} files that don't match any defined category.")
    
    if not files_with_categories:
        raise ValueError(
            f"Could not derive categories for any files in directory: {directory_path}"
        )
    
    # Process using batch_extract with multiprocessing for CPU-bound HTML parsing
    return batch_extract(
        files_with_categories,
        config,
        scrape_date=scrape_date,
        use_multiprocessing=True,
        progress_callback=progress_callback,
        completion_callback=completion_callback,
        show_progress=show_progress,
        stream_to_file=stream_to_file,
        stream_mode=stream_mode,
        stream_format=stream_format
    )


def process_csv(
    csv_path: Union[str, Path],
    default_config: Optional[Dict[str, Any]] = None,
    default_scrape_date: Optional[str] = None,
    default_category: Optional[str] = None,
    progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
    completion_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    show_progress: bool = False,
    stream_to_file: Optional[Union[str, Path]] = None,
    stream_mode: str = 'overwrite',
    stream_format: Optional[str] = None
) -> pd.DataFrame:
    """
    Process multiple HTML files listed in a CSV file.
    
    Supports per-row config, scrape_date, and category overrides. The CSV file should
    have a 'path' column (required) and optional 'config', 'scrape_date', and 'category'
    columns. Per-row values override the default parameters.
    
    Args:
        csv_path: Path to CSV file containing file paths. CSV must have a 'path' column.
                 Optional columns: 'config', 'scrape_date', 'category'
        default_config: Default config to use if CSV row doesn't specify one. If None and
                       CSV row has no config, raises error.
        default_scrape_date: Default scrape date in YYYY-MM-DD format. Used only if CSV row
                             doesn't specify scrape_date. If None, dates are extracted from
                             file paths.
        default_category: Default category to use if CSV row doesn't specify one. Required
                          if config contains multiple categories and CSV doesn't have
                          'category' column.
        progress_callback: Optional callback function that receives ProgressInfo updates.
                          Called after each file is processed. Note: For CSV processing with
                          multiple config groups, progress is aggregated across all groups.
        completion_callback: Optional callback function that receives completion summary.
                            Called once at the end with comprehensive statistics including all processed files.
                            Note: For CSV processing with multiple config groups, callback is called
                            once per group, not once for all groups.
        show_progress: If True, display tqdm progress bar. Default: False.
        stream_to_file: Optional output file path for streaming. If provided, results are written
                        directly to file during processing. If None, results are collected in memory.
        stream_mode: Streaming mode: 'overwrite' (default) or 'append'. Only used if stream_to_file
                     is provided.
        stream_format: Output format for streaming: 'csv' or 'json'. If None, auto-detected from
                       file extension. Only used if stream_to_file is provided.
    
    Returns:
        If stream_to_file is provided: Empty DataFrame (data already written to file).
        If stream_to_file is None: Combined DataFrame with extracted data from all files listed in CSV.
    
    Raises:
        FileNotFoundError: If CSV file not found or if a file path in CSV doesn't exist
        ValueError: If CSV is missing 'path' column, if no config available for a row,
                    or if category is required but not provided
    """
    # Convert to Path object
    csv_file = Path(csv_path)
    
    # Validate CSV file exists
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    # Read CSV file (try UTF-8-BOM first, fallback to UTF-8)
    try:
        df_csv = pd.read_csv(csv_file, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df_csv = pd.read_csv(csv_file, encoding='utf-8')
    
    # Validate required 'path' column exists
    if 'path' not in df_csv.columns:
        raise ValueError(
            f"CSV file must have a 'path' column. Found columns: {list(df_csv.columns)}"
        )
    
    # Process each row
    all_files_with_categories = {}
    all_configs = {}  # Track config per file (for per-row config support)
    all_scrape_dates = {}  # Track scrape_date per file
    
    for idx, row in df_csv.iterrows():
        file_path = row['path']
        
        # Validate file path exists
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"File path in CSV row {idx+1} does not exist: {file_path}")
        
        # Determine config for this row
        if 'config' in df_csv.columns and pd.notna(row.get('config')):
            # Per-row config override
            row_config_path = row['config']
            row_config = load_config(row_config_path)
        elif default_config is not None:
            # Use default config
            row_config = default_config
        else:
            raise ValueError(
                f"No config available for CSV row {idx+1}. "
                f"Either provide default_config or include 'config' column in CSV."
            )
        
        # Determine category for this row
        if 'category' in df_csv.columns and pd.notna(row.get('category')):
            # Per-row category override
            category = str(row['category'])
        elif default_category is not None:
            # Use default category
            category = default_category
        else:
            # Try to derive from path
            try:
                category = _derive_category_from_path(path_obj, row_config)
            except ValueError:
                # Check if config has multiple categories
                categories = row_config.get('categories', [])
                category_list = _get_category_list(categories)
                if len(category_list) > 1:
                    category_names = [cat.get('name') for cat in category_list]
                    raise ValueError(
                        f"Category required for CSV row {idx+1} (file: {file_path}). "
                        f"Config has multiple categories: {category_names}. "
                        f"Either provide default_category or include 'category' column in CSV."
                    )
                else:
                    # Single category - use it
                    category = category_list[0].get('name') if category_list else None
                    if category is None:
                        raise ValueError(
                            f"Could not determine category for CSV row {idx+1} (file: {file_path})"
                        )
        
        # Determine scrape_date for this row
        if 'scrape_date' in df_csv.columns and pd.notna(row.get('scrape_date')):
            # Per-row scrape_date override
            row_scrape_date = str(row['scrape_date'])
        else:
            # Use default scrape_date (may be None)
            row_scrape_date = default_scrape_date
        
        # Store file info
        all_files_with_categories[file_path] = category
        all_configs[file_path] = row_config
        all_scrape_dates[file_path] = row_scrape_date
    
    if not all_files_with_categories:
        return pd.DataFrame()
    
    # Group files by config and scrape_date for efficient batch processing
    # Files with same config and scrape_date can be processed together
    config_groups = {}
    for file_path, category in all_files_with_categories.items():
        config = all_configs[file_path]
        scrape_date = all_scrape_dates[file_path]
        key = (id(config), scrape_date)  # Use config id and scrape_date as key
        
        if key not in config_groups:
            config_groups[key] = {
                'config': config,
                'scrape_date': scrape_date,
                'files_with_categories': {}
            }
        
        config_groups[key]['files_with_categories'][file_path] = category
    
    # Process each group
    if stream_to_file is not None:
        # Streaming mode: write directly to file
        # First group uses specified mode, subsequent groups append
        first_group = True
        for group in config_groups.values():
            group_stream_mode = stream_mode if first_group else 'append'
            batch_extract(
                group['files_with_categories'],
                group['config'],
                scrape_date=group['scrape_date'],
                use_multiprocessing=True,
                progress_callback=progress_callback,
                completion_callback=completion_callback,
                show_progress=show_progress,
                stream_to_file=stream_to_file,
                stream_mode=group_stream_mode,
                stream_format=stream_format
            )
            first_group = False
        
        # Return empty DataFrame (data already written to file)
        return pd.DataFrame()
    else:
        # Collect in memory mode: combine all DataFrames
        all_dataframes = []
        for group in config_groups.values():
            df = batch_extract(
                group['files_with_categories'],
                group['config'],
                scrape_date=group['scrape_date'],
                use_multiprocessing=True,
                progress_callback=progress_callback,
                completion_callback=completion_callback,
                show_progress=show_progress
            )
            if len(df) > 0:
                all_dataframes.append(df)
        
        # Combine all DataFrames
        if all_dataframes:
            return pd.concat(all_dataframes, ignore_index=True)
        else:
            return pd.DataFrame()


def create_csv_template(output_path: Union[str, Path]) -> None:
    """
    Create a CSV template file with headers for bulk processing.
    
    Generates a starter CSV template with example row to help users
    create CSV files for bulk processing via process_csv(). The template
    includes all optional columns (path, config, scrape_date, category)
    with example values showing the expected format.
    
    Args:
        output_path: Path where template will be created. Should have
                     .csv extension. Parent directories will be created
                     if they don't exist.
    
    Raises:
        ValueError: If output_path doesn't have .csv extension
        OSError: If file cannot be written or directory cannot be created
    
    Example:
        >>> create_csv_template('file_list.csv')
        >>> create_csv_template('data/templates/batch_list.csv')
    """
    # Convert to Path object
    output_path = Path(output_path)
    
    # Validate .csv extension
    if output_path.suffix.lower() != '.csv':
        raise ValueError(
            f"Output path must have .csv extension. Got: {output_path.suffix}"
        )
    
    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create template DataFrame with example row
    template_data = {
        'path': ['data/gpu/2025/2025-01-15/page.html'],
        'config': ['data/config.yaml'],
        'scrape_date': ['2025-01-15'],
        'category': ['gpu']
    }
    df = pd.DataFrame(template_data)
    
    # Write CSV with UTF-8-BOM encoding (Excel compatible)
    df.to_csv(
        output_path,
        index=False,  # Don't include row index
        encoding='utf-8-sig'  # UTF-8 with BOM
    )
