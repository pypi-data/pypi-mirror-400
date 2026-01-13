"""
Unit tests for the CLI interface.

Tests cover all CLI functionality including single file processing,
directory processing, CSV processing, template generation, and stdout output.
"""

import subprocess
import sys
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os

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
def sample_config(tmp_path):
    """Create a sample configuration file for testing."""
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


def run_cli(args, cwd=None):
    """Run CLI script and return result."""
    if cwd is None:
        cwd = Path(__file__).parent.parent
    
    # Use the python module directly
    cmd = [sys.executable, "-m", "html_extract.cli"] + args
    
    # Add src to PYTHONPATH
    env = os.environ.copy()
    src_path = str(cwd / "src")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = src_path + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = src_path

    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result


def test_cli_help():
    """Test CLI help message."""
    result = run_cli(['-h'])
    assert result.returncode == 0
    assert 'html-extract' in result.stdout
    assert 'Extract structured data' in result.stdout


def test_cli_template_config(sample_config, tmp_path):
    """Test CLI template generation for config."""
    template_path = tmp_path / "new_config.yaml"
    result = run_cli(['-t', 'config', str(template_path)])
    
    assert result.returncode == 0
    assert template_path.exists()
    assert 'Configuration template created' in result.stdout


def test_cli_template_csv(tmp_path):
    """Test CLI template generation for CSV."""
    template_path = tmp_path / "file_list.csv"
    result = run_cli(['-t', 'csv', str(template_path)])
    
    assert result.returncode == 0
    assert template_path.exists()
    assert 'CSV template created' in result.stdout
    
    # Verify CSV content
    df = pd.read_csv(template_path, encoding='utf-8-sig')
    assert list(df.columns) == ['path', 'config', 'scrape_date', 'category']


def test_cli_template_invalid_type(tmp_path):
    """Test CLI template with invalid type."""
    template_path = tmp_path / "template.txt"
    result = run_cli(['-t', 'invalid', str(template_path)])
    
    assert result.returncode == 1
    assert 'Invalid template type' in result.stderr


def test_cli_single_file(sample_html, sample_config, tmp_path):
    """Test CLI single file processing."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    output_file = tmp_path / "output.csv"
    result = run_cli([
        str(html_file),
        '-c', str(sample_config),
        '-k', 'test',
        '-o', str(output_file)
    ])
    
    assert result.returncode == 0
    assert output_file.exists()
    
    # Verify output
    df = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df) > 0
    assert 'link' in df.columns
    assert 'title' in df.columns


def test_cli_single_file_stdout(sample_html, sample_config, tmp_path):
    """Test CLI single file processing with stdout output."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    result = run_cli([
        str(html_file),
        '-c', str(sample_config),
        '-k', 'test'
    ])
    
    assert result.returncode == 0
    assert len(result.stdout) > 0
    # Should contain CSV headers
    assert 'link' in result.stdout or 'title' in result.stdout


def test_cli_single_file_missing_category(sample_html, sample_config, tmp_path):
    """Test CLI single file processing with missing category for multi-category config."""
    # Create config with multiple categories
    multi_config = tmp_path / "multi_config.yaml"
    multi_config.write_text("""
categories:
  attribute_names: [link]
  categories:
    - name: test1
      attribute_names: []
    - name: test2
      attribute_names: []

attributes:
  - name: link
    required: true
    extract:
      type: text
      selector: a
      extract_attribute: href
""", encoding='utf-8')
    
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    result = run_cli([
        str(html_file),
        '-c', str(multi_config)
    ])
    
    assert result.returncode == 1
    assert 'Category required' in result.stderr
    assert 'test1' in result.stderr or 'test2' in result.stderr


def test_cli_directory(sample_html, sample_config, tmp_path):
    """Test CLI directory processing."""
    # Create directory structure: test/2024-01-15/page.html
    test_dir = tmp_path / "test" / "2024-01-15"
    test_dir.mkdir(parents=True)
    
    html_file = test_dir / "page.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    output_file = tmp_path / "output.csv"
    result = run_cli([
        str(test_dir.parent),
        '-c', str(sample_config),
        '-o', str(output_file)
    ])
    
    assert result.returncode == 0
    assert output_file.exists()
    
    # Verify output
    df = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df) > 0


def test_cli_csv_processing(sample_html, sample_config, tmp_path):
    """Test CLI CSV bulk processing."""
    # Create HTML files
    html_file1 = tmp_path / "file1.html"
    html_file1.write_text(sample_html, encoding='utf-8')
    
    html_file2 = tmp_path / "file2.html"
    html_file2.write_text(sample_html, encoding='utf-8')
    
    # Create CSV file
    csv_file = tmp_path / "file_list.csv"
    csv_data = f"path,category\n{html_file1},test\n{html_file2},test\n"
    csv_file.write_text(csv_data, encoding='utf-8-sig')
    
    output_file = tmp_path / "output.csv"
    result = run_cli([
        str(csv_file),
        '-c', str(sample_config),
        '-o', str(output_file)
    ])
    
    assert result.returncode == 0
    assert output_file.exists()
    
    # Verify output
    df = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df) >= 2


