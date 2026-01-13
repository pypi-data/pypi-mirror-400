"""
Output formatting module for HTML Extract.

Provides functionality to save extracted DataFrames in various formats.
"""

import csv
import json
import threading
from pathlib import Path
from typing import Optional, Union, Any

import pandas as pd


def _save_csv(dataframe: pd.DataFrame, output_path: Path) -> None:
    """Save DataFrame to CSV file with UTF-8-BOM encoding."""
    dataframe.to_csv(
        output_path,
        index=False,  # Don't include row index
        encoding='utf-8-sig',  # UTF-8 with BOM
        errors='replace'  # Handle encoding errors gracefully
    )


def _save_json(dataframe: pd.DataFrame, output_path: Path) -> None:
    """Save DataFrame to JSON file as array of objects."""
    # Convert DataFrame to list of dicts (records format)
    records = dataframe.to_dict('records')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(
            records,
            f,
            indent=2,  # Pretty-print
            ensure_ascii=False,  # Allow Unicode characters
            default=str  # Convert non-serializable types to strings
        )


def _detect_format(output_path: Union[str, Path], format: Optional[str]) -> str:
    """Detect output format from path or use explicit format."""
    # If format is explicitly set, use it
    if format is not None:
        if format not in ['csv', 'json']:
            raise ValueError(f"Invalid format: {format}. Must be 'csv' or 'json'.")
        return format
    
    # Auto-detect from file extension
    path = Path(output_path)
    suffix = path.suffix.lower()
    
    if suffix == '.csv':
        return 'csv'
    elif suffix == '.json':
        return 'json'
    else:
        # Default to CSV for unknown extensions or no extension
        return 'csv'


def save_output(
    dataframe: pd.DataFrame,
    output_path: Union[str, Path],
    format: Optional[str] = None
) -> None:
    """
    Save DataFrame to file in specified format (CSV or JSON).
    
    Args:
        dataframe: DataFrame to save
        output_path: Output file path (required)
        format: Output format: None (auto-detect from path), 'csv', or 'json'
    
    Raises:
        ValueError: If format cannot be determined or is invalid, or if output_path is not provided
        OSError: If file cannot be written
        TypeError: If dataframe is not a DataFrame
    """
    # Validate dataframe
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pd.DataFrame, got {type(dataframe)}")
    
    # Validate output_path is provided
    if output_path is None:
        raise ValueError("output_path is required. For streaming, use processing functions directly.")
    
    # Convert to Path object
    output_path = Path(output_path)
    
    # Determine format
    detected_format = _detect_format(output_path, format)
    
    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save in appropriate format
    if detected_format == 'csv':
        _save_csv(dataframe, output_path)
    elif detected_format == 'json':
        _save_json(dataframe, output_path)


