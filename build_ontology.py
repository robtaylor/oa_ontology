#!/usr/bin/env python3
"""
Build a graph ontology from OpenAccess YAML documentation files.
This script creates a graph representation of the Cadence OpenAccess class hierarchy,
focusing on the relationships between classes in the design module.
"""

import os
import yaml
import re
import networkx as nx
from pathlib import Path
import json
from tqdm import tqdm

# Avoid importing matplotlib for now as we don't directly need it here

# Constants
YAML_DIR = Path("output_test/design")
OUTPUT_DIR = Path("ontology_output")

def extract_relationships_from_method(method, class_name):
    """Extract relationships from a single method definition."""
    relationships = []
    method_name = method.get('name', '')
    return_type = method.get('return_type', '')
    signature = method.get('signature', '')
    
    # Collection getters suggest containment relationships
    if method_name.startswith('get') and 'Collection' in return_type:
        # Extract target class from collection
        target_match = re.search(r'Collection<?[\s]*(\w+)', return_type)
        if target_match:
            target_class = target_match.group(1)
            if target_class != class_name and not target_class.startswith('oa') and len(target_class) > 1:
                # If not fully qualified, assume it's an oa class
                target_class = f"oa{target_class}"
            relationships.append(('CONTAINS', target_class, {'via_method': method_name}))
    
    # Direct object returns suggest references
    elif method_name.startswith('get') and return_type and 'oa' in return_type and not 'Collection' in return_type:
        # Clean up the return type
        target_class = return_type.replace('*', '').strip()
        # Check if it's a pointer or reference
        if '*' in signature or '&' in signature:
            relationships.append(('REFERENCES', target_class, {'via_method': method_name}))
    
    # Create methods suggest creation relationships
    elif method_name == 'create' and return_type:
        relationships.append(('CREATES', return_type, {'via_method': method_name}))
    
    # Parameters suggest dependencies
    param_matches = re.findall(r'const\s+(\w+)\s*[&*]', signature)
    for param in param_matches:
        if param.startswith('oa') and param != class_name and param != 'oaString':
            relationships.append(('DEPENDS_ON', param, {'via_param': True}))
    
    return relationships

def extract_relationships(methods, class_name):
    """Extract all relationships from class methods."""
    relationships = []
    
    if not methods:
        return relationships
        
    for method in methods:
        method_relationships = extract_relationships_from_method(method, class_name)
        relationships.extend(method_relationships)
    
    return relationships

def clean_description(description):
    """Clean and truncate the description for better readability."""
    if not description:
        return ""
    
    # Remove excessive whitespace and truncate if too long
    desc = re.sub(r'\s+', ' ', description).strip()
    if len(desc) > 300:
        desc = desc[:297] + "..."
    
    return desc

def build_ontology(yaml_dir):
    """Build a graph ontology from YAML files."""
    G = nx.DiGraph()
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Get all class files (excluding -members files)
    yaml_files = [f for f in os.listdir(yaml_dir) 
                 if f.endswith('.yaml') and not f.endswith('-members.yaml') 
                 and not f == 'classes.yaml']
    
    print(f"Processing {len(yaml_files)} class files...")
    
    # Process all YAML files
    for filename in tqdm(yaml_files):
        try:
            with open(os.path.join(yaml_dir, filename), 'r') as f:
                data = yaml.safe_load(f)
            
            if 'name' not in data:
                continue
                
            class_name = data['name']
            
            # Add class node
            G.add_node(class_name, 
                      type='Class',
                      description=clean_description(data.get('description', '')),
                      methods_count=len(data.get('methods', [])),
                      enums_count=len(data.get('enumerations', {})),
                      filename=filename)
            
            # Add inheritance relationships
            for parent in data.get('inheritance', []):
                G.add_edge(class_name, parent, type='INHERITS_FROM')
            
            # Add other relationships based on methods
            if 'methods' in data:
                for rel_type, target, attrs in extract_relationships(data['methods'], class_name):
                    if target in G or any(f"class{target}" in f for f in yaml_files):
                        # Only add relationships to classes that exist or will exist
                        G.add_edge(class_name, target, type=rel_type, **attrs)
        
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    
    return G

def export_to_json(G, output_path):
    """Export the graph to a JSON file that can be imported into visualization tools."""
    data = {
        "nodes": [],
        "links": []
    }
    
    # Add nodes
    for node, attrs in G.nodes(data=True):
        node_data = {
            "id": node,
            "label": node,
            **attrs
        }
        data["nodes"].append(node_data)
    
    # Add edges
    for source, target, attrs in G.edges(data=True):
        edge_data = {
            "source": source,
            "target": target,
            **attrs
        }
        data["links"].append(edge_data)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Graph exported to {output_path}")

def generate_graph_metrics(G):
    """Generate metrics about the graph structure."""
    metrics = {
        "total_classes": G.number_of_nodes(),
        "total_relationships": G.number_of_edges(),
        "inheritance_relationships": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'INHERITS_FROM'),
        "containment_relationships": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'CONTAINS'),
        "reference_relationships": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'REFERENCES'),
        "dependency_relationships": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'DEPENDS_ON'),
        "most_connected_classes": sorted([(node, G.degree(node)) for node in G.nodes()], 
                                        key=lambda x: x[1], reverse=True)[:10],
        "classes_by_inheritance_depth": {},
    }
    
    # Compute inheritance depth for each class
    roots = [node for node in G.nodes() if G.out_degree(node) == 0]
    for root in roots:
        for node in G.nodes():
            if node != root:
                try:
                    path_length = len(nx.shortest_path(G, node, root)) - 1
                    if path_length > 0:
                        if path_length not in metrics["classes_by_inheritance_depth"]:
                            metrics["classes_by_inheritance_depth"][path_length] = []
                        metrics["classes_by_inheritance_depth"][path_length].append(node)
                except nx.NetworkXNoPath:
                    pass
    
    return metrics

def save_metrics(metrics, output_path):
    """Save graph metrics to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Metrics saved to {output_path}")

def main():
    """Main function to build and export the ontology."""
    print("Building OpenAccess design ontology...")
    
    # Build the graph
    G = build_ontology(YAML_DIR)
    
    print(f"Created graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Export to JSON for visualization
    export_to_json(G, os.path.join(OUTPUT_DIR, "design_ontology.json"))
    
    # Generate and save metrics
    metrics = generate_graph_metrics(G)
    save_metrics(metrics, os.path.join(OUTPUT_DIR, "ontology_metrics.json"))
    
    print("Done! The ontology has been built and exported.")

if __name__ == "__main__":
    main()