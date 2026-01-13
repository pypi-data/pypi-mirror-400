# Troubleshooting

Common issues and solutions when using HTML Extract from the command line.

## Config File Not Found

**Error**: `Config file not found`

**Solutions**:
- Ensure a configuration file (`.yaml`, `.yml`, or `.json`) exists
- Use `-c` flag to specify config file path explicitly
- Check file permissions
- Verify the path is correct (use absolute path if needed)

**Example**:
```bash
# Specify explicit path
html-extract page.html -c /full/path/to/config.yaml -k category -o output.csv
```

## No Data Extracted

**Error**: Empty output or no data extracted

**Possible Causes**:
- HTML doesn't contain the expected content structure
- Selectors in config don't match HTML structure
- Required attributes are missing from HTML

**Solutions**:
- Inspect HTML file structure using browser dev tools
- Test selectors in browser dev tools
- Check config attribute definitions
- Verify HTML file contains the expected content
- Try extracting with a simpler config first

**Example**:
```bash
# Test with minimal config first
html-extract page.html -c simple_config.yaml -k category
```

## Category Error

**Error**: `Category 'X' not found in config` or `Category must be specified`

**Solutions**:
- Ensure category name matches exactly (case-sensitive)
- Check category exists in config file's `categories` array
- For single file processing, use `-k` flag to specify category
- For folder processing, ensure folder name matches a category in config

**Example**:
```bash
# Specify category explicitly
html-extract page.html -c config.yaml -k gpu -o output.csv
```

## Invalid YAML/JSON

**Error**: `Error parsing YAML config` or `Error parsing JSON config`

**Solutions**:
- Validate YAML/JSON syntax using an online validator
- Check for indentation errors (YAML is sensitive to spacing)
- Ensure all required fields are present
- Check for special characters that need escaping
- Verify file encoding is UTF-8

**Tools**:
- YAML: https://www.yamllint.com/
- JSON: https://jsonlint.com/

## Date Extraction Issues

**Error**: Date not extracted correctly or `Date not found`

**Solutions**:
- Ensure date folders follow YYYY-MM-DD format
- Use `-d` flag to explicitly set scrape date
- Check CSV `scrape_date` column format (YYYY-MM-DD)
- Verify file path contains date information

**Example**:
```bash
# Set explicit date
html-extract page.html -c config.yaml -k category -d 2025-01-15 -o output.csv
```

## File Not Found

**Error**: `File not found` or `FileNotFoundError`

**Solutions**:
- Verify input path is correct
- Use absolute paths if relative paths don't work
- Check file permissions
- Ensure file exists before processing

**Example**:
```bash
# Use absolute path
html-extract /full/path/to/page.html -c config.yaml -k category -o output.csv
```

## Invalid Output Path

**Error**: `Cannot write to output file` or `Permission denied`

**Solutions**:
- Ensure output directory exists
- Check write permissions for output directory
- Verify disk space is available
- Use absolute path for output file

**Example**:
```bash
# Create output directory first
mkdir -p output
html-extract page.html -c config.yaml -k category -o output/results.csv
```

## Processing Errors

**Error**: Processing fails with exception

**Solutions**:
- Check error messages for specific issues
- Verify HTML file is valid
- Test with single file first
- Review config file syntax
- Check file encoding (should be UTF-8)

## Empty Results

**Warning**: `Empty result: <file> - No items found`

**Possible Causes**:
- HTML structure doesn't match config selectors
- Required attributes not found in HTML
- Config selectors are too specific

**Solutions**:
- Inspect HTML structure
- Test selectors in browser dev tools
- Make selectors more flexible
- Check if HTML structure has changed
- Verify config matches actual HTML

## Progress Bar Issues

**Issue**: Progress bar not showing or interfering with output

**Solutions**:
- Use `-p` flag to enable progress bar
- Use `--no-progress` to disable progress bar
- Progress bar is automatically disabled when output is piped

**Example**:
```bash
# Enable progress bar
html-extract folder -c config.yaml -p -o output.csv

# Disable progress bar
html-extract folder -c config.yaml --no-progress -o output.csv
```

## CSV Processing Issues

**Error**: CSV processing fails

**Possible Causes**:
- Missing `path` column in CSV
- File paths in CSV don't exist
- Invalid CSV format
- Encoding issues

**Solutions**:
- Ensure CSV has `path` column (required)
- Verify all file paths in CSV exist
- Check CSV encoding (should be UTF-8-BOM)
- Validate CSV format

**Example**:
```bash
# Create CSV template first
html-extract -t csv file_list.csv
# Then edit and use
html-extract file_list.csv -c config.yaml -o output.csv
```

## Getting Help

If you're still experiencing issues:

1. **Check the logs** - Error messages often contain helpful information
2. **Review examples** - See [Shared Examples](../shared/examples/) for working configurations
3. **Validate your config** - Use online validators to check YAML/JSON syntax
4. **Test incrementally** - Start with a simple config and add complexity gradually
5. **Inspect HTML** - Use browser dev tools to understand HTML structure

## See Also

- [CLI Reference](08-cli-reference.md) - Complete command reference
- [Configuration Guide](07-configuration-guide.md) - Configuration troubleshooting
- [Common Tasks](common-tasks/) - Step-by-step guides
- [Complete Configuration Reference](../shared/20-configuration-reference.md) - Full config documentation
