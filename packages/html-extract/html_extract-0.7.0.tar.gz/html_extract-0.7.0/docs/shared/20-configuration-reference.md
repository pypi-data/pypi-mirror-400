# Configuration Reference

Complete reference guide for YAML configuration files used by the HTML Extract tool.

## File Format

- **Format**: YAML (`.yaml` or `.yml` extension) or JSON (`.json` extension)
- **Encoding**: UTF-8
- **Location**: Placed in the base directory (same level as category folders, e.g., `data/config.yaml`)
- **Programmatic Creation**: Configs can also be created programmatically from dict objects (see [Programmatic Configuration](#programmatic-configuration) section)

**Important Syntax Convention**:
- **Strings**: Always use quotes in YAML/JSON (e.g., `"text with spaces"`). This makes spaces and special characters clearly visible.
- **Variables**: Use `$` prefix without quotes (e.g., `$scrape_date`). The `$` prefix clearly identifies variables in processing steps.

## File Format Support

The tool supports both YAML and JSON file formats. The format is automatically detected from the file extension:
- `.yaml` or `.yml` → YAML format
- `.json` → JSON format

Both formats use the same structure and produce identical results. Choose the format that best fits your workflow.

**YAML Example** (`config.yaml`):
```yaml
categories:
  - name: gpu
    attribute_names: [link, title, price]
attributes:
  - name: link
    required: true
    extract:
      type: regex
      selector: a
      extract_attribute: href
```

**JSON Example** (`config.json`):
```json
{
  "categories": [
    {"name": "gpu", "attribute_names": ["link", "title", "price"]}
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

## Programmatic Configuration

In addition to loading configs from files, you can create configurations programmatically from Python dict objects. This is useful when:
- Generating configs dynamically based on user input or data
- Loading configs from APIs or databases
- Creating configs in code without writing files
- Testing with different config variations

**Using `load_config()` with Dict Objects**:

```python
from html_extract.config import load_config

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
        }
    ]
}

# Load config from dict (no file needed)
config = load_config(config_dict)

# Use config normally
from html_extract.extract import extract_data_from_html
df = extract_data_from_html('page.html', config, category='gpu')
```

**Loading from JSON String**:

```python
import json
from html_extract.config import load_config

# JSON string from API, database, etc.
json_string = '{"categories": [...], "attributes": [...]}'

# Parse JSON and load config
config_dict = json.loads(json_string)
config = load_config(config_dict)
```

**Important Notes**:
- The dict structure must match the YAML/JSON file structure exactly (same keys, same nesting)
- All validation rules apply the same way as file-based configs
- The `load_config()` function automatically detects input type (file path vs dict)
- For file paths, use: `load_config('config.yaml')` or `load_config('config.json')`
- For dict objects, use: `load_config(config_dict)`

## Top-Level Structure

The config file (or dict object) supports multiple categories with common attributes. It has two main sections:

```yaml
categories:
  attribute_names:          # Common attributes inherited by all categories
    - link
    - title
    - price
    - source_file
  categories:                # Category list (can also be array items in YAML)
    - name: <category_name>
      attribute_names:       # Category-specific additions
        - <name>
attributes:
  - name: title
    required: true
    extract: <extract configuration>
```

### Top-Level Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `categories` | dict | Yes | Dictionary with `attribute_names` key for common attributes and category list. Each category can have its own name, description, download URL, and list of attribute names to use |
| `attributes` | array | Yes | List of common attribute configurations for data extraction. These attributes are shared across all categories |

## Common Attributes Inheritance

Categories can inherit common attributes defined at the `categories` level. This reduces duplication when multiple categories share the same attributes.

### Basic Inheritance

```yaml
categories:
  attribute_names:          # Common attributes for all categories
    - link
    - title
    - price
    - source_file
  
  categories:
    - name: phones
      attribute_names:        # Inherits common + adds is_new
        - is_new
  
    - name: gpu
      attribute_names:        # Inherits common + adds brand
        - brand
