#!/usr/bin/env python3
"""
Test the improved UML structure parser on multiple diagram types.
"""

import os
import sys
import json
from oa_ontology.improved_uml_parser import ImprovedUMLParser

def test_parser(image_path):
    """Test the parser on a specific image."""
    print(f"\n=== Testing parser on {image_path} ===")
    
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        return False
    
    # Get the image name without extension
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Output JSON file path
    output_dir = os.path.join("yaml_output", "schema")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{image_name}_structure.json")
    
    print(f"Parsing structure of {image_path}...")
    
    try:
        # Parse the UML diagram structure
        parser = ImprovedUMLParser(image_path)
        structure = parser.save_structure(output_path)
        
        print(f"\nStructure analysis complete!")
        print(f"- {len(structure['boxes'])} class boxes")
        print(f"- {len(structure['horizontal_lines'])} horizontal divider lines")
        print(f"- {len(structure['relationships'])} relationships")
        print(f"- Class names: {structure['box_names']}")
        print(f"Debug images saved to: {parser.debug_dir}")
        print(f"Structure saved to: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    # Test diagrams
    diagrams = [
        "html_source/schema/assignment.png",
        "html_source/schema/term.png"
    ]
    
    success_count = 0
    
    for diagram in diagrams:
        if test_parser(diagram):
            success_count += 1
    
    print(f"\nSuccessfully processed {success_count}/{len(diagrams)} diagrams")
    
    if success_count < len(diagrams):
        sys.exit(1)

if __name__ == "__main__":
    main()