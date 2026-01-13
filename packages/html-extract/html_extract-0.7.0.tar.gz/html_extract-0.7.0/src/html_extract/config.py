"""
Configuration management module for HTML Extract.

Provides functionality to load configuration from YAML files, JSON files, or dict objects.
"""

import json
import os
import yaml
from pathlib import Path
from typing import Union, Dict, Any, List


def _validate_categories_format(categories: Any) -> None:
    """
    Validate that categories is a dict with 'attribute_names' key.
    
    Args:
        categories: Categories value to validate
    
    Raises:
        ValueError: If categories is not a dict or missing 'attribute_names' key
    """
    if not isinstance(categories, dict):
        raise ValueError(
            f"categories must be a dictionary with 'attribute_names' key. "
            f"Got: {type(categories)}"
        )
    
    if 'attribute_names' not in categories:
        raise ValueError(
            "categories must be a dictionary with 'attribute_names' key for common attributes."
        )


def _validate_common_attributes(config: Dict[str, Any]) -> None:
    """
    Validate that common attributes in categories.attribute_names exist in attributes section.
    
    Args:
        config: Configuration dictionary
    
    Raises:
        ValueError: If categories format is invalid or any common attribute doesn't exist
    """
    categories = config.get('categories', {})
    _validate_categories_format(categories)
    
    common_attrs = categories.get('attribute_names', [])
    if common_attrs:
        all_attribute_names = {attr.get('name') for attr in config.get('attributes', [])}
        
        for attr_name in common_attrs:
            if attr_name not in all_attribute_names:
                raise ValueError(
                    f"Common attribute '{attr_name}' in categories.attribute_names "
                    f"not found in attributes section."
                )


def _get_category_list(categories: Dict[str, Any]) -> List[Dict]:
    """
    Extract category list from dict format.
    
    Args:
        categories: Dict with 'attribute_names' key and category items
    
    Returns:
        List of category dictionaries
    
    Raises:
        ValueError: If categories is not a dict or doesn't have 'attribute_names' key
    """
    _validate_categories_format(categories)
    
    # Extract category list (skip attribute_names key)
    # In YAML, when you have:
    # categories:
    #   attribute_names: [...]
    #   - name: cat1
    # YAML parser may create a dict with attribute_names and list items as keys
    # We need to extract all values that are dicts with 'name' key
    category_list = []
    for key, value in categories.items():
        if key == 'attribute_names':
            continue
        if isinstance(value, list):
            # Categories stored as list under a key
            category_list.extend([item for item in value if isinstance(item, dict) and 'name' in item])
        elif isinstance(value, dict) and 'name' in value:
            # Single category dict
            category_list.append(value)
    return category_list


