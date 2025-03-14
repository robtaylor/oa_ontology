#!/usr/bin/env python3
"""
Parse all HTML files containing image maps for UML diagrams.
This script finds all HTML files in the html_source/schema directory
and extracts UML class information from the image maps.
"""

import os
import sys
import glob
import argparse
from oa_ontology.html_imagemap_parser import HTMLImageMapParser

def parse_html_imagemap(html_path, no_debug=False):
    """Parse a single HTML image map."""
    print(f"\nProcessing: {html_path}")
    
    # Get the base name of the HTML file
    html_name = os.path.splitext(os.path.basename(html_path))[0]
    
    # Check if there's a corresponding PNG file
    png_path = os.path.splitext(html_path)[0] + ".png"
    if not os.path.exists(png_path):
        print(f"  Warning: No matching PNG file found at {png_path}")
        return False
    
    # Output JSON file path
    output_dir = os.path.join("yaml_output", "schema")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{html_name}_imagemap.json")
    
    try:
        # Parse the HTML image map
        parser = HTMLImageMapParser(html_path, debug=not no_debug)
        structure = parser.save_structure(output_path)
        
        print(f"  Success! Structure saved to {output_path}")
        print(f"  - {len(structure['classes'])} classes")
        print(f"  - {len(structure['relationships'])} relationships")
        
        return True
        
    except Exception as e:
        print(f"  Error processing {html_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to process all HTML image maps."""
    parser = argparse.ArgumentParser(
        description='Parse all HTML files containing image maps in html_source/schema directory'
    )
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable generation of debug information'
    )
    parser.add_argument(
        '--pattern',
        default='html_source/schema/*.html',
        help='Glob pattern to find HTML files (default: html_source/schema/*.html)'
    )
    parser.add_argument(
        '--specific',
        help='Process only specific HTML files (comma-separated list without .html extension)'
    )
    
    args = parser.parse_args()
    
    # Find all HTML files in the schema directory
    html_files = glob.glob(args.pattern)
    
    if not html_files:
        print(f"No HTML files found matching pattern: {args.pattern}")
        sys.exit(1)
    
    # Filter for specific files if requested
    if args.specific:
        specific_files = args.specific.split(',')
        html_files = [f for f in html_files if os.path.splitext(os.path.basename(f))[0] in specific_files]
        if not html_files:
            print(f"No HTML files found matching specified names: {args.specific}")
            sys.exit(1)
    
    print(f"Found {len(html_files)} HTML files")
    
    # Process each HTML file
    success_count = 0
    for html_path in html_files:
        if parse_html_imagemap(html_path, args.no_debug):
            success_count += 1
    
    print(f"\nSummary: Successfully processed {success_count}/{len(html_files)} HTML files")
    
    # Return success if all files were processed
    if success_count < len(html_files):
        sys.exit(1)

if __name__ == "__main__":
    main()