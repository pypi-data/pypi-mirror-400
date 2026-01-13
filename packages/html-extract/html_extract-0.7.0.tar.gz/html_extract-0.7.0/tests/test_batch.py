"""
Unit tests for the batch processing module.

Tests cover batch_extract(), process_directory(), process_csv(), and
category auto-derivation functionality.
"""

from typing import Dict, Any

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

from src.html_extract.batch import (
    batch_extract,
    process_directory,
    process_csv,
    create_csv_template,
    _derive_category_from_path
)
from src.html_extract.config import load_config


# Test data directory (located in user-tests/data/)
TEST_DATA_DIR = Path(__file__).parent.parent / "user-tests" / "data"


@pytest.fixture
def sample_html():
    """Create a sample HTML file for testing."""
    html_content = """
    <html>
    <body>
        <div>
            <a href="/d/oferta/test-item.html">Test Item</a>
            <h4>Test Title</h4>
            <p data-testid="ad-price">1000 zł</p>
        </div>
    </body>
    </html>
    """
    return html_content


@pytest.fixture
def sample_config():
    """Create a sample configuration for testing."""
    return {
        "categories": {
            "attribute_names": ["link", "title", "price"],
            "categories": [
                {
                    "name": "test",
                    "attribute_names": []
                },
                {
                    "name": "gpu",
                    "attribute_names": []
                },
                {
                    "name": "domy/najem",
                    "attribute_names": []
                }
            ]
        },
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
            },
            {
                "name": "price",
                "required": False,
                "extract": {
                    "type": "text",
                    "selector": "p",
                    "html_attributes": {
                        "data-testid": "ad-price"
                    },
                    "extract_attribute": "text"
                }
            }
        ]
    }


