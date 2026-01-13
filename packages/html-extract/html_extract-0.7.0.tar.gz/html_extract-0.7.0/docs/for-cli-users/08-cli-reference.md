# CLI Reference

Complete documentation for the `html-extract` command-line tool.

## Command

```bash
html-extract [INPUT] [OPTIONS]
```

## Arguments

### Required (unless using `-t`)

- **`INPUT`** (positional) - Path to input source:
  - **HTML file** (`.html` extension) - process single file
  - **Directory** (folder) - process all `.html` files recursively
  - **CSV file** (`.csv` extension) - process files listed in CSV
  - **Note**: Not required when using `-t, --template` (creates template and exits)

- **`-c, --config PATH`** - Path to configuration file (YAML or JSON, required for processing files/directories/CSV)

### Optional

- **`-o, --output PATH`** - Output file path
  - If omitted: print to stdout
  - Format auto-detected from extension: `.csv` → CSV, `.json` → JSON
  - If no extension: defaults to CSV

- **`-d, --scrape_date DATE`** - Set scrape date for all processed files
  - **Date format**: YYYY-MM-DD (e.g., `2025-01-15`)
  - **Special value**: `current` or `today` - uses current date
  - **Priority**: Overrides CSV `scrape_date` column
  - **Behavior**: Applies globally to all files when processing folders or CSV bulk operations

