# Programmatic Config Creation

Create configurations from Python dict objects without needing configuration files.

## Overview

In addition to loading configs from files, you can create configurations programmatically from Python dict objects. This is useful when:

- Generating configs dynamically based on user input or data
- Loading configs from APIs or databases
- Creating configs in code without writing files
- Testing with different config variations

## Basic Example

Create a config from a dict object:

```python
from html_extract import load_config, extract_data_from_html, save_output

# Create config as Python dict
config_dict = {
    "categories": [
        {"name": "gpu", "attribute_names": ["link", "title", "price"]}
    ],
    "attributes": [
        {
            "name": "link",
            "required": True,
            "extract": {
                "type": "regex",
                "selector": "a",
                "extract_attribute": "href",
                "pattern": "/d/oferta/.*\\.html"
            }
        },
        {
            "name": "title",
            "required": True,
            "extract": {
                "type": "text",
                "selector": "h4",
                "extract_attribute": "text"
            }
        },
        {
            "name": "price",
            "required": False,
            "extract": {
                "type": "text",
                "selector": "p",
                "html_attributes": {"data-testid": "ad-price"},
                "extract_attribute": "text"
            }
        }
    ]
}

# Load config from dict (no file needed)
config = load_config(config_dict)

# Use config normally
df = extract_data_from_html('page.html', config, category='gpu')
save_output(df, 'output.csv')
```

## Loading from JSON String

Load config from a JSON string (e.g., from an API):

```python
import json
from html_extract import load_config

# JSON string from API, database, etc.
json_string = '{"categories": [...], "attributes": [...]}'

# Parse JSON and load config
config_dict = json.loads(json_string)
config = load_config(config_dict)
```

## Dynamic Config Generation

Generate configs dynamically based on parameters:

```python
from html_extract import load_config

def create_config(category_name, selectors):
    """Create a config dynamically based on parameters."""
    config_dict = {
        "categories": [
            {"name": category_name, "attribute_names": ["link", "title", "price"]}
        ],
        "attributes": [
            {
                "name": "link",
                "required": True,
                "extract": {
                    "type": "regex",
                    "selector": selectors.get("link_selector", "a"),
                    "extract_attribute": "href",
                    "pattern": selectors.get("link_pattern", "/d/oferta/.*\\.html")
                }
            },
            {
                "name": "title",
                "required": True,
                "extract": {
                    "type": "text",
                    "selector": selectors.get("title_selector", "h4"),
                    "extract_attribute": "text"
                }
            }
        ]
    }
    return load_config(config_dict)

# Use the function
selectors = {
    "link_selector": "a",
    "link_pattern": "/d/oferta/.*\\.html",
    "title_selector": "h4"
}
config = create_config("products", selectors)
```

## Processing Steps in Dict Format

When creating configs programmatically, processing steps are dictionaries:

```python
config_dict = {
    "categories": [{"name": "gpu", "attribute_names": ["title", "price"]}],
    "attributes": [
        {
            "name": "title",
            "required": True,
            "extract": {"type": "text", "selector": "h4", "extract_attribute": "text"},
            "processing": [
                {"strip": True}  # Strip whitespace
            ]
        },
        {
            "name": "price",
            "required": False,
            "extract": {"type": "text", "selector": ".price", "extract_attribute": "text"},
            "processing": [
                {"split": " USD"},
                {"index": 0},
                {"strip": True},
                {"replace": " ", "with": ""}
            ]
        }
    ]
}
```

## Important Notes

- The dict structure must match the YAML/JSON file structure exactly
- All validation rules apply the same way as file-based configs
- The `load_config()` function automatically detects input type (file path vs dict)
- For file paths, use: `load_config('config.yaml')` or `load_config('config.json')`
- For dict objects, use: `load_config(config_dict)`
- No file I/O is performed when loading from dict objects

## Use Cases

### Testing Different Configurations

```python
def test_config(config_dict):
    """Test a configuration without creating a file."""
    config = load_config(config_dict)
    df = extract_data_from_html('test.html', config, category='gpu')
    return len(df) > 0

# Test multiple configs
config1 = {...}
config2 = {...}
print(f"Config 1 works: {test_config(config1)}")
print(f"Config 2 works: {test_config(config2)}")
```

### Loading from Database

```python
import sqlite3
from html_extract import load_config

# Load config from database
conn = sqlite3.connect('configs.db')
cursor = conn.cursor()
cursor.execute("SELECT config_json FROM configs WHERE name = ?", ('gpu',))
result = cursor.fetchone()

if result:
    config_dict = json.loads(result[0])
    config = load_config(config_dict)
```

## See Also

- [Python API Guide](12-python-api-guide.md) - Learn all API functions
- [API Reference](15-api-reference.md) - Complete function reference
- [Configuration Reference](../shared/20-configuration-reference.md) - Full config documentation