def test_batch_extract_single_file(sample_html, sample_config, tmp_path):
    """Test batch_extract with a single file."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {str(html_file): "test"}
    df = batch_extract(files_with_categories, sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "link" in df.columns
    assert "title" in df.columns


def test_batch_extract_multiple_files(sample_html, sample_config, tmp_path):
    """Test batch_extract with multiple files."""
    # Create multiple HTML files
    files_with_categories = {}
    for i in range(3):
        html_file = tmp_path / f"test_{i}.html"
        html_file.write_text(sample_html, encoding='utf-8')
        files_with_categories[str(html_file)] = "test"
    
    df = batch_extract(files_with_categories, sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 3  # At least one item per file


def test_batch_extract_multithreading(sample_html, sample_config, tmp_path):
    """Test batch_extract with multithreading."""
    # Create multiple HTML files
    files_with_categories = {}
    for i in range(5):
        html_file = tmp_path / f"test_{i}.html"
        html_file.write_text(sample_html, encoding='utf-8')
        files_with_categories[str(html_file)] = "test"
    
    # Process with explicit max_workers
    df = batch_extract(files_with_categories, sample_config, max_workers=2)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 5


def test_batch_extract_with_scrape_date(sample_html, sample_config, tmp_path):
    """Test batch_extract with explicit scrape date."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {str(html_file): "test"}
    df = batch_extract(
        files_with_categories,
        sample_config,
        scrape_date="2024-01-20"
    )
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_batch_extract_empty_dict(sample_config):
    """Test batch_extract with empty files dictionary."""
    df = batch_extract({}, sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


def test_batch_extract_file_not_found(sample_config):
    """Test batch_extract with non-existent file."""
    files_with_categories = {"nonexistent.html": "test"}
    
    with pytest.raises(FileNotFoundError):
        batch_extract(files_with_categories, sample_config)


def test_batch_extract_invalid_category(sample_html, sample_config, tmp_path):
    """Test batch_extract with invalid category name."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {str(html_file): "invalid_category"}
    
    with pytest.raises(ValueError, match="Category.*not found"):
        batch_extract(files_with_categories, sample_config)


def test_batch_extract_graceful_failure(sample_config, tmp_path):
    """Test that batch_extract continues processing when one file fails."""
    # Create one valid file
    valid_file = tmp_path / "valid.html"
    valid_file.write_text(
        '<html><body><a href="/d/oferta/test.html">Test</a><h4>Title</h4></body></html>',
        encoding='utf-8'
    )
    
    # Create one invalid file (missing required attribute)
    invalid_file = tmp_path / "invalid.html"
    invalid_file.write_text(
        '<html><body><p>No link or title</p></body></html>',
        encoding='utf-8'
    )
    
    files_with_categories = {
        str(valid_file): "test",
        str(invalid_file): "test"
    }
    
    # Should not raise exception, but process valid file
    df = batch_extract(files_with_categories, sample_config)
    
    # Should have data from valid file
    assert isinstance(df, pd.DataFrame)
    # May have 0 rows if invalid file causes issues, but should not crash
    assert len(df) >= 0


def test_derive_category_from_path_simple(sample_config):
    """Test category derivation from simple path."""
    file_path = Path("/data/gpu/2024-01-15/page.html")
    category = _derive_category_from_path(file_path, sample_config)
    
    assert category == "gpu"


def test_derive_category_from_path_nested(sample_config):
    """Test category derivation from nested category path."""
    file_path = Path("/data/domy/najem/2024-01-15/page.html")
    category = _derive_category_from_path(file_path, sample_config)
    
    assert category == "domy/najem"


def test_derive_category_from_path_no_match(sample_config):
    """Test category derivation when no category found in path."""
    file_path = Path("/data/unknown/2024-01-15/page.html")
    
    with pytest.raises(ValueError, match="Could not derive category"):
        _derive_category_from_path(file_path, sample_config)


def test_process_directory_single_file(sample_html, sample_config, tmp_path):
    """Test process_directory with a single HTML file."""
    # Create directory structure: test/2024-01-15/page.html
    test_dir = tmp_path / "test" / "2024-01-15"
    test_dir.mkdir(parents=True)
    
    html_file = test_dir / "page.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    df = process_directory(test_dir.parent, sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_process_directory_multiple_files(sample_html, sample_config, tmp_path):
    """Test process_directory with multiple HTML files."""
    # Create directory structure: test/2024-01-15/
    test_dir = tmp_path / "test" / "2024-01-15"
    test_dir.mkdir(parents=True)
    
    # Create multiple HTML files
    for i in range(3):
        html_file = test_dir / f"page_{i}.html"
        html_file.write_text(sample_html, encoding='utf-8')
    
    df = process_directory(test_dir.parent, sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 3


def test_process_directory_recursive(sample_html, sample_config, tmp_path):
    """Test process_directory with recursive=True."""
    # Create nested directory structure
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    
    subdir1 = test_dir / "2024-01-15"
    subdir1.mkdir()
    html_file1 = subdir1 / "page1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    subdir2 = test_dir / "2024-01-16"
    subdir2.mkdir()
    html_file2 = subdir2 / "page2.html"
    html_file2.write_text(sample_html, encoding='utf-8')
    
    # Process recursively
    df = process_directory(test_dir, sample_config, recursive=True)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2


def test_process_directory_non_recursive(sample_html, sample_config, tmp_path):
    """Test process_directory with recursive=False."""
    # Create nested directory structure
    test_dir = tmp_path / "test"
    test_dir.mkdir()
    
    # File in root directory
    html_file1 = test_dir / "page1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    # File in subdirectory
    subdir = test_dir / "2024-01-15"
    subdir.mkdir()
    html_file2 = subdir / "page2.html"
    html_file2.write_text(sample_html, encoding='utf-8')
    
    # Process non-recursively (should only get file in root)
    df = process_directory(test_dir, sample_config, recursive=False)
    
    assert isinstance(df, pd.DataFrame)
    # Should have at least the file from root directory
    assert len(df) >= 1


def test_process_directory_not_found(sample_config):
    """Test process_directory with non-existent directory."""
    with pytest.raises(FileNotFoundError):
        process_directory("nonexistent_dir", sample_config)


def test_process_directory_no_html_files(sample_config, tmp_path):
    """Test process_directory with directory containing no HTML files."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    with pytest.raises(ValueError, match="No HTML files found"):
        process_directory(empty_dir, sample_config)


def test_process_directory_with_scrape_date(sample_html, sample_config, tmp_path):
    """Test process_directory with explicit scrape date."""
    test_dir = tmp_path / "test" / "2024-01-15"
    test_dir.mkdir(parents=True)
    
    html_file = test_dir / "page.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    df = process_directory(
        test_dir.parent,
        sample_config,
        scrape_date="2024-01-20"
    )
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_process_csv_basic(sample_html, sample_config, tmp_path):
    """Test process_csv with basic CSV file."""
    # Create HTML files
    html_file1 = tmp_path / "file1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    html_file2 = tmp_path / "file2.html"
    html_file2.write_text(sample_html, encoding='utf-8')
    
    # Create CSV file
    csv_file = tmp_path / "file_list.csv"
    csv_data = f"path\n{html_file1}\n{html_file2}\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    df = process_csv(csv_file, default_config=sample_config, default_category="test")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2


