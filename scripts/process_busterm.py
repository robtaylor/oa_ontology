#!/usr/bin/env python3
"""Process the oaBusTerm class to verify our fixes."""

import sys
import json
from pathlib import Path
from oa_ontology.parse_html import OpenAccessHTMLParser

def main():
    """Process the oaBusTerm class and print the results."""
    html_file = "html_source/design/classoaBusTerm.html"
    yaml_dir = "yaml_output"
    
    # Create a parser
    parser = OpenAccessHTMLParser(html_dir="html_source", yaml_dir=yaml_dir)
    
    # Process the file
    class_data = parser.extract_class_data(html_file)
    
    # Print the extracted data in JSON format
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