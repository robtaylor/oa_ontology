#!/usr/bin/env python3
"""
Visualize the domain ontology focusing on the most connected classes without inheritance.

This script creates an interactive visualization that:
1. Removes all inheritance relationships (SPECIALIZES)
2. Focuses on the most connected classes
3. Provides an interactive HTML visualization
"""

import os
import json
import argparse
import networkx as nx
import random
from oa_ontology.visualization_utils import apply_patches, create_network

# Define color palettes for domains and relationship types
DOMAIN_COLORS = {
    "Physical": "#ff7f0e",  # orange
    "Connectivity": "#1f77b4",  # blue
    "Hierarchy": "#2ca02c",  # green
    "Layout": "#d62728",  # red
    "Device": "#9467bd",  # purple
    "Other": "#8c564b",  # brown
    "Unknown": "#7f7f7f"  # gray
}

RELATIONSHIP_COLORS = {
    "CONTAINS_MANY": "#ff7f0e",  # orange
    "CONTAINS_ONE": "#2ca02c",  # green
    "REFERENCES": "#d62728",  # red
    "ASSOCIATED_WITH_MANY": "#9467bd",  # purple
    "ASSOCIATED_WITH": "#8c564b",  # brown
    "COMPOSED_OF": "#e377c2",  # pink
    "USES": "#7f7f7f",  # gray
    "RELATED_TO": "#bcbd22"  # yellow
}

def load_ontology_as_networkx(input_file):
    """Load the ontology and convert to a NetworkX graph."""
    G = nx.DiGraph()
    
    # Determine file type based on extension
    if input_file.endswith('.json'):
        # Load from JSON
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add nodes
        for node in data.get("nodes", []):
            node_id = node.get("id")
            if node_id:
                G.add_node(node_id, **node)
        
        # Add edges (excluding inheritance)
        edge_count = 0
        for link in data.get("links", []):
            if "source" in link and "target" in link:
                # Skip inheritance relationships
                if link.get("type") == "SPECIALIZES":
                    continue
                    
                source_node = link.get("source")
                target_node = link.get("target")
                
                # For enhanced domain ontology, links may have "api_inferred" as source
                # In this case, we'll create the edge in reverse (target to source_attr)
                if source_node == "api_inferred" and target_node in G:
                    # We'll add edges from the class referenced in target to any class it references
                    # This allows us to still visualize the connections
                    edge_attrs = {k: v for k, v in link.items() if k not in ['source', 'target']}
                    member = link.get("member", "")
                    
                    # Look for any class with this name pattern in the ontology
                    # This helps us connect api_inferred relationships to actual classes
                    if member and member.startswith("oa"):
                        member_class = member
                    elif member:
                        # Try to find a class with a matching name
                        member_class = "oa" + member[0].upper() + member[1:]
                        if member_class not in G.nodes():
                            # Try variations
                            member_class = member
                    else:
                        # If no member specified, skip
                        continue
                    
                    # Only add if the target class exists
                    if member_class in G.nodes():
                        # Create edge from class to its referenced class
                        G.add_edge(target_node, member_class, **edge_attrs)
                        edge_count += 1
                
                # Normal case - both source and target are class names
                elif (isinstance(source_node, str) and isinstance(target_node, str) and 
                      source_node in G and target_node in G):
                    # Create the edge with all attributes
                    edge_attrs = {k: v for k, v in link.items() 
                                if k not in ['source', 'target']}
                    G.add_edge(source_node, target_node, **edge_attrs)
                    edge_count += 1
    
    elif input_file.endswith('.graphml'):
        # Load from GraphML
        try:
            G = nx.read_graphml(input_file)
            print(f"Loaded GraphML file with {len(G.nodes)} nodes and {len(G.edges)} edges")
            
            # Remove inheritance edges
            inheritance_edges = [(u, v) for u, v, attrs in G.edges(data=True) 
                               if attrs.get('type') == 'SPECIALIZES']
            G.remove_edges_from(inheritance_edges)
            print(f"Removed {len(inheritance_edges)} inheritance edges")
            
            # GraphML might have some attributes as strings that need to be processed
            for node, attrs in G.nodes(data=True):
                # Add a 'label' attribute if not present
                if 'label' not in attrs:
                    label = str(node)
                    if label.startswith('oa'):
                        label = label[2:]  # Remove 'oa' prefix
                    G.nodes[node]['label'] = label
                
                # Make sure domain is set
                if 'domain' not in attrs:
                    G.nodes[node]['domain'] = 'Unknown'
            
            return G
            
        except Exception as e:
            print(f"Error loading GraphML: {e}")
            print("Falling back to an empty graph")
            G = nx.DiGraph()
    
    else:
        print(f"Unsupported file format: {input_file}")
        print("Please provide a .json or .graphml file")
    
    print(f"Loaded graph with {len(G.nodes)} nodes and {len(G.edges)} edges")
    return G

