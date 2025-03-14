#!/usr/bin/env python3
"""
Run the enhanced domain ontology extraction from cross-referenced data.

This script processes the cross-referenced data (combining UML and API) to create
an enhanced domain ontology with richer relationships.
"""

import os
import sys
import argparse
from pathlib import Path
from oa_ontology.enhanced_domain_ontology import main as enhanced_domain_main

def main():
    """Main function to run enhanced domain ontology extraction."""
    parser = argparse.ArgumentParser(
        description='Extract enhanced domain ontology from cross-referenced data'
    )
    parser.add_argument(
        '--crossref-dir',
        help='Directory containing cross-referenced JSON files (default: ontology_output/crossref)',
        default='ontology_output/crossref'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for domain ontology (default: outputs)',
        default='outputs'
    )
    
    args = parser.parse_args()
    
    # Ensure directories exist
    crossref_dir = Path(args.crossref_dir)
    output_dir = Path(args.output_dir)
    
    if not os.path.isdir(crossref_dir):
        print(f"Cross-reference directory not found: {crossref_dir}")
        print("Please run the cross-referencing process first.")
        sys.exit(1)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Starting enhanced domain ontology extraction from {crossref_dir}...")
    
    # Run the enhanced domain ontology extraction
    enhanced_domain_main()
    
    print(f"Enhanced domain ontology saved to {output_dir}")
    print(f"Results:")
    print(f"- Enhanced domain ontology: {output_dir}/enhanced_domain_ontology.json")
    print(f"- GraphML file for visualization: {output_dir}/enhanced_domain_ontology.graphml")
    print(f"- Detailed report: {output_dir}/enhanced_domain_ontology_report.md")

if __name__ == "__main__":
    main()