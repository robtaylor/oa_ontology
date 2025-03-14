#!/usr/bin/env python3
"""
Fix the enhanced domain ontology JSON structure for visualization.

This script restructures the enhanced domain ontology JSON to make it compatible
with visualization tools like pyvis.
"""

import json
import os
import networkx as nx
import re

def fix_json_structure(input_file, output_file):
    """Fix the JSON structure to make it compatible with visualization tools."""
    print(f"Loading ontology from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create a networkx graph to help restructure the data
    G = nx.DiGraph()
    
    # Add all nodes first
    print(f"Processing {len(data.get('nodes', []))} nodes...")
    for node in data.get('nodes', []):
        node_id = node.get('id')
        if node_id:
            G.add_node(node_id, **node)
    
    # Extract relationship patterns from the links
    relationship_patterns = {}
    source_counts = {}
    
    print("Analyzing relationships...")
    for link in data.get('links', []):
        source_type = link.get('source')  # This is 'api_inferred' or 'uml'
        if source_type not in source_counts:
            source_counts[source_type] = 0
        source_counts[source_type] += 1
        
        # Look for patterns that could indicate the actual source node
        target = link.get('target')
        rel_type = link.get('type')
        member = link.get('member', '')
        description = link.get('description', '')
        
        # Store pattern information for analysis
        pattern_key = f"{rel_type}|{member}"
        if pattern_key not in relationship_patterns:
            relationship_patterns[pattern_key] = []
        relationship_patterns[pattern_key].append(description)
    
    print(f"Source types in links: {source_counts}")
    
    # Now extract source nodes from descriptions for a subset of relationships
    print("Extracting source nodes from descriptions...")
    fixed_links = []
    
    for link in data.get('links', []):
        source_type = link.get('source')  # This is 'api_inferred' or 'uml'
        target = link.get('target')
        rel_type = link.get('type')
        member = link.get('member', '')
        description = link.get('description', '')
        
        # For specializes relationships, try to extract source from description
        if rel_type == "SPECIALIZES" and " inherits from " in description:
            match = re.match(r"(oa\w+) inherits from", description)
            if match:
                source_node = match.group(1)
                if source_node in G:
                    # Create fixed link with correct source/target
                    fixed_link = {
                        "source_node": source_node,
                        "target_node": target,
                        "type": rel_type,
                        "data_source": source_type,
                        "description": description,
                        "member": member
                    }
                    fixed_links.append(fixed_link)
        # For inferred relationships, try to extract source from method name
        elif source_type == "api_inferred" and "Inferred from method " in description:
            # The source class likely defines the method that returns the target
            # We need to find which class defines the method mentioned in the description
            method_match = re.search(r"method (\w+)", description)
            if method_match:
                method_name = method_match.group(1)
                
                # Check all nodes to see which ones have this method
                possible_sources = []
                for node_id, attrs in G.nodes(data=True):
                    methods = attrs.get("methods", [])
                    for method in methods:
                        if method.get("name") == method_name:
                            possible_sources.append(node_id)
                            break
                
                if len(possible_sources) == 1:
                    source_node = possible_sources[0]
                    fixed_link = {
                        "source_node": source_node,
                        "target_node": target,
                        "type": rel_type,
                        "data_source": source_type,
                        "description": description,
                        "member": member
                    }
                    fixed_links.append(fixed_link)
                    
    print(f"Successfully extracted source nodes for {len(fixed_links)} relationships")
    
    # Create the fixed data structure
    fixed_data = {
        "nodes": data.get("nodes", []),
        "links": []
    }
    
    # Convert fixed links to proper format
    for link in fixed_links:
        fixed_data["links"].append({
            "source": link["source_node"],
            "target": link["target_node"],
            "type": link["type"],
            "data_source": link["data_source"],
            "description": link["description"],
            "member": link["member"]
        })
    
    # Save fixed data
    print(f"Saving fixed ontology with {len(fixed_data['links'])} relationships to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, indent=2)
    
    print("Done!")

if __name__ == "__main__":
    input_file = "outputs/enhanced_domain_ontology.json"
    output_file = "outputs/enhanced_domain_ontology_fixed.json"
    fix_json_structure(input_file, output_file)