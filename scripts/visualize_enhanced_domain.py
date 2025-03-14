#!/usr/bin/env python3
"""
Visualize the enhanced domain ontology using pyvis.

This script creates an interactive visualization of the enhanced domain ontology
that can be viewed in a web browser.
"""

import os
import json
import argparse
import networkx as nx
from pyvis.network import Network
import random

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
    "SPECIALIZES": "#1f77b4",  # blue
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
        
        # Add edges
        edge_count = 0
        for link in data.get("links", []):
            if "source" in link and "target" in link:
                source_node = link.get("source")
                target_node = link.get("target")
                
                # Check if these look like node IDs (should be strings that exist in our nodes)
                if (isinstance(source_node, str) and isinstance(target_node, str) and 
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
            
            # Ensure edge attributes are properly set
            for u, v, attrs in G.edges(data=True):
                if 'type' not in attrs:
                    G.edges[u, v]['type'] = 'RELATED_TO'
            
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

def visualize_ontology(input_file, output_file, limit_nodes=None, filter_domain=None):
    """Create an interactive network visualization of the domain ontology."""
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
    
    # Limit the number of nodes if specified
    if limit_nodes and len(G.nodes) > limit_nodes:
        # Get the most connected nodes
        most_connected = sorted(G.degree(), key=lambda x: x[1], reverse=True)[:limit_nodes]
        most_connected_nodes = [node for node, _ in most_connected]
        
        # Create a subgraph with only those nodes
        G = G.subgraph(most_connected_nodes)
        print(f"Limited to {len(G.nodes)} most connected nodes")
    
    # Create the pyvis network
    net = Network(height="800px", width="100%", directed=True, notebook=False)
    
    # Configure network settings for better visualization
    net.toggle_hide_edges_on_drag(True)
    net.set_edge_smooth('dynamic')
    
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
        label = attrs.get("label", node_id)
        
        # Clean the label if needed
        if label == node_id and node_id.startswith("oa"):
            label = node_id[2:]  # Remove "oa" prefix for cleaner display
        
        # Get other attributes for tooltip
        concept = attrs.get("concept", "")
        description = attrs.get("description", "")
        
        # Create a tooltip with useful information
        title = f"<b>{node_id}</b><br>Domain: {domain}<br>Concept: {concept}<br>{description}"
        
        # Set color based on domain
        color = DOMAIN_COLORS.get(domain, DOMAIN_COLORS["Unknown"])
        
        # Add node to network
        net.add_node(
            node_id, 
            label=label, 
            title=title, 
            color=color, 
            size=15,
            shape="dot"
        )
    
    # Add edges to the network
    for source, target, attrs in G.edges(data=True):
        # Get relationship type
        rel_type = attrs.get("type", "RELATED_TO")
        data_source = attrs.get("source", "unknown")  # This is where the relationship data came from
        
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
        if rel_type == "SPECIALIZES":
            width = 3
            
        # Add edge to network with arrow types
        net.add_edge(
            source, 
            target, 
            title=title, 
            color=color,
            width=width,
            arrows="to",
            # Only show labels for the most important relationship types to avoid clutter
            label=rel_type if rel_type in ["SPECIALIZES", "CONTAINS_MANY", "COMPOSED_OF"] else ""
        )
    
    # Generate HTML file
    net.save_graph(output_file)
    print(f"Visualization saved to {output_file}")
    print(f"Included {len(G.nodes)} nodes and {len(G.edges)} edges")

def main():
    """Main function for visualizing the ontology."""
    parser = argparse.ArgumentParser(
        description="Create an interactive visualization of the enhanced domain ontology."
    )
    parser.add_argument(
        "--input",
        default="outputs/enhanced_domain_ontology.json",
        help="Path to the enhanced domain ontology JSON file"
    )
    parser.add_argument(
        "--output",
        default="outputs/enhanced_domain_visualization.html",
        help="Output HTML file path"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the visualization to the top N most connected nodes"
    )
    parser.add_argument(
        "--domain",
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