```

In this example:
- `phones` category gets: `link`, `title`, `price`, `source_file`, `is_new`
- `gpu` category gets: `link`, `title`, `price`, `source_file`, `brand`

### Multi-Level Inheritance

For hierarchical categories (using `/` separator), attributes are inherited from all parent levels:

```yaml
categories:
  attribute_names: [link, title, price]  # Common attributes
  
  categories:
    - name: domy
      attribute_names: [is_new]          # Parent level 1
    
    - name: domy/najem
      attribute_names: [rooms, area]     # Parent level 2
    
    - name: domy/najem/warszawa
      attribute_names: [district]        # Category-specific
      # Final attributes: link, title, price, is_new, rooms, area, district
```

**Inheritance order**:
1. Common attributes (`categories.attribute_names`)
2. All parent category attributes in hierarchy (in order: `domy`, then `domy/najem`)
3. Category-specific attributes (`domy/najem/warszawa`)

**Duplicate handling**: If an attribute appears in multiple levels, the first occurrence wins (common → parent → category-specific).

## Category Configuration

Each item in the `categories` array defines a single category:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Category name (e.g., `gpu`, `laptopy`, `domy/najem`) |
| `description` | string | No | Description of the category |
| `download_url` | string | No | Base URL for downloading/scraping content for this category (optional, for reference) |
| `attribute_names` | array | No | List of attribute names from the common `attributes` section that should be used for this category. If not specified, all attributes are used |

### Category Example

```yaml
categories:
  - name: gpu
    description: Graphics Processing Units
    download_url: "https://example.com/category/gpu"
    attribute_names:
      - link
      - title
      - price
      - negotiable
      - location
      - date
      - is_new
      - refreshed
```

## Attribute Configuration

Each attribute in the `attributes` array defines how to extract one column from the HTML. Attributes are processed in order, and dependencies are resolved automatically.

**Item Detection**: The tool uses the first required attribute with a regex pattern (typically the "link" attribute) to find all matching elements on the page. For each matching element, it identifies the containing element (parent or ancestor) and extracts all configured attributes from that container. This allows extraction of multiple items from a single HTML file, with each item becoming one row in the output.

### Attribute Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Column name in the output (must be unique) |
| `required` | boolean | No | If `true`, item is skipped if this column is missing (default: `false`) |
| `extract` | object | Yes | Extraction instructions (see Extract Object below) |

### Extract Object

The `extract` object contains all instructions for finding and extracting data from HTML:

| Field               | Type   | Required    | Description                                                                                                                                                              |
| ------------------- | ------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `type`              | string | Yes         | Extraction type: `text`, `regex`, `contains`, `metadata`                                                                                                                 |
| `selector`          | string | Conditional | **For HTML extraction types** (`text`, `regex`): HTML tag name (e.g., `a`, `p`, `h4`, `span`)<br>**For `metadata` type** (only for `source_month`/`scrape_date`/`scrape_datetime`): Date source - `filename`, `parent_folder`, or `file_creation` |
| `fallback_selector` | string | No          | Alternative selector if primary not found                                                                                                                                |
| `html_attributes`   | object | No          | HTML attributes to match (e.g., `data-testid`, `title`)                                                                                                                  |
| `extract_attribute` | string | No          | Which attribute to extract: `text`, `href`, `title`, etc. (default: `text`)                                                                                              |
| `pattern`           | string | Conditional | Regex pattern (required for `type: regex`)                                                                                                                               |
| `depends_on`        | string | No          | Column name this extraction depends on                                                                                                                                   |
| `check`             | string | Conditional | String to check for (required for `type: contains`)                                                                                                                      |
| `processing`        | array  | No          | List of processing steps (see Processing Steps)                                                                                                                          |
| `mapping`           | object | No          | Value mapping dictionary                                                                                                                                                 |


## Extraction Types

### 1. `text` - Standard Text Extraction

Extract text or attribute value from HTML element.

```yaml
- name: title
  required: true
  extract:
    type: text
    selector: h4
    fallback_selector: h6
    extract_attribute: text
```

**Use Cases**:
- Extracting text content from elements
- Extracting attribute values (href, title, etc.)
- Simple, direct extraction

### 2. `regex` - Regular Expression Matching

Find element using regex pattern on attributes.

```yaml
- name: link
  required: true
  extract:
    type: regex
    selector: a
    extract_attribute: href
    pattern: "/d/oferta/.*\\.html"
