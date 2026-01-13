# Performance Optimization

Tips and techniques for optimizing HTML Extract performance.

## Multiprocessing and Threading

HTML Extract supports parallel processing for batch operations to significantly improve performance.

### Using Multiprocessing (Default)

Multiprocessing is the default for CPU-bound HTML parsing:

```python
from html_extract import batch_extract, load_config

config = load_config('config.yaml')
files_with_categories = {
    'file1.html': 'gpu',
    'file2.html': 'gpu',
    # ... many more files
}

# Use default multiprocessing (optimal for CPU-bound tasks)
df = batch_extract(files_with_categories, config)

# Or specify worker count
df = batch_extract(files_with_categories, config, max_workers=4)
```

### Using Threading

For I/O-bound operations, use threading:

```python
# Use threading for I/O-bound operations
df = batch_extract(
    files_with_categories,
    config,
    use_multiprocessing=False,
    max_workers=8
)
```

### Automatic Worker Detection

When `max_workers=None`, the tool automatically detects optimal worker count:
- **Multiprocessing**: CPU count (optimal for CPU-bound tasks)
- **Threading**: 2x CPU count (optimal for I/O-bound tasks, min 4, max 32)

## Batch Optimization

### Process in Batches

For very large datasets, process in smaller batches:

```python
from html_extract import batch_extract, load_config

config = load_config('config.yaml')

# Process in batches of 100 files
all_files = {...}  # Large dictionary of files
batch_size = 100

for i in range(0, len(all_files), batch_size):
    batch = dict(list(all_files.items())[i:i+batch_size])
    df = batch_extract(batch, config, stream_to_file='output.csv', stream_mode='append')
```

### Use Streaming for Large Batches

Stream results directly to file to reduce memory usage:

```python
# Stream results directly to file (memory-efficient)
df = batch_extract(
    files_with_categories,
    config,
    stream_to_file='output.csv',
    stream_mode='overwrite',
    max_workers=4
)
```

## Memory Management

### Streaming Mode

For large batches, use streaming to avoid loading all data into memory:

```python
# Stream to file instead of collecting in memory
df = batch_extract(
    files_with_categories,
    config,
    stream_to_file='output.csv',
    stream_mode='overwrite'
)
```

### Process Incrementally

Process files incrementally and save periodically:

```python
from html_extract import extract_data_from_html, load_config, save_output
import pandas as pd

config = load_config('config.yaml')
all_results = []

for file, category in files_with_categories.items():
    df, _ = extract_data_from_html(file, config, category=category)
    all_results.append(df)
    
    # Save every 100 files
    if len(all_results) >= 100:
        combined = pd.concat(all_results, ignore_index=True)
        save_output(combined, 'partial_results.csv')
        all_results = []
```

## Performance Tips

1. **Use batch_extract()** instead of processing files individually
2. **Set appropriate max_workers** based on your system
3. **Use streaming** for very large batches
4. **Process in batches** if memory is limited
5. **Reuse config objects** - load once, use many times
6. **Use multiprocessing** for CPU-bound HTML parsing (default)
7. **Use threading** only for I/O-bound operations

## See Also

- [Custom Processing](31-custom-processing.md) - Advanced processing techniques
- [Best Practices](32-best-practices.md) - General best practices
