# API Reference

Complete Python API documentation for the `html_extract` module.

## Module Overview

The `html_extract` module provides functions for extracting structured data from HTML files using configuration. The API provides all functionality that is also available through the CLI tool. It consists of multiple submodules:

- **`extract`**: Core extraction functions using configuration
- **`config`**: Configuration management (YAML/JSON file loading, dict objects, and template creation)
- **`output`**: Output formatting and saving utilities
- **`batch`**: Batch processing and folder operations

## Importing

```python
# Import functions
from html_extract import (
    extract_data_from_html,
    load_config,
    create_config_template,
    save_output,
    batch_extract,
    process_directory,
    process_csv,
    create_csv_template
)

# Or import from specific submodules
from html_extract.extract import extract_data_from_html
from html_extract.config import load_config, create_config_template
from html_extract.output import save_output
from html_extract.batch import batch_extract, process_directory, process_csv, create_csv_template
```

## extract Module

### `extract_data_from_html()`

**Signature**: `extract_data_from_html(source_path, config, scrape_date=None, category=None)`

Extract data from HTML file based on configuration.

**Parameters**:
- `source_path` (str or Path): Path to HTML file to process
- `config` (str, dict, or Path): Configuration file path (YAML or JSON) or pre-loaded configuration dictionary. Supports YAML/JSON file paths and dict objects.
- `scrape_date` (str, optional): Explicit scrape date in YYYY-MM-DD format. If provided, overrides automatic date extraction from path. If None, date is extracted from file path or filename.
- `category` (str, optional): Category name to use for extraction. Required if config contains multiple categories. Must exactly match one of the category names in the config's `categories` array.

**Returns**:
- `tuple[pd.DataFrame, int]`: Tuple containing:
  - `pd.DataFrame`: DataFrame with extracted data, one row per item found in the HTML file
  - `int`: Number of items skipped due to missing required attributes

**Raises**:
- `ValueError`: If config is None, no attributes defined, or category is required but not provided
- `FileNotFoundError`: If source file not found

**Example**:
```python
from html_extract import extract_data_from_html, load_config

# Pass config file path directly
df, skipped_count = extract_data_from_html('page.html', 'data/config.yaml', category='gpu')

# Load config first, then extract
config = load_config('data/config.yaml')
df, skipped_count = extract_data_from_html('page.html', config, category='gpu')

# Extract with explicit scrape date and category
df, skipped_count = extract_data_from_html('page.html', config, scrape_date='2025-01-20', category='gpu')

# Extract with nested category
df, skipped_count = extract_data_from_html('page.html', config, category='domy/najem')

# Process the DataFrame
print(df.head())
print(f"Found {len(df)} items")
```

**Notes**:
- Extracts all items found in the HTML file, not just one
- Automatically detects item containers by finding all elements matching the first required attribute
- Category parameter is required if config contains multiple categories
- Category name must exactly match (case-sensitive) one of the category names in config
- Automatically extracts metadata (source_file, scrape_date, source_path, source_month) from file path when scrape_date parameter is None
- Skips items where required attributes are missing
- Returns empty DataFrame with correct columns if no items found

## config Module

### `load_config()`

**Signature**: `load_config(source)`

Load configuration for data extraction from a YAML file, JSON file, or dict object.

**Parameters**:
- `source` (str, Path, or dict): Either:
  - **str or Path**: Path to YAML (`.yaml`/`.yml`) or JSON (`.json`) config file
  - **dict**: Python dictionary with same structure as YAML/JSON config (for programmatic creation)

**Returns**:
- `dict`: Configuration dictionary containing `categories` and `attributes`

**Raises**:
- `FileNotFoundError`: If config file not found (when `source` is str or Path)
- `yaml.YAMLError`: If YAML file has invalid syntax
- `ValueError`: If config file is empty, has unsupported format, has invalid JSON syntax, or dict structure is invalid

**Example**:
```python
from html_extract.config import load_config

# Load from YAML file
config = load_config('data/gpu/config.yaml')

# Load from JSON file
config = load_config('data/gpu/config.json')

# Load from dict object
config_dict = {
    "categories": [{"name": "gpu", "attribute_names": ["link", "title", "price"]}],
    "attributes": [...]
}
config = load_config(config_dict)
```

### `create_config_template()`

**Signature**: `create_config_template(output_path, format='auto')`

Create a configuration template file (YAML or JSON) with example attributes.

**Parameters**:
- `output_path` (str or Path): Path where template will be created. Parent directories will be created if they don't exist.
- `format` (str, optional): Format to use: 'auto' (detect from file extension), 'yaml', or 'json'. Defaults to 'auto'.