- **`-k, --category CATEGORY`** - Specify category to use for extraction
  - **Required for**: Single HTML file processing (when config contains multiple categories)
  - **Optional for**: CSV file processing (used as default if CSV doesn't specify category per-row)
  - **Not used for**: Folder processing (category is automatically derived from folder path)
  - **Format**: Category name must exactly match one of the category names in the config file
  - **Examples**: `gpu`, `laptopy`, `domy/najem` (for nested categories)

- **`-t, --template TYPE PATH`** - Create new template file and exit
  - **TYPE**: `config` or `csv` - type of template to create
  - **PATH**: Output file path for the template
  - **config**: Creates config template (YAML or JSON format, based on file extension)
  - **csv**: Creates CSV template with headers: `path`, `config`, `scrape_date`, `category`
  - **Note**: Exits immediately after creating template (no processing performed)

- **`-p, --progress`** - Display progress bar during batch processing
  - Shows progress for directory and CSV bulk processing operations
  - Displays: current file, percentage complete, processing rate, failed file count
  - Automatically disabled when output is piped (non-interactive mode)

- **`--no-progress`** - Explicitly disable progress bar
  - Useful for non-interactive environments or when piping output
  - Overrides `-p, --progress` flag if both are specified

- **`--stream-mode MODE`** - Streaming mode for batch operations
  - **MODE**: `overwrite` (default) or `append`
  - Only used when `-o, --output` is provided for directory or CSV processing
  - **`overwrite`**: Create new file or replace existing file
  - **`append`**: Append results to existing file (maintains file format integrity)
  - Enables memory-efficient processing for large batches

- **`-h, --help`** - Display help message

## Behavior

### Date Handling Priority

Scrape date is determined in the following priority order (highest to lowest):

1. **`-d, --scrape_date` flag** - If provided, overrides all other sources
2. **CSV `scrape_date` column** - Per-row date from CSV (only for CSV bulk processing)
3. **Automatic extraction from path/filename** - Extracts date from file path or filename

When using `-d`, the same date applies to all files. When using CSV with `scrape_date` column, each row can have its own date.

### Category Handling Priority

Category selection follows different rules based on input type:

**For Single HTML Files**:
- **Required**: Category must be specified via `-k, --category` flag
- **Error**: If not specified and config contains multiple categories

**For CSV Files**:
Category is determined in the following priority order (highest to lowest):
1. **CSV `category` column** - Per-row category from CSV (if present)
2. **`-k, --category` flag** - Default category specified via CLI flag
3. **Error** - If neither CSV column nor flag is provided

**For Folders**:
- **Automatic**: Category is automatically derived from folder path
- **Derivation**: Tool matches folder names in path to category names in config
- **Example**: `data/gpu/2025/2025-01-15` → category: `gpu`
- **Nested categories**: `data/domy/najem/2025/2025-01-15` → category: `domy/najem`
- **Error**: If no matching category found in path

Category name must exactly match (case-sensitive) one of the category names defined in the config file's `categories` array.

### Input Auto-Detection

The tool automatically detects input type:

- **If path ends with `.html`**: treat as single HTML file
- **If path is a directory**: treat as folder, process all `.html` files recursively
- **If path ends with `.csv`**: treat as bulk CSV file with:
  - Standard comma-separated values with UTF-8-BOM encoding
  - Column headers: `path` (required), `config`, `scrape_date`, `category` (all optional)
  - Recognizes columns by name (any order)

### Output Format

- **Format auto-detection**: Detected from output file extension
  - `.csv` → CSV format (UTF-8-BOM encoding)
  - `.json` → JSON format (pretty-printed array of objects)
  - No extension → defaults to CSV
- **CSV**: Standard comma-separated values with UTF-8-BOM encoding
- **JSON**: Array of objects, one per extracted item
- **Stdout**: Same format as file output, printed to console (defaults to CSV if format cannot be determined)

## Examples

### Single File Processing

```bash
# Simplest usage - prints to stdout (category required if config has multiple categories)
html-extract page.html -c config.yaml -k gpu

# Single file with output
html-extract data/gpu/2025/2025-01-15/page_1.html -c config.yaml -k gpu -o output.csv

# With explicit scrape date and category
html-extract page.html -c config.yaml -k gpu -d 2025-01-15 -o output.csv

# Use current date
html-extract page.html -c config.yaml -k gpu -d current -o output.csv

# Nested category
html-extract page.html -c config.yaml -k "domy/najem" -o output.csv
```

### Folder Processing

```bash
# Process all HTML files in a folder
html-extract data/gpu/2025/2025-01-15 -c config.yaml -o output.csv
```

### Bulk Processing from CSV

```bash
# Process files listed in CSV (with per-row categories)
html-extract file_list.csv -c config.yaml -o combined.csv

# Process CSV with default category (used if CSV row doesn't specify category)
html-extract file_list.csv -c config.yaml -k gpu -o combined.csv
```

### Output Formats

```bash
# CSV output (auto-detected from extension)
html-extract page.html -c config.yaml -o output.csv

# JSON output (auto-detected from extension)
html-extract folder -c config.yaml -o output.json

# Print to stdout (defaults to CSV)
html-extract page.html -c config.yaml
```

### Template Creation

```bash
# Create YAML config template
html-extract -t config new_config.yaml

# Create JSON config template
html-extract -t config new_config.json

# Create CSV template
html-extract -t csv new_template.csv
```

### Advanced Examples

```bash
# Process folder with custom scrape date (category auto-derived from path)
html-extract data/gpu/2025/2025-01-15 \
    -c config.yaml \
    -d 2025-01-20 \
    -o output.csv

# Process directory with progress bar
html-extract data/gpu/2025/2025-01-15 -c config.yaml -p -o output.csv

# Process CSV with progress bar and streaming (memory-efficient)
html-extract file_list.csv -c config.yaml -p -o combined.csv --stream-mode overwrite

# Process directory with append mode (adds to existing file)
html-extract data/gpu/2025/2025-01-16 -c config.yaml -o combined.csv --stream-mode append

# Disable progress bar explicitly (useful for piped output)
html-extract data/gpu/2025/2025-01-15 -c config.yaml --no-progress -o output.csv
```

## Error Handling

The tool handles various error conditions:

### Invalid HTML

- **Behavior**: Skip file, log warning, continue processing
- **Output**: Other files still processed, error logged

### Missing Config

- **Behavior**: Raise error and exit
- **Solution**: Use `-c` flag to specify config file path

### Invalid Config YAML/JSON

- **Behavior**: Raise error with details
- **Solution**: Validate YAML/JSON syntax, check structure

### No Data Found

- **Behavior**: Return empty output (empty CSV/JSON array)
- **Possible Causes**: 
  - HTML doesn't contain the expected content structure
  - Selectors don't match HTML structure
  - Required attributes missing

### Invalid Output Path

- **Behavior**: Raise error and exit
- **Solution**: Ensure output directory exists and is writable

### File Not Found

- **Behavior**: Raise error and exit
- **Solution**: Verify input path is correct

## Usage Patterns

### Quick Single File Check

```bash
# Check extraction on a single file
html-extract test.html -c config.yaml -k gpu | head -20
```

### Process Daily Data

```bash
# Process all files for a specific date
html-extract data/gpu/2025/2025-01-15 -c config.yaml -o 2025-01-15.csv
```

### Batch Process Multiple Dates

```bash
# Create CSV template
html-extract -t csv batch_list.csv

# Edit batch_list.csv with all file paths
# Then process
html-extract batch_list.csv -c config.yaml -o all_dates.csv
```

## Tips and Best Practices

1. **Test on single files first** - Verify config works before batch processing
2. **Always specify config file** - Use `-c` flag to specify config file path
3. **Include scrape dates** - Use `-d` flag for consistent date tracking
4. **Create templates** - Use `-t` to generate starting points for configs and CSV lists
5. **Check output format** - Verify CSV/JSON output matches expectations
6. **Use CSV for complex workflows** - CSV input allows per-file config and date overrides
7. **Monitor stdout for errors** - Check console output for warnings and errors
8. **Validate YAML/JSON before processing** - Use validators to catch syntax errors early

## See Also

- [Common Tasks](common-tasks/) - Step-by-step guides for common workflows
- [Configuration Guide](07-configuration-guide.md) - Learn how to configure extraction rules
- [Troubleshooting](09-troubleshooting.md) - Common issues and solutions
- [Complete Configuration Reference](../shared/20-configuration-reference.md) - Full config documentation
