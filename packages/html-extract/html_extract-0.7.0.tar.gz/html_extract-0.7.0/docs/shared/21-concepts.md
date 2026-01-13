# Core Concepts

Understanding how HTML Extract works and the key concepts you'll work with.

## What It Does

HTML Extract reads HTML files and extracts structured data based on configuration files. You define what to extract (attributes), how to find it (selectors), and how to process it (transformations) - all in configuration files, without writing code. The tool automatically detects and extracts all items from each HTML file, returning one row per item found.

## Categories

**Categories** represent types of content to extract (e.g., products, articles, listings). Each category has:

- A unique name
- A download URL for scraping (optional, for reference)
- A list of attributes to extract

Categories can be nested (e.g., `electronics/computers` for computer products).

**Example**:
```yaml
categories:
  - name: products
    attribute_names: [link, title, price]
  - name: electronics/computers
    attribute_names: [link, title, price, specs]
```

## Attributes

**Attributes** define what data to extract from each item. They are configured in the config file and specify:

- Column name in the output
- How to find the data in HTML (selectors, patterns)
- How to process the extracted value (split, strip, replace, etc.)
- Whether the attribute is required or optional
- Dependencies on other attributes

**Example**:
```yaml
attributes:
  - name: title
    required: true
    extract:
      type: text
      selector: h4
      extract_attribute: text
```

## Extraction Types

The tool supports multiple extraction types:

- **`text`**: Extract text or attribute values from HTML elements
- **`regex`**: Find elements using regular expression patterns
- **`contains`**: Check if a value contains a specific string (for derived columns)
- **`metadata`**: Extract metadata from file context (not from HTML)

## Terminology

Throughout this documentation, the following terms are used consistently:

- **Config file**: A YAML (`.yaml`/`.yml`) or JSON (`.json`) file containing extraction rules
- **Config source**: Either a config file path (str) or a config dictionary (dict) for programmatic creation
- **Configuration**: The extraction rules defined in a config file or dict object

When you see references to "configuration" or "config file" in this documentation, they refer to these definitions unless otherwise specified.

## Configuration-Driven

All extraction logic is defined in configuration files (YAML or JSON) or created programmatically, making it:

- **Flexible**: Easy to add new attributes or modify extraction rules
- **Maintainable**: Changes don't require code modifications
- **Reusable**: Same extraction logic can be applied to multiple categories
- **Documented**: Configuration serves as documentation
- **Programmatic**: Configs can be created from dict/JSON objects in code, not just from files

## How It Works

### Item Detection

The tool uses the first required attribute with a regex pattern (typically the "link" attribute) to find all matching elements on the page. For each matching element, it identifies the containing element (parent or ancestor) and extracts all configured attributes from that container. This allows extraction of multiple items from a single HTML file, with each item becoming one row in the output.

### Data Flow

1. **Load Configuration**: Read config file or use dict object
2. **Find Items**: Locate all item containers in HTML using the first required attribute
3. **Extract Attributes**: For each item, extract all configured attributes
4. **Process Values**: Apply processing steps (split, strip, replace, etc.)
5. **Return Results**: Return DataFrame with one row per item

### Processing Steps

Processing steps transform extracted values:

- **split**: Split string by separator(s)
- **index**: Get element at index after split
- **strip**: Remove whitespace or specified characters
- **replace**: Replace text or use variables
- **mapping**: Map values to different output values

## Data Organization

The tool expects data to be organized in a directory structure. While the exact structure is flexible, a common pattern is:

```
{base_dir}/
├── {config_file}
└── {category}/
    └── {year}/
        └── {date}/
            ├── page_1.html
            ├── page_2.html
            └── {extract_file}
```

**Key Points**:
- **Config file**: YAML or JSON configuration defines extraction rules
- **Category folders**: Organize content by type
- **Date folders**: Organize by date (YYYY-MM-DD format) for time-series data
- **HTML files**: Source files containing the content to extract
- **Extract files**: Output files (CSV/JSON) with extracted data

## Key Features

1. **Flexible Configuration**: Define extraction rules declaratively in YAML/JSON files or create configs programmatically
2. **Multiple Extraction Types**: Support for text, regex, contains, and metadata extraction
3. **Data Processing**: Built-in processing steps (split, index, strip, replace, mapping)
4. **Batch Processing**: Process multiple files, folders, or CSV lists
5. **Multiprocessing**: Parallel processing for improved performance
6. **Metadata Tracking**: Automatic extraction of source file, date, and path information
7. **Flexible Output**: Support for CSV and JSON output formats
8. **Dual Interface**: Both command-line interface and Python API with complete feature parity

## See Also

- [Configuration Reference](20-configuration-reference.md) - Complete config documentation
- [Examples](examples/) - Real-world use cases
- [CLI Quick Start](../for-cli-users/01-quick-start.md) - Get started with CLI
- [Python Quick Start](../for-developers/10-quick-start.md) - Get started with Python
