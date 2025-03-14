#!/usr/bin/env python3
"""
Run the cross-referencing between UML diagrams and API documentation.

This script processes all OpenAccess classes, combining information from
UML diagrams and API documentation to create a more complete representation.
"""

import os
import sys
import argparse
from pathlib import Path
from oa_ontology.crossref_api_uml import UMLAPIXReferencer

def main():
    """Main function to run cross-referencing."""
    parser = argparse.ArgumentParser(
        description='Cross-reference UML diagrams with API documentation'
    )
    parser.add_argument(
        '--yaml-dir',
        help='Directory containing YAML parsed files (default: yaml_output)',
        default='yaml_output'
    )
    parser.add_argument(
        '--uml-dir',
        help='Directory containing UML schema files (default: yaml_output/schema)',
        default='yaml_output/schema'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for cross-referenced data (default: ontology_output/crossref)',
        default='ontology_output/crossref'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    parser.add_argument(
        '--class',
        dest='class_name',
        help='Process only a specific class'
    )
    
    args = parser.parse_args()
    
    # Ensure directories exist
    base_dir = Path(__file__).parent
    yaml_dir = base_dir / args.yaml_dir
    uml_dir = base_dir / args.uml_dir
    output_dir = base_dir / args.output_dir
    
    os.makedirs(yaml_dir, exist_ok=True)
    os.makedirs(uml_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print("Starting cross-reference of UML diagrams and API documentation...")
    
    # Create the cross-referencer
    xrefer = UMLAPIXReferencer(str(yaml_dir), str(uml_dir), str(output_dir), debug=args.debug)
    
    # Process all classes or a specific class
    if args.class_name:
        print(f"Processing class: {args.class_name}")
        result = xrefer.process_class(args.class_name)
        if result:
            print(f"Successfully processed {args.class_name}")
            print(f"Output saved to: {output_dir / f'{args.class_name}.json'}")
        else:
            print(f"Failed to process {args.class_name}. Class not found in either API or UML data.")
            sys.exit(1)
    else:
        # Process all classes
        processed_count = xrefer.process_all_classes()
        
        print(f"Cross-referencing complete! Processed {processed_count} classes.")
        
        # Generate summary report
        report_file = xrefer.generate_summary_report()
        print(f"Summary report saved to {report_file}")
    
    print(f"Results saved to {output_dir}")

if __name__ == "__main__":
    main()