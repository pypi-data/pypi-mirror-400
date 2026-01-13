# E-commerce Listings Example

Extract product listings from an e-commerce website HTML file.

## HTML Structure

```html
<div class="product-listing">
  <h4><a href="/d/oferta/product-123.html">Product Title</a></h4>
  <p data-testid="ad-price">1000 USD</p>
  <p data-testid="location-date">Warsaw - Posted today</p>
  <span title="Nowe">New</span>
</div>
```

## Configuration

```yaml
categories:
  - name: products
    attribute_names: [link, title, price, location, is_new]

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
        - strip: true
  
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
```

## CLI Usage

```bash
html-extract data/products/page.html -c config.yaml -k products -o products.csv
```

## Python Usage

```python
from html_extract import extract_data_from_html, load_config, save_output

config = load_config('config.yaml')
df, skipped = extract_data_from_html('data/products/page.html', config, category='products')
save_output(df, 'products.csv')
```

## Output

```csv
link,title,price,location,is_new
/d/oferta/product-123.html,Product Title,1000,Warsaw,1
```
