# Extract from Single File

Extract data from a single HTML file using the command line.

## Basic Usage

The simplest command extracts data and prints to stdout:

```bash
html-extract page.html -c config.yaml -k category
```

Replace `category` with your category name from the config file.

## Save to File

Save extracted data to a CSV file:

```bash
html-extract page.html -c config.yaml -k category -o output.csv
```

Save to JSON format:

```bash
html-extract page.html -c config.yaml -k category -o output.json
```

## Common Options

### Specify Configuration File

Use the `-c` flag to specify your configuration file:

```bash
html-extract page.html -c data/config.yaml -k category -o output.csv
```

### Set Scrape Date

Override the automatic date extraction with an explicit date:

```bash
html-extract page.html -c config.yaml -k category -d 2025-01-15 -o output.csv
```

Use the current date:

```bash
html-extract page.html -c config.yaml -k category -d current -o output.csv
```

### Specify Category

When your config has multiple categories, you must specify which one to use:

```bash
html-extract page.html -c config.yaml -k gpu -o output.csv
```

For nested categories, use the full path:

```bash
html-extract page.html -c config.yaml -k "domy/najem" -o output.csv
```

## Output Formats

The output format is automatically detected from the file extension:

- `.csv` → CSV format (UTF-8-BOM encoding for Excel compatibility)
- `.json` → JSON format (pretty-printed array of objects)
- No extension → defaults to CSV

## Examples

### Basic Extraction

```bash
html-extract data/products/page.html -c config.yaml -k products -o results.csv
```

### With Explicit Date

```bash
html-extract data/products/page.html \
    -c config.yaml \
    -k products \
    -d 2025-01-15 \
    -o results.csv
```

### Print to Console

```bash
html-extract data/products/page.html -c config.yaml -k products
```

## What Gets Extracted

The tool automatically:

1. Finds all item containers in the HTML file
2. Extracts all configured attributes for each item
3. Creates one row per item in the output
4. Skips items with missing required attributes

## Next Steps

- [Process Folder](04-process-folder.md) - Process multiple files in a directory
- [Batch with CSV](05-batch-with-csv.md) - Process files from a CSV list
- [Configuration Guide](../07-configuration-guide.md) - Learn about configuration options
