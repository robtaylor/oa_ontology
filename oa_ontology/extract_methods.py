import re

def extract_methods_from_table(soup):
    """Extract method information from the HTML tables in Public Methods sections."""
    methods = []
    
    # Find all method tables (Public Methods and Static Public Methods sections)
    for section_name in ["Public Methods", "Static Public Methods", "Protected Methods"]:
        is_static = "Static" in section_name
        
        # Find the section heading
        section_regex = re.compile(rf"{section_name}")
        sections = soup.find_all(['h2', 'h3'], string=section_regex)
        
        for section in sections:
            # There are two possible structures in the HTML:
            # 1. Simple table with method info in rows that are direct children
            # 2. Complex nested tables with detailed method signatures
            
            # Get all direct table row elements that follow this section
            # First, get the parent of the section heading
            # In many OpenAccess HTML files, methods are in the same table
            if section.parent and section.parent.name == 'td' and section.parent.parent and section.parent.parent.name == 'tr':
                # The tr element containing the section heading
                section_tr = section.parent.parent
                if section_tr.parent and section_tr.parent.name == 'table':
                    # The table containing all rows including methods
                    section_table = section_tr.parent
                    
                    # Get all row elements that follow the section heading row
                    method_rows = []
                    for tr in section_table.find_all('tr'):
                        if tr is section_tr:
                            # Found the section heading row
                            continue
                        elif tr.find('h2') or tr.find('h3'):
                            # Found next section heading
                            break
                        else:
                            method_rows.append(tr)
                    
                    # Process each row as a method
                    for row in method_rows:
                        cells = row.find_all('td')
                        if len(cells) < 2:
                            continue
                        
                        # First cell is typically return type, second is method name + params
                        return_type_cell = cells[0]
                        method_cell = cells[1]
                        
                        # Skip if no method link
                        method_link = method_cell.find('a')
                        if not method_link:
                            continue
                        
                        # Extract method name and params
                        method_text = method_cell.text.strip()
                        
                        # Extract method name - it can be in different formats
                        if '(' in method_text:
                            # Format: methodName(params)
                            method_match = re.search(r'([a-zA-Z]\w+)\s*\((.*?)\)', method_text)
                            if method_match:
                                method_name = method_match.group(1)
                                params = method_match.group(2).strip()
                            else:
                                # Try to get just the name
                                name_match = re.search(r'([a-zA-Z]\w+)', method_text)
                                if name_match:
                                    method_name = name_match.group(1)
                                    params = ""
                                else:
                                    continue  # Skip if no method name found
                        else:
                            # Format might be just the method name
                            method_name = method_text.strip()
                            params = ""
                        
                        # Get return type
                        return_type = return_type_cell.text.strip()
                        
                        # Add the method
                        methods.append({
                            'name': method_name,
                            'signature': f"{method_name}({params})",
                            'return_type': return_type,
                            'description': "This function is a member of this class.",
                            'is_static': is_static
                        })
                        
                    # Don't look for other tables if we found methods in this one
                    if methods:
                        continue
            
            # If we didn't find methods in the direct table, fall back to looking for tables that follow the section
            tables = section.find_all_next('table', limit=5)  # Look at the next few tables
            
            for table in tables:
                # Skip if we've reached a new section
                if table.find_previous(['h2', 'h3'], string=re.compile(rf"(?!{section_name}).*")) and \
                   table.find_previous(['h2', 'h3'], string=re.compile(rf"(?!{section_name}).*")).find_previous(['h2', 'h3']) == section:
                    break
                
                # Structure 1: Direct table rows
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    
                    # Skip header rows or rows without enough cells
                    if len(cells) < 2:
                        continue
                    
                    # Look for method links
                    method_link = None
                    for cell in cells:
                        if cell.find('a', href=re.compile(r'#[a-zA-Z0-9_]+')):
                            method_link = cell.find('a')
                            method_cell = cell
                            
                            # Try to find return type cell (usually the cell before the method cell)
                            return_type_cell = cells[0] if cell != cells[0] else None
                            break
                    
                    if not method_link:
                        continue
                    
                    # Extract method name and params
                    method_text = method_cell.text.strip()
                    
                    # First try to find a method with parameters
                    method_match = re.search(r'(\w+)\s*\((.*?)\)', method_text)
                    
                    if not method_match:
                        # Try to extract from the link text which often has just the method name
                        link_text = method_link.text.strip()
                        link_match = re.search(r'(\w+)', link_text)
                        
                        if link_match and re.match(r'^[a-zA-Z]', link_match.group(1)):
                            # Make sure it starts with a letter (not a return type like oaUInt4)
                            method_name = link_match.group(1)
                            params = ""
                        else:
                            # Last chance: look for any identifier in the method cell
                            name_match = re.search(r'([a-zA-Z]\w+)', method_text)
                            if name_match:
                                method_name = name_match.group(1)
                                params = ""
                            else:
                                # Skip if we can't figure out the method name
                                continue
                    else:
                        method_name = method_match.group(1)
                        params = method_match.group(2)
                    
                    # Get return type if available
                    return_type = return_type_cell.text.strip() if return_type_cell else ""
                    
                    # Look for static indicator
                    method_is_static = is_static or '[static]' in method_text
                    
                    # Add the method
                    methods.append({
                        'name': method_name,
                        'signature': f"{method_name}({params})",
                        'return_type': return_type,
                        'description': "This function is a member of this class.",
                        'is_static': method_is_static
                    })
                
                # Structure 2: Method signatures in nested tables
                if not methods:
                    # Check for nested tables with complex method signatures
                    for nested_table in table.find_all('table'):
                        method_rows = nested_table.find_all('tr')
                        if not method_rows:
                            continue
                        
                        # Extract method name from first row
                        first_row = method_rows[0]
                        method_cell = first_row.find('td', class_='md')
                        
                        if not method_cell:
                            continue
                        
                        # Try to extract method information
                        method_text = method_cell.text.strip()
                        
                        # For rows that have a full signature with class name and method
                        method_match = re.search(r'(\w+)::([\w~]+)', method_text)
                        
                        if method_match:
                            class_name = method_match.group(1)
                            method_name = method_match.group(2)
                            
                            # Extract return type
                            return_type_match = re.search(r'^(.*?)\s+\w+::', method_text)
                            return_type = return_type_match.group(1).strip() if return_type_match else ""
                        else:
                            # For rows that might just have a method name without class
                            # Often just for error codes or simple methods
                            simple_method_match = re.search(r'([a-zA-Z]\w+)\s*\(', method_text)
                            if simple_method_match:
                                method_name = simple_method_match.group(1)
                                return_type = ""
                            else:
                                # Last resort - try to find any identifier that looks like a method
                                basic_name_match = re.search(r'([a-zA-Z]\w+)', method_text)
                                if basic_name_match:
                                    method_name = basic_name_match.group(1)
                                    return_type = ""
                                else:
                                    # Skip this entry if we can't parse a method name
                                    continue
                            
                            # Extract parameters by joining all rows
                            params = ""
                            for row in method_rows[1:]:
                                param_cell = row.find('td', class_='mdname')
                                if param_cell:
                                    param_text = param_cell.text.strip()
                                    params += param_text.replace("<em>", "").replace("</em>", "")
                            
                            # Clean up parameters
                            params = params.replace("=", " = ")
                            
                            # Check if static
                            method_is_static = is_static or '[static]' in str(nested_table)
                            
                            # Add the method
                            methods.append({
                                'name': method_name,
                                'signature': f"{method_name}({params})",
                                'return_type': return_type,
                                'description': "This function is a member of this class.",
                                'is_static': method_is_static
                            })
    
    # Filter out error codes that are mistakenly identified as methods
    filtered_methods = []
    for method in methods:
        # Skip error codes (typically prefixed with "oac")
        if method['name'].startswith('oac') and method['return_type'] == '':
            continue
            
        # Skip if the method name is a return type (like oaUInt4)
        if re.match(r'^oa(UInt|Int|Boolean|String|Float|Double|Char)\d*$', method['name']):
            continue
            
        filtered_methods.append(method)
    
    # Remove duplicate methods
    unique_methods = {}
    for method in filtered_methods:
        if method['name'] not in unique_methods:
            unique_methods[method['name']] = method
    
    return list(unique_methods.values())