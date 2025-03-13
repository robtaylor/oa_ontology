#!/usr/bin/env python3
"""
HTML to YAML parser for OpenAccess documentation.

This script parses the HTML class documentation from OpenAccess and
converts it to structured YAML files for easier processing.
"""

import os
import re
import tomli
import yaml
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm
from .extract_methods import extract_methods_from_table

# Load configuration from pyproject.toml
try:
    with open('pyproject.toml', 'rb') as f:
        config = tomli.load(f)
    
    # Extract directories from pyproject.toml
    oa_config = config.get('tool', {}).get('oa-ontology', {})
    default_dirs = oa_config.get('default_directories', {})
    
    HTML_DIR = default_dirs.get('html_dir', 'html_source')
    YAML_DIR = default_dirs.get('yaml_dir', 'yaml_output')
    
    # Get the list of modules
    MODULES = oa_config.get('modules', ['design', 'base', 'tech', 'cms', 'wafer', 'block'])
    
    # Create MODULE_DIRS mapping
    MODULE_DIRS = {}
    for module in MODULES:
        MODULE_DIRS[module] = os.path.join(HTML_DIR, module)
except Exception as e:
    print(f"Error loading configuration: {e}")
    # Default values if configuration loading fails
    HTML_DIR = 'html_source'
    YAML_DIR = 'yaml_output'
    MODULE_DIRS = {
        'design': os.path.join(HTML_DIR, 'design'),
        'base': os.path.join(HTML_DIR, 'base'),
        'tech': os.path.join(HTML_DIR, 'tech'),
        'cms': os.path.join(HTML_DIR, 'cms'),
        'wafer': os.path.join(HTML_DIR, 'wafer'),
        'block': os.path.join(HTML_DIR, 'block')
    }

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
            
            # Get content between "Detailed Description" and the next h2 or hr tag
            if section.name == 'h2':
                next_section = section.find_next(['h2', 'hr'])
                if next_section:
                    # Get all content between detailed_desc and next_section
                    content = []
                    current = section.next_sibling
                    
                    while current and current != next_section:
                        if hasattr(current, 'text') and current.text.strip():
                            content.append(current.text.strip())
                        elif isinstance(current, str) and current.strip():
                            content.append(current.strip())
                        current = current.next_sibling
                    
                    if content:
                        # Join the content pieces
                        full_content = ' '.join(content)
                        # Clean it up to ensure we only get the description
                        # Find the first sentence(s) until "Member Function Documentation"
                        member_func_idx = full_content.find("Member Function Documentation")
                        if member_func_idx > 0:
                            description = full_content[:member_func_idx].strip()
                        else:
                            description = full_content.strip()
            
            # If we couldn't find a description, use regex as fallback
            if not description:
                html_content = str(soup)
                detailed_desc_tag = '<h2>Detailed Description</h2>'
                
                if detailed_desc_tag in html_content:
                    # Extract content between detailed description and next tag
                    start_idx = html_content.find(detailed_desc_tag) + len(detailed_desc_tag)
                    end_idx = html_content.find('<hr>', start_idx)
                    
                    if end_idx == -1:
                        end_idx = html_content.find('<h2>', start_idx)
                    
                    if end_idx > start_idx:
                        desc_html = html_content[start_idx:end_idx].strip()
                        desc_soup = BeautifulSoup(desc_html, 'html.parser')
                        description = desc_soup.get_text(separator=' ', strip=True)
        
        # Special case for classes with problematic descriptions
        if not description or len(description) < 20:
            # Try an alternative approach: look for the first paragraph after class name heading
            h1 = soup.find('h1')
            if h1:
                # Get the first substantial paragraph after the h1
                for sibling in h1.find_next_siblings():
                    if sibling.name == 'p' and sibling.text and len(sibling.text.strip()) > 20:
                        description = sibling.text.strip()
                        # Check if we need to get multiple paragraphs
                        next_sibling = sibling.find_next_sibling()
                        while next_sibling and next_sibling.name == 'p' and next_sibling.text.strip():
                            description += " " + next_sibling.text.strip()
                            next_sibling = next_sibling.find_next_sibling()
                        break
        
        # Clean up the description
        if description:
            # Remove excessive whitespace including newlines
            description = re.sub(r'\s+', ' ', description)
            # Remove any remaining HTML tags
            description = re.sub(r'<[^>]+>', ' ', description)
            # Fix the common angle bracket issues in oaObserver references
            description = re.sub(r'oaObserver\s*', 'oaObserver<oaBlock>', description)
            # Clean up common artifacts
            description = re.sub(r'\[static\]', '', description)
            description = re.sub(r'\[virtual\]', '', description)
            # Remove multiple spaces
            description = re.sub(r' {2,}', ' ', description)
            # Remove references to documentation files
            description = re.sub(r'The documentation for this class was generated', '', description)
            # Remove empty parentheses
            description = re.sub(r'\(\s*\)', '', description)
            # Remove "Member Function Documentation" and everything after
            member_func_idx = description.find("Member Function Documentation")
            if member_func_idx > 0:
                description = description[:member_func_idx].strip()
        
        return description.strip()
    
    def extract_inheritance(self, soup):
        """Extract the inheritance hierarchy from the HTML."""
        inheritance = []
        
        # First look for "Inheritance diagram for" section
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
        
        # Alternative approach: look for text like "Inheritance" or "Derived from"
        if not inheritance:
            # Try to find inheritance information in other formats
            inheritance_headings = soup.find_all(['h2', 'h3', 'h4'], string=re.compile(r'Inheritance|Derived from'))
            for heading in inheritance_headings:
                # Check the section after this heading
                next_elem = heading.find_next_sibling()
                while next_elem and next_elem.name not in ['h2', 'h3', 'h4']:
                    # Look for links which are likely to be parent class names
                    links = next_elem.find_all('a')
                    for link in links:
                        class_name = link.text.strip()
                        # Make sure it looks like a class name (typically starts with oa, sd, sr, or I)
                        if re.match(r'^(oa\w+|sd\w+|sr\w+|I\w+)', class_name):
                            inheritance.append(class_name)
                    next_elem = next_elem.find_next_sibling()
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(inheritance))
    
    def extract_methods(self, soup):
        """Extract method information from the HTML."""
        # Use specialized function to extract methods from tables
        methods = extract_methods_from_table(soup)
        
        # If methods were found from tables, return them
        if methods:
            return methods
        
        # Otherwise, try to extract from the full HTML content
        full_html = str(soup)
        
        # Extract all method names and signatures from the HTML
        all_methods = []
        
        # Define patterns to find methods
        method_patterns = [
            r'((?:oa|sd)\w+(?:\s*\*)?)\s+((?:oa|sd)\w+)::([\w~]+)\s*\(([^)]*)\)',  # Return type, class, method, params
            r'(void)\s+((?:oa|sd)\w+)::([\w~]+)\s*\(([^)]*)\)',  # Void methods
            r'(oaBoolean)\s+((?:oa|sd)\w+)::([\w~]+)\s*\(\s*\)'  # Boolean methods without params
        ]
            
        for pattern in method_patterns:
            for match in re.finditer(pattern, full_html):
                return_type = match.group(1).strip()
                class_name = match.group(2).strip()
                method_name = match.group(3).strip()
                params = match.group(4).strip() if len(match.groups()) > 3 else ""
                
                # Find description - look for text after method that starts with "This function"
                start_pos = match.end()
                desc_match = re.search(r'This function[^.;]+[.;]', full_html[start_pos:])
                if desc_match:
                    method_desc = desc_match.group(0)
                else:
                    method_desc = ""
                    
                # Skip if this is a destructor or incorrect method name format
                if method_name.startswith('~') or len(method_name) < 2:
                    continue
                
                # Add to our list of methods
                all_methods.append({
                    'name': method_name,
                    'signature': f"{method_name}({params})",
                    'return_type': return_type,
                    'description': method_desc,
                    'is_static': False  # Can't reliably determine static status here
                })
        
        # If we extracted methods from the HTML, use those
        if all_methods:
            # Remove duplicates
            unique_methods = {}
            for method in all_methods:
                if method['name'] not in unique_methods:
                    unique_methods[method['name']] = method
            
            return list(unique_methods.values())
        
        # Return empty list if no methods were found
        return []
    
    def extract_enumerations(self, soup):
        """Extract enumeration information from the HTML."""
        enumerations = {}
        
        # Find all potential enumeration section headings
        enum_sections = soup.find_all(['h2', 'h3'], string=re.compile(r'Enumerations|Enum(?:eration)? Types?'))
        
        for section in enum_sections:
            # Look for tables immediately after this heading
            current = section.find_next_sibling()
            while current and current.name != 'h2':
                if current.name == 'table':
                    # This is likely an enumeration table
                    rows = current.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            # Extract enumeration name and description
                            enum_cell = cells[1]  # Enum name typically in second cell
                            link = enum_cell.find('a')
                            
                            if link:
                                enum_name = link.text.strip()
                                enum_id = link.get('href', '').replace('#', '')
                                
                                # Look for enumeration values
                                enum_anchor = soup.find('a', {'name': enum_id})
                                if not enum_anchor:
                                    # Try alternate anchor format
                                    enum_anchor = soup.find('a', {'id': enum_id})
                                
                                if enum_anchor:
                                    values = {}
                                    
                                    # Find the enumeration table - try multiple approaches
                                    values_table = enum_anchor.find_next('table')
                                    
                                    # If table not found immediately, look within the next div or section
                                    if not values_table:
                                        next_section = enum_anchor.find_next(['div', 'section'])
                                        if next_section:
                                            values_table = next_section.find('table')
                                    
                                    if values_table:
                                        for value_row in values_table.find_all('tr'):
                                            value_cells = value_row.find_all('td')
                                            if len(value_cells) >= 2:
                                                value_name = value_cells[0].text.strip()
                                                value_desc = value_cells[1].text.strip()
                                                values[value_name] = value_desc
                                    else:
                                        # Alternative: Look for definition list (dl, dt, dd) format
                                        dl = enum_anchor.find_next('dl')
                                        if dl:
                                            dts = dl.find_all('dt')
                                            for dt in dts:
                                                value_name = dt.text.strip()
                                                dd = dt.find_next('dd')
                                                value_desc = dd.text.strip() if dd else ""
                                                values[value_name] = value_desc
                                        else:
                                            # Last resort: look for code blocks that might contain enum values
                                            code_block = enum_anchor.find_next('pre')
                                            if code_block:
                                                enum_text = code_block.text
                                                # Try to parse enum values from the code block
                                                enum_matches = re.findall(r'(\w+)\s*(?:=\s*\w+)?\s*,?\s*(?:///<\s*(.+))?', enum_text)
                                                for match in enum_matches:
                                                    value_name = match[0].strip()
                                                    value_desc = match[1].strip() if len(match) > 1 else ""
                                                    values[value_name] = value_desc
                                    
                                    # Only add non-empty enumerations
                                    if values:
                                        enumerations[enum_name] = values
                
                current = current.find_next_sibling()
        
        # If no enumerations found, try to find them in the detailed description
        if not enumerations:
            # Look for sections that might contain enumerations
            enum_candidates = soup.find_all(['h3', 'h4'], string=re.compile(r'Enum(?:eration)?|Values'))
            for candidate in enum_candidates:
                enum_name = re.sub(r'Enum(?:eration)?|Values', '', candidate.text).strip()
                values = {}
                
                # Look for a table or list after this heading
                table = candidate.find_next('table')
                if table:
                    for row in table.find_all('tr'):
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            value_name = cells[0].text.strip()
                            value_desc = cells[1].text.strip()
                            values[value_name] = value_desc
                else:
                    # Try to find a list
                    list_elem = candidate.find_next(['ul', 'ol', 'dl'])
                    if list_elem:
                        if list_elem.name == 'dl':
                            # Definition list
                            dts = list_elem.find_all('dt')
                            for dt in dts:
                                value_name = dt.text.strip()
                                dd = dt.find_next('dd')
                                value_desc = dd.text.strip() if dd else ""
                                values[value_name] = value_desc
                        else:
                            # Regular list
                            for item in list_elem.find_all('li'):
                                item_text = item.text.strip()
                                # Try to split into name and description
                                parts = re.split(r'[:-]', item_text, 1)
                                if len(parts) >= 2:
                                    value_name = parts[0].strip()
                                    value_desc = parts[1].strip()
                                    values[value_name] = value_desc
                
                # Add if values were found
                if values and enum_name:
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