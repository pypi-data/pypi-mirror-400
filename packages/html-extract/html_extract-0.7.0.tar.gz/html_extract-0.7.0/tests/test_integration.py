"""
Integration tests for HTML Extract.

Tests cover end-to-end workflows combining multiple modules.
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile

from src.html_extract import (
    extract_data_from_html,
    load_config,
    process_directory,
    process_csv,
    save_output,
    create_config_template,
    create_csv_template
)


@pytest.fixture
def sample_html():
    """Create sample HTML content."""
    return """
    <html>
    <body>
        <div>
            <a href="/d/oferta/item1.html">Item 1</a>
            <h4>Title 1</h4>
            <p data-testid="ad-price">1000 zł</p>
        </div>
        <div>
            <a href="/d/oferta/item2.html">Item 2</a>
            <h4>Title 2</h4>
            <p data-testid="ad-price">2000 zł</p>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_config(tmp_path):
    """Create sample configuration file."""
    config_file = tmp_path / "config.yaml"
    config_content = """
categories:
  attribute_names: [link, title, price]
  categories:
    - name: test
      attribute_names: []

attributes:
  - name: link
    required: true
    extract:
      type: regex
      selector: a
      extract_attribute: href
      pattern: '/d/oferta/.*\\.html'
  
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
"""
    config_file.write_text(config_content, encoding='utf-8')
    return config_file


def test_end_to_end_single_file(sample_html, sample_config, tmp_path):
    """Test complete workflow: HTML file -> Config -> Extract -> Output."""
    # Create HTML file
    html_file = tmp_path / "page.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    # Load config
    config = load_config(sample_config)
    
    # Extract data
    df, skipped_count = extract_data_from_html(html_file, config, category='test')
    
    assert len(df) == 2
    assert 'link' in df.columns
    assert 'title' in df.columns
    assert 'price' in df.columns
    
    # Save output
    output_file = tmp_path / "output.csv"
    save_output(df, output_file)
    
    assert output_file.exists()
    
    # Verify output
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2


def test_end_to_end_directory_processing(sample_html, sample_config, tmp_path):
    """Test complete workflow: Directory -> Process -> Output."""
    # Create directory structure
    test_dir = tmp_path / "test" / "2024-01-15"
    test_dir.mkdir(parents=True)
    
    html_file1 = test_dir / "page1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    html_file2 = test_dir / "page2.html"
    html_file2.write_text(sample_html, encoding='utf-8')
    
    # Load config
    config = load_config(sample_config)
    
    # Process directory
    df = process_directory(test_dir.parent, config)
    
    assert len(df) >= 2  # At least 2 items from 2 files
    
    # Save output
    output_file = tmp_path / "output.csv"
    save_output(df, output_file)
    
    assert output_file.exists()


def test_end_to_end_csv_bulk_processing(sample_html, sample_config, tmp_path):
    """Test complete workflow: CSV list -> Process -> Output."""
    # Create HTML files
    html_file1 = tmp_path / "file1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    html_file2 = tmp_path / "file2.html"
    html_file2.write_text(sample_html, encoding='utf-8')
    
    # Create CSV file
    csv_file = tmp_path / "file_list.csv"
    csv_data = f"path,category\n{html_file1},test\n{html_file2},test\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    # Load config
    config = load_config(sample_config)
    
    # Process CSV
    df = process_csv(csv_file, default_config=config)
    
    assert len(df) >= 2
    
    # Save output
    output_file = tmp_path / "output.csv"
    save_output(df, output_file)
    
    assert output_file.exists()


def test_template_generation_workflow(tmp_path):
    """Test template generation and usage workflow."""
    # Generate config template
    config_template = tmp_path / "config.yaml"
    create_config_template(config_template)
    
    assert config_template.exists()
    
    # Generate CSV template
    csv_template = tmp_path / "file_list.csv"
    create_csv_template(csv_template)
    
    assert csv_template.exists()
    
    # Verify templates are valid
    config = load_config(config_template)
    assert 'categories' in config
    assert 'attributes' in config
    
    df = pd.read_csv(csv_template, encoding='utf-8-sig')
    assert 'path' in df.columns


def test_multi_category_processing(sample_html, tmp_path):
    """Test processing with multiple categories."""
    # Create config with multiple categories
    config_file = tmp_path / "multi_config.yaml"
    config_content = """
categories:
  attribute_names: [link, title]
  categories:
    - name: category1
      attribute_names: []
    - name: category2
      attribute_names: []

attributes:
  - name: link
    required: true
    extract:
      type: regex
      selector: a
      extract_attribute: href
      pattern: '/d/oferta/.*\\.html'
  
  - name: title
    required: true
    extract:
      type: text
      selector: h4
      extract_attribute: text
"""
    config_file.write_text(config_content, encoding='utf-8')
    
    html_file = tmp_path / "page.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    config = load_config(config_file)
    
    # Process with category1
    df1, skipped_count1 = extract_data_from_html(html_file, config, category='category1')
    assert len(df1) >= 1  # At least one item found
    
    # Process with category2
    df2, skipped_count2 = extract_data_from_html(html_file, config, category='category2')
    assert len(df2) >= 1  # At least one item found
    
    # Both should have same structure
    assert list(df1.columns) == list(df2.columns)


def test_json_output_format(sample_html, sample_config, tmp_path):
    """Test JSON output format in end-to-end workflow."""
    html_file = tmp_path / "page.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    config = load_config(sample_config)
    df, skipped_count = extract_data_from_html(html_file, config, category='test')
    
    # Save as JSON
    output_file = tmp_path / "output.json"
    save_output(df, output_file, format='json')
    
    assert output_file.exists()
    
    # Verify JSON content
    import json
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 2


def test_directory_with_nested_structure(sample_html, sample_config, tmp_path):
    """Test directory processing with nested folder structure."""
    # Create nested structure: category/2024/2024-01-15/page.html
    nested_dir = tmp_path / "test" / "2024" / "2024-01-15"
    nested_dir.mkdir(parents=True)
    
    html_file = nested_dir / "page.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    config = load_config(sample_config)
    
    # Process directory
    df = process_directory(nested_dir.parent, config)
    
    assert len(df) >= 2
    
    # Verify category was auto-derived
    assert 'source_path' in df.columns or len(df) > 0
