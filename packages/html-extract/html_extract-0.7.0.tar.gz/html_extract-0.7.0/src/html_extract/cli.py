#!/usr/bin/env python3
"""
HTML Extract - Command-line interface.

Extract structured data from HTML files using declarative configuration files.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import pandas as pd

from . import (
    extract_data_from_html,
    load_config,
    process_directory,
    process_csv,
    create_config_template,
    create_csv_template,
    save_output
)
from .config import _get_category_list
from .logging import setup_logging


def _detect_input_type(input_path: Path) -> str:
    """
    Detect input type from path.
    
    Args:
        input_path: Path to input source
    
    Returns:
        Input type: 'file', 'directory', or 'csv'
    
    Raises:
        ValueError: If input type cannot be determined
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input path does not exist: {input_path}")
    
    if input_path.is_file():
        suffix = input_path.suffix.lower()
        if suffix == '.html':
            return 'file'
        elif suffix == '.csv':
            return 'csv'
        else:
            raise ValueError(
                f"Unsupported file type: {suffix}. "
                f"Expected .html file, .csv file, or directory."
            )
    elif input_path.is_dir():
        return 'directory'
    else:
        raise ValueError(f"Cannot determine input type for: {input_path}")


def _parse_scrape_date(date_str: str) -> str:
    """
    Parse scrape date, handling special values.
    
    Args:
        date_str: Date string (YYYY-MM-DD, "current", or "today")
    
    Returns:
        Date string in YYYY-MM-DD format
    
    Raises:
        ValueError: If date format is invalid
    """
    if date_str.lower() in ['current', 'today']:
        return date.today().strftime('%Y-%m-%d')
    
    # Validate YYYY-MM-DD format
    try:
        parsed_date = date.fromisoformat(date_str)
        return parsed_date.strftime('%Y-%m-%d')
    except ValueError:
        raise ValueError(
            f"Invalid date format: {date_str}. "
            f"Expected YYYY-MM-DD format or 'current'/'today'."
        )


def _detect_format_from_path(output_path: Optional[str]) -> str:
    """
    Detect output format from file path extension.
    
    Args:
        output_path: Output file path (may be None)
    
    Returns:
        Format string: 'csv' or 'json'
    """
    if not output_path:
        return 'csv'  # Default
    
    path = Path(output_path)
    suffix = path.suffix.lower()
    
    if suffix == '.json':
        return 'json'
    elif suffix == '.csv':
        return 'csv'
    else:
        return 'csv'  # Default to CSV for unknown extensions


