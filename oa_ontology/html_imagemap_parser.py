#!/usr/bin/env python3
"""
HTML Image Map Parser for UML Diagrams

This module extracts UML class information from HTML image maps in the OpenAccess documentation.
Instead of using computer vision techniques, it parses the HTML files that contain image maps
defining the clickable areas of UML diagrams, which provide exact coordinates and links
for each UML element.
"""

import os
import sys
import re
import json
import yaml
import argparse
from pathlib import Path
from bs4 import BeautifulSoup

class HTMLImageMapParser:
    """Parser for extracting UML diagram information from HTML image maps."""
    
    def __init__(self, html_path, debug=True):
        """Initialize the parser with an HTML file."""
        self.html_path = html_path
        self.debug = debug
        
        # Check if the HTML file exists
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"HTML file not found: {html_path}")
        
        # Get the related PNG file path (same name but with .png extension)
        self.png_path = os.path.splitext(html_path)[0] + ".png"
        if not os.path.exists(self.png_path):
            raise FileNotFoundError(f"PNG file not found: {self.png_path}")
            
        # Get the base directory for output
        base_dir = os.path.dirname(os.path.dirname(html_path))
        self.output_dir = os.path.join(base_dir, "yaml_output", "schema")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up debug directory if needed
        if self.debug:
            self.debug_dir = os.path.join(base_dir, "outputs", "debug", "imagemap")
            os.makedirs(self.debug_dir, exist_ok=True)
        
        # Parse the HTML file
        with open(html_path, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Extract diagram name from HTML path or H1 tag
        self.diagram_name = os.path.splitext(os.path.basename(html_path))[0]
        h1_tag = self.soup.find('h1')
        if h1_tag:
            self.diagram_title = h1_tag.text.strip()
        else:
            self.diagram_title = self.diagram_name.capitalize()
    
    def extract_image_map(self):
        """Extract the image map data from the HTML."""
        # Find the image map
        map_tag = self.soup.find('map')
        if not map_tag:
            raise ValueError(f"No image map found in {self.html_path}")
        
        # Extract area tags
        area_tags = map_tag.find_all('area')
        if not area_tags:
            raise ValueError(f"No area tags found in image map in {self.html_path}")
        
        return area_tags
    
    def parse_areas(self, area_tags):
        """Parse area tags to extract class information."""
        classes = {}
        
        for area in area_tags:
            # Extract shape and coordinates
            shape = area.get('shape', '').lower()
            coords_str = area.get('coords', '')
            href = area.get('href', '')
            
            # Skip if no coordinates or href
            if not coords_str or not href:
                continue
            
            # Parse coordinates
            coords = [int(c.strip()) for c in coords_str.split(',')]
            
            # For rectangular shapes, we expect 4 coordinates: x1, y1, x2, y2
            if shape == 'rect' and len(coords) == 4:
                x1, y1, x2, y2 = coords
                width = x2 - x1
                height = y2 - y1
                
                # Extract class name from href
                class_name = self.extract_class_name(href)
                class_id = len(classes)
                
                # Add to classes dictionary
                classes[class_name] = {
                    'id': class_id,
                    'position': {
                        'x': x1,
                        'y': y1,
                        'width': width,
                        'height': height
                    },
                    'href': href,
                    'methods': [],
                    'attributes': []
                }
        
        return classes
    
    def extract_class_name(self, href, coords=None):
        """
        Extract class name from the href link or make an educated guess based on coordinates.
        
        Args:
            href: The href attribute from the area tag
            coords: Optional coordinates to help identify the class when href is ambiguous
        """
        # First, try to extract from direct class links
        class_match = re.search(r'class(oa\w+)\.html', href)
        if class_match:
            return class_match.group(1)
        
        # If not a direct class link, extract from the path
        path_part = os.path.basename(href)
        name_part = os.path.splitext(path_part)[0]
        
        # For links to other schema pages, use a prefix to avoid name collisions
        if name_part in ['block', 'term', 'net', 'pin', 'inst', 'route', 'occurrence']:
            return f"oa{name_part.capitalize()}"
        
        # Special handling for parasitic.html links which could be various classes
        if name_part == 'parasitic' and coords:
            x1, y1, x2, y2 = [int(c) for c in coords.split(',')]
            
            # Based on y-position in the term.html diagram, make educated guesses
            # These are based on examining the term.html image and coordinates
            if 65 <= y1 <= 75:  # Around y=70
                return "oaReducedModel"
            elif 115 <= y1 <= 125:  # Around y=120
                return "oaElmore"
            elif 155 <= y1 <= 165:  # Around y=160
                return "oaPoleResidue"
            elif 205 <= y1 <= 215:  # Around y=210
                return "oaCellTerm"
            elif 245 <= y1 <= 255:  # Around y=250
                return "oaTermConnectDef"
            elif 455 <= y1 <= 465:  # Around y=460
                return "oaPin"
            elif 485 <= y1 <= 495:  # Around y=490
                return "oaNet"
            elif 525 <= y1 <= 535:  # Around y=530
                return "oaNetTermConnectDefObserver"
            elif 575 <= y1 <= 585:  # Around y=580
                return "oaTermNetObserver"
            elif 715 <= y1 <= 735:  # Around y=720
                return "oaPinFig"
        
        return f"Unknown_{name_part}"
        
    def parse_areas(self, area_tags):
        """Parse area tags to extract class information."""
        classes = {}
        
        for area in area_tags:
            # Extract shape and coordinates
            shape = area.get('shape', '').lower()
            coords_str = area.get('coords', '')
            href = area.get('href', '')
            
            # Skip if no coordinates or href
            if not coords_str or not href:
                continue
            
            # Parse coordinates
            coords = [int(c.strip()) for c in coords_str.split(',')]
            
            # For rectangular shapes, we expect 4 coordinates: x1, y1, x2, y2
            if shape == 'rect' and len(coords) == 4:
                x1, y1, x2, y2 = coords
                width = x2 - x1
                height = y2 - y1
                
                # Extract class name from href, passing coords for special cases
                class_name = self.extract_class_name(href, coords_str)
                
                # Skip duplicate oaTerm entries (can appear multiple times in image map)
                if class_name in classes:
                    # If this is a larger or more centered representation of the class,
                    # replace the old entry with this one
                    old_area = classes[class_name]['position']['width'] * classes[class_name]['position']['height']
                    new_area = width * height
                    
                    if new_area <= old_area:
                        continue
                
                # Add to classes dictionary with a unique ID
                classes[class_name] = {
                    'id': len(classes),
                    'position': {
                        'x': x1,
                        'y': y1,
                        'width': width,
                        'height': height
                    },
                    'href': href,
                    'methods': [],
                    'attributes': []
                }
        
        return classes
    
    def infer_relationships(self, classes):
        """Infer relationships between classes based on the diagram structure and documentation."""
        relationships = []
        
        # Determine diagram type based on the diagram name
        diagram_type = self.diagram_name.lower()
        
        # Add diagram-specific relationships - using documented relationships
        # to ensure accuracy
        if diagram_type == 'assignment':
            # In assignment.html, looking at the diagram and documentation:
            
            # Add documented inheritance relationships 
            inheritance_pairs = [
                ('oaConnectDef', 'oaNetConnectDef'),     # Class inheritance
                ('oaConnectDef', 'oaTermConnectDef'),    # Class inheritance
                ('oaAssignment', 'oaAssignAssignment'),  # Class inheritance
                ('oaAssignment', 'oaAssignValue')        # Class inheritance
            ]
            
            for parent, child in inheritance_pairs:
                if parent in classes and child in classes:
                    relationships.append({
                        'source': parent,
                        'target': child,
                        'type': 'inheritance',
                        'description': f"{child} inherits from {parent}"
                    })
            
            # Add usage relationships
            usage_pairs = [
                ('oaAssignmentDef', 'oaNetConnectDef'),   # Usage relationship
                ('oaAssignmentDef', 'oaTermConnectDef'),  # Usage relationship
                ('oaAssignmentDef', 'oaAssignAssignment') # Usage relationship
            ]
            
            for source, target in usage_pairs:
                if source in classes and target in classes:
                    relationships.append({
                        'source': source,
                        'target': target,
                        'type': 'usage',
                        'description': f"{source} uses {target}"
                    })
            
            # Add association relationships
            association_pairs = [
                ('oaNetConnectDef', 'oaNet'),      # Association
                ('oaTermConnectDef', 'oaTerm')     # Association
            ]
            
            for source, target in association_pairs:
                if source in classes and target in classes:
                    relationships.append({
                        'source': source,
                        'target': target,
                        'type': 'association',
                        'description': f"{source} is associated with {target}"
                    })
        
        elif diagram_type == 'term':
            # In term.html, oaTerm is the parent class for various term types
            
            # Add inheritance relationships based on documentation
            inheritance_pairs = [
                # Primary inheritance from oaTerm
                ('oaTerm', 'oaInstTerm'),          # Class inheritance
                ('oaTerm', 'oaBlockTerm'),         # Class inheritance
                ('oaTerm', 'oaITerm'),             # Class inheritance
                ('oaTerm', 'oaScalarTerm'),        # Class inheritance 
                ('oaTerm', 'oaBusTerm'),           # Class inheritance
                ('oaTerm', 'oaBitTerm'),           # Class inheritance
                ('oaTerm', 'oaBundleTerm'),        # Class inheritance
                
                # Secondary inheritance relationships
                ('oaBusTerm', 'oaBusTermBit'),     # BusTermBit inherits from BusTerm
                ('oaScalarTerm', 'oaBitTerm')      # BitTerm is a specialized ScalarTerm
            ]
            
            for parent, child in inheritance_pairs:
                if parent in classes and child in classes:
                    relationships.append({
                        'source': parent,
                        'target': child,
                        'type': 'inheritance',
                        'description': f"{child} inherits from {parent}"
                    })
            
            # Add more detailed aggregation relationships
            # Format: (container, contained, aggregation_type, member_name, description)
            detailed_aggregation_pairs = [
                # BundleTerm contains a collection of Terms as members
                ('oaBundleTerm', 'oaTerm', 'aggregation-many', 'members',
                 'oaBundleTerm contains a collection of oaTerm objects in its members array'),
                
                # BusTermDef and BusTerm relationships
                ('oaBusTermDef', 'oaBusTerm', 'aggregation-single', 'busTerm',
                 'oaBusTermDef contains a reference to a single oaBusTerm as its busTerm member'),
                
                # BusTermDef and BusTermBit relationships
                ('oaBusTermDef', 'oaBusTermBit', 'aggregation-many', 'bits',
                 'oaBusTermDef contains a collection of oaBusTermBit objects in its bits array'),
                
                # BusTermBit to BusTermDef reverse relationship
                ('oaBusTermBit', 'oaBusTermDef', 'aggregation-single', 'def',
                 'oaBusTermBit contains a reference to its parent oaBusTermDef object'),
                
                # BusTerm to BusTermBit relationship
                ('oaBusTerm', 'oaBusTermBit', 'aggregation-many', 'bits',
                 'oaBusTerm contains access to its BusTermBit members through the bits() method'),
                
                # Term and Route relationships
                ('oaNet', 'oaTerm', 'aggregation-many', 'terms',
                 'oaNet contains a collection of oaTerm objects connected to it'),
                
                # Route's connection to Terms at endpoints
                ('oaRoute', 'oaTerm', 'aggregation-single', 'startConn',
                 'oaRoute contains a reference to an oaTerm as its starting connection point'),
                
                ('oaRoute', 'oaTerm', 'aggregation-single', 'endConn',
                 'oaRoute contains a reference to an oaTerm as its ending connection point'),
                
                # Term to Route relationship
                ('oaTerm', 'oaRoute', 'aggregation-many', 'routes',
                 'oaTerm can have multiple routes connected to it'),
                
                # Pin relationships
                ('oaPin', 'oaTerm', 'aggregation-single', 'term',
                 'oaPin contains a reference to the oaTerm it represents'),
                
                ('oaTerm', 'oaPin', 'aggregation-many', 'pins',
                 'oaTerm can have multiple oaPin objects representing it in different contexts'),
                
                # TermConnectDef relationships
                ('oaTermConnectDef', 'oaTerm', 'aggregation-single', 'term',
                 'oaTermConnectDef contains a reference to the oaTerm it connects'),
                
                # Parasitic model relationships
                ('oaTerm', 'oaReducedModel', 'aggregation-single', 'reducedModel',
                 'oaTerm can have a parasitic reduced model attached to it'),
                
                ('oaReducedModel', 'oaElmore', 'aggregation-single', 'elmore',
                 'oaReducedModel can contain an Elmore delay model'),
                
                ('oaReducedModel', 'oaPoleResidue', 'aggregation-single', 'poleResidue',
                 'oaReducedModel can contain a pole-residue model')
            ]
            
            for container, contained, agg_type, member_name, desc in detailed_aggregation_pairs:
                if container in classes and contained in classes:
                    relationships.append({
                        'source': container,
                        'target': contained,
                        'type': agg_type,
                        'member': member_name,
                        'description': desc
                    })
            
            # Add association relationships (references between classes)
            # Format: (source, target, association_type, description)
            detailed_association_pairs = [
                # InstTerm to Inst relationship
                ('oaInstTerm', 'oaInst', 'association-reference', 
                 'oaInstTerm references the oaInst object it belongs to'),
                
                # InstTerm to Net relationship
                ('oaInstTerm', 'oaNet', 'association-reference',
                 'oaInstTerm can be connected to an oaNet'),
                
                # BitTerm to ScalarTerm relationship
                ('oaBitTerm', 'oaScalarTerm', 'association-reference',
                 'oaBitTerm references an oaScalarTerm representing the bit'),
                
                # BlockTerm to Block relationship
                ('oaBlockTerm', 'oaBlock', 'association-reference',
                 'oaBlockTerm references the oaBlock object it belongs to'),
                
                # Term to ParentTerm (for hierarchical terms)
                ('oaTerm', 'oaTerm', 'association-reference',
                 'oaTerm can reference a parent oaTerm in hierarchical structures'),
                
                # Net to Route relationships
                ('oaNet', 'oaRoute', 'association-many',
                 'oaNet contains multiple routes that connect its terms'),
                
                # Pin to Net relationship
                ('oaPin', 'oaNet', 'association-reference',
                 'oaPin can be connected to an oaNet'),
                
                # Term to TermConnectDef relationship
                ('oaTerm', 'oaTermConnectDef', 'association-reference',
                 'oaTerm can reference a TermConnectDef that defines its connections'),
                
                # Net to TermConnectDef relationship
                ('oaNet', 'oaTermConnectDef', 'association-many',
                 'oaNet can be connected to Terms through TermConnectDefs'),
                
                # Observer relationships
                ('oaTermNetObserver', 'oaTerm', 'association-reference',
                 'oaTermNetObserver watches for changes to Term-Net connections'),
                
                ('oaNetTermConnectDefObserver', 'oaNet', 'association-reference',
                 'oaNetTermConnectDefObserver watches for changes to Net-Term connections'),
                
                # Parasitic relationships
                ('oaPin', 'oaReducedModel', 'association-reference',
                 'oaPin can have parasitic models attached for timing analysis'),
                
                ('oaCellTerm', 'oaTerm', 'association-reference',
                 'oaCellTerm is a specialized term used in cell libraries')
            ]
            
            for source, target, assoc_type, desc in detailed_association_pairs:
                if source in classes and target in classes:
                    relationships.append({
                        'source': source,
                        'target': target,
                        'type': assoc_type,
                        'description': desc
                    })
        
        # For block diagram
        elif diagram_type == 'block':
            # Add relationships specific to block diagram
            # These would be based on documentation and diagram analysis
            inheritance_pairs = [
                ('oaDesign', 'oaBlock'),           # Block is a design
                ('oaBlock', 'oaBlockage')          # Inheritance relationship
            ]
            
            for parent, child in inheritance_pairs:
                if parent in classes and child in classes:
                    relationships.append({
                        'source': parent,
                        'target': child,
                        'type': 'inheritance',
                        'description': f"{child} inherits from {parent}"
                    })
            
            # Add composition relationships (stronger than aggregation)
            composition_pairs = [
                ('oaBlock', 'oaInst'),             # Block contains instances
                ('oaBlock', 'oaNet'),              # Block contains nets
                ('oaBlock', 'oaBlockTerm')         # Block contains block terminals
            ]
            
            for container, contained in composition_pairs:
                if container in classes and contained in classes:
                    relationships.append({
                        'source': container,
                        'target': contained,
                        'type': 'composition',
                        'description': f"{container} is composed of {contained}"
                    })
        
        # For other diagrams, specific relationships would be added here
        # based on documentation and manual analysis
        
        return relationships
    
    def generate_accessor_methods(self, classes, relationships):
        """
        Generate predicted accessor methods for classes based on relationship member names.
        
        This follows the OpenAccess API convention where:
        - Member 'fooBar' has getter 'getFooBar()'
        - Member 'fooBar' has setter 'setFooBar()'
        - Collection members may have additional methods like 'addFooBar()', 'removeFooBar()'
        """
        # For each class, gather member names from relationships
        for class_name, class_data in classes.items():
            # Initialize methods list if not present
            if 'methods' not in class_data or not class_data['methods']:
                class_data['methods'] = []
            
            # Find relationships where this class is the source
            source_relationships = [r for r in relationships 
                                   if r.get('source') == class_name and 'member' in r]
            
            for rel in source_relationships:
                member_name = rel.get('member')
                target_class = rel.get('target')
                rel_type = rel.get('type', '')
                
                if not member_name:
                    continue
                
                # Create method name with proper capitalization
                capitalized_member = member_name[0].upper() + member_name[1:]
                
                # Generate method signatures based on relationship type
                if 'many' in rel_type:
                    # Collection methods
                    methods = [
                        {
                            'name': f'get{capitalized_member}',
                            'return_type': f'oaCollection<oa{target_class[2:] if target_class.startswith("oa") else target_class}>',
                            'parameters': [],
                            'description': f'Get the collection of {target_class} objects in the {member_name} member'
                        },
                        {
                            'name': f'getNum{capitalized_member}',
                            'return_type': 'oaUInt4',
                            'parameters': [],
                            'description': f'Get the number of {target_class} objects in the {member_name} collection'
                        },
                        {
                            'name': f'add{capitalized_member[:-1] if member_name.endswith("s") else capitalized_member}',
                            'return_type': 'void',
                            'parameters': [f'{target_class} *{member_name[:-1] if member_name.endswith("s") else member_name}'],
                            'description': f'Add a {target_class} object to the {member_name} collection'
                        }
                    ]
                else:
                    # Single object methods
                    methods = [
                        {
                            'name': f'get{capitalized_member}',
                            'return_type': f'{target_class} *',
                            'parameters': [],
                            'description': f'Get the {target_class} object referenced by the {member_name} member'
                        },
                        {
                            'name': f'set{capitalized_member}',
                            'return_type': 'void',
                            'parameters': [f'{target_class} *{member_name}'],
                            'description': f'Set the {target_class} object for the {member_name} member'
                        }
                    ]
                
                # Add methods to class if they don't exist already
                existing_method_names = [m.get('name') for m in class_data['methods']]
                for method in methods:
                    if method['name'] not in existing_method_names:
                        class_data['methods'].append(method)
                        
        return classes
    
    def create_structure(self, classes, relationships):
        """Create a structured representation of the UML diagram."""
        # Generate accessor methods based on relationships
        enhanced_classes = self.generate_accessor_methods(classes, relationships)
        
        structure = {
            'diagram': self.diagram_name,
            'title': self.diagram_title,
            'classes': enhanced_classes,
            'relationships': relationships
        }
        
        return structure
    
    def save_structure(self, output_path=None):
        """Parse the HTML and save the extracted structure."""
        # Extract image map data
        area_tags = self.extract_image_map()
        
        # Parse areas to get class information
        classes = self.parse_areas(area_tags)
        print(f"Extracted {len(classes)} classes from image map")
        
        # Infer relationships between classes
        relationships = self.infer_relationships(classes)
        print(f"Inferred {len(relationships)} relationships between classes")
        
        # Create structure
        structure = self.create_structure(classes, relationships)
        
        # Determine output path if not provided
        if output_path is None:
            output_path = os.path.join(self.output_dir, f"{self.diagram_name}_imagemap.json")
        
        # Save as JSON
        with open(output_path, 'w') as f:
            json.dump(structure, f, indent=2)
        
        print(f"Structure saved to {output_path}")
        
        # Also save as YAML
        yaml_path = os.path.splitext(output_path)[0] + '.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(structure, f, default_flow_style=False, sort_keys=False)
        
        print(f"YAML saved to {yaml_path}")
        
        # If debug is enabled, save additional information
        if self.debug:
            # Save the formatted HTML for inspection
            debug_html_path = os.path.join(self.debug_dir, f"{self.diagram_name}_imagemap.html")
            with open(debug_html_path, 'w') as f:
                f.write('<html><head>')
                f.write('<style>')
                f.write('''
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #336699; }
                h2 { color: #336699; margin-top: 20px; }
                .class-box { border: 1px solid #ccc; padding: 10px; margin: 5px; border-radius: 5px; }
                .relationship { margin: 10px 0; padding: 5px; border-left: 3px solid #8899aa; }
                .inheritance { border-left-color: #ff6600; }
                .aggregation { border-left-color: #339933; }
                .composition { border-left-color: #cc0000; }
                .association { border-left-color: #0066cc; }
                .usage { border-left-color: #9900cc; }
                .description { font-style: italic; color: #666; margin-left: 20px; }
                .image-container { margin-top: 20px; border: 1px solid #ccc; padding: 10px; }
                ''')
                f.write('</style>')
                f.write('</head><body>\n')
                f.write(f'<h1>{self.diagram_title}</h1>\n')
                
                # Classes section
                f.write(f'<h2>Classes ({len(classes)})</h2>\n')
                f.write('<div style="display: flex; flex-wrap: wrap;">\n')
                for class_name, class_data in classes.items():
                    pos = class_data['position']
                    href = class_data.get("href", "")
                    methods = class_data.get("methods", [])
                    
                    f.write(f'<div class="class-box">\n')
                    if href:
                        f.write(f'<strong><a href="../../{href}" target="_blank">{class_name}</a></strong><br>\n')
                    else:
                        f.write(f'<strong>{class_name}</strong><br>\n')
                    f.write(f'Position: x:{pos["x"]}, y:{pos["y"]}, width:{pos["width"]}, height:{pos["height"]}<br>\n')
                    
                    # Show methods if any
                    if methods:
                        f.write(f'<details><summary><b>Methods ({len(methods)})</b></summary>\n')
                        f.write('<ul style="font-size: 0.9em; max-height: 150px; overflow-y: auto;">\n')
                        for method in methods:
                            name = method.get('name', '')
                            return_type = method.get('return_type', 'void')
                            params = ', '.join(method.get('parameters', []))
                            f.write(f'<li><code>{return_type} {name}({params})</code></li>\n')
                        f.write('</ul>\n')
                        f.write('</details>\n')
                    
                    f.write('</div>\n')
                f.write('</div>\n')
                
                # Relationships section with color coding
                f.write(f'<h2>Relationships ({len(relationships)})</h2>\n')
                
                # Group relationships by type for better organization
                rel_by_type = {}
                for rel in relationships:
                    rel_type = rel.get("type", "unknown")
                    if rel_type not in rel_by_type:
                        rel_by_type[rel_type] = []
                    rel_by_type[rel_type].append(rel)
                
                # Show each relationship type in a separate section
                for rel_type, rels in rel_by_type.items():
                    f.write(f'<h3>{rel_type.capitalize()} Relationships ({len(rels)})</h3>\n')
                    for rel in rels:
                        source = rel.get("source", "")
                        target = rel.get("target", "")
                        description = rel.get("description", "")
                        
                        f.write(f'<div class="relationship {rel_type}">\n')
                        f.write(f'<strong>{source}</strong> --({rel_type})--> <strong>{target}</strong>\n')
                        if description:
                            f.write(f'<div class="description">{description}</div>\n')
                        f.write('</div>\n')
                
                # Original diagram image
                f.write('<h2>Original Diagram</h2>\n')
                f.write('<div class="image-container">\n')
                f.write(f'<img src="../../{self.png_path}" border="0">\n')
                f.write('</div>\n')
                
                f.write('</body></html>\n')
            
            print(f"Debug HTML saved to {debug_html_path}")
        
        return structure

def main():
    """Main function to parse HTML image maps."""
    parser = argparse.ArgumentParser(
        description='Extract UML class information from HTML image maps'
    )
    parser.add_argument(
        'html_path',
        help='Path to the HTML file containing the image map'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: yaml_output/schema/<diagram>_imagemap.json)'
    )
    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable generation of debug information'
    )
    
    args = parser.parse_args()
    
    try:
        # Parse the HTML image map
        imagemap_parser = HTMLImageMapParser(args.html_path, debug=not args.no_debug)
        structure = imagemap_parser.save_structure(args.output)
        
        # Print a summary
        print(f"\nImagemap parsing complete:")
        print(f"- Diagram: {structure['diagram']} ({structure['title']})")
        print(f"- {len(structure['classes'])} classes")
        print(f"- {len(structure['relationships'])} relationships")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()