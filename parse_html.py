#!/usr/bin/env python3
"""
HTML to YAML parser for OpenAccess documentation.

This script parses the HTML class documentation from OpenAccess and
converts it to structured YAML files for easier processing.
"""

import os
import re
import json
import yaml
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm

# Load configuration
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

# Constants
HTML_DIR = CONFIG["html_dir"]
YAML_DIR = CONFIG["yaml_dir"]
MODULE_DIRS = CONFIG["module_dirs"]

class OpenAccessHTMLParser:
    """Parser for OpenAccess HTML class documentation."""
    
    def __init__(self, html_dir, yaml_dir):
        """Initialize the parser with input and output directories."""
        self.html_dir = html_dir
        self.yaml_dir = yaml_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(yaml_dir, exist_ok=True)
    
    def extract_name(self, soup):
        """Extract the class name from the HTML."""
        title = soup.find('title')
        if title:
            # Extract class name from title (e.g., "oaDesign Class Reference")
            title_text = title.text.strip()
            match = re.search(r'^(oa\w+|sd\w+|sr\w+|I\w+)', title_text)
            if match:
                return match.group(1)
        
        # Fallback: try to find the class name in the first heading
        h1 = soup.find('h1')
        if h1:
            h1_text = h1.text.strip()
            match = re.search(r'^(oa\w+|sd\w+|sr\w+|I\w+)', h1_text)
            if match:
                return match.group(1)
        
        return None
    
    def extract_description(self, soup):
        """Extract the class description from the HTML."""
        # Look for the detailed description section
        description = ""
        detailed_desc = soup.find(string=re.compile("Detailed Description"))
        if detailed_desc and detailed_desc.parent:
            # Find the section after the heading
            section = detailed_desc.parent
            
            # Try to find the content after the heading
            content_section = None
            
            # Try different approaches to find the description
            if section.name == 'h2':
                # Find all text until the next h2 or hr
                content_section = section.find_next_sibling()
                if content_section:
                    # Get all content until next h2 or hr
                    description_parts = []
                    current = content_section
                    while current and current.name not in ['h2', 'hr']:
                        if current.string:
                            description_parts.append(current.text.strip())
                        current = current.find_next_sibling()
                    description = ' '.join(description_parts)
            
            # If we couldn't find a description, use regex as fallback
            if not description:
                html_content = str(soup)
                match = re.search(r'<h2>Detailed Description</h2>(.*?)(?:<hr>|<h2)', html_content, re.DOTALL)
                if match:
                    # Clean up HTML tags
                    desc_html = match.group(1).strip()
                    desc_soup = BeautifulSoup(desc_html, 'html.parser')
                    description = desc_soup.get_text(separator=' ', strip=True)
        
        # Special case for oaBlock and similar classes with problematic descriptions
        if not description or len(description) < 20:
            # Try an alternative approach: look for the first paragraph after class name heading
            h1 = soup.find('h1')
            if h1:
                # Get the first substantial paragraph after the h1
                for sibling in h1.find_next_siblings():
                    if sibling.name == 'p' and sibling.text and len(sibling.text.strip()) > 20:
                        description = sibling.text.strip()
                        break
        
        return description.strip()
    
    def extract_inheritance(self, soup):
        """Extract the inheritance hierarchy from the HTML."""
        inheritance = []
        inheritance_section = soup.find(string=re.compile("Inheritance diagram for"))
        
        if inheritance_section and inheritance_section.parent:
            # Look for the inheritance diagram image
            img = inheritance_section.parent.find_next('img')
            if img and img.get('src', '').endswith('.png'):
                # Try to find the inheritance list
                div = img.parent
                if div:
                    # Find ordered or unordered lists
                    lists = div.find_all(['ol', 'ul'])
                    for list_elem in lists:
                        # Extract class names from list items
                        for item in list_elem.find_all('li'):
                            class_link = item.find('a')
                            if class_link:
                                class_name = class_link.text.strip()
                                inheritance.append(class_name)
        
        return inheritance
    
    def extract_methods(self, soup):
        """Extract method information from the HTML."""
        methods = []
        
        # Find the member functions section
        member_functions = soup.find(string=re.compile("Member Functions"))
        
        if member_functions and member_functions.parent:
            # Find all tables in this section
            tables = member_functions.parent.find_all_next('table', limit=5)
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Extract method signature
                        sig_cell = cells[1]
                        link = sig_cell.find('a')
                        
                        if link:
                            method_name = link.text.strip()
                            sig_text = sig_cell.text.strip()
                            
                            # Extract return type from the first cell
                            return_type = cells[0].text.strip()
                            
                            # Try to find the method description
                            method_id = link.get('href', '').replace('#', '')
                            method_desc = ""
                            
                            # Look for the method details
                            method_anchor = soup.find('a', {'name': method_id})
                            if method_anchor:
                                # Find the method description
                                desc_section = method_anchor.find_next('div', {'class': 'memdoc'})
                                if desc_section:
                                    method_desc = desc_section.text.strip()
                            
                            # Determine if method is static
                            is_static = "[static]" in sig_text
                            
                            methods.append({
                                'name': method_name,
                                'signature': sig_text,
                                'return_type': return_type,
                                'description': method_desc,
                                'is_static': is_static
                            })
        
        return methods
    
    def extract_enumerations(self, soup):
        """Extract enumeration information from the HTML."""
        enumerations = {}
        
        # Find the enumerations section
        enum_section = soup.find(string=re.compile("Enumerations"))
        
        if enum_section and enum_section.parent:
            # Find all enumeration tables
            tables = enum_section.parent.find_all_next('table', limit=5)
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Extract enumeration name and description
                        enum_cell = cells[1]
                        link = enum_cell.find('a')
                        
                        if link:
                            enum_name = link.text.strip()
                            enum_id = link.get('href', '').replace('#', '')
                            
                            # Look for enumeration values
                            enum_anchor = soup.find('a', {'name': enum_id})
                            if enum_anchor:
                                values = {}
                                
                                # Find the enumeration table
                                values_table = enum_anchor.find_next('table')
                                if values_table:
                                    for value_row in values_table.find_all('tr'):
                                        value_cells = value_row.find_all('td')
                                        if len(value_cells) >= 2:
                                            value_name = value_cells[0].text.strip()
                                            value_desc = value_cells[1].text.strip()
                                            values[value_name] = value_desc
                                
                                enumerations[enum_name] = values
        
        return enumerations
    
    def extract_class_data(self, html_file):
        """Extract all class data from an HTML file."""
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        class_data = {
            'name': self.extract_name(soup),
            'description': self.extract_description(soup),
            'inheritance': self.extract_inheritance(soup),
            'methods': self.extract_methods(soup),
            'enumerations': self.extract_enumerations(soup)
        }
        
        return class_data
    
    def save_as_yaml(self, data, output_file):
        """Save data as YAML file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    
    def process_html_file(self, html_file, output_dir):
        """Process a single HTML file."""
        try:
            class_data = self.extract_class_data(html_file)
            
            if class_data['name']:
                # Create output filename based on the input filename
                basename = os.path.basename(html_file)
                yaml_file = os.path.join(output_dir, basename.replace('.html', '.yaml'))
                
                self.save_as_yaml(class_data, yaml_file)
                return True
            else:
                return False
        except Exception as e:
            print(f"Error processing {html_file}: {str(e)}")
            return False
    
    def process_directory(self, input_dir, output_dir):
        """Process all HTML files in a directory."""
        if not os.path.isdir(input_dir):
            print(f"Directory not found: {input_dir}")
            return 0
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all class HTML files
        html_files = []
        for filename in os.listdir(input_dir):
            if filename.endswith('.html') and (
                filename.startswith('class') or 
                filename.startswith('struct')
            ):
                html_files.append(os.path.join(input_dir, filename))
        
        # Process each file
        success_count = 0
        for html_file in tqdm(html_files, desc=f"Processing {os.path.basename(input_dir)}"):
            if self.process_html_file(html_file, output_dir):
                success_count += 1
        
        return success_count

def main():
    """Main function."""
    parser = OpenAccessHTMLParser(HTML_DIR, YAML_DIR)
    total_processed = 0
    
    print(f"Converting HTML documentation to YAML...")
    
    # Process each module directory
    for module, html_dir in MODULE_DIRS.items():
        yaml_output_dir = os.path.join(YAML_DIR, module)
        success_count = parser.process_directory(html_dir, yaml_output_dir)
        
        print(f"✓ Processed {success_count} files from {module}")
        total_processed += success_count
    
    print(f"\nTotal files processed: {total_processed}")
    print(f"YAML files saved to: {YAML_DIR}")

if __name__ == "__main__":
    main()