def _print_to_stdout(dataframe: pd.DataFrame, format: str = 'csv') -> None:
    """
    Print DataFrame to stdout in specified format.
    
    Args:
        dataframe: DataFrame to print
        format: Output format ('csv' or 'json')
    """
    # Ensure stdout uses UTF-8 encoding (especially important on Windows)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    
    if format == 'csv':
        # CSV to stdout (no BOM for stdout)
        dataframe.to_csv(
            sys.stdout,
            index=False,
            encoding='utf-8',  # No BOM for stdout
            errors='replace'  # Handle encoding errors gracefully
        )
    elif format == 'json':
        # JSON to stdout (pretty-printed)
        records = dataframe.to_dict('records')
        json.dump(
            records,
            sys.stdout,
            indent=2,
            ensure_ascii=False,
            default=str
        )
        sys.stdout.write('\n')  # Add newline after JSON
    else:
        raise ValueError(f"Unsupported output format: {format}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='html-extract',
        description='Extract structured data from HTML files using configuration files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            'Examples:\n'
            '  html-extract page.html -c config.yaml -k gpu -o output.csv\n'
            '  html-extract data/gpu/2025/2025-01-15 -c config.yaml -o output.csv -p\n'
            '  html-extract file_list.csv -c config.yaml -o combined.csv --progress\n'
            '  html-extract -t config new_config.yaml\n'
            '  html-extract -t csv file_list.csv'
        )
    )
    
    # Positional argument (optional if using -t)
    parser.add_argument(
        'input',
        nargs='?',
        help='Input source: HTML file, directory, or CSV file'
    )
    
    # Required (unless -t)
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file (YAML or JSON). Required unless using -t flag.'
    )
    
    # Optional flags
    parser.add_argument(
        '-o', '--output',
        help='Output file path (omit to print to stdout)'
    )
    
    parser.add_argument(
        '-d', '--scrape_date',
        help='Scrape date in YYYY-MM-DD format (or "current"/"today" for current date)'
    )
    
    parser.add_argument(
        '-k', '--category',
        help='Category name to use for extraction (required for single files when config has multiple categories)'
    )
    
    parser.add_argument(
        '-p', '--progress',
        action='store_true',
        help='Display progress bar during batch processing'
    )
    
    parser.add_argument(
        '--no-progress',
        action='store_true',
        help='Explicitly disable progress bar (useful for non-interactive/piped output)'
    )
    
    parser.add_argument(
        '-t', '--template',
        nargs=2,
        metavar=('TYPE', 'PATH'),
        help='Create template file and exit. TYPE: "config" or "csv". PATH: output file path.'
    )
    
    parser.add_argument(
        '--stream-mode',
        choices=['overwrite', 'append'],
        default='overwrite',
        help='Streaming mode for batch operations: overwrite (default) or append. Only used when -o/--output is provided for batch operations.'
    )
    
    parser.add_argument(
        '--log-file',
        help='Path to log file. If not specified, logs are written to stderr.'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (equivalent to --log-level DEBUG)'
    )
    
    args = parser.parse_args()
    
    # Initialize logging
    setup_logging(
        log_level=args.log_level,
        log_file=args.log_file,
        verbose=args.verbose
    )
    
    # Handle template generation
    if args.template:
        template_type, template_path = args.template
        
        if template_type == 'config':
            try:
                create_config_template(template_path)
                print(f"Configuration template created: {template_path}")
                sys.exit(0)
            except Exception as e:
                print(f"Error creating config template: {e}", file=sys.stderr)
                sys.exit(1)
        
        elif template_type == 'csv':
            try:
                create_csv_template(template_path)
                print(f"CSV template created: {template_path}")
                sys.exit(0)
            except Exception as e:
                print(f"Error creating CSV template: {e}", file=sys.stderr)
                sys.exit(1)
        
        else:
            print(f"Error: Invalid template type: {template_type}. Must be 'config' or 'csv'.", file=sys.stderr)
            sys.exit(1)
    
    # Validate required arguments for processing
    if not args.input:
        parser.error("INPUT is required unless using -t, --template flag.")
    
    if not args.config:
        parser.error("-c, --config is required unless using -t, --template flag.")
    
    # Parse scrape date if provided
    scrape_date = None
    if args.scrape_date:
        try:
            scrape_date = _parse_scrape_date(args.scrape_date)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Detect input type
    input_path = Path(args.input)
    try:
        input_type = _detect_input_type(input_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process based on input type
    try:
        if input_type == 'file':
            # Single file processing
            # Check if category is required
            categories_dict = config.get('categories', {})
            category_list = _get_category_list(categories_dict)
            if len(category_list) > 1 and not args.category:
                category_names = [cat.get('name') for cat in category_list if cat.get('name')]
                print(
                    f"Error: Category required when configuration has multiple categories.\n"
                    f"Available categories: {', '.join(sorted(category_names))}\n"
                    f"Use -k, --category flag to specify category.",
                    file=sys.stderr
                )
                sys.exit(1)
            
            df, skipped_count = extract_data_from_html(
                input_path,
                config,
                scrape_date=scrape_date,
                category=args.category
            )
        
        elif input_type == 'directory':
            # Directory processing (category auto-derived)
            # Determine if progress should be shown
            show_progress = args.progress and not args.no_progress
            # Auto-disable if output is piped (tqdm handles this, but explicit check for clarity)
            if show_progress and not sys.stdout.isatty():
                show_progress = False
            
            if args.output:
                # Streaming mode: write directly to file
                process_directory(
                    input_path,
                    config,
                    scrape_date=scrape_date,
                    show_progress=show_progress,
                    stream_to_file=args.output,
                    stream_mode=args.stream_mode
                )
                # No output handling needed - data already written to file
            else:
                # Collect in memory and print to stdout
                df = process_directory(
                    input_path,
                    config,
                    scrape_date=scrape_date,
                    show_progress=show_progress
                )
                output_format = _detect_format_from_path(None)  # Defaults to 'csv'
                try:
                    _print_to_stdout(df, format=output_format)
                except Exception as e:
                    print(f"Error writing to stdout: {e}", file=sys.stderr)
                    sys.exit(1)
        
        elif input_type == 'csv':
            # CSV bulk processing
            # Determine if progress should be shown
            show_progress = args.progress and not args.no_progress
            # Auto-disable if output is piped (tqdm handles this, but explicit check for clarity)
            if show_progress and not sys.stdout.isatty():
                show_progress = False
            
            if args.output:
                # Streaming mode: write directly to file
                process_csv(
                    input_path,
                    default_config=config,
                    default_scrape_date=scrape_date,
                    default_category=args.category,
                    show_progress=show_progress,
                    stream_to_file=args.output,
                    stream_mode=args.stream_mode
                )
                # No output handling needed - data already written to file
            else:
                # Collect in memory and print to stdout
                df = process_csv(
                    input_path,
                    default_config=config,
                    default_scrape_date=scrape_date,
                    default_category=args.category,
                    show_progress=show_progress
                )
                output_format = _detect_format_from_path(None)  # Defaults to 'csv'
                try:
                    _print_to_stdout(df, format=output_format)
                except Exception as e:
                    print(f"Error writing to stdout: {e}", file=sys.stderr)
                    sys.exit(1)
        
        else:
            print(f"Error: Unsupported input type: {input_type}", file=sys.stderr)
            sys.exit(1)
        
        # Handle output for single file processing only
        if input_type == 'file':
            if args.output:
                # Save to file (single file processing uses regular save_output)
                try:
                    save_output(df, args.output)
                except Exception as e:
                    print(f"Error saving output: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                # Print to stdout
                output_format = _detect_format_from_path(None)  # Defaults to 'csv'
                try:
                    _print_to_stdout(df, format=output_format)
                except Exception as e:
                    print(f"Error writing to stdout: {e}", file=sys.stderr)
                    sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
