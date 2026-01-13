"""
Core extraction module for HTML Extract.

Provides functionality to extract structured data from HTML files using
configuration-driven rules.
"""

import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple

import pandas as pd
from bs4 import BeautifulSoup

from .config import load_config, _get_category_list
from .logging import (
    get_logger,
    log_file_start,
    log_file_success,
    log_file_empty,
    log_file_error,
    log_missing_required_attribute
)


def _resolve_category_attributes(
    category_name: str,
    config_dict: Dict[str, Any],
    selected_category: Dict[str, Any]
) -> List[str]:
    """
    Resolve final attribute list for a category through inheritance.
    
    Supports multiple levels of hierarchy (e.g., domy/najem/warszawa).
    
    Inheritance order:
    1. Common attributes (categories.attribute_names)
    2. All parent category attributes in hierarchy (in order)
    3. Category-specific attributes
    
    Args:
        category_name: Name of the category (may contain '/' for hierarchy)
        config_dict: Configuration dictionary
        selected_category: The selected category dictionary
    
    Returns:
        List of attribute names in inheritance order (duplicates removed, first occurrence wins)
    """
    # Get common attributes
    categories = config_dict.get('categories', {})
    common_attrs = categories.get('attribute_names', []) if isinstance(categories, dict) else []
    
    # Get all parent category attributes (if hierarchical)
    # For domy/najem/warszawa: get domy, then domy/najem
    parent_attrs_list = []
    if '/' in category_name:
        category_list = _get_category_list(categories)
        category_parts = category_name.split('/')
        
        # Build parent paths: domy, domy/najem (for domy/najem/warszawa)
        for i in range(1, len(category_parts)):
            parent_path = '/'.join(category_parts[:i])
            # Find parent category
            parent_found = False
            for cat in category_list:
                if cat.get('name') == parent_path:
                    parent_attrs = cat.get('attribute_names', [])
                    if parent_attrs:
                        parent_attrs_list.append(parent_attrs)
                    parent_found = True
                    break
            
            # Validate parent category exists (optional - warn but don't fail)
            if not parent_found:
                # Parent category not found - this is allowed but may indicate misconfiguration
                # We'll continue without that parent's attributes
                pass
    
    # Get category-specific attributes
    category_attrs = selected_category.get('attribute_names', [])
    
    # Merge: common → all parents (in order) → category-specific (first occurrence wins)
    merged = []
    seen = set()
    all_attrs = common_attrs.copy() if common_attrs else []
    for parent_attrs in parent_attrs_list:
        all_attrs.extend(parent_attrs)
    if category_attrs:
        all_attrs.extend(category_attrs)
    
    for attr in all_attrs:
        if attr not in seen:
            merged.append(attr)
            seen.add(attr)
    
    return merged


