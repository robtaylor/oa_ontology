#!/usr/bin/env python3
"""
Convert UML structure JSON representations to YAML format for the ontology.

This script takes the JSON structure files produced by the UML parser
and converts them to YAML format that can be used by the ontology.
"""

import os
import sys
import json
import yaml
import glob
import argparse
from pathlib import Path

def json_to_yaml(json_path, yaml_dir):
    """Convert a JSON structure file to YAML format."""
    print(f"Converting {json_path}")
    
    # Read the JSON file
    with open(json_path, 'r') as f:
        structure = json.load(f)
    
    # Extract diagram name and box names
    diagram_name = structure.get('diagram_name', os.path.basename(json_path).split('_')[0])
    box_names = structure.get('box_names', {})
    boxes = structure.get('boxes', [])
    relationships = structure.get('relationships', [])
    
    # Create a YAML representation
    yaml_data = {
        'diagram': diagram_name,
        'classes': {},
        'relationships': []
    }
    
    # Process class boxes
    for box in boxes:
        box_id = str(box['id'])
        class_name = box_names.get(box_id, f"Class{box_id}")
        
        yaml_data['classes'][class_name] = {
            'id': box_id,
            'position': {
                'x': box['x'],
                'y': box['y'],
                'width': box['width'],
                'height': box['height']
            },
            'methods': [],
            'attributes': []
        }
    
    # Process relationships
    for rel in relationships:
        source_id = str(rel['source_box_id'])
        target_id = str(rel['target_box_id'])
        
        source_name = box_names.get(source_id, f"Class{source_id}")
        target_name = box_names.get(target_id, f"Class{target_id}")
        
        yaml_data['relationships'].append({
            'source': source_name,
            'target': target_name,
            'type': rel['type']
        })
    
    # Create the output YAML file path
    output_file = os.path.join(yaml_dir, f"{diagram_name}.yaml")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the YAML file
    with open(output_file, 'w') as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
    
    print(f"  Created {output_file}")
    return output_file

def main():
    """Main function to convert all JSON structure files to YAML."""
    parser = argparse.ArgumentParser(
        description='Convert UML structure JSON to YAML format for the ontology'
    )
    parser.add_argument(
        '--json-dir',
        default='yaml_output/schema',
        help='Directory containing JSON structure files (default: yaml_output/schema)'
    )
    parser.add_argument(
        '--yaml-dir',
        default='yaml_output/ontology',
        help='Output directory for YAML files (default: yaml_output/ontology)'
    )
    parser.add_argument(
        '--pattern',
        default='*_structure.json',
        help='Glob pattern to find JSON structure files (default: *_structure.json)'
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.yaml_dir, exist_ok=True)
    
    # Find all JSON structure files
    json_pattern = os.path.join(args.json_dir, args.pattern)
    json_files = glob.glob(json_pattern)
    
    if not json_files:
        print(f"No JSON structure files found matching pattern: {json_pattern}")
        sys.exit(1)
    
    print(f"Found {len(json_files)} JSON structure files")
    
    # Convert each JSON file to YAML
    yaml_files = []
    for json_path in json_files:
        yaml_file = json_to_yaml(json_path, args.yaml_dir)
        yaml_files.append(yaml_file)
    
    print(f"\nSummary: Converted {len(yaml_files)} JSON files to YAML format")
    
    # List the created YAML files
    print("\nCreated YAML files:")
    for yaml_file in yaml_files:
        print(f"  {yaml_file}")

if __name__ == "__main__":
    main()