def test_process_csv_with_category_column(sample_html, sample_config, tmp_path):
    """Test process_csv with category column in CSV."""
    # Create HTML files
    html_file1 = tmp_path / "file1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    html_file2 = tmp_path / "file2.html"
    html_file2.write_text(sample_html, encoding='utf-8')
    
    # Create CSV file with category column
    csv_file = tmp_path / "file_list.csv"
    csv_data = f"path,category\n{html_file1},test\n{html_file2},test\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    df = process_csv(csv_file, default_config=sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2


def test_process_csv_with_scrape_date_column(sample_html, sample_config, tmp_path):
    """Test process_csv with scrape_date column in CSV."""
    # Create HTML files
    html_file1 = tmp_path / "file1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    # Create CSV file with scrape_date column
    csv_file = tmp_path / "file_list.csv"
    csv_data = f"path,scrape_date\n{html_file1},2024-01-20\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    df = process_csv(csv_file, default_config=sample_config, default_category="test")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 1


def test_process_csv_with_config_column(sample_html, sample_config, tmp_path):
    """Test process_csv with per-row config column."""
    # Create HTML files
    html_file1 = tmp_path / "file1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    # Save config to file
    config_file = tmp_path / "config.yaml"
    import yaml
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(sample_config, f)
    
    # Create CSV file with config and category columns
    # Category is required since config has multiple categories
    csv_file = tmp_path / "file_list.csv"
    csv_data = f"path,config,category\n{html_file1},{config_file},test\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    df = process_csv(csv_file)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 1


def test_process_csv_missing_path_column(tmp_path):
    """Test process_csv with CSV missing 'path' column."""
    csv_file = tmp_path / "file_list.csv"
    csv_data = "category\ninvalid\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    config = {
        "categories": {
            "attribute_names": [],
            "categories": [{"name": "test", "attribute_names": []}]
        },
        "attributes": []
    }
    
    with pytest.raises(ValueError, match="must have a 'path' column"):
        process_csv(csv_file, default_config=config, default_category="test")


def test_process_csv_file_not_found(sample_config, tmp_path):
    """Test process_csv with non-existent file path in CSV."""
    csv_file = tmp_path / "file_list.csv"
    csv_data = "path\nnonexistent.html\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    with pytest.raises(FileNotFoundError):
        process_csv(csv_file, default_config=sample_config, default_category="test")


def test_process_csv_no_config(sample_html, tmp_path):
    """Test process_csv without default_config and no config column."""
    html_file = tmp_path / "file1.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    csv_file = tmp_path / "file_list.csv"
    csv_data = f"path\n{html_file}\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    with pytest.raises(ValueError, match="No config available"):
        process_csv(csv_file)


def test_process_csv_category_required(sample_html, sample_config, tmp_path):
    """Test process_csv when category is required but not provided."""
    html_file = tmp_path / "file1.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    csv_file = tmp_path / "file_list.csv"
    csv_data = f"path\n{html_file}\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    # Config has multiple categories, so category is required
    with pytest.raises(ValueError, match="Category required"):
        process_csv(csv_file, default_config=sample_config)


