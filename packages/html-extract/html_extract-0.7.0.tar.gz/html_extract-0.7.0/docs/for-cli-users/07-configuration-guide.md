# Configuration Guide

Learn how to create and customize configuration files for HTML Extract.

## Overview

Configuration files define what data to extract from HTML files. They use YAML or JSON format and specify:

- **Categories**: Types of content to extract
- **Attributes**: What data to extract (e.g., title, price, link)
- **Extraction Rules**: How to find and extract each attribute

## Quick Start

### Generate a Template

Create a configuration template to get started:

```bash
html-extract -t config data/config.yaml
```

This creates a template with example attributes that you can customize.

### Basic Structure

A configuration file has two main sections:

```yaml
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
```

## Categories

Categories define types of content. Each category has:

- **name**: Category identifier (e.g., `gpu`, `products`)
- **attribute_names**: List of attributes to extract for this category

```yaml
categories:
  - name: products
    attribute_names: [link, title, price, location]
```

## Attributes

Attributes define what data to extract. Each attribute specifies:

- **name**: Column name in output
- **required**: Whether item is skipped if this attribute is missing
- **extract**: How to find and extract the data

### Extraction Types

**Text Extraction** - Extract text or attribute values:

```yaml
- name: title
  extract:
    type: text
    selector: h4
    extract_attribute: text
```

**Regex Extraction** - Find elements using patterns:

```yaml
- name: link
  extract:
    type: regex
    selector: a
    extract_attribute: href
    pattern: "/d/oferta/.*\\.html"
```

**Contains Extraction** - Check if value contains text:

```yaml
- name: negotiable
  extract:
    type: contains
    depends_on: price
    check: "negotiable"
```

**Metadata Extraction** - Extract file information:

```yaml
- name: source_file
  extract:
    type: metadata
```

## Processing Steps

Process extracted values to clean and transform data:

```yaml
- name: price
  extract:
    type: text
    selector: p
    extract_attribute: text
  processing:
    - split: " USD"
    - index: 0
    - strip: true
```

Common processing steps:
- **split**: Split string by separator
- **index**: Get element at index after split
- **strip**: Remove whitespace
- **replace**: Replace text or use variables

## File Formats

### YAML Format

YAML files (`.yaml` or `.yml`) support comments and are easier to read:

```yaml
categories:
  - name: products
    attribute_names: [link, title, price]  # Required attributes

attributes:
  - name: link
    required: true
    extract:
      type: regex
      selector: a
      extract_attribute: href
```

### JSON Format

JSON files (`.json`) use the same structure without comments:

```json
{
  "categories": [
    {"name": "products", "attribute_names": ["link", "title", "price"]}
  ],
  "attributes": [
    {
      "name": "link",
      "required": true,
      "extract": {
        "type": "regex",
        "selector": "a",
        "extract_attribute": "href"
      }
    }
  ]
}
```

## Common Patterns

### Extract Link and Title

```yaml
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
```

### Extract Price with Processing

```yaml
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
    - strip: true
```

### Extract Location from Combined Field

```yaml
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
    - strip: true
```

## Tips

1. **Start Simple**: Begin with one or two attributes, then add more
2. **Test Selectors**: Use browser dev tools to verify selectors match your HTML
3. **Mark Required**: Use `required: true` for critical attributes (like `link` and `title`)
4. **Use Fallbacks**: Add `fallback_selector` to handle HTML structure changes
5. **Test Incrementally**: Test your config on a single file before batch processing

## Next Steps

- **[Complete Configuration Reference](../shared/20-configuration-reference.md)** - Full documentation of all options
- **[Common Tasks](common-tasks/)** - See configuration in action
- **[Examples](../shared/examples/)** - Real-world configuration examples
