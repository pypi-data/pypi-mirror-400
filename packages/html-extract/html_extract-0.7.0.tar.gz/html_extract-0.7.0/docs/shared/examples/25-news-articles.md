# News Articles Example

Extract article metadata from a news website HTML file.

## HTML Structure

```html
<article class="news-item">
  <h2><a href="/news/article-123.html">Breaking News Title</a></h2>
  <p class="author">By John Doe</p>
  <p class="date">2025-01-15</p>
  <p class="category">Technology</p>
  <p class="excerpt">Article excerpt text here...</p>
</article>
```

## Configuration

```yaml
categories:
  - name: articles
    attribute_names: [link, title, author, date, category, excerpt]

attributes:
  - name: link
    required: true
    extract:
      type: regex
      selector: a
      extract_attribute: href
      pattern: "/news/.*\\.html"
  
  - name: title
    required: true
    extract:
      type: text
      selector: h2
      extract_attribute: text
  
  - name: author
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        class: author
      extract_attribute: text
      processing:
        - replace: "By "
          with: ""
        - strip: true
  
  - name: date
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        class: date
      extract_attribute: text
  
  - name: category
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        class: category
      extract_attribute: text
  
  - name: excerpt
    required: false
    extract:
      type: text
      selector: p
      html_attributes:
        class: excerpt
      extract_attribute: text
      processing:
        - strip: true
```

## CLI Usage

```bash
html-extract data/news/page.html -c config.yaml -k articles -o articles.csv
```

## Python Usage

```python
from html_extract import extract_data_from_html, load_config, save_output

config = load_config('config.yaml')
df, skipped = extract_data_from_html('data/news/page.html', config, category='articles')
save_output(df, 'articles.csv')
```

## Output

```csv
link,title,author,date,category,excerpt
/news/article-123.html,Breaking News Title,John Doe,2025-01-15,Technology,Article excerpt text here...
```