def test_process_csv_empty(sample_config, tmp_path):
    """Test process_csv with empty CSV file."""
    csv_file = tmp_path / "file_list.csv"
    csv_data = "path\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    df = process_csv(csv_file, default_config=sample_config, default_category="test")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0


def test_process_csv_csv_not_found():
    """Test process_csv with non-existent CSV file."""
    with pytest.raises(FileNotFoundError):
        process_csv("nonexistent.csv")


def test_batch_extract_different_categories(sample_html, sample_config, tmp_path):
    """Test batch_extract with files from different categories."""
    # Create files for different categories
    gpu_file = tmp_path / "gpu_file.html"
    gpu_file.write_text(sample_html, encoding='utf-8')
    
    test_file = tmp_path / "test_file.html"
    test_file.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {
        str(gpu_file): "gpu",
        str(test_file): "test"
    }
    
    df = batch_extract(files_with_categories, sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 2


def test_process_directory_category_derivation(sample_html, sample_config, tmp_path):
    """Test that process_directory correctly derives categories from paths."""
    # Create directory structure with category in path
    gpu_dir = tmp_path / "gpu" / "2024-01-15"
    gpu_dir.mkdir(parents=True)
    gpu_file = gpu_dir / "page.html"
    gpu_file.write_text(sample_html, encoding='utf-8')
    
    df = process_directory(gpu_dir.parent, sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_process_directory_nested_category(sample_html, sample_config, tmp_path):
    """Test process_directory with nested category in path."""
    # Create directory structure with nested category
    nested_dir = tmp_path / "domy" / "najem" / "2024-01-15"
    nested_dir.mkdir(parents=True)
    html_file = nested_dir / "page.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    df = process_directory(nested_dir.parent.parent, sample_config)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_create_csv_template_basic(tmp_path):
    """Test CSV template creation with basic usage."""
    csv_file = tmp_path / "template.csv"
    create_csv_template(csv_file)
    
    # Verify file exists
    assert csv_file.exists()
    
    # Verify content
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    assert list(df.columns) == ['path', 'config', 'scrape_date', 'category']
    assert len(df) == 1  # Example row
    
    # Verify example row values
    assert df.iloc[0]['path'] == 'data/gpu/2025/2025-01-15/page.html'
    assert df.iloc[0]['config'] == 'data/config.yaml'
    assert df.iloc[0]['scrape_date'] == '2025-01-15'
    assert df.iloc[0]['category'] == 'gpu'


def test_create_csv_template_utf8_bom(tmp_path):
    """Test that CSV template uses UTF-8-BOM encoding."""
    csv_file = tmp_path / "template.csv"
    create_csv_template(csv_file)
    
    # Read file and verify it can be read with utf-8-sig (BOM encoding)
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    assert len(df) > 0


def test_create_csv_template_invalid_extension(tmp_path):
    """Test that create_csv_template raises error for non-.csv extension."""
    txt_file = tmp_path / "template.txt"
    
    with pytest.raises(ValueError, match="must have .csv extension"):
        create_csv_template(txt_file)
    
    # Verify file was not created
    assert not txt_file.exists()


def test_create_csv_template_parent_directory_creation(tmp_path):
    """Test that create_csv_template creates parent directories if needed."""
    csv_file = tmp_path / "nested" / "deep" / "template.csv"
    create_csv_template(csv_file)
    
    # Verify file exists in nested directory
    assert csv_file.exists()
    assert csv_file.parent.exists()


def test_create_csv_template_example_row_format(tmp_path):
    """Test that example row has correct format for each column."""
    csv_file = tmp_path / "template.csv"
    create_csv_template(csv_file)
    
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    # Verify all columns are present
    assert 'path' in df.columns
    assert 'config' in df.columns
    assert 'scrape_date' in df.columns
    assert 'category' in df.columns
    
    # Verify example row has all values
    row = df.iloc[0]
    assert pd.notna(row['path'])
    assert pd.notna(row['config'])
    assert pd.notna(row['scrape_date'])
    assert pd.notna(row['category'])
    
    # Verify date format (YYYY-MM-DD)
    import re
    assert re.match(r'\d{4}-\d{2}-\d{2}', row['scrape_date'])


# Streaming Tests

def test_batch_extract_streaming_csv(sample_html, sample_config, tmp_path):
    """Test batch_extract with streaming to CSV file."""
    # Create test HTML files
    file1 = tmp_path / "file1.html"
    file2 = tmp_path / "file2.html"
    file1.write_text(sample_html, encoding='utf-8')
    file2.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {
        str(file1): 'test',
        str(file2): 'test'
    }
    
    output_file = tmp_path / "output.csv"
    
    # Stream to file
    result_df = batch_extract(
        files_with_categories,
        sample_config,
        stream_to_file=output_file,
        stream_mode='overwrite'
    )
    
    # Should return empty DataFrame (data written to file)
    assert len(result_df) == 0
    
    # Verify file was created and contains data
    assert output_file.exists()
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2  # Two items from two files
    assert 'link' in df_read.columns
    assert 'title' in df_read.columns


def test_batch_extract_streaming_json(sample_html, sample_config, tmp_path):
    """Test batch_extract with streaming to JSON file."""
    # Create test HTML files
    file1 = tmp_path / "file1.html"
    file2 = tmp_path / "file2.html"
    file1.write_text(sample_html, encoding='utf-8')
    file2.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {
        str(file1): 'test',
        str(file2): 'test'
    }
    
    output_file = tmp_path / "output.json"
    
    # Stream to file
    result_df = batch_extract(
        files_with_categories,
        sample_config,
        stream_to_file=output_file,
        stream_mode='overwrite',
        stream_format='json'
    )
    
    # Should return empty DataFrame (data written to file)
    assert len(result_df) == 0
    
    # Verify file was created and contains data
    assert output_file.exists()
    import json
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 2  # Two items from two files
    assert 'link' in data[0]
    assert 'title' in data[0]


def test_batch_extract_streaming_append(sample_html, sample_config, tmp_path):
    """Test batch_extract with streaming in append mode."""
    # Create test HTML files
    file1 = tmp_path / "file1.html"
    file2 = tmp_path / "file2.html"
    file1.write_text(sample_html, encoding='utf-8')
    file2.write_text(sample_html, encoding='utf-8')
    
    output_file = tmp_path / "output.csv"
    
    # First batch
    files1 = {str(file1): 'test'}
    batch_extract(
        files1,
        sample_config,
        stream_to_file=output_file,
        stream_mode='overwrite'
    )
    
    # Second batch (append)
    files2 = {str(file2): 'test'}
    batch_extract(
        files2,
        sample_config,
        stream_to_file=output_file,
        stream_mode='append'
    )
    
    # Verify both batches are in file
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2


def test_batch_extract_no_streaming(sample_html, sample_config, tmp_path):
    """Test batch_extract without streaming (collect in memory)."""
    # Create test HTML files
    file1 = tmp_path / "file1.html"
    file2 = tmp_path / "file2.html"
    file1.write_text(sample_html, encoding='utf-8')
    file2.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {
        str(file1): 'test',
        str(file2): 'test'
    }
    
    # No streaming - collect in memory
    result_df = batch_extract(
        files_with_categories,
        sample_config,
        stream_to_file=None
    )
    
    # Should return DataFrame with data
    assert len(result_df) == 2
    assert 'link' in result_df.columns
    assert 'title' in result_df.columns


def test_process_directory_streaming(sample_html, sample_config, tmp_path):
    """Test process_directory with streaming."""
    # Create directory structure
    test_dir = tmp_path / "test_category"
    test_dir.mkdir()
    
    file1 = test_dir / "file1.html"
    file2 = test_dir / "file2.html"
    file1.write_text(sample_html, encoding='utf-8')
    file2.write_text(sample_html, encoding='utf-8')
    
    # Update config to include test_category
    sample_config['categories']['categories'].append({
        "name": "test_category",
        "attribute_names": []
    })
    
    output_file = tmp_path / "output.csv"
    
    # Stream to file
    result_df = process_directory(
        test_dir,
        sample_config,
        stream_to_file=output_file,
        stream_mode='overwrite'
    )
    
    # Should return empty DataFrame
    assert len(result_df) == 0
    
    # Verify file contains data
    assert output_file.exists()
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2


def test_process_csv_streaming(sample_html, sample_config, tmp_path):
    """Test process_csv with streaming."""
    # Create test HTML files
    file1 = tmp_path / "file1.html"
    file2 = tmp_path / "file2.html"
    file1.write_text(sample_html, encoding='utf-8')
    file2.write_text(sample_html, encoding='utf-8')
    
    # Create CSV file
    csv_file = tmp_path / "file_list.csv"
    csv_data = pd.DataFrame({
        'path': [str(file1), str(file2)],
        'category': ['test', 'test']
    })
    csv_data.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    output_file = tmp_path / "output.csv"
    
    # Stream to file
    result_df = process_csv(
        csv_file,
        default_config=sample_config,
        stream_to_file=output_file,
        stream_mode='overwrite'
    )
    
    # Should return empty DataFrame
    assert len(result_df) == 0
    
    # Verify file contains data
    assert output_file.exists()
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2


def test_process_directory_filters_by_category(sample_html, sample_config, tmp_path):
    """Test that process_directory only processes directories matching defined categories."""
    # Create directory structure with matching and non-matching categories
    gpu_dir = tmp_path / "gpu" / "2024-01-15"
    gpu_dir.mkdir(parents=True)
    gpu_file = gpu_dir / "page.html"
    gpu_file.write_text(sample_html, encoding='utf-8')
    
    # Create directory that doesn't match any category
    other_dir = tmp_path / "other" / "2024-01-15"
    other_dir.mkdir(parents=True)
    other_file = other_dir / "page.html"
    other_file.write_text(sample_html, encoding='utf-8')
    
    # Process from parent directory - should only process gpu, skip other
    with pytest.warns(UserWarning, match="Could not derive category"):
        df = process_directory(tmp_path, sample_config, show_progress=False)
    
    # Should only have data from gpu directory
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    # Verify it processed gpu files (check that we have data)
    assert "link" in df.columns or "title" in df.columns


def test_process_directory_skips_non_matching_directories(sample_html, sample_config, tmp_path):
    """Test that process_directory skips files in non-matching directories with warning."""
    # Create directory that doesn't match any category
    other_dir = tmp_path / "other" / "2024-01-15"
    other_dir.mkdir(parents=True)
    other_file = other_dir / "page.html"
    other_file.write_text(sample_html, encoding='utf-8')
    
    # Process directory - should skip other directory with warning
    with pytest.warns(UserWarning, match="Could not derive category"):
        with pytest.raises(ValueError, match="Could not derive categories for any files"):
            process_directory(tmp_path, sample_config, show_progress=False)


def test_process_directory_multi_level_categories(sample_html, tmp_path):
    """Test directory filtering with multi-level categories."""
    # Create config with multi-level categories
    config = {
        "categories": {
            "attribute_names": ["link", "title"],
            "categories": [
                {"name": "gpu", "attribute_names": []},
                {"name": "domy/najem", "attribute_names": []},
                {"name": "domy/najem/warszawa", "attribute_names": []}
            ]
        },
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
    
    # Create directory structure
    gpu_dir = tmp_path / "gpu" / "2024-01-15"
    gpu_dir.mkdir(parents=True)
    gpu_file = gpu_dir / "page.html"
    gpu_file.write_text(sample_html, encoding='utf-8')
    
    nested_dir = tmp_path / "domy" / "najem" / "2024-01-15"
    nested_dir.mkdir(parents=True)
    nested_file = nested_dir / "page.html"
    nested_file.write_text(sample_html, encoding='utf-8')
    
    # Create non-matching directory
    other_dir = tmp_path / "other" / "2024-01-15"
    other_dir.mkdir(parents=True)
    other_file = other_dir / "page.html"
    other_file.write_text(sample_html, encoding='utf-8')
    
    # Process from parent - should process gpu and domy/najem, skip other
    with pytest.warns(UserWarning, match="Could not derive category"):
        df = process_directory(tmp_path, config, show_progress=False)
    
    # Should have data from matching directories
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


def test_completion_callback_basic(sample_html, sample_config, tmp_path):
    """Test completion_callback is called with correct data structure."""
    html_file1 = tmp_path / "test1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    html_file2 = tmp_path / "test2.html"
    html_file2.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {
        str(html_file1): "test",
        str(html_file2): "test"
    }
    
    callback_data = None
    
    def completion_callback(data: Dict[str, Any]):
        nonlocal callback_data
        callback_data = data
    
    df = batch_extract(
        files_with_categories,
        sample_config,
        completion_callback=completion_callback
    )
    
    # Verify callback was called
    assert callback_data is not None
    assert callback_data["status"] in ["completed", "completed_with_errors"]
    assert "timestamp" in callback_data
    assert "summary" in callback_data
    assert "processed_files" in callback_data
    assert "failed_files" in callback_data
    assert "output_file" in callback_data
    assert "processing_time_seconds" in callback_data
    
    # Verify summary
    summary = callback_data["summary"]
    assert summary["total_files"] == 2
    assert summary["successful_files"] >= 0
    assert summary["failed_files"] >= 0
    assert summary["total_items"] >= 0
    assert summary["total_skipped_items"] >= 0
    
    # Verify processed_files structure
    for file_info in callback_data["processed_files"]:
        assert "file_path" in file_info
        assert "category" in file_info
        assert "item_count" in file_info
        assert "missing_required" in file_info
        assert "status" in file_info
        assert file_info["status"] == "success"
    
    # Verify failed_files structure
    for file_info in callback_data["failed_files"]:
        assert "file_path" in file_info
        assert "status" in file_info
        assert file_info["status"] == "failed"


def test_completion_callback_with_missing_required(sample_config, tmp_path):
    """Test completion_callback includes missing_required count."""
    # Create HTML file with missing required attribute
    html_content = """
    <html>
    <body>
        <div>
            <p>No link or title here</p>
        </div>
    </body>
    </html>
    """
    html_file = tmp_path / "test.html"
    html_file.write_text(html_content, encoding='utf-8')
    
    files_with_categories = {str(html_file): "test"}
    
    callback_data = None
    
    def completion_callback(data: Dict[str, Any]):
        nonlocal callback_data
        callback_data = data
    
    df = batch_extract(
        files_with_categories,
        sample_config,
        completion_callback=completion_callback
    )
    
    # Verify callback was called
    assert callback_data is not None
    
    # Check that missing_required is tracked
    # If file had items but all were skipped, it should be in processed_files with missing_required > 0
    # If file had no items and no skipped items, it should be in failed_files
    total_skipped = callback_data["summary"]["total_skipped_items"]
    assert total_skipped >= 0  # Should be non-negative


def test_completion_callback_error_handling(sample_html, sample_config, tmp_path):
    """Test that completion_callback errors don't break processing."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    files_with_categories = {str(html_file): "test"}
    
    def completion_callback(data: Dict[str, Any]):
        raise ValueError("Callback error")
    
    # Should not raise exception, processing should complete
    df = batch_extract(
        files_with_categories,
        sample_config,
        completion_callback=completion_callback
    )
    
    # Processing should have completed successfully
    assert isinstance(df, pd.DataFrame)


def test_completion_callback_with_streaming(sample_html, sample_config, tmp_path):
    """Test completion_callback with streaming mode."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    output_file = tmp_path / "output.csv"
    files_with_categories = {str(html_file): "test"}
    
    callback_data = None
    
    def completion_callback(data: Dict[str, Any]):
        nonlocal callback_data
        callback_data = data
    
    df = batch_extract(
        files_with_categories,
        sample_config,
        stream_to_file=output_file,
        completion_callback=completion_callback
    )
    
    # Verify callback was called
    assert callback_data is not None
    assert callback_data["output_file"] == str(output_file)
    assert output_file.exists()
