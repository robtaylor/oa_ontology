#!/usr/bin/env python3
"""
Parse all UML diagrams in the html_source/schema directory.
This script finds all PNG files and processes them with the ImprovedUMLParser.
"""

import os
import sys
import glob
import argparse
from oa_ontology.improved_uml_parser import ImprovedUMLParser

def parse_diagram(image_path, output_dir, no_debug=False):
    """Parse a single UML diagram."""
    print(f"\nProcessing: {image_path}")
    
    # Get the base name of the image
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Output JSON file path
    output_path = os.path.join(output_dir, f"{image_name}_structure.json")
    
    try:
        # Parse the UML diagram structure
        parser = ImprovedUMLParser(image_path, debug=not no_debug)
        structure = parser.save_structure(output_path)
        
        print(f"  Success! Structure saved to {output_path}")
        print(f"  - {len(structure['boxes'])} class boxes")
        print(f"  - {len(structure['horizontal_lines'])} horizontal divider lines")
        print(f"  - {len(structure['relationships'])} relationships")
        print(f"  - Class names: {structure['box_names']}")
        
        if not no_debug:
            print(f"  - Debug images saved to: {parser.debug_dir}")
        
        return True
        
    except Exception as e:
        print(f"  Error processing {image_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to process all diagrams."""
    parser = argparse.ArgumentParser(
        description='Parse all UML diagrams in html_source/schema directory'
    )
    parser.add_argument(
        '--output-dir', 
        default='yaml_output/schema',
        help='Output directory for structure JSON files (default: yaml_output/schema)'
    )
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable generation of debug images'
    )
    parser.add_argument(
        '--pattern',
        default='html_source/schema/*.png',
        help='Glob pattern to find UML diagrams (default: html_source/schema/*.png)'
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Find all PNG files in the schema directory
    diagram_files = glob.glob(args.pattern)
    
    if not diagram_files:
        print(f"No diagram files found matching pattern: {args.pattern}")
        sys.exit(1)
    
    print(f"Found {len(diagram_files)} diagram files")
    
    # Process each diagram
    success_count = 0
    for image_path in diagram_files:
        if parse_diagram(image_path, args.output_dir, args.no_debug):
            success_count += 1
    
    print(f"\nSummary: Successfully processed {success_count}/{len(diagram_files)} diagrams")
    
    # Return success if all diagrams were processed
    if success_count < len(diagram_files):
        sys.exit(1)

if __name__ == "__main__":
    main()