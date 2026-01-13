# CLI Quick Start

Get started with HTML Extract using the command line in 5 minutes.

## Installation

Install HTML Extract from PyPI:

```bash
pip install html-extract
```

Verify installation:

```bash
html-extract --help
```

## Your First Extraction

### Step 1: Create a Configuration File

Generate a configuration template:

```bash
html-extract -t config data/config.yaml
```

This creates `data/config.yaml` with example attributes.

### Step 2: Customize the Configuration

Edit `data/config.yaml` to match your HTML structure. At minimum, you'll need to define:

1. **Categories**: What type of content you're extracting
2. **Attributes**: What data to extract (e.g., title, price, link)

The tool automatically detects all items in your HTML file by finding all elements matching the first required attribute (typically the "link" attribute with a regex pattern). Each matching element's container becomes one item, and all configured attributes are extracted from that container.

See the [Configuration Guide](07-configuration-guide.md) for details, or the [Complete Configuration Reference](../shared/20-configuration-reference.md) for all options.

### Step 3: Extract Data

Process your HTML file:

```bash
html-extract data/page.html -c data/config.yaml -k gpu -o output.csv
```

Replace `gpu` with your category name from the config file.

### Step 4: View Results

Open `output.csv` to see your extracted data!

## Example: Extract Product Listings

Let's extract product listings from an HTML file.

### HTML Structure (Example)

```html
<div class="listing">
  <h4><a href="/d/oferta/product-123.html">Product Title</a></h4>
  <p data-testid="ad-price">1000 USD</p>
  <p data-testid="location-date">Warsaw - Posted today</p>
</div>
```

### Configuration (config.yaml)

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
  
  - name: location
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        data-testid: location-date
      extract_attribute: text
      processing:
        - split: " - "
        - index: 0
```

### Extract Data

```bash
html-extract data/page.html -c config.yaml -k products -o results.csv
```

### Output (results.csv)

```csv
link,title,price,location
/d/oferta/product-123.html,Product Title,1000,Warsaw
```

## Next Steps

Now that you've completed your first extraction, explore common tasks:

- **[Extract from Single File](common-tasks/03-extract-single-file.md)** - Detailed guide for single file processing
- **[Process Folder](common-tasks/04-process-folder.md)** - Process all files in a directory
- **[Batch with CSV](common-tasks/05-batch-with-csv.md)** - Process multiple files from a CSV list
- **[Generate Templates](common-tasks/06-generate-templates.md)** - Create config and CSV templates

For complete documentation:

- [Configuration Guide](07-configuration-guide.md) - Learn how to configure extraction rules
- [CLI Reference](08-cli-reference.md) - Complete command reference
- [Troubleshooting](09-troubleshooting.md) - Common issues and solutions

## Tips for Success

1. **Start Simple**: Begin with one or two attributes, then add more
2. **Test on Single Files**: Verify your config works before batch processing
3. **Use Browser Dev Tools**: Inspect HTML structure to find correct selectors
4. **Check Examples**: See [Shared Examples](../shared/examples/) for real-world scenarios
