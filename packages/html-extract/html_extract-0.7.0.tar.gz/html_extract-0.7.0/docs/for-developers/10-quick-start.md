# Python Quick Start

Get started with HTML Extract using the Python API in 5 minutes.

## Installation

Install HTML Extract from PyPI:

```bash
pip install html-extract
```

Verify installation:

```python
from html_extract import extract_data_from_html, load_config
print("HTML Extract installed successfully!")
```

## Your First Extraction

### Step 1: Load Configuration

Load a configuration file:

```python
from html_extract import load_config

config = load_config('data/config.yaml')
```

### Step 2: Extract Data

Extract data from an HTML file:

```python
from html_extract import extract_data_from_html, save_output

df, skipped_count = extract_data_from_html(
    'data/page.html',
    config,
    category='products'
)

print(f"Extracted {len(df)} items")
print(f"Skipped {skipped_count} items due to missing required attributes")
```

### Step 3: Save Results

Save extracted data to a file:

```python
from html_extract import save_output

save_output(df, 'output.csv')
# Or save as JSON
save_output(df, 'output.json')
```

## Complete Example

```python
from html_extract import (
    extract_data_from_html,
    load_config,
    save_output
)

# Load configuration
config = load_config('data/config.yaml')

# Extract data from HTML file
df, skipped = extract_data_from_html(
    'data/page.html',
    config,
    category='products'
)

# View results
print(df.head())
print(f"Found {len(df)} items")

# Save output
save_output(df, 'results.csv')
```

## Example: Extract Product Listings

Here's a complete example extracting product listings:

```python
from html_extract import extract_data_from_html, load_config, save_output

# Load config
config = load_config('config.yaml')

# Extract data
df, skipped = extract_data_from_html(
    'data/products/page.html',
    config,
    category='products'
)

# Process the DataFrame
print(f"Extracted {len(df)} products")
print(df[['title', 'price', 'location']].head())

# Save results
save_output(df, 'products.csv')
```

**Configuration (config.yaml)**:

```yaml
categories:
  - name: products
    attribute_names: [link, title, price, location]

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
      processing:
        - split: " USD"
        - index: 0
```

## Next Steps

Now that you've completed your first extraction, explore more:

- **[Python API Guide](12-python-api-guide.md)** - Complete guide to all API functions
- **[Programmatic Configs](13-programmatic-configs.md)** - Create configs from Python dicts
- **[Integration Examples](14-integration-examples.md)** - Integrate with Pandas and other tools
- **[API Reference](15-api-reference.md)** - Complete function reference

## Key Functions

- `load_config()` - Load configuration from file or dict
- `extract_data_from_html()` - Extract data from single HTML file
- `process_directory()` - Process all files in a directory
- `process_csv()` - Process files from CSV list
- `save_output()` - Save DataFrame to CSV or JSON

See the [API Reference](15-api-reference.md) for complete documentation.