def extract_data_from_html(
    source_path: Union[str, Path],
    config: Union[str, Dict[str, Any]],
    scrape_date: Optional[str] = None,
    category: Optional[str] = None
) -> Tuple[pd.DataFrame, int]:
    """
    Extract structured data from HTML file using configuration.
    
    Args:
        source_path: Path to HTML file
        config: Configuration dict or path to YAML config file
        scrape_date: Optional scrape date in YYYY-MM-DD format
        category: Optional category name (required if config has multiple categories)
    
    Returns:
        Tuple of (DataFrame, skipped_count):
        - DataFrame: Extracted data, one row per item found in HTML
        - skipped_count: Number of items skipped due to missing required attributes
    
    Raises:
        FileNotFoundError: If HTML file doesn't exist
        ValueError: If configuration is invalid or category not specified when required
    """
    # Convert source_path to Path object
    html_path = Path(source_path)
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {source_path}")
    
    # Load config if it's a file path
    if isinstance(config, str):
        config_dict = load_config(config)
    else:
        config_dict = config
    
    # Log file processing start
    log_file_start(str(html_path), category)
    
    try:
        # Validate config structure
        if not isinstance(config_dict, dict):
            raise ValueError("Configuration must be a dictionary")
        
        if 'categories' not in config_dict or 'attributes' not in config_dict:
            raise ValueError(
                "Configuration must contain 'categories' and 'attributes' keys"
            )
        
        # Determine category to use
        categories = config_dict.get('categories', [])
        category_list = _get_category_list(categories)
        
        if len(category_list) == 0:
            raise ValueError("Configuration must contain at least one category")
        
        if len(category_list) == 1:
            # Single category - use it automatically
            selected_category = category_list[0]
            category_name = selected_category.get('name')
        else:
            # Multiple categories - require explicit category parameter
            if category is None:
                raise ValueError(
                    "Category must be specified when configuration contains "
                    f"multiple categories: {[c.get('name') for c in category_list]}"
                )
            
            # Find matching category
            selected_category = None
            for cat in category_list:
                if cat.get('name') == category:
                    selected_category = cat
                    category_name = category
                    break
            
            if selected_category is None:
                raise ValueError(
                    f"Category '{category}' not found in configuration. "
                    f"Available categories: {[c.get('name') for c in category_list]}"
                )
        
        # Resolve attributes through inheritance chain
        resolved_attribute_names = _resolve_category_attributes(
            category_name,
            config_dict,
            selected_category
        )
        
        # Get attributes for this category
        all_attributes = config_dict.get('attributes', [])
        
        if resolved_attribute_names:
            # Filter attributes based on resolved attribute_names
            attributes = [
                attr for attr in all_attributes
                if attr.get('name') in resolved_attribute_names
            ]
            # Maintain order from resolved_attribute_names
            attribute_order = {name: idx for idx, name in enumerate(resolved_attribute_names)}
            attributes.sort(key=lambda attr: attribute_order.get(attr.get('name'), 999))
        else:
            # Use all attributes if no attribute_names specified
            attributes = all_attributes
        
        # Parse HTML
        # Use 'lxml' parser for better performance (C-based, faster than 'html.parser')
        # Falls back to 'html.parser' if lxml is not available
        with open(html_path, 'r', encoding='utf-8') as f:
            try:
                soup = BeautifulSoup(f.read(), 'lxml')
            except Exception:
                # Fallback to html.parser if lxml is not available
                soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Find all items on the page
        # Strategy: Use the first required attribute (usually "link") to find all item containers
        item_containers = _find_item_containers(soup, attributes)
        
        # If no item containers found, try extracting from entire page as single item
        if not item_containers:
            item_containers = [soup]
        
        # Extract data for each item
        all_items = []
        skipped_count = 0
        
        for container in item_containers:
            item_data = {}
            skip_item = False
            missing_attr_name = None
            
            # Extract each attribute in order (to handle dependencies)
            for attr_config in attributes:
                attr_name = attr_config.get('name')
                required = attr_config.get('required', False)
                extract_config = attr_config.get('extract', {})
                
                try:
                    value = _extract_attribute_value(
                        container,  # Use container instead of full soup
                        extract_config,
                        html_path,
                        scrape_date,
                        item_data,  # Pass already-extracted values for dependencies
                        attr_name,  # Pass attribute name for metadata extraction
                        category_name  # Pass category name for metadata extraction
                    )
                    
                    if value is None and required:
                        # Skip this item if required attribute is missing
                        skip_item = True
                        missing_attr_name = attr_name
                        break
                    
                    item_data[attr_name] = value
                
                except Exception as e:
                    # If extraction fails and attribute is required, skip item
                    if required:
                        skip_item = True
                        missing_attr_name = attr_name
                        break
                    # Otherwise, set to None
                    item_data[attr_name] = None
            
            # Add item if not skipped
            if not skip_item:
                all_items.append(item_data)
            else:
                # Log warning for missing required attribute
                if missing_attr_name:
                    log_missing_required_attribute(str(html_path), missing_attr_name)
                skipped_count += 1
        
        # Create DataFrame
        if all_items:
            df = pd.DataFrame(all_items)
            # Log successful extraction
            log_file_success(str(html_path), len(all_items), skipped_count)
            return df, skipped_count
        else:
            # Return empty DataFrame with correct columns
            column_names = [attr.get('name') for attr in attributes]
            df = pd.DataFrame(columns=column_names)
            # Log empty result
            if skipped_count > 0:
                # If items were skipped but none extracted, still log success with skipped count
                log_file_success(str(html_path), 0, skipped_count)
            else:
                log_file_empty(str(html_path))
            
            return df, skipped_count
    
    except Exception as e:
        # Log error and re-raise
        log_file_error(str(html_path), e)
        raise


