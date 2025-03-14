#!/usr/bin/env python3
"""
HTML Documentation Extractor for OpenAccess API

This module extracts attributes and methods from OpenAccess API HTML documentation
and enriches the ontology model with this information.
"""

import os
import sys
import re
import json
import yaml
import argparse
import glob
from bs4 import BeautifulSoup

class HTMLDocExtractor:
    """Extracts information from OpenAccess API HTML documentation."""
    
    def __init__(self, html_root_dir, output_dir=None, debug=True):
        """Initialize the extractor with root HTML directory."""
        self.html_root_dir = html_root_dir
        self.debug = debug
        
        # Output directory for extracted structures
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(os.path.dirname(html_root_dir), "yaml_output/api_docs")
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Debug directory
        if debug:
            self.debug_dir = os.path.join(os.path.dirname(html_root_dir), "outputs/debug/api_docs")
            os.makedirs(self.debug_dir, exist_ok=True)
    
    def extract_class_info(self, class_name):
        """Extract class information from HTML documentation."""
        # Try to find the class documentation file
        class_pattern = os.path.join(self.html_root_dir, "design", f"class{class_name}.html")
        if not os.path.exists(class_pattern):
            # Try other common directories
            class_pattern = os.path.join(self.html_root_dir, "base", f"class{class_name}.html")
            if not os.path.exists(class_pattern):
                print(f"Warning: Could not find documentation for {class_name}")
                return None
        
        # Parse the HTML file, trying different encodings
        try:
            with open(class_pattern, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
        except UnicodeDecodeError:
            try:
                with open(class_pattern, 'r', encoding='latin-1') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
            except Exception as e:
                print(f"Error reading {class_pattern}: {str(e)}")
                return None
        
        # Extract class description
        description = ""
        
        # First method: Look for the "Detailed Description" section
        detail_section = None
        for h2 in soup.find_all('h2'):
            if "Detailed Description" in h2.text.strip():
                detail_section = h2
                break
        
        if detail_section:
            # Get the content after the h2 but before the next h2
            desc_content = []
            next_tag = detail_section.find_next()
            
            while next_tag and next_tag.name != 'h2':
                if next_tag.name == 'p':
                    desc_content.append(next_tag.text.strip())
                next_tag = next_tag.find_next()
            
            description = ' '.join(desc_content)
        
        # If the first method fails, try looking for the description in the main content
        if not description:
            # Sometimes the description is just after the inheritance diagram
            inherit_p = soup.find('p', text=lambda text: text and "Inheritance diagram" in text)
            if inherit_p:
                # Get the paragraph after the inheritance diagram
                next_p = inherit_p.find_next('p')
                if next_p:
                    description = next_p.text.strip()
                    
        # Clean up the description
        description = description.replace('\n', ' ').replace('  ', ' ').strip()
        
        # Extract method information
        methods = self.extract_methods(soup, class_name)
        
        # Extract attribute information - attributes are often not explicitly listed
        # but can be inferred from getter/setter methods
        attributes = self.infer_attributes_from_methods(methods)
        
        # Extract inheritance information
        inheritance = self.extract_inheritance(soup)
        
        # Create the class info structure
        class_info = {
            'name': class_name,
            'description': description,
            'methods': methods,
            'attributes': attributes,
            'inheritance': inheritance
        }
        
        return class_info
    
    def extract_methods(self, soup, class_name):
        """Extract method information from class documentation."""
        methods = []
        
        # Method to clean up text by removing excess whitespace and non-breaking spaces
        def clean_text(text):
            if not text:
                return ""
            return re.sub(r'\s+', ' ', text.replace('\u00a0', ' ')).strip()
        
        # Look for method sections in the "Public Methods" section
        public_methods_h2 = None
        for h2 in soup.find_all('h2'):
            if "Public Methods" in h2.text.strip():
                public_methods_h2 = h2
                break
        
        if public_methods_h2:
            # Find the table after the Public Methods header
            methods_table = public_methods_h2.find_next('table')
            if methods_table:
                # Extract methods from the table rows
                for row in methods_table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # First cell typically contains return type, second cell contains method name and params
                        return_type = clean_text(cells[0].get_text())
                        method_sig = clean_text(cells[1].get_text())
                        
                        # Extract method name
                        method_match = re.search(r'([a-zA-Z0-9_]+)\s*\(', method_sig)
                        if method_match:
                            method_name = method_match.group(1)
                            
                            # Skip if this is a constructor or destructor
                            if method_name == class_name or method_name == f"~{class_name}":
                                continue
                            
                            # Extract parameters (everything between parentheses)
                            param_match = re.search(r'\((.*?)\)', method_sig)
                            parameters = []
                            if param_match:
                                param_str = param_match.group(1).strip()
                                if param_str and param_str != "":
                                    # Split parameters by comma, but not commas in template arguments
                                    params = []
                                    current_param = ""
                                    bracket_depth = 0
                                    
                                    for char in param_str:
                                        if char == '<':
                                            bracket_depth += 1
                                            current_param += char
                                        elif char == '>':
                                            bracket_depth -= 1
                                            current_param += char
                                        elif char == ',' and bracket_depth == 0:
                                            params.append(current_param.strip())
                                            current_param = ""
                                        else:
                                            current_param += char
                                    
                                    if current_param:
                                        params.append(current_param.strip())
                                    
                                    parameters = params
                            
                            # Find the detailed method description
                            method_detail = None
                            for a in soup.find_all('a', {'name': True}):
                                if a.get('doxytag') and method_name in a.get('doxytag'):
                                    method_detail = a
                                    break
                            
                            description = ""
                            if method_detail:
                                desc_table = method_detail.find_next('table')
                                if desc_table:
                                    next_p = desc_table.find_next('p')
                                    if next_p:
                                        description = clean_text(next_p.text)
                            
                            # Create the method info
                            method_info = {
                                'name': method_name,
                                'return_type': return_type,
                                'parameters': parameters,
                                'description': description
                            }
                            
                            # Add to methods list
                            methods.append(method_info)
        
        # If we didn't find any methods using the table approach, try the alternate method
        if not methods:
            # Find method documentation sections
            method_sections = soup.find_all('a', {'doxytag': re.compile(fr'{class_name}::[a-zA-Z0-9_]+')})
            
            for section in method_sections:
                # Extract method name
                doxytag = section.get('doxytag', '')
                method_name_match = re.search(fr'{class_name}::([a-zA-Z0-9_]+)', doxytag)
                if not method_name_match:
                    continue
                
                method_name = method_name_match.group(1)
                
                # Skip if this is a constructor or destructor
                if method_name == class_name or method_name == f"~{class_name}":
                    continue
                
                # Find the method signature table
                table = section.find_next('table')
                if not table:
                    continue
                
                # Find the row with the method signature
                signature_row = None
                for row in table.find_all('tr'):
                    text = row.get_text().strip()
                    if method_name in text and '(' in text:
                        signature_row = row
                        break
                
                if not signature_row:
                    continue
                
                # Extract return type and parameters from the signature
                full_sig = clean_text(signature_row.get_text())
                
                # Extract return type (everything before the method name)
                return_type_match = re.search(fr'(.+?){method_name}', full_sig)
                return_type = ""
                if return_type_match:
                    return_type = clean_text(return_type_match.group(1))
                
                # Extract parameters (everything between parentheses)
                param_match = re.search(r'\((.*?)\)', full_sig)
                parameters = []
                if param_match:
                    param_str = param_match.group(1).strip()
                    if param_str and param_str != "":
                        parameters = [p.strip() for p in param_str.split(',')]
                
                # Find the method description
                description = ""
                desc_p = table.find_next('p')
                if desc_p:
                    description = clean_text(desc_p.text)
                
                # Create the method info
                method_info = {
                    'name': method_name,
                    'return_type': return_type,
                    'parameters': parameters,
                    'description': description
                }
                
                # Add to methods list
                methods.append(method_info)
        
        return methods
    
    def infer_attributes_from_methods(self, methods):
        """Infer class attributes from getter/setter methods."""
        attributes = {}
        
        # Look for getter methods (e.g., getName, getValue, etc.)
        for method in methods:
            method_name = method.get('name', '')
            
            # Check if this is a potential getter method
            if method_name.startswith('get') and len(method_name) > 3:
                # Extract attribute name (convert first letter to lowercase)
                attr_name = method_name[3:]
                attr_name = attr_name[0].lower() + attr_name[1:]
                
                # Add attribute if not already present
                if attr_name not in attributes:
                    attributes[attr_name] = {
                        'name': attr_name,
                        'type': method.get('return_type', 'unknown'),
                        'description': f"Inferred from {method_name} method",
                        'has_getter': True,
                        'has_setter': False
                    }
            
            # Check if this is a potential setter method
            elif method_name.startswith('set') and len(method_name) > 3:
                # Extract attribute name (convert first letter to lowercase)
                attr_name = method_name[3:]
                attr_name = attr_name[0].lower() + attr_name[1:]
                
                # Add attribute if not already present, or update existing
                if attr_name in attributes:
                    attributes[attr_name]['has_setter'] = True
                else:
                    attributes[attr_name] = {
                        'name': attr_name,
                        'type': 'unknown',  # Cannot infer type from setter
                        'description': f"Inferred from {method_name} method",
                        'has_getter': False,
                        'has_setter': True
                    }
        
        # Convert dictionary to list
        return list(attributes.values())
    
    def extract_inheritance(self, soup):
        """Extract inheritance information from class documentation."""
        inheritance = []
        
        # Find the inheritance diagram map
        map_tag = soup.find('map')
        if map_tag:
            # Extract parent class links
            area_tags = map_tag.find_all('area')
            for area in area_tags:
                href = area.get('href', '')
                alt = area.get('alt', '')
                
                # Skip if no href or alt
                if not href or not alt:
                    continue
                
                # Extract class name from alt text
                parent_class = alt.strip()
                
                # Add to inheritance list
                inheritance.append(parent_class)
        
        return inheritance
    
    def enhance_ontology_class(self, class_name, existing_class):
        """Enhance an existing ontology class with extracted documentation."""
        class_info = self.extract_class_info(class_name)
        if not class_info:
            return existing_class
        
        # Extract description, methods, and attributes from documentation
        description = class_info.get('description', '')
        doc_methods = class_info.get('methods', [])
        doc_attributes = class_info.get('attributes', [])
        
        # Update the existing class with documentation
        if description:
            existing_class['description'] = description
        
        # Add methods from documentation
        existing_methods = existing_class.get('methods', [])
        existing_method_names = [m.get('name') for m in existing_methods]
        
        for method in doc_methods:
            method_name = method.get('name')
            if method_name not in existing_method_names:
                existing_methods.append(method)
        
        existing_class['methods'] = existing_methods
        
        # Add attributes from documentation
        existing_attributes = existing_class.get('attributes', [])
        existing_attribute_names = [a.get('name') for a in existing_attributes]
        
        for attribute in doc_attributes:
            attr_name = attribute.get('name')
            if attr_name not in existing_attribute_names:
                existing_attributes.append(attribute)
        
        existing_class['attributes'] = existing_attributes
        
        return existing_class
    
    def enhance_ontology(self, ontology_path):
        """Enhance an existing ontology with extracted documentation."""
        # Load the ontology
        with open(ontology_path, 'r') as f:
            if ontology_path.endswith('.json'):
                ontology = json.load(f)
            else:
                ontology = yaml.safe_load(f)
        
        # Enhance each class in the ontology
        classes = ontology.get('classes', {})
        for class_name, class_data in classes.items():
            enhanced_class = self.enhance_ontology_class(class_name, class_data)
            classes[class_name] = enhanced_class
        
        # Update the ontology
        ontology['classes'] = classes
        
        # Save the enhanced ontology
        output_path = os.path.join(self.output_dir, os.path.basename(ontology_path))
        with open(output_path, 'w') as f:
            if output_path.endswith('.json'):
                json.dump(ontology, f, indent=2)
            else:
                yaml.dump(ontology, f, default_flow_style=False, sort_keys=False)
        
        print(f"Enhanced ontology saved to {output_path}")
        
        return ontology

def main():
    """Main function to run the HTML documentation extractor."""
    parser = argparse.ArgumentParser(
        description='Extract and enhance ontology with OpenAccess API documentation'
    )
    parser.add_argument(
        '--html-dir',
        default='html_source',
        help='Root directory containing HTML documentation (default: html_source)'
    )
    parser.add_argument(
        '--ontology',
        default='yaml_output/ontology/combined_schema.yaml',
        help='Path to the ontology file to enhance (default: yaml_output/ontology/combined_schema.yaml)'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for enhanced ontology (default: yaml_output/api_docs)'
    )
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable generation of debug information'
    )
    parser.add_argument(
        '--class',
        dest='class_name',
        help='Extract documentation for a specific class'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize extractor
        extractor = HTMLDocExtractor(
            args.html_dir,
            args.output_dir,
            debug=not args.no_debug
        )
        
        # Extract for a specific class if requested
        if args.class_name:
            class_info = extractor.extract_class_info(args.class_name)
            if class_info:
                # Save to file
                output_path = os.path.join(extractor.output_dir, f"{args.class_name}.json")
                with open(output_path, 'w') as f:
                    json.dump(class_info, f, indent=2)
                print(f"Class information saved to {output_path}")
            else:
                print(f"Failed to extract information for class {args.class_name}")
        else:
            # Enhance the entire ontology
            enhanced_ontology = extractor.enhance_ontology(args.ontology)
            print(f"Enhanced ontology with {len(enhanced_ontology.get('classes', {}))} classes")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()