#!/usr/bin/env python3
"""
Cross-reference UML diagrams with API documentation.

This script combines information from UML diagrams and API documentation
to create a more complete representation of the OpenAccess class structure.
"""

import os
import re
import json
import yaml
import glob
from pathlib import Path
from tqdm import tqdm

class UMLAPIXReferencer:
    """Cross-reference UML diagrams with API documentation."""
    
    def __init__(self, yaml_dir, uml_dir, output_dir, debug=False):
        """Initialize with directories for YAML, UML, and output."""
        self.yaml_dir = yaml_dir
        self.uml_dir = uml_dir
        self.output_dir = output_dir
        self.debug = debug
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        if debug:
            self.debug_dir = os.path.join(output_dir, "debug")
            os.makedirs(self.debug_dir, exist_ok=True)
    
    def load_api_class(self, class_name):
        """Load the API documentation for a class."""
        # Check all module directories for the class
        for module in os.listdir(self.yaml_dir):
            module_dir = os.path.join(self.yaml_dir, module)
            if not os.path.isdir(module_dir):
                continue
                
            # Look for class YAML file - try both class* and struct* prefixes
            for prefix in ["class", "struct"]:
                class_file = os.path.join(module_dir, f"{prefix}{class_name}.yaml")
                if os.path.exists(class_file):
                    with open(class_file, 'r', encoding='utf-8') as f:
                        return yaml.safe_load(f), module
        
        return None, None
    
    def load_uml_class(self, class_name):
        """Load UML information for a class from all available schema files."""
        class_info = None
        relationships = []
        source_files = []
        
        # Look through all UML schema files
        schema_files = glob.glob(os.path.join(self.uml_dir, "*_imagemap.json"))
        
        for schema_file in schema_files:
            with open(schema_file, 'r', encoding='utf-8') as f:
                try:
                    schema_data = json.load(f)
                    
                    # Look for the class in this schema
                    if class_name in schema_data.get('classes', {}):
                        # If class_info is not set yet, use this one
                        if not class_info:
                            class_info = schema_data['classes'][class_name]
                            source_files.append(os.path.basename(schema_file))
                        
                        # Collect relationships from this schema
                        for rel in schema_data.get('relationships', []):
                            if rel.get('source') == class_name or rel.get('target') == class_name:
                                # Check if this relationship is already in our list
                                # We only want to add unique relationships
                                is_duplicate = False
                                for existing_rel in relationships:
                                    if (existing_rel.get('source') == rel.get('source') and
                                        existing_rel.get('target') == rel.get('target') and
                                        existing_rel.get('type') == rel.get('type')):
                                        is_duplicate = True
                                        break
                                
                                if not is_duplicate:
                                    relationships.append(rel)
                                    if schema_file not in source_files:
                                        source_files.append(os.path.basename(schema_file))
                except json.JSONDecodeError:
                    print(f"Error: Could not parse JSON in {schema_file}")
                    continue
        
        return class_info, relationships, source_files
    
    def merge_methods(self, api_methods, uml_methods):
        """Merge method information from API and UML."""
        # Start with API methods since they're more detailed
        merged_methods = []
        
        # Use a dictionary to track methods by signature for quick lookup
        method_map = {}
        
        # Process API methods first
        if api_methods:
            for method in api_methods:
                method_name = method.get('name')
                if not method_name:
                    continue
                
                # Clean up return type - normalize spacing around * for pointers
                return_type = method.get('return_type', '')
                if return_type:
                    # Add space before * but not after (consistent formatting)
                    return_type = re.sub(r'(\w)\*', r'\1 *', return_type)
                    # Remove spaces after * (if any)
                    return_type = re.sub(r'\*\s+', r'*', return_type)
                    method['return_type'] = return_type
                
                # Create a method key that includes signature to handle overloads
                method_sig = method.get('signature', f"{method_name}()")
                method_key = f"{method_name}|{method_sig}"
                
                # Mark the method source
                method['source'] = 'api'
                
                # Add to our merged list
                merged_methods.append(method)
                # Add to map for quick lookup
                method_map[method_key] = method
        
        # Add UML methods if they're not in the API methods
        if uml_methods:
            for method in uml_methods:
                method_name = method.get('name')
                if not method_name:
                    continue
                
                # Clean up return type
                return_type = method.get('return_type', '')
                if return_type:
                    # Add space before * but not after (consistent formatting)
                    return_type = re.sub(r'(\w)\*', r'\1 *', return_type)
                    # Remove spaces after * (if any)
                    return_type = re.sub(r'\*\s+', r'*', return_type)
                    method['return_type'] = return_type
                
                # Create a method key that includes signature to handle overloads
                method_sig = method.get('signature', f"{method_name}()")
                method_key = f"{method_name}|{method_sig}"
                
                # Check if this method exists in API methods
                if method_key in method_map:
                    # Method already exists, update the source to indicate it's in both
                    method_map[method_key]['source'] = 'both'
                    # If API didn't have a description but UML does, use the UML description
                    if (not method_map[method_key].get('description') and method.get('description')):
                        method_map[method_key]['description'] = method.get('description')
                else:
                    # Mark the method source
                    method['source'] = 'uml'
                    # Add to our merged list
                    merged_methods.append(method)
                    # Add to map for quick lookup
                    method_map[method_key] = method
        
        # Sort methods by name for consistency
        return sorted(merged_methods, key=lambda m: m.get('name', ''))
    
    def merge_class_info(self, class_name):
        """Merge API and UML information for a class."""
        # Load API info
        api_info, module = self.load_api_class(class_name)
        
        # Load UML info
        uml_info, relationships, uml_sources = self.load_uml_class(class_name)
        
        # If neither exists, return None
        if not api_info and not uml_info:
            return None
        
        # Start with API info as base
        merged_info = {
            'name': class_name,
            'description': '',
            'module': module if module else 'unknown',
            'inheritance': [],
            'methods': [],
            'attributes': [],
            'relationships': relationships,
            'enumerations': {},
            'sources': {
                'api': bool(api_info),
                'uml': uml_sources if uml_sources else []
            }
        }
        
        # Add API description and methods if available
        if api_info:
            merged_info['description'] = api_info.get('description', '')
            merged_info['inheritance'] = api_info.get('inheritance', [])
            merged_info['enumerations'] = api_info.get('enumerations', {})
        
        # Get UML attributes if available
        if uml_info:
            merged_info['attributes'] = uml_info.get('attributes', [])
        
        # Merge methods from both sources
        api_methods = api_info.get('methods', []) if api_info else []
        uml_methods = uml_info.get('methods', []) if uml_info else []
        merged_info['methods'] = self.merge_methods(api_methods, uml_methods)
        
        return merged_info
    
    def infer_attributes_from_methods(self, merged_info):
        """Infer class attributes from getter/setter methods."""
        methods = merged_info.get('methods', [])
        attributes = merged_info.get('attributes', [])
        attributes_map = {attr.get('name'): attr for attr in attributes if attr.get('name')}
        
        # Look for getter/setter patterns to infer attributes
        getter_pattern = re.compile(r'^get([A-Z]\w+)$')
        setter_pattern = re.compile(r'^set([A-Z]\w+)$')
        is_pattern = re.compile(r'^is([A-Z]\w+)$')
        has_pattern = re.compile(r'^has([A-Z]\w+)$')
        
        for method in methods:
            method_name = method.get('name', '')
            return_type = method.get('return_type', '')
            
            # Skip if no method name or return type
            if not method_name or not return_type:
                continue
            
            # Check for getter pattern
            getter_match = getter_pattern.match(method_name)
            if getter_match:
                attr_name = getter_match.group(1)
                # Convert first letter to lowercase
                attr_name = attr_name[0].lower() + attr_name[1:]
                
                # Add attribute if not already present
                if attr_name not in attributes_map:
                    attributes_map[attr_name] = {
                        'name': attr_name,
                        'type': return_type,
                        'description': f"Inferred from getter method {method_name}",
                        'inferred': True
                    }
                # Update type if we have it and the existing entry doesn't
                elif 'type' not in attributes_map[attr_name] and return_type:
                    attributes_map[attr_name]['type'] = return_type
            
            # Check for is/has pattern (boolean attributes)
            is_match = is_pattern.match(method_name)
            has_match = has_pattern.match(method_name)
            if is_match or has_match:
                attr_match = is_match or has_match
                attr_name = attr_match.group(1)
                # Convert first letter to lowercase
                attr_name = attr_name[0].lower() + attr_name[1:]
                
                # Add attribute if not already present
                if attr_name not in attributes_map:
                    attributes_map[attr_name] = {
                        'name': attr_name,
                        'type': 'oaBoolean',  # is/has methods return boolean values
                        'description': f"Inferred from {'is' if is_match else 'has'} method {method_name}",
                        'inferred': True
                    }
        
        # Convert map back to list
        merged_info['attributes'] = list(attributes_map.values())
        return merged_info
    
    def clean_description(self, description):
        """Clean up class descriptions."""
        if not description:
            return ""
        
        # Remove excessive whitespace
        description = re.sub(r'\s+', ' ', description)
        
        # Remove common noise
        noise_patterns = [
            r'Member Function Documentation',
            r'Member Data Documentation',
            r'Protected Member Functions',
            r'Protected Attributes',
            r'Return to top of page',
            r'Copyright .* Cadence Design Systems, Inc\.',
            r'All Rights Reserved\.',
            r'The documentation for this class was generated from the following file'
        ]
        
        for pattern in noise_patterns:
            description = re.sub(pattern, '', description)
        
        # Fix common encoding issues
        description = description.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        
        return description.strip()
    
    def process_class(self, class_name):
        """Process a single class, merging API and UML information."""
        # Merge information
        merged_info = self.merge_class_info(class_name)
        
        # If no information found, return
        if not merged_info:
            return None
        
        # Clean description
        merged_info['description'] = self.clean_description(merged_info['description'])
        
        # Infer attributes from methods
        merged_info = self.infer_attributes_from_methods(merged_info)
        
        # Save to output file
        output_file = os.path.join(self.output_dir, f"{class_name}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_info, f, indent=2)
        
        # Save debug info if enabled
        if self.debug:
            debug_file = os.path.join(self.debug_dir, f"{class_name}_debug.json")
            debug_info = {
                'class_name': class_name,
                'api_info': self.load_api_class(class_name)[0],
                'uml_info': self.load_uml_class(class_name)[0],
                'merged_info': merged_info
            }
            with open(debug_file, 'w', encoding='utf-8') as f:
                json.dump(debug_info, f, indent=2)
        
        return merged_info
    
    def get_all_class_names(self):
        """Get a list of all class names from API YAML files and UML diagrams."""
        class_names = set()
        
        # Add class names from API YAML files
        for module in os.listdir(self.yaml_dir):
            module_dir = os.path.join(self.yaml_dir, module)
            if not os.path.isdir(module_dir):
                continue
                
            # Look for class YAML files
            for yaml_file in glob.glob(os.path.join(module_dir, "class*.yaml")):
                # Extract class name from filename
                filename = os.path.basename(yaml_file)
                if filename.startswith("class") and filename.endswith(".yaml"):
                    class_name = filename[5:-5]  # Remove "class" prefix and ".yaml" suffix
                    class_names.add(class_name)
            
            # Look for struct YAML files too
            for yaml_file in glob.glob(os.path.join(module_dir, "struct*.yaml")):
                # Extract class name from filename
                filename = os.path.basename(yaml_file)
                if filename.startswith("struct") and filename.endswith(".yaml"):
                    class_name = filename[6:-5]  # Remove "struct" prefix and ".yaml" suffix
                    class_names.add(class_name)
        
        # Add class names from UML schema files
        schema_files = glob.glob(os.path.join(self.uml_dir, "*_imagemap.json"))
        for schema_file in schema_files:
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
                    
                    # Add classes from this schema
                    for class_name in schema_data.get('classes', {}):
                        class_names.add(class_name)
            except json.JSONDecodeError:
                print(f"Error: Could not parse JSON in {schema_file}")
                continue
        
        return sorted(class_names)
    
    def process_all_classes(self):
        """Process all available classes."""
        # Get all class names
        class_names = self.get_all_class_names()
        print(f"Found {len(class_names)} unique class names")
        
        # Process each class
        processed_classes = 0
        for class_name in tqdm(class_names, desc="Processing classes"):
            if self.process_class(class_name):
                processed_classes += 1
        
        print(f"Processed {processed_classes} classes")
        return processed_classes
    
    def generate_summary_report(self):
        """Generate a summary report of the cross-referencing results."""
        # Get all processed class files
        class_files = glob.glob(os.path.join(self.output_dir, "*.json"))
        
        if not class_files:
            print("No processed classes found. Cannot generate report.")
            return
        
        # Initialize counters
        total_classes = len(class_files)
        api_only = 0
        uml_only = 0
        both_sources = 0
        has_description = 0
        has_methods = 0
        has_attributes = 0
        has_relationships = 0
        method_counts = []
        attribute_counts = []
        relationship_counts = []
        
        for class_file in class_files:
            with open(class_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    
                    # Count source types
                    has_api = data.get('sources', {}).get('api', False)
                    has_uml = bool(data.get('sources', {}).get('uml', []))
                    
                    if has_api and has_uml:
                        both_sources += 1
                    elif has_api:
                        api_only += 1
                    elif has_uml:
                        uml_only += 1
                    
                    # Count content types
                    if data.get('description'):
                        has_description += 1
                    
                    methods = data.get('methods', [])
                    if methods:
                        has_methods += 1
                        method_counts.append(len(methods))
                    
                    attributes = data.get('attributes', [])
                    if attributes:
                        has_attributes += 1
                        attribute_counts.append(len(attributes))
                    
                    relationships = data.get('relationships', [])
                    if relationships:
                        has_relationships += 1
                        relationship_counts.append(len(relationships))
                        
                except json.JSONDecodeError:
                    continue
        
        # Calculate averages
        avg_methods = sum(method_counts) / len(method_counts) if method_counts else 0
        avg_attributes = sum(attribute_counts) / len(attribute_counts) if attribute_counts else 0
        avg_relationships = sum(relationship_counts) / len(relationship_counts) if relationship_counts else 0
        
        # Generate report
        report = f"""# Cross-Reference Summary Report

## Overview
- Total classes processed: {total_classes}
- Classes with API documentation only: {api_only} ({api_only/total_classes:.1%})
- Classes with UML diagrams only: {uml_only} ({uml_only/total_classes:.1%})
- Classes with both sources: {both_sources} ({both_sources/total_classes:.1%})

## Content Completeness
- Classes with descriptions: {has_description} ({has_description/total_classes:.1%})
- Classes with methods: {has_methods} ({has_methods/total_classes:.1%})
- Classes with attributes: {has_attributes} ({has_attributes/total_classes:.1%})
- Classes with relationships: {has_relationships} ({has_relationships/total_classes:.1%})

## Statistics
- Average methods per class: {avg_methods:.1f}
- Average attributes per class: {avg_attributes:.1f}
- Average relationships per class: {avg_relationships:.1f}

## Next Steps
1. Review classes missing descriptions
2. Validate relationship types
3. Check for missing inheritance relationships
4. Enhance attribute extraction from UML diagrams
"""
        
        # Save report
        report_file = os.path.join(self.output_dir, "crossref_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"Summary report saved to {report_file}")
        return report_file

def main():
    """Main function."""
    # Define directories
    yaml_dir = "yaml_output"
    uml_dir = "yaml_output/schema"
    output_dir = "ontology_output/crossref"
    
    # Create the cross-referencer
    xrefer = UMLAPIXReferencer(yaml_dir, uml_dir, output_dir, debug=True)
    
    # Process all classes
    print("Cross-referencing UML diagrams with API documentation...")
    xrefer.process_all_classes()
    
    # Generate summary report
    print("Generating summary report...")
    xrefer.generate_summary_report()
    
    print(f"Cross-referenced data saved to {output_dir}")

if __name__ == "__main__":
    main()