# Process Folder

Process all HTML files in a directory using the command line.

## Basic Usage

Process all HTML files in a folder:

```bash
html-extract data/gpu/2025/2025-01-15 -c config.yaml -o combined.csv
```

The tool automatically:
- Finds all `.html` files recursively in the directory
- Combines all extracted items into a single output file
- Derives the category from the folder path

## Category Auto-Detection

When processing a folder, the category is automatically derived from the folder path:

```bash
# Category automatically extracted: data/gpu/2025/2025-01-15 → category: gpu
html-extract data/gpu/2025/2025-01-15 -c config.yaml -o output.csv

# Nested category: data/domy/najem/2025/2025-01-15 → category: domy/najem
html-extract data/domy/najem/2025/2025-01-15 -c config.yaml -o output.csv
```

The tool matches folder names in the path to category names in your config file.

## Set Scrape Date for All Files

Override date extraction for all files in the folder:

```bash
html-extract data/gpu/2025/2025-01-15 \
    -c config.yaml \
    -d 2025-01-20 \
    -o output.csv
```

Use the current date:

```bash
html-extract data/gpu/2025/2025-01-15 \
    -c config.yaml \
    -d current \
    -o output.csv
```

## Output

All extracted items from all HTML files in the folder are combined into a single output file. Each row represents one item from one HTML file.

## Examples

### Process Date Folder

```bash
html-extract data/gpu/2025/2025-01-15 -c config.yaml -o gpu_2025-01-15.csv
```

### Process with Custom Date

```bash
html-extract data/gpu/2025/2025-01-15 \
    -c config.yaml \
    -d 2025-01-20 \
    -o output.csv
```

### Process Nested Category

```bash
html-extract data/domy/najem/2025/2025-01-15 \
    -c config.yaml \
    -o rentals_2025-01-15.csv
```

## Directory Structure

The tool expects a directory structure like:

```
data/
├── config.yaml
├── gpu/
│   └── 2025/
│       └── 2025-01-15/
│           ├── page_1.html
│           └── page_2.html
```

The category name (`gpu`) should match a category in your config file.

## Next Steps

- [Extract from Single File](03-extract-single-file.md) - Process individual files
- [Batch with CSV](05-batch-with-csv.md) - Process files from a CSV list
- [Configuration Guide](../07-configuration-guide.md) - Learn about configuration
