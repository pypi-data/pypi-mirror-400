#!/usr/bin/env python3
"""
Command Line Interface for XHS Note Extractor
"""

import argparse
import sys
from pathlib import Path

from .extractor import XHSNoteExtractor
from .utils import NetworkUtils


def main():
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="Extract Xiaohongshu (Little Red Book) note data from URLs"
    )
    parser.add_argument(
        "url",
        help="Xiaohongshu note URL to extract data from"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not NetworkUtils.is_valid_xhs_url(args.url):
        print(f"Error: Invalid Xiaohongshu URL: {args.url}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.verbose:
            print(f"Extracting data from: {args.url}")
        
        # Initialize extractor
        extractor = XHSNoteExtractor()
        
        # Extract note data
        note_data = extractor.extract_note(args.url)
        
        if not note_data:
            print("Error: Failed to extract note data", file=sys.stderr)
            sys.exit(1)
        
        # Format output
        if args.format == "json":
            import json
            output = json.dumps(note_data, ensure_ascii=False, indent=2)
        else:  # csv
            import csv
            from io import StringIO
            
            # Convert to CSV format (simplified)
            output_buffer = StringIO()
            writer = csv.writer(output_buffer)
            
            # Write headers
            writer.writerow(["Field", "Value"])
            
            # Write data rows
            for key, value in note_data.items():
                if isinstance(value, (list, dict)):
                    value = str(value)
                writer.writerow([key, value])
            
            output = output_buffer.getvalue()
        
        # Output result
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding='utf-8')
            if args.verbose:
                print(f"Output saved to: {output_path}")
        else:
            print(output)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()