#!/usr/bin/env python3
"""
Test the UML structure parser on the assignment.png diagram.
"""

import os
import sys
from oa_ontology.uml_structure_parser import UMLStructureParser

def main():
    """Main function."""
    # Path to the assignment.png file
    image_path = "html_source/schema/assignment.png"
    
    # Check if the file exists
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        sys.exit(1)
    
    # Output JSON file path
    output_path = "yaml_output/schema/assignment_structure.json"
    
    print(f"Parsing structure of {image_path}...")
    
    try:
        # Parse the UML diagram structure
        parser = UMLStructureParser(image_path)
        structure = parser.save_structure(output_path)
        
        print(f"\nStructure analysis complete!")
        print(f"Debug images saved to: {parser.debug_dir}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()