class CSVStreamWriter:
    """
    Thread/process-safe CSV stream writer for incremental file writing.
    
    Writes CSV data incrementally as DataFrames are processed, maintaining
    file format integrity with proper header management.
    """
    
    def __init__(
        self,
        output_path: Union[str, Path],
        mode: str = 'overwrite',
        lock: Optional[Any] = None
    ):
        """
        Initialize CSV stream writer.
        
        Args:
            output_path: Path to output CSV file
            mode: 'overwrite' to create new file, 'append' to append to existing
            lock: Optional lock object for thread/process safety (threading.Lock or multiprocessing.Lock)
        """
        self.output_path = Path(output_path)
        self.mode = mode
        self.lock = lock if lock is not None else threading.Lock()
        self.header_written = False
        self.first_write = True
        
        # Create parent directories if needed
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file in appropriate mode
        if mode == 'append' and self.output_path.exists():
            # Append mode: file exists, skip header
            self.file_handle = open(self.output_path, 'a', encoding='utf-8-sig', newline='', errors='replace')
            self.writer = csv.writer(self.file_handle)
            self.header_written = True  # Assume header already exists
        else:
            # Overwrite mode or new file: write header on first write
            self.file_handle = open(self.output_path, 'w', encoding='utf-8-sig', newline='', errors='replace')
            self.writer = csv.writer(self.file_handle)
            self.header_written = False
    
    def write_dataframe(self, dataframe: pd.DataFrame) -> None:
        """
        Write DataFrame rows to CSV file.
        
        Args:
            dataframe: DataFrame to write (rows will be written incrementally)
        
        Raises:
            OSError: If file write fails
        """
        if dataframe is None or len(dataframe) == 0:
            return
        
        try:
            with self.lock:
                # Write header on first write (overwrite mode only)
                if not self.header_written:
                    self.writer.writerow(dataframe.columns.tolist())
                    self.header_written = True
                
                # Write rows
                for _, row in dataframe.iterrows():
                    # Convert row to list, handling None values
                    row_values = [str(val) if pd.notna(val) else '' for val in row.values]
                    self.writer.writerow(row_values)
                
                # Flush to ensure data is written
                self.file_handle.flush()
        except Exception as e:
            # Re-raise with context
            raise OSError(f"Failed to write DataFrame to CSV file '{self.output_path}': {e}") from e
    
    def close(self) -> None:
        """Close the file handle."""
        if hasattr(self, 'file_handle') and not self.file_handle.closed:
            self.file_handle.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close file."""
        self.close()


class JSONStreamWriter:
    """
    Thread/process-safe JSON stream writer for incremental file writing.
    
    Writes JSON data incrementally as DataFrames are processed, maintaining
    proper JSON array format with comma handling.
    """
    
    def __init__(
        self,
        output_path: Union[str, Path],
        mode: str = 'overwrite',
        lock: Optional[Any] = None
    ):
        """
        Initialize JSON stream writer.
        
        Args:
            output_path: Path to output JSON file
            mode: 'overwrite' to create new file, 'append' to append to existing
            lock: Optional lock object for thread/process safety (threading.Lock or multiprocessing.Lock)
        """
        self.output_path = Path(output_path)
        self.mode = mode
        self.lock = lock if lock is not None else threading.Lock()
        self.first_item = True
        
        # Create parent directories if needed
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Open file in appropriate mode
        if mode == 'append' and self.output_path.exists():
            # Append mode: file exists, need to handle existing content
            # Read existing content to check if it's a valid JSON array
            try:
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content and content.startswith('[') and content.endswith(']'):
                        # Valid JSON array - we'll append to it
                        # Open in append mode and truncate before closing bracket
                        self.file_handle = open(self.output_path, 'r+', encoding='utf-8', errors='replace')
                        # Find position of closing bracket
                        file_size = self.file_handle.seek(0, 2)  # Seek to end, get size
                        if file_size > 1:  # More than just "[]"
                            # Truncate before closing bracket
                            self.file_handle.seek(file_size - 1)
                            self.file_handle.truncate()
                            self.first_item = False  # Not first item, need comma
                        else:
                            # Empty array "[]" - start fresh
                            self.file_handle.seek(0)
                            self.file_handle.truncate(0)
                            self.file_handle.write('[\n')
                            self.first_item = True
                    else:
                        # Invalid or empty - start fresh
                        self.file_handle = open(self.output_path, 'w', encoding='utf-8', errors='replace')
                        self.file_handle.write('[\n')
                        self.first_item = True
            except Exception:
                # File read error - start fresh
                self.file_handle = open(self.output_path, 'w', encoding='utf-8', errors='replace')
                self.file_handle.write('[\n')
                self.first_item = True
        else:
            # Overwrite mode or new file: write opening bracket
            self.file_handle = open(self.output_path, 'w', encoding='utf-8', errors='replace')
            self.file_handle.write('[\n')
            self.first_item = True
    
    def write_dataframe(self, dataframe: pd.DataFrame) -> None:
        """
        Write DataFrame rows to JSON file as array of objects.
        
        Args:
            dataframe: DataFrame to write (rows will be written as JSON objects)
        
        Raises:
            OSError: If file write fails
        """
        if dataframe is None or len(dataframe) == 0:
            return
        
        try:
            with self.lock:
                # Convert DataFrame to records
                records = dataframe.to_dict('records')
                
                for record in records:
                    # Write comma before item if not first
                    if not self.first_item:
                        self.file_handle.write(',\n')
                    
                    # Write JSON object with indentation
                    json_str = json.dumps(
                        record,
                        indent=2,
                        ensure_ascii=False,
                        default=str
                    )
                    # Add indentation to each line (except first)
                    lines = json_str.split('\n')
                    for i, line in enumerate(lines):
                        if i == 0:
                            self.file_handle.write('  ' + line)
                        else:
                            self.file_handle.write('\n  ' + line)
                    
                    self.first_item = False
                
                # Flush to ensure data is written
                self.file_handle.flush()
        except Exception as e:
            # Re-raise with context
            raise OSError(f"Failed to write DataFrame to JSON file '{self.output_path}': {e}") from e
    
    def close(self) -> None:
        """Close the file handle and write closing bracket."""
        if hasattr(self, 'file_handle') and not self.file_handle.closed:
            # Write closing bracket and newline
            self.file_handle.write('\n]')
            self.file_handle.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close file and write closing bracket."""
        self.close()


def _create_stream_writer(
    output_path: Union[str, Path],
    format: str,
    mode: str = 'overwrite',
    lock: Optional[Any] = None
) -> Union[CSVStreamWriter, JSONStreamWriter]:
    """
    Create appropriate stream writer based on format.
    
    Args:
        output_path: Path to output file
        format: Output format ('csv' or 'json')
        mode: 'overwrite' or 'append'
        lock: Optional lock object for thread/process safety
    
    Returns:
        CSVStreamWriter or JSONStreamWriter instance
    
    Raises:
        ValueError: If format is invalid
    """
    if format == 'csv':
        return CSVStreamWriter(output_path, mode=mode, lock=lock)
    elif format == 'json':
        return JSONStreamWriter(output_path, mode=mode, lock=lock)
    else:
        raise ValueError(f"Invalid format: {format}. Must be 'csv' or 'json'.")