```

**Use Cases**:
- Matching URLs with specific patterns
- Finding elements by attribute patterns
- Filtering elements by complex criteria

### 3. `contains` - Dependency Check

Check if a value contains a specific string (depends on another column).

```yaml
- name: negotiable
  required: false
  extract:
    type: contains
    depends_on: price
    check: "negotiable"
```

**Use Cases**:
- Derived columns based on other columns
- Boolean flags based on text content
- Conditional extraction

### 4. `metadata` - Context Metadata

Extract metadata from file context (not from HTML).

```yaml
- name: source_file
  required: false
  extract:
    type: metadata
```

**Available metadata attributes**:
- `source_month`: Source month (YYYY-MM format)
- `source_file`: Source file name
- `source_path`: Full path to source file (relative to data folder)
- `scrape_date`: **Scrape date (YYYY-MM-DD format)** - when the HTML file was scraped/saved, extracted from file path/filename. This is different from the `date` attribute which is extracted from HTML content.
- `scrape_datetime`: Scrape date and time (YYYY-MM-DD HH:MM:SS format)
- `category`: Return task category

**Important**: `scrape_date` (metadata) and `date` (HTML content) are two different attributes:
- **`date`**: Extracted from HTML content using `type: text` - represents when an item was posted/listed on the website
- **`scrape_date`**: Extracted from file path/filename using `type: metadata` - represents when the HTML file was scraped/saved

**Date Source Configuration** (for `source_month`, `scrape_date`, and `scrape_datetime` only):

For date-related metadata attributes, you can specify where the date should be extracted from using the `selector` field:

```yaml
- name: scrape_date
  required: false
  extract:
    type: metadata
    selector: parent_folder  # Options: filename, parent_folder, file_creation
