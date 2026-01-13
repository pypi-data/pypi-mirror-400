# Troubleshooting

Common issues and solutions when using HTML Extract's Python API.

## Import Errors

**Error**: `ModuleNotFoundError: No module named 'html_extract'`

**Solutions**:
- Ensure html-extract is installed: `pip install html-extract`
- Check Python environment (virtual environment, conda, etc.)
- Verify installation: `pip show html-extract`
- Try reinstalling: `pip install --upgrade html-extract`

**Error**: `ImportError: cannot import name 'X' from 'html_extract'`

**Solutions**:
- Check function name spelling
- Verify function exists in the API
- Check version compatibility
- Review import statement

## Configuration Errors

**Error**: `ValueError: Config file is empty` or `Config is None`

**Solutions**:
- Verify config file exists and is not empty
- Check file path is correct (use absolute path if needed)
- Validate config structure has `categories` and `attributes` keys
- Test config loading separately: `config = load_config('config.yaml')`

**Error**: `ValueError: Category 'X' not found in config`

**Solutions**:
- Ensure category name matches exactly (case-sensitive)
- Check category exists in config's `categories` array
- Verify category name spelling
- List available categories: `print([c['name'] for c in config['categories']])`

**Error**: `yaml.YAMLError` or JSON parsing errors

**Solutions**:
- Validate YAML/JSON syntax using online validators
- Check for indentation errors (YAML is sensitive to spacing)
- Verify file encoding is UTF-8
- Check for special characters that need escaping

## Extraction Errors

**Error**: `FileNotFoundError: HTML file not found`

**Solutions**:
- Verify file path is correct
- Use absolute paths if relative paths don't work
- Check file permissions
- Ensure file exists before processing

**Error**: Empty DataFrame returned

**Possible Causes**:
- HTML doesn't contain expected content structure
- Selectors in config don't match HTML structure
- Required attributes missing from HTML
- Category doesn't match HTML content

**Solutions**:
- Inspect HTML file structure
- Test selectors in browser dev tools
- Check config attribute definitions
- Verify HTML file contains expected content
- Try extracting with a simpler config first

**Error**: `ValueError: Category must be specified`

**Solutions**:
- Provide category parameter when config has multiple categories
- Use: `extract_data_from_html('page.html', config, category='gpu')`
- Or use single-category config

## DataFrame Handling

**Error**: `AttributeError: 'NoneType' object has no attribute 'head'`

**Solutions**:
- Check if extraction returned None (error occurred)
- Handle errors with try/except
- Verify extraction succeeded before using DataFrame

**Example**:
```python
try:
    df, skipped = extract_data_from_html('page.html', config, category='gpu')
    if df is not None and len(df) > 0:
        print(df.head())
    else:
        print("No data extracted")
except Exception as e:
    print(f"Error: {e}")
```

**Error**: Column not found in DataFrame

**Solutions**:
- Check which columns were extracted: `print(df.columns.tolist())`
- Verify attribute names in config match expected column names
- Check if attribute is in category's `attribute_names` list
- Ensure attribute extraction succeeded

## Batch Processing Errors

**Error**: `ValueError: files_with_categories is empty`

**Solutions**:
- Ensure dictionary is not empty
- Check file paths exist
- Verify dictionary structure: `{'file.html': 'category'}`

**Error**: Processing fails for some files

**Solutions**:
- Check error messages in logs
- Process files individually to identify problematic files
- Use error handling to continue processing other files
- Check file encoding and validity

**Example**:
```python
from html_extract import batch_extract, load_config

config = load_config('config.yaml')
files_with_categories = {
    'file1.html': 'gpu',
    'file2.html': 'gpu'
}

try:
    df = batch_extract(files_with_categories, config)
except Exception as e:
    print(f"Batch processing error: {e}")
    # Process files individually to identify issue
    for file, category in files_with_categories.items():
        try:
            df = extract_data_from_html(file, config, category=category)
            print(f"Success: {file}")
        except Exception as e:
            print(f"Failed: {file} - {e}")
```

## Performance Issues

**Issue**: Processing is slow

**Solutions**:
- Use `max_workers` parameter for parallel processing
- Use `batch_extract()` instead of processing files individually
- Consider streaming to file for large batches
- Check if multiprocessing is working (CPU usage)

**Example**:
```python
# Use parallel processing
df = batch_extract(
    files_with_categories,
    config,
    max_workers=4,
    use_multiprocessing=True
)
```

**Issue**: Memory errors with large batches

**Solutions**:
- Use streaming to file instead of collecting in memory
- Process in smaller batches
- Use `stream_to_file` parameter

**Example**:
```python
# Stream results directly to file
df = batch_extract(
    files_with_categories,
    config,
    stream_to_file='output.csv',
    stream_mode='overwrite'
)
```

## Output Errors

**Error**: `OSError: Cannot write to output file`

**Solutions**:
- Ensure output directory exists
- Check write permissions for output directory
- Verify disk space is available
- Use absolute path for output file

**Error**: `ValueError: Format cannot be determined`

**Solutions**:
- Specify format explicitly: `save_output(df, 'output.txt', format='csv')`
- Use standard file extensions: `.csv` or `.json`
- Check output_path parameter is provided

## Getting Help

If you're still experiencing issues:

1. **Check the error messages** - They often contain helpful information
2. **Review examples** - See [Integration Examples](14-integration-examples.md) for working code
3. **Validate your config** - Use online validators to check YAML/JSON syntax
4. **Test incrementally** - Start with a simple config and add complexity gradually
5. **Inspect HTML** - Use browser dev tools to understand HTML structure
6. **Check logs** - Enable logging to see detailed error information

## See Also

- [API Reference](15-api-reference.md) - Complete function reference
- [Python API Guide](12-python-api-guide.md) - Complete guide to using the API
- [Integration Examples](14-integration-examples.md) - Working code examples
- [Configuration Reference](../shared/20-configuration-reference.md) - Config troubleshooting
