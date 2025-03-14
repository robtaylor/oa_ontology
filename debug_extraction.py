#!/usr/bin/env python3
"""Debug script for HTML extraction issues."""

import os
import sys
from bs4 import BeautifulSoup
from oa_ontology.parse_html import OpenAccessHTMLParser

def find_html_file(directory, class_name):
    """Find the HTML file for a specific class."""
    # First try direct match with the class name
    direct_match = os.path.join(directory, "guide", f"{class_name}.html")
    if os.path.exists(direct_match):
        return direct_match
        
    # Then try class or struct prefix
    class_match = os.path.join(directory, "guide", f"class{class_name}.html")
    if os.path.exists(class_match):
        return class_match
        
    struct_match = os.path.join(directory, "guide", f"struct{class_name}.html")
    if os.path.exists(struct_match):
        return struct_match
    
    # Finally search all files
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.html'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Check for both the class name and a common pattern like "class className"
                        if class_name in content and (
                            f"class {class_name}" in content or 
                            f"<title>{class_name}" in content or
                            f">{class_name} Class<" in content
                        ):
                            return file_path
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    return None

def debug_extraction(html_dir, class_name):
    """Debug the extraction process for a specific class."""
    # For oaBusTerm, we know the exact file path
    if class_name == "oaBusTerm":
        file_path = "html_source/design/classoaBusTerm.html"
    else:
        file_path = find_html_file(html_dir, class_name)
    
    if not file_path:
        print(f"Could not find HTML file for {class_name}")
        return
    
    print(f"Found HTML file: {file_path}")
    
    # Create parser
    parser = OpenAccessHTMLParser(html_dir, "yaml_output")
    
    # Extract class data
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Print the modified date of the file
    import os
    print(f"File last modified: {os.path.getmtime(file_path)}")
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract and print detailed components for debugging
    print("\n=== Class Name ===")
    name = parser.extract_name(soup)
    print(f"Extracted name: {name}")
    
    print("\n=== Class Description ===")
    description = parser.extract_description(soup)
    print(f"Description: {description}")
    
    print("\n=== Class Methods ===")
    methods = parser.extract_methods(soup)
    
    # Group methods by name
    method_groups = {}
    for method in methods:
        name = method['name']
        if name not in method_groups:
            method_groups[name] = []
        method_groups[name].append(method)
    
    # Display methods grouped by name
    for i, (name, variants) in enumerate(sorted(method_groups.items())):
        print(f"{i+1}. {name} - Return: {variants[0]['return_type']} - Static: {variants[0]['is_static']}")
        for j, variant in enumerate(variants):
            print(f"   {j+1}. Signature: {variant['signature']}")
    
    # Check if "Member Function Documentation" is in the HTML
    member_func_text = "Member Function Documentation"
    member_func_idx = content.find(member_func_text)
    if member_func_idx > -1:
        context_start = max(0, member_func_idx - 100)
        context_end = min(len(content), member_func_idx + 100)
        print(f"\nFound '{member_func_text}' at position {member_func_idx}")
        print(f"Context: {content[context_start:context_end]}")
    
    # Find the "Detailed Description" section for debug
    detailed_desc = soup.find(string="Detailed Description")
    if detailed_desc and detailed_desc.parent:
        print("\n=== Detailed Description Section ===")
        section = detailed_desc.parent
        print(f"Section: {section}")
        
        # Find the next heading or hr
        next_section = section.find_next(['h2', 'hr'])
        if next_section:
            print(f"\nNext section: {next_section}")
            
            # Get content between detailed description and next section
            content = []
            current = section.next_sibling
            
            print("\nContent between sections:")
            count = 0
            while current and current != next_section and count < 10:
                print(f"Type: {type(current)}, Content: {current}")
                count += 1
                current = current.next_sibling

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_extraction.py <class_name>")
        sys.exit(1)
    
    html_dir = "html_source"
    class_name = sys.argv[1]
    
    debug_extraction(html_dir, class_name)