```

**Date Source Options** (used as `selector` value for metadata type):

| Value | Description | Example |
|-------|-------------|---------|
| `filename` | Extract date from file name | `page_2025-01-15.html` → `2025-01-15` (or `2025-01-15_14-30-00` → `2025-01-15 14:30:00` for datetime) |
| `parent_folder` | Extract date from parent folder name | `data/gpu/2025-01-15/page.html` → `2025-01-15` (or `2025-01-15_14-30-00/page.html` → `2025-01-15 14:30:00` for datetime) |
| `file_creation` | Use file system creation/modification date | Uses OS file creation timestamp (includes time for datetime) |

**Default Behavior**:
- If `selector` is not specified for date-related metadata attributes, the tool searches in this order:
  1. File name (YYYY-MM-DD pattern for date, YYYY-MM-DD_HH-MM-SS for datetime)
  2. Parent folder name (YYYY-MM-DD pattern for date, YYYY-MM-DD_HH-MM-SS for datetime)
  3. File creation date (if neither found, includes time for datetime)
- For `scrape_datetime`: If time is not found in path/filename, time portion defaults to `00:00:00` when extracted from date-only patterns

**Note**: For metadata type attributes, the `selector` field has a different meaning than for HTML extraction types:
- **HTML extraction types** (`text`, `regex`): `selector` specifies the HTML tag name (e.g., `a`, `p`, `h4`)
- **Metadata type**: `selector` specifies the date source (only for `source_month`, `scrape_date`, `scrape_datetime`). For other metadata attributes (`source_file`, `source_path`, `category`), `selector` is not used.

## Processing Steps

Processing steps are applied in order to transform the extracted value:

| Step | Type | Description | Example |
|------|------|-------------|---------|
| `split` | string or array | Split string by separator(s) | `split: " USD"` or `split: [" - ", "<!-- -->"]` |
| `index` | integer | Get element at index (after split) | `index: 0` |
| `strip` | boolean or string | Strip whitespace (if `true`) or specified characters (if string) | `strip: true` or `strip: "chars"` |
| `replace` | object | Replace text or use variable/attribute | `replace: "old"` with `with: "new"` (quoted string) or `with: $scrape_date` (variable with `$` prefix) or `with: $attribute_name` (attribute reference). **Strings must be quoted** (e.g., `"text with spaces"`). **Variables use `$` prefix** (e.g., `$scrape_date`). If `with` is a variable/attribute, replaces entire value when pattern found. |
| `check_today` | string | If value contains specified text pattern, replace entire value with scrape date | `check_today: "Dzisiaj o"` or `check_today: "Today at"` |
| `use_scrape_date` | boolean or object | Use scrape date as value if pattern matches. Generic, language-agnostic. | `use_scrape_date: true` or `use_scrape_date: {pattern: "Dzisiaj"}` |

### Processing Step Dictionary Structure

For programmatic config creation, processing steps are Python dictionaries with specific key names. The YAML format maps directly to these dictionary structures:

**YAML Format** → **Python Dict Format**:

| YAML | Python Dict |
|------|-------------|
| `split: " USD"` | `{'split': ' USD'}` |
| `split: [" - ", "<!-- -->"]` | `{'split': [' - ', '<!-- -->']}` |
| `index: 0` | `{'index': 0}` |
| `strip: true` | `{'strip': True}` |
| `strip: "chars"` | `{'strip': 'chars'}` |
| `replace: "old"`<br>`with: "new"` | `{'replace': 'old', 'with': 'new'}` |
| `replace: "pattern"`<br>`with: $scrape_date` | `{'replace': 'pattern', 'with': '$scrape_date'}` |
| `check_today: "Dzisiaj o"` | `{'check_today': 'Dzisiaj o'}` |
| `use_scrape_date: true` | `{'use_scrape_date': True}` |
| `use_scrape_date: {pattern: "Dzisiaj"}` | `{'use_scrape_date': {'pattern': 'Dzisiaj'}}` |

**Important Notes**:
- Each processing step is a dictionary with the operation name as a key
- The code checks for specific keys: `'split'`, `'index'`, `'strip'`, `'replace'`, `'with'`, `'check_today'`, `'use_scrape_date'`
- The code does **not** recognize a `'type'` key - each step type is identified by its specific key name
- For `replace`, both `'replace'` and `'with'` keys must be present in the same dictionary
- For `strip`, use `True` for whitespace stripping, or a string for custom characters

**Complete Example - Side-by-Side Comparison**:

Here's a complete processing array showing the same steps in both YAML and Python dict formats:

**YAML Format**:
```yaml
processing:
  - split: [" - ", "<!-- -->"]
  - index: 0
  - strip: true
  - replace: "Dzisiaj o"
    with: $scrape_date
```

**Python Dict Format**:
```python
"processing": [
    {"split": [" - ", "<!-- -->"]},
    {"index": 0},
    {"strip": True},
    {"replace": "Dzisiaj o", "with": "$scrape_date"}
]
```

**Example - Programmatic Config with Processing Steps**:

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

### Processing Example

```yaml
processing:
  - split: [" - ", "<!-- -->"]
  - index: 0
  - strip: true
  - replace: "Odświeżono dnia"  # Quoted string (spaces are visible)
    with: ""                     # Quoted empty string
  - replace: "Dzisiaj o"        # Quoted string pattern
    with: $scrape_date          # Variable with $ prefix (no quotes)
```

### String vs Variable Syntax

**Important**: The `replace` step uses different syntax for strings and variables to make the distinction clear:

**Strings** (quoted in YAML/JSON):
- Must be quoted: `"text with spaces"`, `"old_text"`, `""`
- Helps you see all spaces and special characters clearly
- Used for literal text replacement

**Variables** (use `$` prefix, no quotes):
- Use `$` prefix: `$scrape_date`, `$attribute_name`
- No quotes needed: `with: $scrape_date` (not `with: "$scrape_date"`)
- The `$` prefix clearly identifies variables

**Variable Types**:
- **Context variables**: `$scrape_date` (available from processing context)
- **Attribute references**: `$attribute_name` (references already-extracted attributes)

**Examples**:
```yaml
# String replacement (quoted)
- replace: "old text"
  with: "new text"

# Variable replacement (no quotes, $ prefix)
- replace: "Dzisiaj o"
  with: $scrape_date

# Variable in replace field
- replace: $pattern  # Uses value from 'pattern' attribute
  with: "Replaced"