def _parse_selector(selector_item: Union[str, Dict[str, Any]]) -> Tuple[str, Dict[str, Any], Optional[str]]:
    """
    Parse a selector item (string or dict) to extract tag name, attributes, and extract attribute.
    
    Args:
        selector_item: String like "a" or dict like {div: {id: "hydrate-root"}}
    
    Returns:
        Tuple of (tag_name, attributes_dict, extract_attr)
        - tag_name: HTML tag name (e.g., "div", "a", "p")
        - attributes_dict: Dictionary of HTML attributes to match (e.g., {"id": "hydrate-root"})
        - extract_attr: Attribute to extract (e.g., "href") or None
    """
    if isinstance(selector_item, str):
        # Simple string: just the tag name
        return selector_item, {}, None
    
    if isinstance(selector_item, dict):
        # Object format: {tag: {attr1: value1, attr2: value2}}
        if len(selector_item) != 1:
            raise ValueError(f"Selector object must have exactly one key (tag name), got: {selector_item}")
        
        tag_name = list(selector_item.keys())[0]
        tag_config = selector_item[tag_name]
        
        if not isinstance(tag_config, dict):
            raise ValueError(f"Selector object value must be a dict, got: {type(tag_config)}")
        
        # Check for extract attribute
        extract_attr = tag_config.pop('extract', None)
        
        # Remaining items are HTML attributes
        attributes = tag_config.copy()
        
        return tag_name, attributes, extract_attr
    
    raise ValueError(f"Selector item must be string or dict, got: {type(selector_item)}")


def _apply_selector_chain(
    soup: BeautifulSoup,
    selector_chain: List[Union[str, Dict[str, Any]]],
    find_all: bool = False
) -> Union[Any, List[Any], None]:
    """
    Apply selector chain to find element(s) in HTML.
    
    Supports mixed format selector chains:
    - Strings for simple tags: "a"
    - Objects for complex selectors: {div: {id: "hydrate-root"}}
    
    Args:
        soup: BeautifulSoup object (root element)
        selector_chain: List of selector items (strings or dicts)
        find_all: If True, return all matches; if False, return first match
    
    Returns:
        Element(s) found or None/empty list
    """
    if not selector_chain or len(selector_chain) == 0:
        return None if not find_all else []
    
    # Start with soup
    current = soup
    
    # If single element, apply directly
    if len(selector_chain) == 1:
        tag_name, attrs, _ = _parse_selector(selector_chain[0])
        if find_all:
            if attrs:
                return current.find_all(tag_name, attrs)
            else:
                return current.find_all(tag_name)
        else:
            if attrs:
                return current.find(tag_name, attrs)
            else:
                return current.find(tag_name)
    
    # Multiple elements: apply chain
    # Parse first element (root scope)
    root_tag, root_attrs, _ = _parse_selector(selector_chain[0])
    
    if root_attrs:
        root = current.find(root_tag, root_attrs)
    else:
        root = current.find(root_tag)
    
    if root is None:
        return None if not find_all else []
    
    # Apply remaining selectors within root
    current = root
    for i, selector_item in enumerate(selector_chain[1:], 1):
        is_last = (i == len(selector_chain) - 1)
        tag_name, attrs, _ = _parse_selector(selector_item)
        
        if is_last and find_all:
            # Last selector: use find_all
            if attrs:
                return current.find_all(tag_name, attrs)
            else:
                return current.find_all(tag_name)
        else:
            # Not last selector: use find to continue chain
            if attrs:
                current = current.find(tag_name, attrs)
            else:
                current = current.find(tag_name)
            
            if current is None:
                return None if not find_all else []
    
    # If we get here and find_all is False, return the element
    return current


