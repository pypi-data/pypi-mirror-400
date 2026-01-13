# Integration Examples

Examples of integrating HTML Extract with other Python tools and libraries.

## Integration with Pandas

HTML Extract returns pandas DataFrames, so you can use all pandas operations:

```python
import pandas as pd
from html_extract import extract_data_from_html, load_config

config = load_config('config.yaml')
df = extract_data_from_html('page.html', config, category='gpu')

# Convert price to numeric
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# Filter by price
filtered_df = df[df['price'] > 1000]

# Sort by price
sorted_df = filtered_df.sort_values('price', ascending=False)

# Group by location
location_counts = df.groupby('location').size()

# Statistical analysis
print(df['price'].describe())
print(df['price'].mean())
```

## Custom Processing Pipeline

Process extracted data with custom logic:

```python
from html_extract import process_directory, load_config
import pandas as pd

config = load_config('data/config.yaml')
df = process_directory('data/gpu/2025/2025-01-15', config)

# Custom processing
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df = df[df['price'] > 0]  # Remove invalid prices
df['price_per_unit'] = df['price'] / df.get('quantity', 1)

# Filter and analyze
high_price = df[df['price'] > 1000]
print(f"Found {len(high_price)} items over 1000")
print(high_price[['title', 'price', 'location']].head())
```

## Batch Processing with Progress Tracking

Track progress during batch operations:

```python
from html_extract import batch_extract, load_config, ProgressInfo

def progress_callback(progress: ProgressInfo):
    print(f"Processed {progress.current}/{progress.total} files")
    print(f"Percentage: {progress.percentage:.1f}%")
    print(f"Rate: {progress.rate:.1f} files/s")
    if progress.failed_count > 0:
        print(f"Failed: {progress.failed_count} files")

config = load_config('config.yaml')
files_with_categories = {
    'file1.html': 'gpu',
    'file2.html': 'gpu',
    'file3.html': 'gpu'
}

df = batch_extract(
    files_with_categories,
    config,
    progress_callback=progress_callback,
    show_progress=True
)
```

## Error Handling Patterns

Handle errors gracefully in production code:

```python
from html_extract import extract_data_from_html, load_config
from html_extract.config import FileNotFoundError, ValueError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_extract(file_path, config_path, category):
    """Extract data with error handling."""
    try:
        config = load_config(config_path)
        df, skipped = extract_data_from_html(file_path, config, category=category)
        logger.info(f"Extracted {len(df)} items from {file_path}")
        return df
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return None
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

# Use the function
df = safe_extract('page.html', 'config.yaml', 'gpu')
if df is not None:
    print(f"Successfully extracted {len(df)} items")
```

## Streaming for Large Batches

Stream results directly to file for memory-efficient processing:

```python
from html_extract import batch_extract, load_config

config = load_config('config.yaml')
files_with_categories = {
    f'file_{i}.html': 'gpu' for i in range(1000)
}

# Stream results directly to file (memory-efficient)
df = batch_extract(
    files_with_categories,
    config,
    stream_to_file='output.csv',
    stream_mode='overwrite',
    max_workers=4
)
```

## Combining Multiple Sources

Combine data from multiple extraction runs:

```python
from html_extract import process_directory, load_config
import pandas as pd

config = load_config('config.yaml')

# Process multiple directories
gpu_df = process_directory('data/gpu/2025/2025-01-15', config)
laptopy_df = process_directory('data/laptopy/2025/2025-01-15', config)

# Combine DataFrames
combined_df = pd.concat([gpu_df, laptopy_df], ignore_index=True)

# Add source category
combined_df['source_category'] = 'mixed'

# Save combined results
combined_df.to_csv('all_products.csv', index=False)
```

## Custom Analysis

Perform custom analysis on extracted data:

```python
from html_extract import process_directory, load_config
import pandas as pd

config = load_config('config.yaml')
df = process_directory('data/gpu/2025/2025-01-15', config)

# Convert price to numeric
df['price'] = pd.to_numeric(df['price'], errors='coerce')

# Analysis
avg_price = df['price'].mean()
new_items = df[df.get('is_new', 0) == 1]
location_counts = df['location'].value_counts()

print(f"Average price: {avg_price}")
print(f"New items: {len(new_items)}")
print(f"Top locations:\n{location_counts.head()}")
```

## Webhook Integration

Send completion notifications (e.g., for n8n):

```python
from html_extract import batch_extract, load_config
import requests

def send_to_webhook(completion_data):
    """Send completion summary to webhook."""
    try:
        response = requests.post(
            "https://your-webhook-url.com/html-extract",
            json=completion_data,
            timeout=10
        )
        response.raise_for_status()
        print("Webhook notification sent successfully")
    except Exception as e:
        print(f"Failed to send webhook: {e}")

config = load_config('config.yaml')
files_with_categories = {
    'file1.html': 'gpu',
    'file2.html': 'gpu'
}

df = batch_extract(
    files_with_categories,
    config,
    completion_callback=send_to_webhook
)
```

## See Also

- [Python API Guide](12-python-api-guide.md) - Complete API guide
- [API Reference](15-api-reference.md) - Full function reference
- [Advanced Topics](../advanced/) - Performance and best practices