```

## Value Mapping

Map extracted values to different output values:

```yaml
mapping:
  "Nowe": 1
  "Używane": 0
  default: null
```

**Behavior**:
- If value matches a key, use the mapped value
- If no match and `default` exists, use default value
- Otherwise, keep original value

## Complete Example

```yaml
categories:
  - name: gpu
    description: Graphics Processing Units
    download_url: "https://example.com/category/gpu"
    attribute_names:
      - link
      - title
      - price
      - negotiable
      - location
      - date
      - is_new
      - refreshed
      - source_file
      - source_month
      - scrape_date
      - scrape_datetime

attributes:
  # Required: Link to item
  - name: link
    required: true
    extract:
      type: regex
      selector: a
      extract_attribute: href
      pattern: "/d/oferta/.*\\.html"

  # Required: Item title
  - name: title
    required: true
    extract:
      type: text
      selector: h4
      fallback_selector: h6
      extract_attribute: text

  # Optional: Price (with processing)
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

  # Optional: Negotiable flag (depends on price)
  - name: negotiable
    required: false
    extract:
      type: contains
      depends_on: price
      check: "negotiable"

  # Optional: Location
  - name: location
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        data-testid: location-date
      extract_attribute: text
      processing:
        - split: [" - ", "<!-- -->"]
        - index: 0
        - strip: true

  # Optional: Date (extracted from HTML content - when item was posted/listed)
  # Note: This is different from scrape_date (metadata from file path - when HTML was scraped)
  - name: date
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        data-testid: location-date
      extract_attribute: text
      processing:
        - split: [" - ", "<!-- -->"]
        - index: 1
        - replace: "Refreshed on"
          with: ""
        - replace: "Dzisiaj o"  # Quoted string pattern
          with: $scrape_date    # Variable with $ prefix (no quotes) - replaces entire value when pattern found
        # Alternative: use plain string replacement
        # - replace: "old_text"   # Quoted string
        #   with: "new_text"      # Quoted string - normal substring replacement
        # Alternative: use attribute reference
        # - replace: $pattern      # Variable in replace field (uses value from 'pattern' attribute)
        #   with: "Replaced"       # Quoted string replacement

  # Optional: New/Used status
  - name: is_new
    required: false
    extract:
      type: regex
      selector: span
      html_attributes:
        title: "^(Nowe|Używane)$"
      extract_attribute: title
      mapping:
        "Nowe": 1
        "Używane": 0
        default: null

  # Optional: Refreshed flag
  - name: refreshed
    required: false
    extract:
      type: contains
      depends_on: date
      check: "Refreshed"

  # Metadata: Source file name
  - name: source_file
    required: false
    extract:
      type: metadata

  # Metadata: Source month
  - name: source_month
    required: false
    extract:
      type: metadata

  # Metadata: Scrape date (when HTML file was scraped/saved, extracted from file path/filename)
  # Note: This is different from 'date' attribute (extracted from HTML content - when item was posted)
  - name: scrape_date
    required: false
    extract:
      type: metadata
      selector: parent_folder

  # Metadata: Scrape datetime
  - name: scrape_datetime
    required: false
    extract:
      type: metadata
      selector: filename
