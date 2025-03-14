#!/usr/bin/env python3
"""Process the oaBusTerm class to verify our fixes."""

import sys
import json
from pathlib import Path
from oa_ontology.parse_html import OpenAccessHTMLParser

def main():
    """Process the oaBusTerm class and print the results with command line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process the oaBusTerm class to extract and save its information."
    )
    parser.add_argument(
        "--html-file",
        default="html_source/design/classoaBusTerm.html",
        help="Path to the HTML file (default: html_source/design/classoaBusTerm.html)"
    )
    parser.add_argument(
        "--yaml-dir",
        default="yaml_output",
        help="Output YAML directory (default: yaml_output)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress JSON output to console"
    )
    
    args = parser.parse_args()
    
    html_file = args.html_file
    yaml_dir = args.yaml_dir
    
    # Create a parser
    html_parser = OpenAccessHTMLParser(html_dir="html_source", yaml_dir=yaml_dir)
    
    # Process the file
    class_data = html_parser.extract_class_data(html_file)
    
    # Print the extracted data in JSON format
    if not args.quiet:
        print(json.dumps(class_data, indent=2))
    
    # Save it to a JSON file as well
    output_dir = Path(yaml_dir) / "api_docs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "oaBusTerm.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(class_data, f, indent=2)
    
    print(f"\nSaved to {output_file}")

if __name__ == "__main__":
    main()