def test_cli_scrape_date(sample_html, sample_config, tmp_path):
    """Test CLI with explicit scrape date."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    output_file = tmp_path / "output.csv"
    result = run_cli([
        str(html_file),
        '-c', str(sample_config),
        '-k', 'test',
        '-d', '2024-01-20',
        '-o', str(output_file)
    ])
    
    assert result.returncode == 0
    assert output_file.exists()


def test_cli_scrape_date_current(sample_html, sample_config, tmp_path):
    """Test CLI with current date."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    output_file = tmp_path / "output.csv"
    result = run_cli([
        str(html_file),
        '-c', str(sample_config),
        '-k', 'test',
        '-d', 'current',
        '-o', str(output_file)
    ])
    
    assert result.returncode == 0
    assert output_file.exists()


def test_cli_scrape_date_today(sample_html, sample_config, tmp_path):
    """Test CLI with today date."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    output_file = tmp_path / "output.csv"
    result = run_cli([
        str(html_file),
        '-c', str(sample_config),
        '-k', 'test',
        '-d', 'today',
        '-o', str(output_file)
    ])
    
    assert result.returncode == 0
    assert output_file.exists()


def test_cli_invalid_date(sample_html, sample_config, tmp_path):
    """Test CLI with invalid date format."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    result = run_cli([
        str(html_file),
        '-c', str(sample_config),
        '-k', 'test',
        '-d', 'invalid-date'
    ])
    
    assert result.returncode == 1
    assert 'Invalid date format' in result.stderr


def test_cli_missing_input(sample_config):
    """Test CLI with missing input argument."""
    result = run_cli(['-c', str(sample_config)])
    
    assert result.returncode != 0
    assert 'INPUT is required' in result.stderr or 'required' in result.stderr.lower()


def test_cli_missing_config(tmp_path):
    """Test CLI with missing config argument."""
    html_file = tmp_path / "test.html"
    html_file.write_text("<html><body>Test</body></html>", encoding='utf-8')
    
    result = run_cli([str(html_file)])
    
    assert result.returncode != 0
    assert 'config' in result.stderr.lower() or 'required' in result.stderr.lower()


def test_cli_file_not_found(sample_config):
    """Test CLI with non-existent input file."""
    result = run_cli([
        'nonexistent.html',
        '-c', str(sample_config),
        '-k', 'test'
    ])
    
    assert result.returncode == 1
    assert 'not exist' in result.stderr.lower() or 'not found' in result.stderr.lower()


def test_cli_config_not_found(tmp_path):
    """Test CLI with non-existent config file."""
    html_file = tmp_path / "test.html"
    html_file.write_text("<html><body>Test</body></html>", encoding='utf-8')
    
    result = run_cli([
        str(html_file),
        '-c', 'nonexistent.yaml',
        '-k', 'test'
    ])
    
    assert result.returncode == 1
    assert 'not found' in result.stderr.lower() or 'Error loading' in result.stderr


def test_cli_json_output(sample_html, sample_config, tmp_path):
    """Test CLI with JSON output format."""
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    output_file = tmp_path / "output.json"
    result = run_cli([
        str(html_file),
        '-c', str(sample_config),
        '-k', 'test',
        '-o', str(output_file)
    ])
    
    assert result.returncode == 0
    assert output_file.exists()
    
    # Verify JSON output
    import json
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) > 0


def test_cli_directory_not_found(sample_config):
    """Test CLI with non-existent directory."""
    result = run_cli([
        'nonexistent_dir',
        '-c', str(sample_config)
    ])
    
    assert result.returncode == 1
    assert 'not exist' in result.stderr.lower() or 'not found' in result.stderr.lower()


def test_cli_csv_not_found(sample_config):
    """Test CLI with non-existent CSV file."""
    result = run_cli([
        'nonexistent.csv',
        '-c', str(sample_config)
    ])
    
    assert result.returncode == 1
    assert 'not exist' in result.stderr.lower() or 'not found' in result.stderr.lower()


def test_cli_template_config_json(tmp_path):
    """Test CLI template generation for JSON config."""
    template_path = tmp_path / "new_config.json"
    result = run_cli(['-t', 'config', str(template_path)])
    
    assert result.returncode == 0
    assert template_path.exists()
    
    # Verify it's valid JSON
    import json
    with open(template_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert 'categories' in data
    assert 'attributes' in data


def test_cli_empty_output(sample_config, tmp_path):
    """Test CLI with HTML file that produces no data."""
    # Create HTML file with no matching content
    html_file = tmp_path / "empty.html"
    html_file.write_text("<html><body><p>No matching content</p></body></html>", encoding='utf-8')
    
    output_file = tmp_path / "output.csv"
    result = run_cli([
        str(html_file),
        '-c', str(sample_config),
        '-k', 'test',
        '-o', str(output_file)
    ])
    
    # Should succeed but produce empty output
    assert result.returncode == 0
    assert output_file.exists()
    
    df = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df) == 0  # Empty DataFrame


def test_cli_category_validation(sample_html, tmp_path):
    """Test CLI category validation with invalid category."""
    # Create config with multiple categories
    multi_config = tmp_path / "multi_config.yaml"
    multi_config.write_text("""
categories:
  attribute_names: [link]
  categories:
    - name: test1
      attribute_names: []
    - name: test2
      attribute_names: []

attributes:
  - name: link
    required: true
    extract:
      type: text
      selector: a
      extract_attribute: href
""", encoding='utf-8')
    
    html_file = tmp_path / "test.html"
    html_file.write_text(sample_html, encoding='utf-8')
    
    result = run_cli([
        str(html_file),
        '-c', str(multi_config),
        '-k', 'invalid_category'
    ])
    
    # Should fail with category validation error
    assert result.returncode == 1
    # Error should mention category issue
    stderr_lower = result.stderr.lower()
    assert 'category' in stderr_lower or 'not found' in stderr_lower