```

## Available Columns Reference

The following columns can be configured for extraction:

| Column | Description | Common Extraction Type |
|--------|-------------|------------------------|
| `link` | URL to the item | `regex` on anchor tag href |
| `title` | Item title | `text` from h4/h6 tag |
| `price` | Price value without currency symbol | `text` with processing to remove currency |
| `negotiable` | Boolean indicating if price is negotiable | `contains` checking for specific text |
| `location` | Location of the item | `text` from location-date element |
| `is_new` | 1 for new items, 0 for used items, None if not specified | `regex` with mapping |
| `date` | **Date when the item was posted/listed** (extracted from HTML content) | `text` with date processing |
| `refreshed` | Boolean indicating if the item was refreshed | `contains` checking for refresh indicator |
| `source_month` | Source month (YYYY-MM format) | `metadata` |
| `source_file` | Source file name | `metadata` |
| `source_path` | Full path to source file | `metadata` |
| `scrape_date` | **Date when HTML file was scraped/saved** (extracted from file path/filename) | `metadata` |
| `scrape_datetime` | Scrape date and time (YYYY-MM-DD HH:MM:SS format) | `metadata` |

## Best Practices

1. **Always mark critical columns as `required: true`** - This ensures data quality (e.g., `link`, `title`)

2. **Use `fallback_selector`** - Provides resilience if HTML structure changes slightly

3. **Order matters** - Place dependent columns after their dependencies (e.g., `negotiable` after `price`)

4. **Use metadata attributes** - Include `source_file`, `scrape_date` for tracking and analysis

5. **Test processing steps** - Verify each processing step works with actual HTML samples

6. **Validate regex patterns** - Test regex patterns with actual HTML to ensure they match correctly

7. **Use value mapping** - Convert text values to numeric codes for easier analysis (e.g., "Nowe" → 1)

8. **Document custom attributes** - Add comments in YAML to explain non-obvious extraction logic

9. **Keep configs versioned** - Track changes to config files to understand data evolution

## Handling Multiple Categories

When a config file contains multiple categories, the tool needs to determine which category to use for each file. The category selection follows different rules depending on the input type:

### Category Selection Rules

| Input Type | Category Source | Priority |
|------------|----------------|----------|
| **Single HTML file** | User must explicitly specify | Required via `-k, --category` CLI flag or `category` parameter in API |
| **CSV file** | CSV `category` column, or user-defined default | 1. CSV `category` column (per-row), 2. Default category (if specified), 3. Error if neither provided |
| **Folder** | Derived from folder name | Automatically extracted from folder path (e.g., `data/gpu/2025/...` → category `gpu`) |

### Single HTML File Processing

For single HTML files, you **must** specify the category explicitly:

**CLI Usage**:
```bash
# Specify category via -k flag
html-extract page.html -c config.yaml -k gpu -o output.csv

# Category name must match one of the categories defined in config
html-extract page.html -c config.yaml -k laptopy -o output.csv
```

**API Usage**:
```python
from html_extract.extract import extract_data_from_html
from html_extract.config import load_config

config = load_config('data/config.yaml')
# Specify category parameter
df = extract_data_from_html('page.html', config, category='gpu')
```

**Behavior**:
- If category is not specified, the tool raises an error
- Category name must exactly match one of the `name` values in the `categories` array
- Only attributes listed in the selected category's `attribute_names` are extracted (or all attributes if `attribute_names` is not specified)

### CSV File Processing

For CSV bulk processing, category can be specified per-row in the CSV or as a default:

**CSV Format with Category Column**:
```csv
path,config,scrape_date,category
data/gpu/2025/2025-01-15/page_1.html,data/config.yaml,2025-01-15,gpu
data/laptopy/2025/2025-01-15/page_1.html,data/config.yaml,2025-01-15,laptopy
data/domy/2025/2025-01-15/page_1.html,data/config.yaml,2025-01-15,domy/najem
```

**CLI Usage**:
```bash
# Process CSV with per-row categories
html-extract file_list.csv -c config.yaml -o output.csv

# Process CSV with default category (used if CSV row doesn't specify category)
html-extract file_list.csv -c config.yaml -k gpu -o output.csv
```

**API Usage**:
```python
from html_extract.batch import process_csv
from html_extract.config import load_config

default_config = load_config('data/config.yaml')
# Default category used if CSV row doesn't specify one
df = process_csv('file_list.csv', default_config=default_config, default_category='gpu')
```

**Priority**:
1. **CSV `category` column** (if present) - per-row category override
2. **Default category** (if specified via `-k` flag or `default_category` parameter)
3. **Error** - if neither CSV column nor default is provided

### Folder Processing

For folder processing, category is **automatically derived** from the folder path:

**Folder Structure**:
```
data/
├── config.yaml
├── gpu/
│   └── 2025/
│       └── 2025-01-15/
│           └── page_1.html
├── laptopy/
│   └── 2025/
│       └── 2025-01-15/
│           └── page_1.html
└── domy/
    └── najem/
        └── 2025/
            └── 2025-01-15/
                └── page_1.html