def visualize_ontology(input_file, output_file, max_nodes=100, filter_domain=None):
    """Create an interactive network visualization of the domain ontology."""
    # Apply patches to the visualization libraries to use the correct lib path
    lib_dir = apply_patches()
    
    # Load the graph
    G = load_ontology_as_networkx(input_file)
    
    # Filter by domain if requested
    if filter_domain:
        nodes_to_remove = []
        for node, attrs in G.nodes(data=True):
            if attrs.get("domain") != filter_domain:
                nodes_to_remove.append(node)
        G.remove_nodes_from(nodes_to_remove)
        print(f"Filtered to {len(G.nodes)} nodes in the {filter_domain} domain")
    
    # Get the most connected nodes
    node_connections = {}
    for node in G.nodes():
        # Count both incoming and outgoing edges
        connections = G.in_degree(node) + G.out_degree(node)
        node_connections[node] = connections
    
    # Sort nodes by connection count
    most_connected = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)
    
    # Limit to the top N most connected nodes
    top_nodes = [node for node, _ in most_connected[:max_nodes]]
    
    # Create a subgraph with only the most connected nodes
    G = G.subgraph(top_nodes)
    print(f"Limited to {len(G.nodes)} most connected nodes")
    
    # Setup the lib directory in outputs
    apply_patches()
    
    # Create the pyvis network with proper configuration
    net = create_network(height="800px", width="100%", directed=True)
    
    # Add physics options for a better layout
    physics_options = {
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
            "gravitationalConstant": -100,
            "centralGravity": 0.01,
            "springLength": 150,
            "springConstant": 0.08
        },
        "maxVelocity": 50,
        "minVelocity": 0.1,
        "timestep": 0.5,
        "stabilization": {
            "enabled": True,
            "iterations": 1000
        }
    }
    net.barnes_hut(overlap=0.5)
    net.show_buttons(filter_=['physics'])
    
    # Add nodes to the network
    for node_id, attrs in G.nodes(data=True):
        domain = attrs.get("domain", "Unknown")
        
        # Always use the class name (node_id) as the label
        # Clean the label for display
        if node_id.startswith("oa"):
            label = node_id[2:]  # Remove "oa" prefix for cleaner display
        else:
            label = node_id
            
        # Get other attributes for tooltip
        concept = attrs.get("concept", "")
        description = attrs.get("description", "")
        
        # Create a tooltip with useful information
        title = f"<b>{node_id}</b><br>Domain: {domain}<br>Concept: {concept}<br>{description}"
        
        # Set color based on domain
        color = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["Unknown"])
        
        # Calculate node size based on connectivity (between 10 and 40)
        connections = node_connections.get(node_id, 0)
        size = 10 + min(30, connections / 2)
        
        # Add node to network
        net.add_node(
            node_id, 
            label=label, 
            title=title, 
            color=color, 
            size=size,
            shape="dot"
        )
    
    # Add edges to the network
    for source, target, attrs in G.edges(data=True):
        # Get relationship type
        rel_type = attrs.get("type", "RELATED_TO")
        data_source = attrs.get("source", "unknown")
        
        # Set color based on relationship type
        color = RELATIONSHIP_COLORS.get(rel_type, "#7f7f7f")
        
        # Create a tooltip with edge information
        title = f"Type: {rel_type}<br>Source: {data_source}"
        if "member" in attrs:
            title += f"<br>Member: {attrs['member']}"
        if "description" in attrs:
            title += f"<br>{attrs['description']}"
            
        # Define arrow width based on relationship type
        width = 1
        if rel_type in ["CONTAINS_MANY", "CONTAINS_ONE"]:
            width = 2
            
        # Add edge to network with arrow types
        net.add_edge(
            source, 
            target, 
            title=title, 
            color=color,
            width=width,
            arrows="to",
            label=rel_type if rel_type in ["CONTAINS_MANY", "COMPOSED_OF"] else ""
        )
    
    # Generate HTML file
    net.save_graph(output_file)
    print(f"Visualization saved to {output_file}")
    print(f"Included {len(G.nodes)} nodes and {len(G.edges)} edges")

def main():
    """Main function for visualizing the ontology."""
    parser = argparse.ArgumentParser(
        description="Create a visualization of domain ontology excluding inheritance and focusing on most connected classes."
    )
    parser.add_argument(
        "--input", "-i",
        default="outputs/visualization_graph.json",
        help="Path to the domain ontology JSON file"
    )
    parser.add_argument(
        "--output", "-o",
        default="outputs/connected_classes_visualization.html",
        help="Output HTML file path"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=75,
        help="Limit the visualization to the top N most connected nodes"
    )
    parser.add_argument(
        "--domain", "-d",
        choices=["Physical", "Connectivity", "Hierarchy", "Layout", "Device", "Other"],
        help="Filter nodes by domain"
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Create visualization
    visualize_ontology(args.input, args.output, args.limit, args.domain)
    
    print(f"Visualization completed. Open {args.output} in a web browser to view.")

if __name__ == "__main__":
    main()