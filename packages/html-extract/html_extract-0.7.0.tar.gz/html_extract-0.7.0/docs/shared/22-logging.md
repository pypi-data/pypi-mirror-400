# Logging Reference

Complete documentation for logging functionality in HTML Extract.

## Overview

HTML Extract provides comprehensive logging to track file processing, outcomes, and errors. Logging helps you monitor processing progress, debug issues, and understand what happened during extraction operations.

**Features**:
- Structured logging with timestamps and log levels
- Console output (stderr) by default, optional log file support
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Detailed tracking of each processed HTML file with outcomes
- Warnings for missing required attributes
- Summary statistics for batch operations

**Default Behavior**: Logs are written to stderr at INFO level. This ensures logs don't interfere with stdout data output (CSV/JSON).

## Log Format

All log messages follow this format:

```
YYYY-MM-DD HH:MM:SS LEVEL message
```

**Example**:
```
2025-01-04 10:30:15 INFO Processing: data/gpu/2024-01-15/page.html (category: gpu)
2025-01-04 10:30:16 WARNING Skipped item in data/gpu/2024-01-15/page.html - Missing required attribute: 'link'
2025-01-04 10:30:16 INFO Success: data/gpu/2024-01-15/page.html - Extracted 42 items (1 skipped due to missing required attributes)
2025-01-04 10:30:17 WARNING Empty result: data/gpu/2024-01-15/page2.html - No items found
2025-01-04 10:30:18 ERROR Failed: data/gpu/2024-01-15/page3.html - FileNotFoundError: HTML file not found
2025-01-04 10:30:20 INFO Summary: Processed 100 files, 98 successful, 2 failed, 4200 total items, 15 items skipped
```

## CLI Logging Options

### `--log-file PATH`

Write logs to a file in addition to (or instead of) console output.

**Usage**:
```bash
html-extract data/gpu -c config.yaml -o output.csv --log-file processing.log
```

**Behavior**:
- Creates log file if it doesn't exist (creates parent directories if needed)
- Appends to existing log file (does not overwrite)
- Logs are written in UTF-8 encoding
- Both file and console (stderr) receive logs by default

**Example**:
```bash
# Log to file only (still see errors on console)
html-extract data/gpu -c config.yaml --log-file logs/processing.log 2>/dev/null

# Log to both file and console
html-extract data/gpu -c config.yaml --log-file logs/processing.log
```

### `--log-level LEVEL`

Set the minimum logging level. Messages at or above this level are logged.

**Levels** (from least to most verbose):
- `CRITICAL`: Only critical errors
- `ERROR`: Errors and critical issues
- `WARNING`: Warnings, errors, and critical issues (default for production)
- `INFO`: Informational messages, warnings, and errors (default)
- `DEBUG`: All messages including detailed debugging information

**Usage**:
```bash
# Show only errors and warnings
html-extract data/gpu -c config.yaml --log-level WARNING

# Show all messages including debug info
html-extract data/gpu -c config.yaml --log-level DEBUG
```

**Default**: `INFO`

### `-v, --verbose`

Enable verbose logging (equivalent to `--log-level DEBUG`).

**Usage**:
```bash
html-extract data/gpu -c config.yaml -v
```

**Behavior**:
- Sets log level to DEBUG regardless of `--log-level` setting
- Shows detailed debugging information
- Useful for troubleshooting extraction issues

**Example**:
```bash
# Verbose logging to file
html-extract data/gpu -c config.yaml --log-file debug.log -v
```

## What Gets Logged

### File Processing Events

**INFO Level**:
- File processing start: `Processing: <file_path> (category: <category>)`
- Successful extraction: `Success: <file_path> - Extracted <count> items`
- Successful extraction with skipped items: `Success: <file_path> - Extracted <count> items (<skipped> skipped due to missing required attributes)`
- Batch summary: `Summary: Processed <total> files, <successful> successful, <failed> failed, <items> total items`

