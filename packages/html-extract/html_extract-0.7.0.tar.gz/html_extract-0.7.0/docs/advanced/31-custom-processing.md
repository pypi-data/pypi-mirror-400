# Custom Processing

Advanced processing techniques and custom transformations.

## Processing Steps

HTML Extract provides built-in processing steps to transform extracted values:

### Split and Index

Split strings and select specific parts:

```yaml
processing:
  - split: " - "
  - index: 0
  - strip: true
```

### Multiple Splits

Split by multiple separators:

```yaml
processing:
  - split: [" - ", "<!-- -->"]
  - index: 0
```

### Strip Whitespace

Remove whitespace or specific characters:

```yaml
processing:
  - strip: true  # Remove all whitespace
  # Or
  - strip: "chars"  # Remove specific characters
```

### Replace Text

Replace text with strings or variables:

```yaml
processing:
  - replace: "old text"
    with: "new text"
  
  # Use variables
  - replace: "Dzisiaj o"
    with: $scrape_date
```

### Value Mapping

Map values to different output values:

```yaml
mapping:
  "Nowe": 1
  "Używane": 0
  default: null
```

## Complex Processing Chains

Combine multiple processing steps:

```yaml
processing:
  - split: [" - ", "<!-- -->"]
  - index: 0
  - strip: true
  - replace: "Old Text"
    with: "New Text"
  - replace: "Dzisiaj o"
    with: $scrape_date
```

## Custom Transformations with Python

After extraction, use pandas for custom transformations:

```python
import pandas as pd
from html_extract import extract_data_from_html, load_config

config = load_config('config.yaml')
df = extract_data_from_html('page.html', config, category='gpu')

# Custom processing
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['price_per_unit'] = df['price'] / df.get('quantity', 1)
df['is_expensive'] = df['price'] > 1000

# Custom filtering
filtered_df = df[df['price'] > 1000]
```

## Date Processing

Process dates and use scrape date:

```yaml
processing:
  - split: [" - ", "<!-- -->"]
  - index: 1
  - replace: "Dzisiaj o"
    with: $scrape_date
  - check_today: "Dzisiaj o"  # Alternative approach
```

## Derived Columns

Create derived columns based on other columns:

```yaml
- name: negotiable
  extract:
    type: contains
    depends_on: price
    check: "negotiable"
```

## See Also

- [Configuration Reference](../shared/20-configuration-reference.md) - Complete processing documentation
- [Best Practices](32-best-practices.md) - Recommended practices
- [Performance Optimization](30-performance.md) - Performance tips
