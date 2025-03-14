#!/usr/bin/env python3
"""
Combine Schema Structures

This script combines multiple UML structure files (from both image map parsing
and computer vision parsing) into a single ontology file that represents
the complete OpenAccess schema structure.
"""

import os
import sys
import glob
import json
import yaml
import argparse
from pathlib import Path

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def merge_structures(structures):
    """Merge multiple structure files into a single ontology structure."""
    # Create the combined structure
    combined = {
        'diagrams': {},
        'classes': {},
        'relationships': []
    }
    
    # Track class IDs to avoid duplicates
    class_id_counter = 0
    
    # Iterate through all structures
    for structure in structures:
        # Skip invalid structures
        if not structure:
            continue
        
        # Get the diagram name
        diagram_name = structure.get('diagram', 'unknown')
        
        # Add this diagram to the combined structure
        combined['diagrams'][diagram_name] = {
            'title': structure.get('title', diagram_name.capitalize()),
            'classes': [],
            'relationships': []
        }
        
        # Process classes
        classes = structure.get('classes', {})
        for class_name, class_data in classes.items():
            # Skip if this class is already in the combined structure
            if class_name in combined['classes']:
                # Just add this class to the diagram's class list
                combined['diagrams'][diagram_name]['classes'].append(class_name)
                continue
            
            # Create a new class entry
            combined['classes'][class_name] = {
                'id': class_id_counter,
                'name': class_name,
                'position': class_data.get('position', {}),
                'methods': class_data.get('methods', []),
                'attributes': class_data.get('attributes', []),
                'diagrams': [diagram_name]
            }
            
            # Add href if available
            if 'href' in class_data:
                combined['classes'][class_name]['href'] = class_data['href']
            
            # Add to the diagram's class list
            combined['diagrams'][diagram_name]['classes'].append(class_name)
            
            # Increment the class ID counter
            class_id_counter += 1
        
        # Process relationships
        relationships = structure.get('relationships', [])
        for rel in relationships:
            # Get source and target class names
            source = rel.get('source', '')
            target = rel.get('target', '')
            rel_type = rel.get('type', 'association')
            
            # Skip invalid relationships
            if not source or not target:
                continue
            
            # Check if this relationship is already in the combined structure
            existing_rel = next((r for r in combined['relationships'] 
                              if r['source'] == source and 
                                 r['target'] == target and 
                                 r['type'] == rel_type), None)
                                 
            if existing_rel:
                # If it exists, add this diagram to its list of diagrams
                if diagram_name not in existing_rel['diagrams']:
                    existing_rel['diagrams'].append(diagram_name)
            else:
                # Create a new relationship entry
                combined['relationships'].append({
                    'source': source,
                    'target': target,
                    'type': rel_type,
                    'diagrams': [diagram_name]
                })
            
            # Add to the diagram's relationship list
            combined['diagrams'][diagram_name]['relationships'].append({
                'source': source,
                'target': target,
                'type': rel_type
            })
    
    return combined

def save_combined_structure(combined, output_path):
    """Save the combined structure to a file."""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save as JSON
    json_path = output_path
    with open(json_path, 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"Combined structure saved to {json_path}")
    
    # Also save as YAML
    yaml_path = os.path.splitext(output_path)[0] + '.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(combined, f, default_flow_style=False, sort_keys=False)
    
    print(f"Combined YAML saved to {yaml_path}")
    
    return combined

def main():
    """Main function to combine schema structures."""
    parser = argparse.ArgumentParser(
        description='Combine multiple UML structure files into a single ontology file'
    )
    parser.add_argument(
        '--input-dir',
        default='yaml_output/schema',
        help='Directory containing structure files (default: yaml_output/schema)'
    )
    parser.add_argument(
        '--output',
        default='yaml_output/ontology/combined_schema.json',
        help='Output file path (default: yaml_output/ontology/combined_schema.json)'
    )
    parser.add_argument(
        '--pattern',
        default='*_imagemap.json',
        help='Glob pattern to find structure files (default: *_imagemap.json)'
    )
    
    args = parser.parse_args()
    
    # Find all structure files
    pattern = os.path.join(args.input_dir, args.pattern)
    structure_files = glob.glob(pattern)
    
    if not structure_files:
        print(f"No structure files found matching pattern: {pattern}")
        sys.exit(1)
    
    print(f"Found {len(structure_files)} structure files")
    
    # Load all structure files
    structures = []
    for file_path in structure_files:
        print(f"Loading {file_path}")
        structure = load_json_file(file_path)
        if structure:
            structures.append(structure)
    
    print(f"Loaded {len(structures)} valid structure files")
    
    # Merge the structures
    combined = merge_structures(structures)
    
    # Save the combined structure
    save_combined_structure(combined, args.output)
    
    # Print a summary
    print(f"\nCombined structure summary:")
    print(f"- {len(combined['diagrams'])} diagrams")
    print(f"- {len(combined['classes'])} classes")
    print(f"- {len(combined['relationships'])} relationships")

if __name__ == "__main__":
    main()