def _find_item_containers(soup: BeautifulSoup, attributes: List[Dict[str, Any]]) -> List[Any]:
    """
    Find all item containers on the page.
    
    Strategy: Use the first required attribute with regex pattern (usually "link")
    to find all matching elements, then return their containers.
    """
    # Find first required attribute with regex pattern (typically "link")
    link_attr = None
    for attr in attributes:
        if attr.get('required', False):
            extract_config = attr.get('extract', {})
            if extract_config.get('type') == 'regex' and extract_config.get('pattern'):
                link_attr = attr
                break
    
    if not link_attr:
        # No link attribute found, return empty list (will extract from entire page)
        return []
    
    extract_config = link_attr.get('extract', {})
    selector = extract_config.get('selector')
    pattern = extract_config.get('pattern')
    extract_attribute = extract_config.get('extract_attribute', 'text')
    
    if not selector or not pattern:
        return []
    
    # Ensure selector is a list
    if not isinstance(selector, list):
        selector = [selector]
    
    # Find all matching elements using selector chain
    elements = _apply_selector_chain(soup, selector, find_all=True)
    
    if not elements:
        elements = []
    
    # Try fallback if no matches
    if not elements:
        fallback_selector = extract_config.get('fallback_selector')
        if fallback_selector:
            # Ensure fallback_selector is a list
            if not isinstance(fallback_selector, list):
                fallback_selector = [fallback_selector]
            elements = _apply_selector_chain(soup, fallback_selector, find_all=True)
            if not elements:
                elements = []
    
    # Filter by pattern and get containers
    containers = []
    for element in elements:
        if extract_attribute == 'text':
            value = element.get_text(strip=True)
        else:
            value = element.get(extract_attribute)
        
        if value and re.search(pattern, value):
            # Find container - try parent, or parent's parent, or element itself
            # Common patterns: item is in parent div/article, or element itself is the container
            container = element
            # Try going up to find a reasonable container (max 3 levels up)
            for _ in range(3):
                parent = container.parent
                if parent and parent.name and parent.name not in ['html', 'body']:
                    container = parent
                else:
                    break
            
            containers.append(container)
    
    return containers


def _extract_attribute_value(
    container: BeautifulSoup,
    extract_config: Dict[str, Any],
    html_path: Path,
    scrape_date: Optional[str],
    extracted_values: Dict[str, Any],
    attribute_name: str,
    category_name: Optional[str] = None
) -> Optional[Any]:
    """
    Extract value for a single attribute based on extraction configuration.
    
    Args:
        container: BeautifulSoup element (item container or full soup)
        extract_config: Extraction configuration dict
        html_path: Path to HTML file (for metadata extraction)
        scrape_date: Optional scrape date
        extracted_values: Dictionary of already-extracted values (for dependencies)
        attribute_name: Name of the attribute being extracted (for metadata type)
        category_name: Optional category name (for metadata extraction)
    
    Returns:
        Extracted value or None
    """
    extract_type = extract_config.get('type')
    
    if extract_type == 'text':
        value = _extract_text(container, extract_config)
    
    elif extract_type == 'regex':
        value = _extract_regex(container, extract_config)
    
    elif extract_type == 'contains':
        value = _extract_contains(extract_config, extracted_values)
    
    elif extract_type == 'metadata':
        value = _extract_metadata(html_path, extract_config, scrape_date, attribute_name, category_name)
    
    else:
        raise ValueError(f"Unknown extraction type: {extract_type}")
    
    # Apply processing
    if value is not None:
        value = _apply_processing(value, extract_config, scrape_date, extracted_values)
    
    return value


def _extract_text(container: BeautifulSoup, extract_config: Dict[str, Any]) -> Optional[str]:
    """Extract text or attribute value from HTML element within container."""
    selector = extract_config.get('selector')
    if not selector:
        return None
    
    # Ensure selector is a list
    if not isinstance(selector, list):
        selector = [selector]
    
    # When extracting from container, skip root scope if selector is array
    # Container is already scoped, so use only final selector(s)
    if len(selector) > 1:
        # Skip first element (root scope), use remaining selectors
        selector = selector[1:]
    
    # Check if last selector specifies extract attribute
    extract_attribute = extract_config.get('extract_attribute', 'text')
    if selector:
        _, _, selector_extract = _parse_selector(selector[-1])
        if selector_extract:
            extract_attribute = selector_extract
    
    # Find element within container using selector chain
    element = _apply_selector_chain(container, selector, find_all=False)
    
    # Try fallback if not found
    if element is None:
        fallback_selector = extract_config.get('fallback_selector')
        if fallback_selector:
            # Ensure fallback_selector is a list
            if not isinstance(fallback_selector, list):
                fallback_selector = [fallback_selector]
            # Skip root scope for fallback too
            if len(fallback_selector) > 1:
                fallback_selector = fallback_selector[1:]
            element = _apply_selector_chain(container, fallback_selector, find_all=False)
            # Check extract attribute from fallback selector too
            if element and fallback_selector:
                _, _, fallback_extract = _parse_selector(fallback_selector[-1])
                if fallback_extract:
                    extract_attribute = fallback_extract
    
    if element is None:
        return None
    
    # Extract attribute or text
    if extract_attribute == 'text':
        value = element.get_text(strip=True)
    else:
        value = element.get(extract_attribute)
    
    return value


