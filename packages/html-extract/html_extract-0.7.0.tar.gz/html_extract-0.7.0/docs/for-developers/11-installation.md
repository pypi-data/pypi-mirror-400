# Installation

Install HTML Extract to start extracting data from HTML files using Python.

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Install from PyPI

Install the package:

```bash
pip install html-extract
```

This installs the package with all features.

## Verify Installation

Check that the installation was successful:

```python
from html_extract import extract_data_from_html, load_config
print("HTML Extract installed successfully!")
```

Test the import:

```python
import html_extract
print(html_extract.__version__)
```

## Dependencies

The following packages are automatically installed with html-extract:

- `beautifulsoup4` - HTML parsing
- `pandas` - Data manipulation and DataFrame operations
- `pyyaml` - YAML configuration file parsing

**Note**: JSON config file support uses Python standard library (`json` module), no additional dependency needed.

## Import Functions

Import the functions you need:

```python
# Import main functions
from html_extract import (
    extract_data_from_html,
    load_config,
    save_output,
    process_directory,
    process_csv
)

# Or import from specific modules
from html_extract.extract import extract_data_from_html
from html_extract.config import load_config
from html_extract.output import save_output
```

## Next Steps

After installation, proceed to:

- [Quick Start](10-quick-start.md) - Get started in 5 minutes
- [Python API Guide](12-python-api-guide.md) - Learn all API functions
- [API Reference](15-api-reference.md) - Complete function reference
