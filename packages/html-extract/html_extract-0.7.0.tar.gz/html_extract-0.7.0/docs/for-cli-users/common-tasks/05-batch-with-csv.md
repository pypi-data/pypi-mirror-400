# Batch Processing with CSV

Process multiple files listed in a CSV file using the command line.

## Overview

CSV batch processing allows you to:
- Process multiple files with different configs
- Set different scrape dates per file
- Use different categories per file
- Combine results into a single output

## Step 1: Create CSV Template

Generate a CSV template:

```bash
html-extract -t csv file_list.csv
```

This creates `file_list.csv` with the required columns.

## Step 2: Edit the CSV

Edit `file_list.csv` with your file paths:

```csv
path,config,scrape_date,category
data/gpu/2025/2025-01-15/page_1.html,data/config.yaml,2025-01-15,gpu
data/gpu/2025/2025-01-15/page_2.html,data/config.yaml,2025-01-15,gpu
data/gpu/2025/2025-01-16/page_1.html,data/config.yaml,2025-01-16,gpu
data/laptopy/2025/2025-01-15/page_1.html,data/config.yaml,2025-01-15,laptopy
```

### CSV Columns

- **`path`** (required): Path to HTML file
- **`config`** (optional): Path to config file for this row (overrides default)
- **`scrape_date`** (optional): Scrape date in YYYY-MM-DD format (overrides default)
- **`category`** (optional): Category name for this row (overrides default)

## Step 3: Process the CSV

Process all files listed in the CSV:

```bash
html-extract file_list.csv -c config.yaml -o combined_output.csv
```

### With Default Category

If your CSV doesn't specify categories per row, provide a default:

```bash
html-extract file_list.csv -c config.yaml -k gpu -o combined_output.csv
```

The default category is used for rows that don't specify a category.

## CSV Examples

### Simple CSV (Default Config and Category)

```csv
path
data/gpu/2025/2025-01-15/page_1.html
data/gpu/2025/2025-01-15/page_2.html
data/gpu/2025/2025-01-16/page_1.html
```

Process with:

```bash
html-extract file_list.csv -c config.yaml -k gpu -o output.csv
```

### CSV with Per-Row Categories

```csv
path,config,scrape_date,category
data/gpu/2025/2025-01-15/page_1.html,data/config.yaml,2025-01-15,gpu
data/laptopy/2025/2025-01-15/page_1.html,data/config.yaml,2025-01-15,laptopy
data/domy/2025/2025-01-15/page_1.html,data/config.yaml,2025-01-15,domy/najem
```

Process with:

```bash
html-extract file_list.csv -c config.yaml -o output.csv
```

### CSV with Per-Row Configs

```csv
path,config,scrape_date,category
data/gpu/2025/2025-01-15/page_1.html,data/gpu/config.yaml,2025-01-15,gpu
data/laptopy/2025/2025-01-15/page_1.html,data/laptopy/config.yaml,2025-01-15,laptopy
```

Each row can use a different config file.

## Priority Rules

When processing CSV files, values are determined in this priority:

1. **Per-row values** (from CSV columns) - highest priority
2. **Default values** (from CLI flags) - used if CSV row doesn't specify
3. **Automatic extraction** - dates extracted from paths if not specified

## Output

All extracted items from all files listed in the CSV are combined into a single output file. Each row represents one item from one HTML file.

## Examples

### Process Multiple Dates

```bash
# Create CSV with files from multiple dates
html-extract -t csv dates_list.csv

# Edit dates_list.csv, then process
html-extract dates_list.csv -c config.yaml -k gpu -o all_dates.csv
```

### Process Multiple Categories

```bash
# CSV with different categories per row
html-extract file_list.csv -c config.yaml -o all_categories.csv
```

## Next Steps

- [Extract from Single File](03-extract-single-file.md) - Process individual files
- [Process Folder](04-process-folder.md) - Process directories
- [Generate Templates](06-generate-templates.md) - Create CSV templates