**Returns**:
- `None`: Creates file at output_path

**Raises**:
- `ValueError`: If format is invalid or cannot be determined from file extension
- `OSError`: If file cannot be written or directory cannot be created

**Example**:
```python
from html_extract.config import create_config_template

# Create YAML config template
create_config_template('data/new_config.yaml')

# Create JSON config template
create_config_template('data/new_config.json')
```

## batch Module

### `ProgressInfo` Class

Progress information dataclass for batch processing operations.

**Attributes**:
- `current` (int): Number of files processed so far
- `total` (int): Total number of files to process
- `percentage` (float): Completion percentage (0.0 to 100.0)
- `rate` (float): Processing rate in files per second
- `elapsed_time` (float): Time elapsed in seconds
- `current_file` (str, optional): Path of the file currently being processed (or None)
- `failed_count` (int): Number of files that returned empty DataFrames

**Example**:
```python
from html_extract import batch_extract, load_config, ProgressInfo

def progress_callback(progress: ProgressInfo):
    print(f"Processed {progress.current}/{progress.total} files ({progress.percentage:.1f}%)")
    print(f"Rate: {progress.rate:.1f} files/s")

config = load_config('data/config.yaml')
files = {'file1.html': 'gpu', 'file2.html': 'gpu'}

df = batch_extract(files, config, progress_callback=progress_callback, show_progress=True)
```

### `batch_extract()`

**Signature**: `batch_extract(files_with_categories, config, scrape_date=None, max_workers=None, use_multiprocessing=True, progress_callback=None, completion_callback=None, show_progress=False, stream_to_file=None, stream_mode='overwrite', stream_format=None)`

Core batch processing function that processes multiple HTML files and combines results into a single DataFrame.

**Parameters**:
- `files_with_categories` (dict[str, str]): Dictionary mapping file paths to category names
- `config` (dict): Pre-loaded configuration dictionary (from `load_config()`)
- `scrape_date` (str, optional): Explicit scrape date in YYYY-MM-DD format
- `max_workers` (int, optional): Maximum number of worker processes/threads. If None, automatically detects optimal worker count
- `use_multiprocessing` (bool, optional): If True, use ProcessPoolExecutor. If False, use ThreadPoolExecutor. Default: True
- `progress_callback` (callable, optional): Callback function that receives `ProgressInfo` updates
- `completion_callback` (callable, optional): Callback function that receives completion summary
- `show_progress` (bool, optional): If True, display tqdm progress bar. Default: False
- `stream_to_file` (str or Path, optional): Output file path for streaming
- `stream_mode` (str, optional): Streaming mode: 'overwrite' (default) or 'append'
- `stream_format` (str, optional): Output format for streaming: 'csv' or 'json'

**Returns**:
- If `stream_to_file` is provided: Empty DataFrame (data already written to file)
- If `stream_to_file` is None: Combined DataFrame with extracted data from all files

**Example**:
```python
from html_extract import batch_extract, load_config

config = load_config('data/config.yaml')
files_with_categories = {
    'data/gpu/2025/2025-01-15/page_1.html': 'gpu',
    'data/gpu/2025/2025-01-15/page_2.html': 'gpu'
}

# Process with auto-extracted dates
df = batch_extract(files_with_categories, config)

# Process with explicit scrape date
df = batch_extract(files_with_categories, config, scrape_date='2025-01-20')

# Process with custom worker count
df = batch_extract(files_with_categories, config, max_workers=4)

# Stream results directly to file
df = batch_extract(files_with_categories, config, stream_to_file='output.csv')
```

### `process_directory()`

**Signature**: `process_directory(directory_path, config, scrape_date=None, recursive=True, progress_callback=None, completion_callback=None, show_progress=False, stream_to_file=None, stream_mode='overwrite', stream_format=None)`

Process all HTML files in a directory and return combined DataFrame.

**Parameters**:
- `directory_path` (str or Path): Path to directory containing HTML files
- `config` (dict): Pre-loaded config dictionary (from `load_config()`)
- `scrape_date` (str, optional): Explicit scrape date in YYYY-MM-DD format
- `recursive` (bool, optional): If True, process HTML files recursively in subdirectories (default: True)
- `progress_callback` (callable, optional): Callback function that receives `ProgressInfo` updates
- `completion_callback` (callable, optional): Callback function that receives completion summary
- `show_progress` (bool, optional): If True, display tqdm progress bar. Default: False
- `stream_to_file` (str or Path, optional): Output file path for streaming
- `stream_mode` (str, optional): Streaming mode: 'overwrite' (default) or 'append'
- `stream_format` (str, optional): Output format for streaming: 'csv' or 'json'

