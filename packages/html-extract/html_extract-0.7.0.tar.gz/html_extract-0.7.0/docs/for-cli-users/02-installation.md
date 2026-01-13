# Installation

Install HTML Extract to start extracting data from HTML files.

## Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

## Install from PyPI

Install the package:

```bash
pip install html-extract
```

This installs the package with all features, including the `html-extract` CLI command.

## Verify Installation

Check that the installation was successful:

```bash
html-extract --help
```

You should see the help message with available commands and options.

## Dependencies

The following packages are automatically installed with html-extract:

- `beautifulsoup4` - HTML parsing
- `pandas` - Data manipulation and CSV/JSON output
- `pyyaml` - YAML configuration file parsing

**Note**: JSON config file support uses Python standard library (`json` module), no additional dependency needed.

## Next Steps

After installation, proceed to:

- [Quick Start](01-quick-start.md) - Get started in 5 minutes
- [Common Tasks](common-tasks/) - Learn common workflows
