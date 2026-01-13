# HTML Extract

A Python tool for extracting structured data from HTML files using declarative configuration files (YAML or JSON). No code required - define what to extract, how to find it, and how to process it, all in configuration files. Automatically detects and extracts all items from each HTML file.

## Features

- **Configuration-Driven**: Define extraction rules in YAML or JSON files
- **Multiple Extraction Types**: Text, regex, contains, and metadata extraction
- **Batch Processing**: Process single files, directories, or CSV lists
- **Multiprocessing**: Parallel processing for improved performance
- **Flexible Output**: CSV and JSON output formats
- **Dual Interface**: Python API and CLI with complete feature parity
- **Programmatic Configs**: Create configurations from Python dict objects

## Quick Start

### Installation

```bash
pip install html-extract
```

This installs the package with all features, including the `html-extract` CLI command.

### Basic Usage

1. **Create a configuration file**:
```bash
html-extract -t config data/config.yaml
```

2. **Customize the configuration** to match your HTML structure

3. **Extract data**:
```bash
html-extract data/page.html -c data/config.yaml -k category -o output.csv
```

## Choose Your Path

HTML Extract provides two interfaces - choose the one that fits your workflow:

### 🖥️ Using the Command Line?

If you prefer working with command-line tools, start here:

→ **[CLI Quick Start](docs/for-cli-users/01-quick-start.md)** - Get started in 5 minutes

**CLI Documentation:**
- [Installation](docs/for-cli-users/02-installation.md)
- [Common Tasks](docs/for-cli-users/common-tasks/)
  - [Extract from Single File](docs/for-cli-users/common-tasks/03-extract-single-file.md)
  - [Process Folder](docs/for-cli-users/common-tasks/04-process-folder.md)
  - [Batch with CSV](docs/for-cli-users/common-tasks/05-batch-with-csv.md)
  - [Generate Templates](docs/for-cli-users/common-tasks/06-generate-templates.md)
- [Configuration Guide](docs/for-cli-users/07-configuration-guide.md)
- [CLI Reference](docs/for-cli-users/08-cli-reference.md)
- [Troubleshooting](docs/for-cli-users/09-troubleshooting.md)

### 🐍 Using Python?

If you're building Python applications or scripts, start here:

→ **[Python Quick Start](docs/for-developers/10-quick-start.md)** - Get started in 5 minutes

**Python Documentation:**
- [Installation](docs/for-developers/11-installation.md)
- [Python API Guide](docs/for-developers/12-python-api-guide.md)
- [Programmatic Configs](docs/for-developers/13-programmatic-configs.md)
- [Integration Examples](docs/for-developers/14-integration-examples.md)
- [API Reference](docs/for-developers/15-api-reference.md)
- [Troubleshooting](docs/for-developers/16-troubleshooting.md)

### 📚 Shared Resources

Both CLI and Python users can access:

- [Configuration Reference](docs/shared/20-configuration-reference.md) - Complete config guide
- [Core Concepts](docs/shared/21-concepts.md) - Understanding how it works
- [Examples](docs/shared/examples/) - Real-world use cases
- [Logging Guide](docs/shared/22-logging.md) - Logging configuration

### 🚀 Advanced Topics

- [Performance Optimization](docs/advanced/30-performance.md)
- [Custom Processing](docs/advanced/31-custom-processing.md)
- [Best Practices](docs/advanced/32-best-practices.md)

## Example

Extract product listings from HTML:

```yaml
# config.yaml
categories:
  - name: products
    attribute_names: [link, title, price]

attributes:
  - name: link
    required: true
    extract:
      type: regex
      selector: a
      extract_attribute: href
      pattern: "/d/oferta/.*\\.html"
  
  - name: title
    required: true
    extract:
      type: text
      selector: h4
      extract_attribute: text
  
  - name: price
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        data-testid: ad-price
      extract_attribute: text
```

**Using CLI:**
```bash
html-extract data/page.html -c config.yaml -k products -o output.csv
```

**Using Python:**
```python
from html_extract import extract_data_from_html, load_config, save_output

config = load_config('config.yaml')
df = extract_data_from_html('page.html', config, category='products')
save_output(df, 'output.csv')
```

## Requirements

- Python 3.7+
- beautifulsoup4
- pandas
- pyyaml

## Development Status

⚠️ **Note**: This project was created with vibe coding and is still under heavy development. Features and APIs may change. Use with caution in production environments.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