def _extract_regex(container: BeautifulSoup, extract_config: Dict[str, Any]) -> Optional[str]:
    """Extract value using regex pattern matching within container."""
    selector = extract_config.get('selector')
    pattern = extract_config.get('pattern')
    extract_attribute = extract_config.get('extract_attribute', 'text')

    if not selector or not pattern:
        return None

    # Ensure selector is a list
    if not isinstance(selector, list):
        selector = [selector]

    # When extracting from container, skip root scope if selector is array
    # Container is already scoped, so use only final selector(s)
    if len(selector) > 1:
        # Skip first element (root scope), use remaining selectors
        selector = selector[1:]

    # Check if last selector specifies extract attribute
    if selector:
        _, _, selector_extract = _parse_selector(selector[-1])
        if selector_extract:
            extract_attribute = selector_extract

    # Find matching elements within container using selector chain
    elements = _apply_selector_chain(container, selector, find_all=True)

    if not elements:
        elements = []

    # Try fallback if no matches
    if not elements:
        fallback_selector = extract_config.get('fallback_selector')
        if fallback_selector:
            # Ensure fallback_selector is a list
            if not isinstance(fallback_selector, list):
                fallback_selector = [fallback_selector]
            # Skip root scope for fallback too
            if len(fallback_selector) > 1:
                fallback_selector = fallback_selector[1:]
            elements = _apply_selector_chain(container, fallback_selector, find_all=True)
            # Check extract attribute from fallback selector too
            if elements and fallback_selector:
                _, _, fallback_extract = _parse_selector(fallback_selector[-1])
                if fallback_extract:
                    extract_attribute = fallback_extract
            if not elements:
                elements = []

    # Match pattern against attribute values (return first match)
    for element in elements:
        if extract_attribute == 'text':
            value = element.get_text(strip=True)
        else:
            value = element.get(extract_attribute)
        
        if value and re.search(pattern, value):
            return value
    
    return None


def _extract_contains(
    extract_config: Dict[str, Any],
    extracted_values: Dict[str, Any]
) -> Optional[bool]:
    """Extract value based on contains check (depends on another column)."""
    depends_on = extract_config.get('depends_on')
    check = extract_config.get('check')
    
    if not depends_on or not check:
        return None
    
    # Get dependent value
    dependent_value = extracted_values.get(depends_on)
    
    if dependent_value is None:
        return None
    
    # Check if dependent value contains the check string
    if isinstance(dependent_value, str):
        return check in dependent_value
    else:
        return check in str(dependent_value)


def _extract_metadata(
    html_path: Path,
    extract_config: Dict[str, Any],
    scrape_date: Optional[str],
    attribute_name: str,
    category_name: Optional[str] = None
) -> Optional[str]:
    """
    Extract metadata from file context.
    
    Args:
        html_path: Path to HTML file
        extract_config: Extraction configuration dict
        scrape_date: Optional scrape date
        attribute_name: Name of the metadata attribute to extract
        category_name: Optional category name (for category metadata extraction)
    
    Returns:
        Metadata value based on attribute_name
    """
    # Determine which metadata to extract based on attribute name
    if attribute_name == 'source_file':
        return html_path.name
    
    elif attribute_name == 'source_path':
        # Return relative path (simplified for Phase 1)
        return html_path.as_posix()
    
    elif attribute_name == 'source_month':
        # Extract month from date
        date_value = _extract_date_from_path(html_path, extract_config, scrape_date)
        if date_value:
            # Extract YYYY-MM from YYYY-MM-DD
            return date_value[:7] if len(date_value) >= 7 else None
        return None
    
    elif attribute_name == 'scrape_date':
        return _extract_date_from_path(html_path, extract_config, scrape_date)
    
    elif attribute_name == 'scrape_datetime':
        return _extract_datetime_from_path(html_path, extract_config, scrape_date)
    
    elif attribute_name == 'category':
        # Return category name if available
        return category_name
    
    else:
        # Unknown metadata type
        return None