```

**CLI Usage**:
```bash
# Category automatically extracted from folder path
# data/gpu/2025/2025-01-15 → category: gpu
html-extract data/gpu/2025/2025-01-15 -c config.yaml -o output.csv

# Nested category: data/domy/najem/2025/2025-01-15 → category: domy/najem
html-extract data/domy/najem/2025/2025-01-15 -c config.yaml -o output.csv
```

**Category Derivation Rules**:
- The tool looks for the first folder name in the path that matches a category name in the config
- For nested categories (e.g., `domy/najem`), the tool matches the full path segment
- Matching is done by comparing folder names to category `name` values in the config
- **Only directories matching defined categories are processed** - files in non-matching directories are skipped with a warning
- If no matching category is found for a file, the file is skipped (with warning) instead of raising an error

**API Usage**:
```python
from html_extract.batch import process_directory
from html_extract.config import load_config

config = load_config('data/config.yaml')
# Category automatically extracted from directory_path
df = process_directory('data/gpu/2025/2025-01-15', config)
```

### Category Matching

Category names in the config are matched using the following rules:

1. **Exact match**: Category name must exactly match the specified or derived name
2. **Case-sensitive**: Matching is case-sensitive (`gpu` ≠ `GPU`)
3. **Nested categories**: Use forward slash (`/`) for nested categories (e.g., `domy/najem`)
4. **Path segments**: For folder-derived categories, the tool matches folder path segments to category names

**Example Config with Multiple Categories**:
```yaml
categories:
  - name: gpu
    description: Graphics Processing Units
    attribute_names:
      - link
      - title
      - price
  - name: laptopy
    description: Laptops
    attribute_names:
      - link
      - title
      - price
      - screen_size
  - name: domy/najem
    description: Houses for rent
    attribute_names:
      - link
      - title
      - price
      - location
      - rooms

attributes:
  # ... attribute definitions ...
```

### Error Handling

**Category Not Found**:
- **Error**: `Category 'X' not found in config`
- **Cause**: Specified or derived category name doesn't match any category in config
- **Solution**: Check category name spelling, ensure it exists in config's `categories` array

**Category Not Specified (Single HTML)**:
- **Error**: `Category must be specified for single HTML file processing`
- **Cause**: Processing single HTML file without specifying category
- **Solution**: Use `-k, --category` flag to specify category

**No Category Match (Folder)**:
- **Error**: `Could not determine category from folder path`
- **Cause**: Folder path doesn't contain a folder name matching any category in config
- **Solution**: Ensure folder structure matches expected pattern, or use explicit category override

## Creating a Config Template

You can create a configuration template using either the Python API or the CLI tool.

**Using Python API**:

```python
from html_extract.config import create_config_template

# Create YAML template
create_config_template('new_config.yaml')

# Create JSON template
create_config_template('new_config.json')

# Explicitly specify format
create_config_template('config.txt', format='yaml')
```

**Using CLI**:

```bash
html-extract -t config new_config.yaml
```

The template includes example attributes (`link`, `title`, `price`, `location`, `date`) that you can customize for your specific category. YAML templates include helpful comments; JSON templates use the same structure without comments. For more details, see the [API Reference](../for-developers/15-api-reference.md#create_config_template) or [CLI Reference](../for-cli-users/08-cli-reference.md#template-creation).

## Troubleshooting Configuration

### Attribute Not Extracting

**Possible Causes**:
- Selector doesn't match HTML structure
- HTML attributes have changed
- Element is nested differently

**Solutions**:
- Use browser dev tools to inspect HTML
- Add `fallback_selector` as backup
- Check `html_attributes` match exactly

### Processing Steps Not Working

**Possible Causes**:
- Processing order is incorrect
- Split separator doesn't match actual text
- Index out of range after split

**Solutions**:
- Test each processing step individually
- Print intermediate values to debug
- Ensure split produces expected number of parts

### Required Attributes Missing

**Possible Causes**:
- HTML structure changed
- Selector too specific
- Element not present in all items

**Solutions**:
- Make selector more flexible
- Remove `required: true` if attribute is truly optional
- Check if element exists in HTML samples

