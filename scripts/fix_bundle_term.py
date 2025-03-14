#!/usr/bin/env python3
"""Process the oaBundleTerm class to fix the description issue."""

import sys
import json
import os
from pathlib import Path
from bs4 import BeautifulSoup

def extract_class_description(html_file):
    """Extract just the class description from HTML file."""
    try:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return "Unable to open HTML file"
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Look for "Detailed Description" section
    detailed_desc = soup.find(string="Detailed Description")
    if not detailed_desc or not detailed_desc.parent:
        return "Description not found"
    
    section = detailed_desc.parent
    
    # Find the next h2 or hr tag
    next_section = section.find_next(['h2', 'hr'])
    if not next_section:
        return "Unable to find end of description section"
    
    # Get all content between section and next_section
    content = []
    current = section.next_sibling
    
    while current and current != next_section:
        if hasattr(current, 'text') and current.text.strip():
            content.append(current.text.strip())
        elif isinstance(current, str) and current.strip():
            content.append(current.strip())
        current = current.next_sibling
    
    # Join the content and clean it up
    description = ' '.join(content)
    
    # Remove Member Function Documentation and everything after
    member_func_idx = description.find("Member Function Documentation")
    if member_func_idx > 0:
        description = description[:member_func_idx].strip()
    
    # Clean up the description
    import re
    description = re.sub(r'\s+', ' ', description)  # Replace multiple whitespace with a single space
    description = description.replace('\n', ' ')
    description = description.strip()
    
    return description

def main():
    """Fix the oaBundleTerm description with command line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix the oaBundleTerm class description and clean up method return types."
    )
    parser.add_argument(
        "--html-file", 
        default="html_source/design/classoaBundleTerm.html",
        help="Path to the HTML file (default: html_source/design/classoaBundleTerm.html)"
    )
    parser.add_argument(
        "--json-file",
        default="yaml_output/api_docs/oaBundleTerm.json",
        help="Path to the JSON file (default: yaml_output/api_docs/oaBundleTerm.json)"
    )
    
    args = parser.parse_args()
    
    html_file = args.html_file
    json_file = args.json_file
    
    if not os.path.exists(html_file):
        print(f"Error: {html_file} not found")
        return
    
    # Extract the correct description
    description = extract_class_description(html_file)
    print(f"Extracted description: {description[:100]}...")
    
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Update the description
    data['description'] = description
    
    # Also clean up the method return types
    for method in data.get('methods', []):
        return_type = method.get('return_type', '')
        if '\n' in return_type:
            # Extract just the return type part
            parts = return_type.split(' ', 1)
            if len(parts) > 0:
                method['return_type'] = parts[0]
    
    # And clean up the attribute types
    for attr in data.get('attributes', []):
        attr_type = attr.get('type', '')
        if '\n' in attr_type:
            # Extract just the type part
            parts = attr_type.split(' ', 1)
            if len(parts) > 0:
                attr['type'] = parts[0]
    
    # Save back to JSON
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Updated {json_file} with fixed description")

if __name__ == "__main__":
    main()