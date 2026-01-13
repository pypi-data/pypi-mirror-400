"""
Unit tests for the output formatting module.

Tests cover save_output() function and format detection.
"""

import pytest
import pandas as pd
from pathlib import Path
import json
import tempfile
import os

from src.html_extract.output import (
    save_output, 
    _detect_format,
    CSVStreamWriter,
    JSONStreamWriter,
    _create_stream_writer
)


def test_save_output_csv(tmp_path):
    """Test saving DataFrame to CSV file."""
    df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    
    output_file = tmp_path / "output.csv"
    save_output(df, output_file)
    
    assert output_file.exists()
    
    # Verify CSV content
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 3
    assert list(df_read.columns) == ['col1', 'col2']


def test_save_output_json(tmp_path):
    """Test saving DataFrame to JSON file."""
    df = pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })
    
    output_file = tmp_path / "output.json"
    save_output(df, output_file)
    
    assert output_file.exists()
    
    # Verify JSON content
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]['col1'] == 1
    assert data[0]['col2'] == 'a'


def test_save_output_auto_detect_csv(tmp_path):
    """Test auto-detection of CSV format from extension."""
    df = pd.DataFrame({'col1': [1, 2]})
    
    output_file = tmp_path / "output.csv"
    save_output(df, output_file, format=None)
    
    assert output_file.exists()
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2


def test_save_output_auto_detect_json(tmp_path):
    """Test auto-detection of JSON format from extension."""
    df = pd.DataFrame({'col1': [1, 2]})
    
    output_file = tmp_path / "output.json"
    save_output(df, output_file, format=None)
    
    assert output_file.exists()
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)


def test_save_output_explicit_format_csv(tmp_path):
    """Test explicit CSV format specification."""
    df = pd.DataFrame({'col1': [1, 2]})
    
    output_file = tmp_path / "output.txt"  # Non-standard extension
    save_output(df, output_file, format='csv')
    
    assert output_file.exists()
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2


def test_save_output_explicit_format_json(tmp_path):
    """Test explicit JSON format specification."""
    df = pd.DataFrame({'col1': [1, 2]})
    
    output_file = tmp_path / "output.txt"  # Non-standard extension
    save_output(df, output_file, format='json')
    
    assert output_file.exists()
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert isinstance(data, list)


def test_save_output_defaults_to_csv(tmp_path):
    """Test that unknown extensions default to CSV."""
    df = pd.DataFrame({'col1': [1, 2]})
    
    output_file = tmp_path / "output.txt"  # Unknown extension
    save_output(df, output_file, format=None)
    
    assert output_file.exists()
    # Should be CSV format
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2


def test_save_output_empty_dataframe(tmp_path):
    """Test saving empty DataFrame."""
    df = pd.DataFrame()
    
    output_file = tmp_path / "output.csv"
    save_output(df, output_file)
    
    assert output_file.exists()
    # Empty DataFrame with no columns creates empty file, verify it exists
    assert output_file.stat().st_size >= 0


def test_save_output_creates_parent_directories(tmp_path):
    """Test that parent directories are created if needed."""
    df = pd.DataFrame({'col1': [1, 2]})
    
    output_file = tmp_path / "subdir" / "nested" / "output.csv"
    save_output(df, output_file)
    
    assert output_file.exists()
    assert output_file.parent.exists()


def test_save_output_unicode_characters(tmp_path):
    """Test saving DataFrame with Unicode characters."""
    df = pd.DataFrame({
        'text': ['Test', 'Przykład', '1000 zł']
    })
    
    output_file = tmp_path / "output.csv"
    save_output(df, output_file)
    
    assert output_file.exists()
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert df_read['text'].iloc[1] == 'Przykład'
    assert df_read['text'].iloc[2] == '1000 zł'


def test_save_output_invalid_dataframe_type():
    """Test that non-DataFrame raises TypeError."""
    with pytest.raises(TypeError, match="Expected pd.DataFrame"):
        save_output("not a dataframe", "output.csv")


def test_save_output_none_path():
    """Test that None output_path raises ValueError."""
    df = pd.DataFrame({'col1': [1, 2]})
    
    with pytest.raises(ValueError, match="output_path is required"):
        save_output(df, None)


def test_save_output_invalid_format(tmp_path):
    """Test that invalid format raises ValueError."""
    df = pd.DataFrame({'col1': [1, 2]})
    
    with pytest.raises(ValueError, match="Invalid format"):
        save_output(df, tmp_path / "output.csv", format='xml')


def test_detect_format_from_extension():
    """Test format detection from file extension."""
    assert _detect_format("output.csv", None) == 'csv'
    assert _detect_format("output.json", None) == 'json'
    assert _detect_format("output.txt", None) == 'csv'  # Defaults to CSV


