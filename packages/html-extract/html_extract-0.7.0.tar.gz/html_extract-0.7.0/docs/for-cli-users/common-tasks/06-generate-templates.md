# Generate Templates

Create configuration and CSV templates to get started quickly.

## Configuration Templates

Generate a configuration template file to start defining your extraction rules.

### Create YAML Config Template

```bash
html-extract -t config data/config.yaml
```

This creates a YAML configuration file with example attributes.

### Create JSON Config Template

```bash
html-extract -t config data/config.json
```

This creates a JSON configuration file with the same structure (JSON doesn't support comments).

### Template Contents

The generated template includes:

- Basic structure: `categories` and `attributes` sections
- Example category: `gpu` with common attribute names
- Example attributes demonstrating:
  - Required vs optional attributes
  - Text extraction with processing steps
  - Regex extraction with pattern matching
  - Common processing operations

### Customize the Template

After generating the template:

1. Edit the category name to match your content type
2. Modify attribute names to match what you want to extract
3. Adjust selectors to match your HTML structure
4. Add or remove attributes as needed

See the [Configuration Guide](../07-configuration-guide.md) for detailed instructions.

## CSV Templates

Generate a CSV template for batch processing multiple files.

### Create CSV Template

```bash
html-extract -t csv file_list.csv
```

This creates a CSV file with the required columns.

### Template Structure

The generated CSV includes:

- Header row: `path`, `config`, `scrape_date`, `category`
- Example row showing the format
- UTF-8-BOM encoding

### Fill in the CSV

After generating the template:

1. Add file paths to the `path` column
2. Optionally specify `config` for per-row config files
3. Optionally specify `scrape_date` for per-row dates
4. Optionally specify `category` for per-row categories

See [Batch with CSV](05-batch-with-csv.md) for detailed instructions.

## Examples

### Generate Config Template

```bash
# Create YAML template
html-extract -t config data/my_config.yaml

# Create JSON template
html-extract -t config data/my_config.json
```

### Generate CSV Template

```bash
# Create CSV template
html-extract -t csv batch_files.csv
```

## Next Steps

- [Configuration Guide](../07-configuration-guide.md) - Learn how to configure extraction rules
- [Batch with CSV](05-batch-with-csv.md) - Use CSV templates for batch processing
- [Quick Start](../01-quick-start.md) - Complete walkthrough