**WARNING Level**:
- Missing required attribute: `Skipped item in <file_path> - Missing required attribute: '<attribute_name>'`
- Empty result: `Empty result: <file_path> - No items found`

**ERROR Level**:
- Processing failure: `Failed: <file_path> - <ExceptionType>: <error_message>`
- File write errors: `Failed to write DataFrame to stream for file '<file_path>': <error>`

### Log Levels by Event Type

| Event Type | Log Level | Description |
|------------|-----------|-------------|
| File processing start | INFO | When a file begins processing |
| Successful extraction | INFO | When items are successfully extracted |
| Missing required attribute | WARNING | When an item is skipped due to missing required attribute |
| Empty result | WARNING | When no items are found in a file |
| Processing error | ERROR | When file processing fails with an exception |
| Batch summary | INFO | Summary statistics at end of batch operations |

## Programmatic Logging API

For programmatic use, you can configure logging directly in Python code.

### `setup_logging()`

Configure logging for the html_extract module.

**Signature**: `setup_logging(log_level='INFO', log_file=None, verbose=False)`

**Parameters**:
- `log_level` (str, optional): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'). Default: 'INFO'
- `log_file` (str or Path, optional): Path to log file. If None, logs only to stderr. Default: None
- `verbose` (bool, optional): If True, sets level to DEBUG regardless of log_level. Default: False

**Example**:
```python
from html_extract import setup_logging, extract_data_from_html, load_config

# Configure logging before processing
setup_logging(log_level='INFO', log_file='processing.log')

# Process files (logs will be written)
config = load_config('config.yaml')
df = extract_data_from_html('page.html', config, category='gpu')
```

### `get_logger()`

Get the module logger instance for custom logging.

**Signature**: `get_logger() -> logging.Logger`

**Returns**: Configured logger instance

**Example**:
```python
from html_extract.logging import get_logger

logger = get_logger()
logger.info("Custom log message")
logger.warning("Custom warning")
```

## Logging Helper Functions

The logging module provides helper functions for common logging scenarios. These are used internally but can also be used programmatically:

- `log_file_start(file_path, category=None)`: Log file processing start
- `log_file_success(file_path, item_count, skipped_count=0)`: Log successful extraction
- `log_file_empty(file_path)`: Log empty result
- `log_file_error(file_path, error)`: Log processing error
- `log_missing_required_attribute(file_path, attribute_name)`: Log missing required attribute warning
- `log_batch_summary(total_files, successful_files, failed_files, total_items, total_skipped_items=0)`: Log batch summary

**Example**:
```python
from html_extract.logging import log_file_start, log_file_success

log_file_start('page.html', category='gpu')
# ... process file ...
log_file_success('page.html', item_count=42, skipped_count=1)
```

## Examples

### Basic Usage (Default Logging)

```bash
# Logs to stderr at INFO level
html-extract data/gpu -c config.yaml -o output.csv
```

**Output** (to stderr):
```
2025-01-04 10:30:15 INFO Processing: data/gpu/2024-01-15/page.html (category: gpu)
2025-01-04 10:30:16 INFO Success: data/gpu/2024-01-15/page.html - Extracted 42 items
2025-01-04 10:30:20 INFO Summary: Processed 100 files, 98 successful, 2 failed, 4200 total items
```

### Logging to File

```bash
# Log to file while processing
html-extract data/gpu -c config.yaml -o output.csv --log-file processing.log
```

**File content** (`processing.log`):
```
2025-01-04 10:30:15 INFO Processing: data/gpu/2024-01-15/page.html (category: gpu)
2025-01-04 10:30:16 WARNING Skipped item in data/gpu/2024-01-15/page.html - Missing required attribute: 'link'
2025-01-04 10:30:16 INFO Success: data/gpu/2024-01-15/page.html - Extracted 42 items (1 skipped due to missing required attributes)
...
```

### Verbose Debugging

