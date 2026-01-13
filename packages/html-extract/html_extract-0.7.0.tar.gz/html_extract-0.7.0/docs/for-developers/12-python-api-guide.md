# Python API Guide

Complete guide to using HTML Extract's Python API.

## Overview

HTML Extract provides a Python API for programmatic data extraction. All functionality available through the CLI is also available through the Python API.

## Core Functions

### Loading Configuration

Load configuration from a file or dict object:

```python
from html_extract import load_config

# From YAML file
config = load_config('data/config.yaml')

# From JSON file
config = load_config('data/config.json')

# From dict object (programmatic)
config_dict = {
    "categories": [{"name": "gpu", "attribute_names": ["link", "title"]}],
    "attributes": [...]
}
config = load_config(config_dict)
```

### Extracting from Single File

Extract data from a single HTML file:

```python
from html_extract import extract_data_from_html, load_config

config = load_config('config.yaml')
df, skipped_count = extract_data_from_html(
    'page.html',
    config,
    category='gpu'
)

print(f"Extracted {len(df)} items")
print(f"Skipped {skipped_count} items")
```

The function returns:
- `df`: DataFrame with extracted data (one row per item)
- `skipped_count`: Number of items skipped due to missing required attributes

### Processing Directories

Process all HTML files in a directory:

```python
from html_extract import process_directory, load_config

config = load_config('config.yaml')
df = process_directory('data/gpu/2025/2025-01-15', config)

print(f"Total items: {len(df)}")
```

Category is automatically derived from the folder path.

### Processing CSV Lists

Process multiple files listed in a CSV:

```python
from html_extract import process_csv, load_config

default_config = load_config('config.yaml')
df = process_csv(
    'file_list.csv',
    default_config=default_config,
    default_category='gpu'
)
```

### Saving Output

Save extracted data to file:

```python
from html_extract import save_output

# Save as CSV
save_output(df, 'output.csv')

# Save as JSON
save_output(df, 'output.json')

# Format is auto-detected from extension
```

## Usage Patterns

### Pattern 1: Single File Processing

```python
from html_extract import extract_data_from_html, load_config, save_output

config = load_config('data/config.yaml')
df = extract_data_from_html('page.html', config, category='gpu')
save_output(df, 'output.csv')
```

### Pattern 2: Process Directory

```python
from html_extract import process_directory, load_config, save_output

config = load_config('data/config.yaml')
df = process_directory('data/gpu/2025/2025-01-15', config)
save_output(df, 'output.csv')
```

### Pattern 3: Process CSV Bulk List

```python
from html_extract import process_csv, load_config, save_output

default_config = load_config('data/config.yaml')
df = process_csv(
    'file_list.csv',
    default_config=default_config,
    default_category='gpu'
)
save_output(df, 'combined.csv')
```

### Pattern 4: Batch Processing Multiple Files

```python
from html_extract import batch_extract, load_config

config = load_config('data/config.yaml')
files_with_categories = {
    'data/gpu/2025/2025-01-15/page_1.html': 'gpu',
    'data/gpu/2025/2025-01-15/page_2.html': 'gpu',
    'data/gpu/2025/2025-01-16/page_1.html': 'gpu'
}

df = batch_extract(files_with_categories, config, max_workers=4)
print(f"Processed {len(df)} items from {len(files_with_categories)} files")
```

### Pattern 5: Custom Processing Pipeline

```python
from html_extract import batch_extract, load_config
import pandas as pd

config = load_config('data/config.yaml')

files_with_categories = {
    'data/gpu/2025/2025-01-15/page_1.html': 'gpu',
    'data/gpu/2025/2025-01-15/page_2.html': 'gpu',
}

# Process files
combined_df = batch_extract(files_with_categories, config)

# Custom filtering
filtered_df = combined_df[combined_df['price'] > 1000]

# Save
filtered_df.to_csv('high_price_listings.csv', index=False)
```

## Working with DataFrames

The API returns pandas DataFrames, so you can use all pandas operations:

```python
import pandas as pd
from html_extract import extract_data_from_html, load_config

config = load_config('config.yaml')
df = extract_data_from_html('page.html', config, category='gpu')

# Pandas operations
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df[df['price'] > 0]
df = df.sort_values('price', ascending=False)

# View results
print(df.head())
print(df.describe())
```

## Error Handling

Handle errors gracefully:

```python
from html_extract import extract_data_from_html, load_config
from html_extract.config import FileNotFoundError, ValueError

try:
    config = load_config('config.yaml')
    df = extract_data_from_html('page.html', config, category='gpu')
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Features

### Progress Tracking

Track progress during batch operations:

```python
from html_extract import batch_extract, load_config, ProgressInfo

def progress_callback(progress: ProgressInfo):
    print(f"Processed {progress.current}/{progress.total} files ({progress.percentage:.1f}%)")
    print(f"Rate: {progress.rate:.1f} files/s")

config = load_config('config.yaml')
files_with_categories = {
    'file1.html': 'gpu',
    'file2.html': 'gpu'
}

df = batch_extract(
    files_with_categories,
    config,
    progress_callback=progress_callback,
    show_progress=True
)
```

### Streaming to File

Stream results directly to file for memory-efficient processing:

```python
from html_extract import batch_extract, load_config

config = load_config('config.yaml')
files_with_categories = {
    'file1.html': 'gpu',
    'file2.html': 'gpu'
}

# Stream results directly to file
df = batch_extract(
    files_with_categories,
    config,
    stream_to_file='output.csv',
    stream_mode='overwrite'
)
```

## Next Steps

- **[Programmatic Configs](13-programmatic-configs.md)** - Create configs from Python dicts
- **[Integration Examples](14-integration-examples.md)** - Integrate with other tools
- **[API Reference](15-api-reference.md)** - Complete function reference with all parameters
