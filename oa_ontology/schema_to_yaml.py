#!/usr/bin/env python3
"""
Schema to YAML Converter

This script converts UML schema diagrams from the OpenAccess documentation
to YAML representation that can be integrated with the ontology.

It uses the UMLParser class to parse diagram images and extract class information.
"""

import os
import sys
import argparse
import json
from pathlib import Path

try:
    from .uml_parser import UMLParser
except ImportError:
    # Allow running as a standalone script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from oa_ontology.uml_parser import UMLParser


def process_schema_diagram(image_path, output_dir):
    """Process a single schema diagram and save the YAML output."""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Parse the image and get the output path
        input_path = Path(image_path)
        output_path = os.path.join(output_dir, input_path.stem + '.yaml')
        
        # Parse the UML diagram
        parser = UMLParser(image_path)
        uml_structure = parser.save_as_yaml(output_path)
        
        return True, output_path
    except Exception as e:
        return False, str(e)


def process_schema_directory(schema_dir, output_dir):
    """Process all PNG files in the schema directory."""
    # Find all PNG files in the schema directory
    image_files = []
    for root, _, files in os.walk(schema_dir):
        for file in files:
            if file.lower().endswith('.png'):
                image_files.append(os.path.join(root, file))
    
    print(f"Found {len(image_files)} schema diagrams")
    
    # Process each image
    results = []
    for image_path in image_files:
        rel_path = os.path.relpath(image_path, schema_dir)
        print(f"Processing {rel_path}...")
        
        success, result = process_schema_diagram(image_path, output_dir)
        
        if success:
            print(f"✓ Saved to {result}")
            results.append({
                'input': rel_path,
                'output': result,
                'status': 'success'
            })
        else:
            print(f"✗ Failed: {result}")
            results.append({
                'input': rel_path,
                'error': result,
                'status': 'error'
            })
    
    # Save a summary of the results
    summary_path = os.path.join(output_dir, 'schema_processing_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSummary saved to {summary_path}")
    print(f"Successful conversions: {sum(1 for r in results if r['status'] == 'success')}/{len(results)}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Convert UML schema diagrams to YAML')
    parser.add_argument('--schema_dir', help='Directory containing schema diagram images', 
                        default='html_source/schema')
    parser.add_argument('--output_dir', help='Directory for YAML output',
                        default='yaml_output/schema')
    parser.add_argument('--single', help='Process a single schema diagram')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.single:
        # Process a single schema diagram
        success, result = process_schema_diagram(args.single, args.output_dir)
        if success:
            print(f"Schema diagram successfully converted to {result}")
            return 0
        else:
            print(f"Error processing schema diagram: {result}")
            return 1
    else:
        # Process all schema diagrams in the directory
        process_schema_directory(args.schema_dir, args.output_dir)
        return 0


if __name__ == "__main__":
    sys.exit(main())