def load_config(source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Load configuration from YAML file, JSON file, or dict object.
    
    Args:
        source: File path (str or Path) to YAML/JSON config file, or dict object (already loaded config)
    
    Returns:
        Configuration dictionary
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML file is invalid
        ValueError: If source type is not supported, config structure is invalid, or JSON syntax is invalid
    """
    # Support dict objects (already loaded config)
    if isinstance(source, dict):
        # Validate dict structure
        if 'categories' not in source or 'attributes' not in source:
            raise ValueError(
                "Configuration dict must contain 'categories' and 'attributes' keys"
            )
        
        # Validate categories format and common attributes
        _validate_common_attributes(source)
        
        return source
    
    # Support YAML file paths (str or Path)
    elif isinstance(source, (str, Path)):
        config_path = Path(source)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {source}")
        
        # Detect format from extension
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    config = yaml.safe_load(f)
                    if config is None:
                        raise ValueError(f"Configuration file is empty: {source}")
                    
                    # Validate loaded config structure
                    if not isinstance(config, dict):
                        raise ValueError(f"Configuration file must contain a dictionary, got: {type(config)}")
                    
                    if 'categories' not in config or 'attributes' not in config:
                        raise ValueError(
                            f"Configuration file must contain 'categories' and 'attributes' keys. "
                            f"Found keys: {list(config.keys())}"
                        )
                    
                    # Validate categories format and common attributes
                    _validate_common_attributes(config)
                    
                    return config
                except yaml.YAMLError as e:
                    raise yaml.YAMLError(f"Invalid YAML syntax in {source}: {e}")
        elif config_path.suffix.lower() == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    config = json.load(f)
                    if config is None:
                        raise ValueError(f"Configuration file is empty: {source}")
                    
                    # Validate loaded config structure
                    if not isinstance(config, dict):
                        raise ValueError(f"Configuration file must contain a dictionary, got: {type(config)}")
                    
                    if 'categories' not in config or 'attributes' not in config:
                        raise ValueError(
                            f"Configuration file must contain 'categories' and 'attributes' keys. "
                            f"Found keys: {list(config.keys())}"
                        )
                    
                    # Validate categories format and common attributes
                    _validate_common_attributes(config)
                    
                    return config
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON syntax in {source}: {e}")
        else:
            raise ValueError(
                f"Unsupported file format: {source}. "
                f"Supported formats: YAML (.yaml, .yml) and JSON (.json)."
            )
    
    else:
        raise ValueError(
            f"Unsupported source type: {type(source)}. "
            f"Expected str, Path (file path) or dict."
        )


def create_config_template(output_path: Union[str, Path], format: str = 'auto') -> None:
    """
    Create a configuration template file.
    
    Generates a starter configuration template with example categories and attributes
    to help users get started quickly. The template includes common extraction patterns
    and helpful comments (in YAML format).
    
    Args:
        output_path: Path where template will be created. Parent directories will be
                     created if they don't exist.
        format: Format to use: 'auto' (detect from file extension), 'yaml', or 'json'.
                Defaults to 'auto'.
    
    Raises:
        ValueError: If format is invalid or cannot be determined from file extension
        OSError: If file cannot be written or directory cannot be created
    
    Example:
        >>> create_config_template('config.yaml')
        >>> create_config_template('config.json', format='json')
        >>> create_config_template('data/config.yaml', format='auto')
    """
    output_path = Path(output_path)
    
    # Determine format
    if format == 'auto':
        suffix = output_path.suffix.lower()
        if suffix in ['.yaml', '.yml']:
            format = 'yaml'
        elif suffix == '.json':
            format = 'json'
        else:
            raise ValueError(
                f"Cannot determine format from file extension '{suffix}'. "
                f"Please specify format='yaml' or format='json', or use .yaml/.yml/.json extension."
            )
    elif format not in ['yaml', 'json']:
        raise ValueError(f"Invalid format: {format}. Must be 'auto', 'yaml', or 'json'.")
    
    # Create parent directories if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create template structure
    template = {
        'categories': {
            'attribute_names': ['link', 'title', 'price', 'location', 'date'],
            'categories': [
                {
                    'name': 'gpu',
                    'attribute_names': []
                }
            ]
        },
        'attributes': [
            {
                'name': 'link',
                'required': True,
                'extract': {
                    'type': 'regex',
                    'selector': 'a',
                    'extract_attribute': 'href',
                    'pattern': '/d/oferta/.*\\.html'
                }
            },
            {
                'name': 'title',
                'required': True,
                'extract': {
                    'type': 'text',
                    'selector': 'h4',
                    'extract_attribute': 'text'
                },
                'processing': [
                    {'strip': True}
                ]
            },
            {
                'name': 'price',
                'required': True,
                'extract': {
                    'type': 'text',
                    'selector': '.price',
                    'extract_attribute': 'text'
                },
                'processing': [
                    {'strip': True},
                    {'replace': ' ', 'with': ''}
                ]
            },
            {
                'name': 'location',
                'required': False,
                'extract': {
                    'type': 'text',
                    'selector': '.location',
                    'extract_attribute': 'text'
                }
            },
            {
                'name': 'date',
                'required': False,
                'extract': {
                    'type': 'text',
                    'selector': '.date',
                    'extract_attribute': 'text'
                }
            }
        ]
    }
    
    # Write template based on format
    if format == 'yaml':
        # Generate YAML using yaml.dump() for proper escaping
        yaml_output = yaml.dump(template, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Add header comment
        yaml_content = '# Configuration template generated by html-extract\n'
        yaml_content += '# Customize the selectors and patterns for your specific HTML structure\n'
        yaml_content += '# See documentation for details: https://github.com/your-repo/html-extract\n'
        yaml_content += '\n'
        yaml_content += yaml_output
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
    else:  # format == 'json'
        # Write JSON (pretty-printed, no comments)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