```bash
# Enable debug logging to troubleshoot issues
html-extract data/gpu -c config.yaml -v --log-file debug.log
```

### Warning-Only Logging

```bash
# Show only warnings and errors (suppress INFO messages)
html-extract data/gpu -c config.yaml --log-level WARNING
```

**Output**:
```
2025-01-04 10:30:16 WARNING Skipped item in data/gpu/2024-01-15/page.html - Missing required attribute: 'link'
2025-01-04 10:30:17 WARNING Empty result: data/gpu/2024-01-15/page2.html - No items found
2025-01-04 10:30:18 ERROR Failed: data/gpu/2024-01-15/page3.html - FileNotFoundError: HTML file not found
```

### Programmatic Logging Configuration

```python
from html_extract import setup_logging, process_directory, load_config

# Configure logging before batch processing
setup_logging(
    log_level='INFO',
    log_file='batch_processing.log',
    verbose=False
)

# Process directory (logs will be written)
config = load_config('config.yaml')
df = process_directory('data/gpu', config, show_progress=True)
```

## Best Practices

### Production Use

For production environments:
- Use `--log-level WARNING` to reduce log volume
- Write logs to file with `--log-file` for later analysis
- Monitor ERROR level messages for processing failures

```bash
html-extract data/gpu -c config.yaml -o output.csv \
  --log-file /var/log/html-extract/processing.log \
  --log-level WARNING
```

### Development/Debugging

For development and debugging:
- Use `-v, --verbose` or `--log-level DEBUG` for detailed information
- Log to file for analysis: `--log-file debug.log`

```bash
html-extract data/gpu -c config.yaml -v --log-file debug.log
```

### Separating Logs from Data

When piping output to other tools, logs go to stderr (not stdout), so they don't interfere with data:

```bash
# Logs to stderr, data to stdout
html-extract page.html -c config.yaml | jq '.[0]'

# Redirect logs to file, data to stdout
html-extract page.html -c config.yaml --log-file processing.log | jq '.[0]'
```

## Understanding Log Messages

### Missing Required Attributes

When an item is skipped due to a missing required attribute, you'll see:

```
WARNING Skipped item in <file_path> - Missing required attribute: '<attribute_name>'
```

**What this means**:
- An item container was found in the HTML
- The extraction attempted to extract the required attribute
- The attribute value was `None` or not found
- The entire item was skipped (not included in results)

**Action**: Review your configuration selectors for the missing attribute, or check if the HTML structure has changed.

### Empty Results

When no items are found in a file:

```
WARNING Empty result: <file_path> - No items found
```

**What this means**:
- The file was processed successfully
- No item containers were found matching the configuration
- The result DataFrame is empty

**Action**: Verify the file contains the expected HTML structure, or check if selectors need adjustment.

### Processing Errors

When file processing fails:

```
ERROR Failed: <file_path> - <ExceptionType>: <error_message>
```

**What this means**:
- An exception occurred during processing
- The file was not processed
- Processing continues with other files (in batch operations)

**Action**: Check the error message and file for issues (encoding, corruption, permissions, etc.).

## Integration with Other Tools

### Log Analysis

Logs can be analyzed with standard Unix tools:

```bash
# Count errors
grep ERROR processing.log | wc -l

# Find files with missing required attributes
grep "Missing required attribute" processing.log

# Extract summary statistics
grep "Summary:" processing.log
```

### Log Rotation

For long-running batch operations, consider log rotation:

```bash
# Use logrotate or similar tools
html-extract data/gpu -c config.yaml --log-file /var/log/html-extract/processing.log
```

## Notes

- **Logs don't affect performance**: Logging is designed to be lightweight and doesn't significantly impact processing speed
- **Thread/Process safe**: Logging works correctly with multiprocessing and multithreading
- **Encoding**: Log files use UTF-8 encoding to support international characters
- **Backward compatibility**: Existing code continues to work without changes (logging is opt-in via CLI or programmatic setup)