**Returns**:
- If `stream_to_file` is provided: Empty DataFrame (data already written to file)
- If `stream_to_file` is None: Combined DataFrame with extracted data from all HTML files

**Example**:
```python
from html_extract import process_directory, load_config

config = load_config('data/config.yaml')

# Process directory (auto-extract dates from file paths)
df = process_directory('data/gpu/2025/2025-01-15', config)

# Process directory with explicit scrape date
df = process_directory('data/gpu/2025/2025-01-15', config, scrape_date='2025-01-20')
```

**Notes**:
- Finds all `.html` files in the directory (recursively by default)
- Category is automatically derived from folder path
- Uses `batch_extract()` internally for processing

### `process_csv()`

**Signature**: `process_csv(csv_path, default_config=None, default_scrape_date=None, default_category=None, progress_callback=None, completion_callback=None, show_progress=False, stream_to_file=None, stream_mode='overwrite', stream_format=None)`

Process multiple HTML files listed in a CSV file.

**Parameters**:
- `csv_path` (str): Path to CSV file containing file paths. CSV must have a `path` column. Optional columns: `config`, `scrape_date`, `category`
- `default_config` (dict, optional): Default config to use if CSV row doesn't specify one
- `default_scrape_date` (str, optional): Default scrape date in YYYY-MM-DD format
- `default_category` (str, optional): Default category to use if CSV row doesn't specify one
- `progress_callback` (callable, optional): Callback function that receives `ProgressInfo` updates
- `completion_callback` (callable, optional): Callback function that receives completion summary
- `show_progress` (bool, optional): If True, display tqdm progress bar. Default: False
- `stream_to_file` (str or Path, optional): Output file path for streaming
- `stream_mode` (str, optional): Streaming mode: 'overwrite' (default) or 'append'
- `stream_format` (str, optional): Output format for streaming: 'csv' or 'json'

**Returns**:
- If `stream_to_file` is provided: Empty DataFrame (data already written to file)
- If `stream_to_file` is None: Combined DataFrame with extracted data from all files listed in CSV

**Example**:
```python
from html_extract import process_csv, load_config

default_config = load_config('data/config.yaml')

# Process CSV with default config and category
df = process_csv(
    'file_list.csv',
    default_config=default_config,
    default_category='gpu'
)
```

### `create_csv_template()`

**Signature**: `create_csv_template(output_path)`

Create a CSV template file with headers for bulk processing.

**Parameters**:
- `output_path` (str): Path where the template file should be created. Should have `.csv` extension

**Returns**:
- `None`: Creates file at output_path

**Example**:
```python
from html_extract.batch import create_csv_template

create_csv_template('file_list.csv')
```

## output Module

### `save_output()`

**Signature**: `save_output(dataframe, output_path, format=None)`

Save DataFrame to file in specified format (CSV or JSON).

**Parameters**:
- `dataframe` (pd.DataFrame): DataFrame to save
- `output_path` (str or Path): Output file path (required)
- `format` (str, optional): Output format: `None` (auto-detect from path), `'csv'`, or `'json'`. Defaults to `None`

**Returns**:
- `None`: Saves file to disk

**Raises**:
- `ValueError`: If format cannot be determined or is invalid
- `OSError`: If output directory doesn't exist or file cannot be written

**Example**:
```python
from html_extract.output import save_output

# Save as CSV (auto-detected from extension)
save_output(df, 'output.csv')

# Save as JSON (auto-detected from extension)
save_output(df, 'output.json')

# Explicitly specify format
save_output(df, 'output.txt', format='csv')
```

**Output Formats**:
- **CSV**: Standard comma-separated values with UTF-8-BOM encoding (Excel compatible)
- **JSON**: Array of objects, one per extracted item (pretty-printed, indented)

## Error Handling

### Common Exceptions

**`FileNotFoundError`**:
- Config file not found
- Source HTML file not found
- Folder path does not exist
- CSV file not found

**`ValueError`**:
- Config is None or invalid
- No attributes defined in config
- No HTML files found in folder/directory
- Date cannot be extracted from path
- YAML/JSON parsing error
- CSV missing required `path` column
- Format cannot be determined for output

**Example Error Handling**:
```python
from html_extract import extract_data_from_html, load_config

try:
    config = load_config('data/config.yaml')
    df = extract_data_from_html('page.html', config, category='gpu')
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## See Also

- [Python API Guide](12-python-api-guide.md) - Complete guide to using the API
- [Programmatic Configs](13-programmatic-configs.md) - Create configs from dict objects
- [Integration Examples](14-integration-examples.md) - Integration with other tools
- [Configuration Reference](../shared/20-configuration-reference.md) - Complete config documentation