def _extract_date_from_path(
    html_path: Path,
    extract_config: Dict[str, Any],
    scrape_date: Optional[str]
) -> Optional[str]:
    """Extract date (YYYY-MM-DD) from file path."""
    if scrape_date:
        return scrape_date
    
    date_selector = extract_config.get('selector')
    
    # Try filename first
    filename = html_path.name
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        return date_match.group(1)
    
    # Try parent folder
    if date_selector != 'filename':
        parent_folder = html_path.parent.name
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', parent_folder)
        if date_match:
            return date_match.group(1)
    
    # Use file creation time
    if date_selector == 'file_creation' or date_selector is None:
        stat = html_path.stat()
        dt = datetime.fromtimestamp(stat.st_mtime)
        return dt.strftime('%Y-%m-%d')
    
    return None


def _extract_datetime_from_path(
    html_path: Path,
    extract_config: Dict[str, Any],
    scrape_date: Optional[str]
) -> Optional[str]:
    """Extract datetime (YYYY-MM-DD HH:MM:SS) from file path."""
    date_selector = extract_config.get('selector')
    
    # Try filename first
    filename = html_path.name
    datetime_match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})', filename)
    if datetime_match:
        date_value = datetime_match.group(1)
        time_value = datetime_match.group(2).replace('-', ':')
        return f"{date_value} {time_value}"
    
    # Try date-only pattern in filename
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        date_value = date_match.group(1)
        return f"{date_value} 00:00:00"
    
    # Try parent folder
    if date_selector != 'filename':
        parent_folder = html_path.parent.name
        datetime_match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})', parent_folder)
        if datetime_match:
            date_value = datetime_match.group(1)
            time_value = datetime_match.group(2).replace('-', ':')
            return f"{date_value} {time_value}"
        
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', parent_folder)
        if date_match:
            date_value = date_match.group(1)
            return f"{date_value} 00:00:00"
    
    # Use file creation time
    if date_selector == 'file_creation' or date_selector is None:
        stat = html_path.stat()
        dt = datetime.fromtimestamp(stat.st_mtime)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Fallback to scrape_date if provided
    if scrape_date:
        return f"{scrape_date} 00:00:00"
    
    return None


