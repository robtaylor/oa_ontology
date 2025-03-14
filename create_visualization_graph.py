#!/usr/bin/env python3
"""
Create a simplified graph for visualization from the enhanced domain ontology.
"""

import json
import os
import networkx as nx
import re
from collections import defaultdict

def extract_source_class(json_file, output_file):
    """Extract a simplified graph for visualization."""
    print(f"Loading ontology from {json_file}...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create a networkx graph for the visualization data
    G = nx.DiGraph()
    
    # Add all nodes first
    print(f"Processing {len(data.get('nodes', []))} nodes...")
    for node in data.get('nodes', []):
        node_id = node.get('id')
        if node_id:
            G.add_node(node_id, **node)
    
    # Create manually defined relationships based on class names and patterns
    print("Creating relationships based on naming patterns...")
    
    # Pattern 1: Class inheritance relationships (if a class name contains another)
    class_names = list(G.nodes())
    inheritance_count = 0
    
    # For each class, check if it's a subclass of another class based on naming patterns
    for class_name in class_names:
        if class_name.startswith('oa'):
            # Find potential parent classes
            base_name = class_name[2:]  # Remove 'oa' prefix
            for potential_parent in class_names:
                if potential_parent.startswith('oa') and potential_parent != class_name:
                    parent_base = potential_parent[2:]
                    # Check if the parent name is contained in the child name but not equal
                    if parent_base in base_name and parent_base != base_name:
                        # Check if it's a clean inheritance match (parent is a suffix)
                        if base_name.endswith(parent_base) or re.match(f".*{parent_base}[A-Z].*", base_name):
                            G.add_edge(class_name, potential_parent, type='SPECIALIZES', source='pattern')
                            inheritance_count += 1
    
    print(f"Created {inheritance_count} inheritance relationships")
    
    # Pattern 2: Container relationships based on domain concepts
    container_count = 0
    for class_name in class_names:
        attrs = G.nodes[class_name]
        domain = attrs.get('domain', 'Unknown')
        concept = attrs.get('concept', 'Unknown')
        
        # Common container patterns in OpenAccess
        if 'Block' in class_name:
            # Blocks typically contain other elements
            for other_class in class_names:
                if other_class != class_name and ('Shape' in other_class or 'Fig' in other_class or 
                                                'Via' in other_class or 'Pin' in other_class):
                    G.add_edge(class_name, other_class, type='CONTAINS_MANY', source='pattern')
                    container_count += 1
                    
        elif 'Design' in class_name:
            # Designs contain blocks and modules
            for other_class in class_names:
                if other_class != class_name and ('Block' in other_class or 'Module' in other_class):
                    G.add_edge(class_name, other_class, type='CONTAINS_MANY', source='pattern')
                    container_count += 1
                    
        elif 'Net' in class_name:
            # Nets connect to Terms, Pins, etc.
            for other_class in class_names:
                if other_class != class_name and ('Term' in other_class or 'Pin' in other_class):
                    G.add_edge(class_name, other_class, type='CONNECTS', source='pattern')
                    container_count += 1
    
    print(f"Created {container_count} container relationships")
    
    # Pattern 3: Associate classes in same domain with similar concepts
    domain_groups = defaultdict(list)
    for class_name in class_names:
        attrs = G.nodes[class_name]
        domain = attrs.get('domain', 'Unknown')
        domain_groups[domain].append(class_name)
    
    association_count = 0
    for domain, classes in domain_groups.items():
        if domain != 'Unknown' and len(classes) > 1:
            # Associate classes in the same domain using a random sample
            sample_size = min(len(classes), 100)  # Limit connections to avoid too many edges
            for i in range(sample_size):
                source = classes[i]
                # Create about 3 associations per class
                for j in range(3):
                    k = (i + j + 1) % len(classes)
                    target = classes[k]
                    if not G.has_edge(source, target) and not G.has_edge(target, source):
                        G.add_edge(source, target, type='ASSOCIATED_WITH', source='pattern')
                        association_count += 1
    
    print(f"Created {association_count} association relationships")
    
    # Convert to visualization-friendly JSON
    vis_data = {
        "nodes": [],
        "links": []
    }
    
    # Add nodes
    for node_id, attrs in G.nodes(data=True):
        node_data = {
            "id": node_id,
            "label": attrs.get("label", node_id),
            "type": attrs.get("type", "Class"),
            "domain": attrs.get("domain", "Unknown"),
            "concept": attrs.get("concept", "Unknown"),
            "description": attrs.get("description", "")
        }
        vis_data["nodes"].append(node_data)
    
    # Add edges
    for source, target, attrs in G.edges(data=True):
        link_data = {
            "source": source,
            "target": target,
            "type": attrs.get("type", "RELATED_TO"),
            "data_source": attrs.get("source", "pattern")
        }
        vis_data["links"].append(link_data)
    
    # Save the visualization data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(vis_data, f, indent=2)
    
    print(f"Created visualization graph with {len(vis_data['nodes'])} nodes and {len(vis_data['links'])} edges")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    input_file = "outputs/enhanced_domain_ontology.json"
    output_file = "outputs/visualization_graph.json"
    extract_source_class(input_file, output_file)