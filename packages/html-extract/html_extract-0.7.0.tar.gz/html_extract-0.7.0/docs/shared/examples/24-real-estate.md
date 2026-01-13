# Real Estate Listings Example

Extract property listings from a real estate website HTML file.

## HTML Structure

```html
<div class="property-listing">
  <h4><a href="/property/12345.html">Beautiful House in Warsaw</a></h4>
  <p class="price">500000 PLN</p>
  <p class="details">3 rooms, 120 m², Warsaw Center</p>
  <span class="status">For Rent</span>
</div>
```

## Configuration

```yaml
categories:
  - name: properties
    attribute_names: [link, title, price, rooms, area, location, type]

attributes:
  - name: link
    required: true
    extract:
      type: regex
      selector: a
      extract_attribute: href
      pattern: "/property/.*\\.html"
  
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
        class: price
      extract_attribute: text
      processing:
        - split: " PLN"
        - index: 0
        - strip: true
  
  - name: rooms
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        class: details
      extract_attribute: text
      processing:
        - split: " rooms"
        - index: 0
        - strip: true
  
  - name: area
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        class: details
      extract_attribute: text
      processing:
        - split: " m²"
        - index: 0
        - split: ", "
        - index: -1
        - strip: true
  
  - name: location
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        class: details
      extract_attribute: text
      processing:
        - split: ", "
        - index: -1
        - strip: true
  
  - name: type
    required: false
    extract:
      type: text
      selector: span
      html_attributes:
        class: status
      extract_attribute: text
```

## CLI Usage

```bash
html-extract data/properties/page.html -c config.yaml -k properties -o properties.csv
```

## Python Usage

```python
from html_extract import extract_data_from_html, load_config, save_output

config = load_config('config.yaml')
df, skipped = extract_data_from_html('data/properties/page.html', config, category='properties')
save_output(df, 'properties.csv')
```

## Output

```csv
link,title,price,rooms,area,location,type
/property/12345.html,Beautiful House in Warsaw,500000,3,120,Warsaw Center,For Rent
```
