"""
Unit tests for the configuration management module.

Tests cover load_config() and create_config_template() functions.
"""

import pytest
import yaml
import json
from pathlib import Path
import tempfile

from src.html_extract.config import load_config, create_config_template


def test_load_config_from_dict():
    """Test loading config from dict object."""
    config_dict = {
        'categories': {
            'attribute_names': ['link', 'title'],
            'categories': [
                {'name': 'test', 'attribute_names': []}
            ]
        },
        'attributes': [
            {'name': 'link', 'required': True},
            {'name': 'title', 'required': False}
        ]
    }
    
    result = load_config(config_dict)
    assert result == config_dict
    assert 'categories' in result
    assert 'attributes' in result
    assert isinstance(result['categories'], dict)
    assert 'attribute_names' in result['categories']


def test_load_config_from_yaml_file(tmp_path):
    """Test loading config from YAML file."""
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
  - name: title
    required: false
"""
    config_file.write_text(config_content, encoding='utf-8')
    
    result = load_config(config_file)
    assert 'categories' in result
    assert 'attributes' in result
    assert isinstance(result['categories'], dict)
    assert 'attribute_names' in result['categories']


def test_load_config_from_json_file(tmp_path):
    """Test loading config from JSON file."""
    config_file = tmp_path / "config.json"
    config_content = {
        'categories': {
            'attribute_names': ['link', 'title'],
            'categories': [
                {'name': 'test', 'attribute_names': []}
            ]
        },
        'attributes': [
            {'name': 'link', 'required': True},
            {'name': 'title', 'required': False}
        ]
    }
    config_file.write_text(json.dumps(config_content), encoding='utf-8')
    
    result = load_config(config_file)
    assert 'categories' in result
    assert 'attributes' in result
    assert isinstance(result['categories'], dict)
    assert 'attribute_names' in result['categories']


def test_load_config_from_string_path(tmp_path):
    """Test loading config from string path."""
    config_file = tmp_path / "config.yaml"
    config_content = """
categories:
  attribute_names: [link]
  categories:
    - name: test
      attribute_names: []

attributes:
  - name: link
    required: true
"""
    config_file.write_text(config_content, encoding='utf-8')
    
    result = load_config(str(config_file))
    assert 'categories' in result
    assert 'attributes' in result
    assert isinstance(result['categories'], dict)


def test_load_config_file_not_found():
    """Test that missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config('nonexistent.yaml')


def test_load_config_invalid_dict_missing_categories():
    """Test that dict without categories raises ValueError."""
    invalid_dict = {'attributes': []}
    
    with pytest.raises(ValueError, match="categories"):
        load_config(invalid_dict)


def test_load_config_invalid_dict_missing_attributes():
    """Test that dict without attributes raises ValueError."""
    invalid_dict = {'categories': []}
    
    with pytest.raises(ValueError, match="attributes"):
        load_config(invalid_dict)


def test_load_config_invalid_yaml_syntax(tmp_path):
    """Test that invalid YAML syntax raises error."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("invalid: yaml: syntax: [", encoding='utf-8')
    
    with pytest.raises(yaml.YAMLError):
        load_config(config_file)


def test_load_config_invalid_json_syntax(tmp_path):
    """Test that invalid JSON syntax raises error."""
    config_file = tmp_path / "config.json"
    config_file.write_text("{invalid json}", encoding='utf-8')
    
    with pytest.raises(ValueError, match="Invalid JSON syntax"):
        load_config(config_file)


def test_load_config_empty_yaml_file(tmp_path):
    """Test that empty YAML file raises ValueError."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("", encoding='utf-8')
    
    with pytest.raises(ValueError, match="empty"):
        load_config(config_file)


def test_load_config_empty_json_file(tmp_path):
    """Test that empty JSON file raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text("", encoding='utf-8')
    
    with pytest.raises(ValueError, match="empty"):
        load_config(config_file)


def test_load_config_yaml_not_dict(tmp_path):
    """Test that YAML file with non-dict content raises ValueError."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("- item1\n- item2", encoding='utf-8')
    
    with pytest.raises(ValueError, match="dictionary"):
        load_config(config_file)


def test_load_config_json_not_dict(tmp_path):
    """Test that JSON file with non-dict content raises ValueError."""
    config_file = tmp_path / "config.json"
    config_file.write_text("[1, 2, 3]", encoding='utf-8')
    
    with pytest.raises(ValueError, match="dictionary"):
        load_config(config_file)


def test_load_config_unsupported_file_format(tmp_path):
    """Test that unsupported file format raises ValueError."""
    config_file = tmp_path / "config.xml"
    config_file.write_text("<config></config>", encoding='utf-8')
    
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_config(config_file)


