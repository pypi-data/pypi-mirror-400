"""
Performance tests for HTML Extract.

Tests measure processing time and establish performance baselines.
"""

import pytest
import time
import pandas as pd
from pathlib import Path

from src.html_extract import (
    extract_data_from_html,
    process_directory,
    load_config
)


@pytest.fixture
def sample_html_small():
    """Create small HTML content."""
    return """
    <html>
    <body>
        <div>
            <a href="/d/oferta/item1.html">Item 1</a>
            <h4>Title 1</h4>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_large():
    """Create large HTML content with many items."""
    items = []
    for i in range(100):
        items.append(f"""
        <div>
            <a href="/d/oferta/item{i}.html">Item {i}</a>
            <h4>Title {i}</h4>
            <p>Price {i * 100}</p>
        </div>
        """)
    
    return f"""
    <html>
    <body>
        {''.join(items)}
    </body>
    </html>
    """


@pytest.fixture
def sample_config(tmp_path):
    """Create sample configuration."""
    config_file = tmp_path / "config.yaml"
    config_content = """
categories:
  attribute_names: [link, title]
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
"""
    config_file.write_text(config_content, encoding='utf-8')
    return config_file


def test_single_file_processing_time(sample_html_small, sample_config, tmp_path):
    """Test that single file processing completes in reasonable time (< 1 second)."""
    html_file = tmp_path / "page.html"
    html_file.write_text(sample_html_small, encoding='utf-8')
    
    config = load_config(sample_config)
    
    start_time = time.time()
    df, skipped_count = extract_data_from_html(html_file, config, category='test')
    elapsed_time = time.time() - start_time
    
    assert elapsed_time < 1.0, f"Processing took {elapsed_time:.3f}s, expected < 1.0s"
    assert len(df) > 0


def test_large_file_processing(sample_html_large, sample_config, tmp_path):
    """Test processing of large HTML file with many items."""
    html_file = tmp_path / "large_page.html"
    html_file.write_text(sample_html_large, encoding='utf-8')
    
    config = load_config(sample_config)
    
    start_time = time.time()
    df, skipped_count = extract_data_from_html(html_file, config, category='test')
    elapsed_time = time.time() - start_time
    
    # Should process 100 items in reasonable time (< 5 seconds)
    assert elapsed_time < 5.0, f"Processing took {elapsed_time:.3f}s, expected < 5.0s"
    assert len(df) == 100


def test_batch_processing_performance(sample_html_small, sample_config, tmp_path):
    """Test batch processing performance with multiple files."""
    # Create directory structure with category name: test/page_*.html
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    
    for i in range(10):
        html_file = test_dir / f"page_{i}.html"
        html_file.write_text(sample_html_small, encoding='utf-8')
    
    config = load_config(sample_config)
    
    start_time = time.time()
    df = process_directory(test_dir, config)
    elapsed_time = time.time() - start_time
    
    # Should process 10 files in reasonable time (< 5 seconds)
    assert elapsed_time < 5.0, f"Batch processing took {elapsed_time:.3f}s, expected < 5.0s"
    assert len(df) >= 10  # At least one item per file


def test_config_loading_performance(sample_config):
    """Test that config loading is fast."""
    start_time = time.time()
    config = load_config(sample_config)
    elapsed_time = time.time() - start_time
    
    # Config loading should be very fast (< 0.1 seconds)
    assert elapsed_time < 0.1, f"Config loading took {elapsed_time:.3f}s, expected < 0.1s"
    assert 'categories' in config


def test_dataframe_creation_performance():
    """Test DataFrame creation performance."""
    # Create large DataFrame
    data = {
        'col1': list(range(1000)),
        'col2': [f'item_{i}' for i in range(1000)]
    }
    
    start_time = time.time()
    df = pd.DataFrame(data)
    elapsed_time = time.time() - start_time
    
    # DataFrame creation should be fast (< 0.1 seconds)
    assert elapsed_time < 0.1, f"DataFrame creation took {elapsed_time:.3f}s"
    assert len(df) == 1000