def _apply_processing(
    value: str,
    extract_config: Dict[str, Any],
    scrape_date: Optional[str],
    extracted_values: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Apply processing steps to extracted value.
    
    Args:
        value: The value to process
        extract_config: Extraction configuration dict
        scrape_date: Optional scrape date
        extracted_values: Dictionary of already-extracted attribute values (for variable substitution)
    
    Returns:
        Processed value or None
    """
    if not isinstance(value, str):
        return value
    
    if extracted_values is None:
        extracted_values = {}
    
    # Build context dictionary with available variables
    # This makes it generic and extensible for future plugins/variables
    context_variables = {
        'scrape_date': scrape_date,
        # Future variables can be added here (e.g., 'current_time', 'user_id', etc.)
    }
    
    processing = extract_config.get('processing', [])
    split_parts = None  # Store split result for index step
    
    for step in processing:
        if isinstance(step, dict):
            # Split step
            if 'split' in step:
                separators = step['split']
                if isinstance(separators, str):
                    separators = [separators]
                
                for sep in separators:
                    if sep in value:
                        split_parts = value.split(sep)
                        value = split_parts[0] if len(split_parts) > 0 else value
                        break
            
            # Index step (works on split result or space-split)
            if 'index' in step:
                idx = step['index']
                if split_parts is not None:
                    # Use split result
                    if 0 <= idx < len(split_parts):
                        value = split_parts[idx]
                    else:
                        value = None
                else:
                    # Fallback to space-split
                    parts = value.split()
                    if 0 <= idx < len(parts):
                        value = parts[idx]
                    else:
                        value = None
                split_parts = None  # Reset after index
            
            # Strip step
            if 'strip' in step:
                strip_value = step.get('strip')
                if strip_value is True:
                    # Default: strip whitespace
                    value = value.strip() if value else value
                elif isinstance(strip_value, str):
                    # Custom characters: strip specified characters
                    value = value.strip(strip_value) if value else value
            
            # Replace step
            if 'replace' in step and 'with' in step:
                # Resolve replace pattern (can be variable or string)
                # Variables are identified by $ prefix (e.g., $scrape_date, $attribute_name)
                replace_pattern = step['replace']
                old_text = None
                
                # Check if replace pattern is a variable (starts with $)
                if isinstance(replace_pattern, str) and replace_pattern.startswith('$'):
                    var_name = replace_pattern[1:]  # Remove $ prefix
                    # Check if variable is a context variable
                    if var_name in context_variables:
                        var_value = context_variables[var_name]
                        if var_value is not None:
                            old_text = str(var_value) if not isinstance(var_value, str) else var_value
                    # Check if variable is an already-extracted attribute name
                    elif var_name in extracted_values:
                        attr_value = extracted_values[var_name]
                        if attr_value is not None:
                            old_text = str(attr_value) if not isinstance(attr_value, str) else attr_value
                    else:
                        # Variable not found, skip replacement
                        old_text = None
                else:
                    # Plain string pattern (quoted in YAML/JSON)
                    old_text = str(replace_pattern) if replace_pattern is not None else ''
                
                # Resolve replacement value (can be variable or string)
                replacement = step.get('with', '')
                replacement_value = None
                is_variable = False
                
                # Check if replacement is a variable (starts with $)
                if isinstance(replacement, str) and replacement.startswith('$'):
                    var_name = replacement[1:]  # Remove $ prefix
                    # Check if variable is a context variable
                    if var_name in context_variables:
                        var_value = context_variables[var_name]
                        if var_value is not None:
                            replacement_value = str(var_value) if not isinstance(var_value, str) else var_value
                            is_variable = True
                        else:
                            # Variable not available, skip replacement
                            replacement_value = None
                    # Check if variable is an already-extracted attribute name
                    elif var_name in extracted_values:
                        attr_value = extracted_values[var_name]
                        if attr_value is not None:
                            replacement_value = str(attr_value) if not isinstance(attr_value, str) else attr_value
                            is_variable = True
                        else:
                            # Attribute value is None, skip replacement
                            replacement_value = None
                    else:
                        # Variable name not found, skip replacement
                        replacement_value = None
                else:
                    # Plain string replacement (quoted in YAML/JSON)
                    replacement_value = str(replacement) if replacement is not None else ''
                    is_variable = False
                
                # Perform replacement
                if value and old_text and old_text in value and replacement_value is not None:
                    if is_variable:
                        # Variable replacement: replace entire value when pattern found
                        # This is useful for replacing "Today" patterns with dates, etc.
                        value = replacement_value
                    else:
                        # Normal substring replacement
                        value = value.replace(old_text, replacement_value)
            
            # Check today step
            if 'check_today' in step:
                check_text = step['check_today']
                if value and check_text in value and scrape_date:
                    value = scrape_date
            
            # Use scrape date step
            # Generic implementation: works with any pattern specified via 'pattern' key
            # Supports both boolean (backward compatibility) and object (with pattern) formats
            use_scrape_date_config = step.get('use_scrape_date')
            if use_scrape_date_config:
                if scrape_date and value:
                    # Handle object format: use_scrape_date: {pattern: "Dzisiaj"}
                    if isinstance(use_scrape_date_config, dict):
                        pattern = use_scrape_date_config.get('pattern')
                        if pattern and pattern in value:
                            value = scrape_date
                    # Handle boolean format: use_scrape_date: true (backward compatibility)
                    elif use_scrape_date_config is True:
                        # Fallback: check common patterns for backward compatibility
                        # Users should use object format with explicit pattern for clarity
                        common_patterns = ['Dzisiaj', 'Today', 'today', 'dzisiaj']
                        if any(p in value for p in common_patterns):
                            value = scrape_date
        
        if value is None:
            break
    
    # Apply mapping if present
    mapping = extract_config.get('mapping')
    if mapping and value is not None:
        if value in mapping:
            value = mapping[value]
        elif 'default' in mapping:
            value = mapping['default']
    
    return value
