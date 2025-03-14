#!/usr/bin/env python3
"""
Cross-reference UML diagram information with API documentation to create a complete class model.
"""

import os
import sys
import json
import yaml
from pathlib import Path

def load_json_file(file_path):
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None

def merge_class_info(uml_info, api_info):
    """Merge UML diagram information with API documentation."""
    if not uml_info or not api_info:
        return None
        
    # Create a merged class model
    merged = {
        'name': api_info.get('name'),
        'description': api_info.get('description', ''),
        'methods': [],
        'inheritance': api_info.get('inheritance', []),
        'uml_position': uml_info.get('position', {}),
        'relationships': []
    }
    
    # Combine methods from both sources
    uml_methods = uml_info.get('methods', [])
    api_methods = api_info.get('methods', [])
    
    # Create a dictionary of methods by name for easier lookup
    method_dict = {}
    
    # Add UML methods first
    for method in uml_methods:
        method_name = method.get('name')
        if method_name:
            method_dict[method_name] = method
    
    # Add or update with API methods
    for method in api_methods:
        method_name = method.get('name')
        if not method_name:
            continue
            
        if method_name in method_dict:
            # Update existing method with API details
            method_dict[method_name].update({
                'signature': method.get('signature', ''),
                'return_type': method.get('return_type', ''),
                'is_static': method.get('is_static', False),
                'api_verified': True
            })
        else:
            # Add new method from API
            method['api_verified'] = True
            method_dict[method_name] = method
    
    # Convert back to a list
    merged['methods'] = list(method_dict.values())
    
    return merged

def find_relationships(schema_file, class_name):
    """Find relationships involving the specified class from a schema file."""
    schema = load_json_file(schema_file)
    if not schema:
        return []
        
    relationships = []
    
    # Extract all relationships involving this class
    for rel in schema.get('relationships', []):
        source = rel.get('source')
        target = rel.get('target')
        
        if source == class_name or target == class_name:
            relationships.append(rel)
    
    return relationships

def find_uml_info(schema_files, class_name):
    """Find UML information for a class across all schema files."""
    uml_info = None
    
    for schema_file in schema_files:
        schema = load_json_file(schema_file)
        if not schema:
            continue
            
        classes = schema.get('classes', {})
        if class_name in classes:
            uml_info = classes[class_name]
            break
    
    return uml_info

def main():
    """Main function to cross-reference UML with API."""
    if len(sys.argv) < 2:
        print("Usage: python crossref_api_uml.py <class_name>")
        sys.exit(1)
    
    class_name = sys.argv[1]
    
    # Define paths
    api_file = f"yaml_output/api_docs/{class_name}.json"
    
    # Find schema files
    schema_dir = "yaml_output/schema"
    schema_files = [os.path.join(schema_dir, f) for f in os.listdir(schema_dir) 
                   if f.endswith('_imagemap.json') or f.endswith('_structure.json')]
    
    # Load API info
    api_info = load_json_file(api_file)
    if not api_info:
        print(f"Error: API information not found for {class_name}")
        sys.exit(1)
    
    # Find UML info
    uml_info = find_uml_info(schema_files, class_name)
    if not uml_info:
        print(f"Warning: No UML information found for {class_name} in schema files")
    
    # Find relationships
    relationships = []
    for schema_file in schema_files:
        rels = find_relationships(schema_file, class_name)
        relationships.extend(rels)
    
    # Merge information
    merged_info = merge_class_info(uml_info, api_info)
    if not merged_info:
        print(f"Error merging information for {class_name}")
        sys.exit(1)
    
    # Add relationships
    merged_info['relationships'] = relationships
    
    # Save merged info
    output_file = f"yaml_output/crossref/{class_name}_merged.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(merged_info, f, indent=2)
    
    print(f"Merged information saved to {output_file}")
    
    # Print a summary
    print(f"\nSummary for {class_name}:")
    print(f"- Description: {merged_info.get('description', '')[:100]}...")
    print(f"- Methods: {len(merged_info.get('methods', []))}")
    print(f"- Relationships: {len(merged_info.get('relationships', []))}")
    
    # Print relationship details
    if relationships:
        print("\nRelationships:")
        for rel in relationships:
            source = rel.get('source')
            target = rel.get('target')
            rel_type = rel.get('type')
            direction = "to" if source == class_name else "from"
            other_class = target if source == class_name else source
            
            print(f"- {rel_type} {direction} {other_class}")

if __name__ == "__main__":
    main()