def test_load_config_unsupported_source_type():
    """Test that unsupported source type raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported source type"):
        load_config(123)  # Integer, not supported


def test_create_config_template_yaml(tmp_path):
    """Test creating YAML config template."""
    template_file = tmp_path / "config.yaml"
    create_config_template(template_file)
    
    assert template_file.exists()
    
    # Verify it's valid YAML
    with open(template_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    assert 'categories' in config
    assert 'attributes' in config


def test_create_config_template_json(tmp_path):
    """Test creating JSON config template."""
    template_file = tmp_path / "config.json"
    create_config_template(template_file, format='json')
    
    assert template_file.exists()
    
    # Verify it's valid JSON
    with open(template_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    assert 'categories' in config
    assert 'attributes' in config


def test_create_config_template_auto_detect_yaml(tmp_path):
    """Test auto-detection of YAML format from extension."""
    template_file = tmp_path / "config.yaml"
    create_config_template(template_file, format='auto')
    
    assert template_file.exists()
    with open(template_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    assert 'categories' in config


def test_create_config_template_auto_detect_json(tmp_path):
    """Test auto-detection of JSON format from extension."""
    template_file = tmp_path / "config.json"
    create_config_template(template_file, format='auto')
    
    assert template_file.exists()
    with open(template_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    assert 'categories' in config


def test_create_config_template_creates_parent_directories(tmp_path):
    """Test that parent directories are created if needed."""
    template_file = tmp_path / "subdir" / "nested" / "config.yaml"
    create_config_template(template_file)
    
    assert template_file.exists()
    assert template_file.parent.exists()


def test_create_config_template_invalid_format(tmp_path):
    """Test that invalid format raises ValueError."""
    template_file = tmp_path / "config.txt"
    
    with pytest.raises(ValueError, match="Invalid format"):
        create_config_template(template_file, format='xml')


def test_create_config_template_unknown_extension_raises_error(tmp_path):
    """Test that unknown extension raises ValueError."""
    template_file = tmp_path / "config.txt"
    
    with pytest.raises(ValueError, match="Cannot determine format"):
        create_config_template(template_file, format='auto')


def test_load_config_with_common_attributes_dict():
    """Test loading config with common attributes (new format) from dict."""
    config_dict = {
        'categories': {
            'attribute_names': ['link', 'title', 'price'],
            'categories': [
                {'name': 'phones', 'attribute_names': ['is_new']},
                {'name': 'gpu', 'attribute_names': ['brand']}
            ]
        },
        'attributes': [
            {'name': 'link', 'required': True},
            {'name': 'title', 'required': True},
            {'name': 'price', 'required': False},
            {'name': 'is_new', 'required': False},
            {'name': 'brand', 'required': False}
        ]
    }
    
    result = load_config(config_dict)
    assert result == config_dict
    assert 'categories' in result
    assert isinstance(result['categories'], dict)
    assert 'attribute_names' in result['categories']
    assert result['categories']['attribute_names'] == ['link', 'title', 'price']


def test_load_config_with_common_attributes_yaml(tmp_path):
    """Test loading config with common attributes from YAML file."""
    config_file = tmp_path / "config.yaml"
    # Note: YAML structure for mixed dict/list is tricky
    # We'll use a structure that works: categories as dict with attribute_names and a list key
    config_content = """
categories:
  attribute_names: [link, title, price]
  categories:
    - name: phones
      attribute_names: [is_new]
    - name: gpu
      attribute_names: [brand]

attributes:
  - name: link
    required: true
  - name: title
    required: true
  - name: price
    required: false
  - name: is_new
    required: false
  - name: brand
    required: false
"""
    config_file.write_text(config_content, encoding='utf-8')
    
    result = load_config(config_file)
    assert 'categories' in result
    assert isinstance(result['categories'], dict)
    assert 'attribute_names' in result['categories']
    assert result['categories']['attribute_names'] == ['link', 'title', 'price']


def test_load_config_with_common_attributes_json(tmp_path):
    """Test loading config with common attributes from JSON file."""
    config_file = tmp_path / "config.json"
    config_content = {
        'categories': {
            'attribute_names': ['link', 'title', 'price'],
            'categories': [
                {'name': 'phones', 'attribute_names': ['is_new']},
                {'name': 'gpu', 'attribute_names': ['brand']}
            ]
        },
        'attributes': [
            {'name': 'link', 'required': True},
            {'name': 'title', 'required': True},
            {'name': 'price', 'required': False},
            {'name': 'is_new', 'required': False},
            {'name': 'brand', 'required': False}
        ]
    }
    config_file.write_text(json.dumps(config_content), encoding='utf-8')
    
    result = load_config(config_file)
    assert 'categories' in result
    assert isinstance(result['categories'], dict)
    assert 'attribute_names' in result['categories']


def test_load_config_requires_dict_format():
    """Test that categories must be a dict with attribute_names key."""
    config_dict = {
        'categories': [
            {'name': 'test', 'attribute_names': ['link', 'title']}
        ],
        'attributes': [
            {'name': 'link', 'required': True},
            {'name': 'title', 'required': False}
        ]
    }
    
    with pytest.raises(ValueError, match="categories must be a dictionary with 'attribute_names' key"):
        load_config(config_dict)


def test_validation_missing_common_attribute():
    """Test validation error when common attribute doesn't exist."""
    config_dict = {
        'categories': {
            'attribute_names': ['link', 'title', 'nonexistent'],
            'categories': [
                {'name': 'test', 'attribute_names': ['link']}
            ]
        },
        'attributes': [
            {'name': 'link', 'required': True},
            {'name': 'title', 'required': False}
        ]
    }
    
    with pytest.raises(ValueError, match="Common attribute 'nonexistent'"):
        load_config(config_dict)


def test_validation_invalid_common_attribute():
    """Test validation with invalid attribute reference."""
    config_dict = {
        'categories': {
            'attribute_names': ['invalid_attr'],
            'categories': [
                {'name': 'test', 'attribute_names': ['link']}
            ]
        },
        'attributes': [
            {'name': 'link', 'required': True}
        ]
    }
    
    with pytest.raises(ValueError, match="Common attribute 'invalid_attr'"):
        load_config(config_dict)