def test_detect_format_explicit():
    """Test explicit format specification."""
    assert _detect_format("output.txt", 'csv') == 'csv'
    assert _detect_format("output.txt", 'json') == 'json'


def test_detect_format_invalid():
    """Test that invalid explicit format raises ValueError."""
    with pytest.raises(ValueError, match="Invalid format"):
        _detect_format("output.csv", 'xml')


# Stream Writer Tests

def test_csv_stream_writer_overwrite(tmp_path):
    """Test CSVStreamWriter in overwrite mode."""
    output_file = tmp_path / "output.csv"
    
    df1 = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
    df2 = pd.DataFrame({'col1': [3, 4], 'col2': ['c', 'd']})
    
    with CSVStreamWriter(output_file, mode='overwrite') as writer:
        writer.write_dataframe(df1)
        writer.write_dataframe(df2)
    
    assert output_file.exists()
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 4
    assert list(df_read.columns) == ['col1', 'col2']
    assert df_read['col1'].tolist() == [1, 2, 3, 4]


def test_csv_stream_writer_append(tmp_path):
    """Test CSVStreamWriter in append mode."""
    output_file = tmp_path / "output.csv"
    
    # Create initial file
    df1 = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
    df1.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # Append more data
    df2 = pd.DataFrame({'col1': [3, 4], 'col2': ['c', 'd']})
    with CSVStreamWriter(output_file, mode='append') as writer:
        writer.write_dataframe(df2)
    
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 4
    assert df_read['col1'].tolist() == [1, 2, 3, 4]


def test_csv_stream_writer_empty_dataframe(tmp_path):
    """Test CSVStreamWriter with empty DataFrame."""
    output_file = tmp_path / "output.csv"
    
    df = pd.DataFrame({'col1': [1, 2]})
    empty_df = pd.DataFrame()
    
    with CSVStreamWriter(output_file, mode='overwrite') as writer:
        writer.write_dataframe(df)
        writer.write_dataframe(empty_df)  # Should be ignored
    
    df_read = pd.read_csv(output_file, encoding='utf-8-sig')
    assert len(df_read) == 2


def test_json_stream_writer_overwrite(tmp_path):
    """Test JSONStreamWriter in overwrite mode."""
    output_file = tmp_path / "output.json"
    
    df1 = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
    df2 = pd.DataFrame({'col1': [3, 4], 'col2': ['c', 'd']})
    
    with JSONStreamWriter(output_file, mode='overwrite') as writer:
        writer.write_dataframe(df1)
        writer.write_dataframe(df2)
    
    assert output_file.exists()
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]['col1'] == 1
    assert data[3]['col1'] == 4


def test_json_stream_writer_append(tmp_path):
    """Test JSONStreamWriter in append mode."""
    output_file = tmp_path / "output.json"
    
    # Create initial file
    df1 = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(df1.to_dict('records'), f, indent=2)
    
    # Append more data
    df2 = pd.DataFrame({'col1': [3, 4], 'col2': ['c', 'd']})
    with JSONStreamWriter(output_file, mode='append') as writer:
        writer.write_dataframe(df2)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]['col1'] == 1
    assert data[3]['col1'] == 4


def test_json_stream_writer_empty_dataframe(tmp_path):
    """Test JSONStreamWriter with empty DataFrame."""
    output_file = tmp_path / "output.json"
    
    df = pd.DataFrame({'col1': [1, 2]})
    empty_df = pd.DataFrame()
    
    with JSONStreamWriter(output_file, mode='overwrite') as writer:
        writer.write_dataframe(df)
        writer.write_dataframe(empty_df)  # Should be ignored
    
    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data) == 2


def test_create_stream_writer_csv(tmp_path):
    """Test _create_stream_writer creates CSVStreamWriter."""
    output_file = tmp_path / "output.csv"
    writer = _create_stream_writer(output_file, 'csv', mode='overwrite')
    
    assert isinstance(writer, CSVStreamWriter)
    writer.close()


def test_create_stream_writer_json(tmp_path):
    """Test _create_stream_writer creates JSONStreamWriter."""
    output_file = tmp_path / "output.json"
    writer = _create_stream_writer(output_file, 'json', mode='overwrite')
    
    assert isinstance(writer, JSONStreamWriter)
    writer.close()


def test_create_stream_writer_invalid_format(tmp_path):
    """Test _create_stream_writer with invalid format."""
    output_file = tmp_path / "output.txt"
    
    with pytest.raises(ValueError, match="Invalid format"):
        _create_stream_writer(output_file, 'xml', mode='overwrite')
