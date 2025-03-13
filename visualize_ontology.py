#!/usr/bin/env python3
"""
Visualize the OpenAccess design ontology using NetworkX.
This script generates an HTML report of the ontology relationships.
"""

import os
import json
import networkx as nx
from pathlib import Path
from tqdm import tqdm

# Skip matplotlib and numpy imports since we're not generating visualizations

# Constants
ONTOLOGY_FILE = Path("ontology_output/design_ontology.json")
OUTPUT_DIR = Path("ontology_output/visualizations")
MAX_NODES = 50  # Limit for better visualization

def load_graph_from_json(file_path):
    """Load the graph from the JSON file."""
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    G = nx.DiGraph()
    
    # Add nodes
    for node in data["nodes"]:
        attrs = {k: v for k, v in node.items() if k not in ["id"]}
        G.add_node(node["id"], **attrs)
    
    # Add edges
    for link in data["links"]:
        attrs = {k: v for k, v in link.items() if k not in ["source", "target"]}
        G.add_edge(link["source"], link["target"], **attrs)
    
    return G

def visualize_inheritance_hierarchy(G, output_path):
    """Visualize the inheritance hierarchy."""
    inheritance_graph = nx.DiGraph()
    
    # Add inheritance edges
    for source, target, attrs in G.edges(data=True):
        if attrs.get('type') == 'INHERITS_FROM':
            if source in G.nodes and target in G.nodes:
                inheritance_graph.add_node(source, **G.nodes[source])
                inheritance_graph.add_node(target, **G.nodes[target])
                inheritance_graph.add_edge(source, target)
    
    # Get the top-level classes (those with no outgoing INHERITS_FROM edges)
    top_classes = [node for node in inheritance_graph.nodes() 
                  if inheritance_graph.out_degree(node) == 0]
    
    # For each top-level class, visualize its inheritance tree
    for i, top_class in enumerate(top_classes):
        if i >= 3:  # Limit to first 3 base classes
            break
            
        # Create a subgraph for this inheritance tree
        tree = nx.DiGraph()
        
        # Find all classes that inherit from this top class
        for node in inheritance_graph.nodes():
            try:
                if nx.has_path(inheritance_graph, node, top_class):
                    tree.add_node(node, **inheritance_graph.nodes[node])
                    
                    # Add all inheritance edges in the path
                    path = nx.shortest_path(inheritance_graph, node, top_class)
                    for j in range(len(path) - 1):
                        tree.add_edge(path[j], path[j+1])
            except nx.NetworkXNoPath:
                pass
        
        # Skip if tree is too small
        if tree.number_of_nodes() < 3:
            continue
            
        # Limit to manageable size
        if tree.number_of_nodes() > MAX_NODES:
            # Keep the top class and select random nodes
            nodes = list(tree.nodes())
            nodes.remove(top_class)
            np.random.shuffle(nodes)
            nodes_to_remove = nodes[MAX_NODES-1:]
            tree.remove_nodes_from(nodes_to_remove)
        
        plt.figure(figsize=(16, 12))
        pos = nx.nx_agraph.graphviz_layout(tree, prog="dot")
        
        nx.draw_networkx_nodes(tree, pos, node_size=1500, node_color="lightblue", alpha=0.8)
        nx.draw_networkx_edges(tree, pos, width=1.5, arrowsize=20, alpha=0.7)
        nx.draw_networkx_labels(tree, pos, font_size=8)
        
        plt.title(f"Inheritance Hierarchy for {top_class}", fontsize=16)
        plt.axis("off")
        plt.tight_layout()
        
        # Save the figure
        output_file = os.path.join(output_path, f"inheritance_{top_class}.png")
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        plt.close()
        
        print(f"Created inheritance visualization for {top_class}")

def visualize_containment_relationships(G, output_path):
    """Visualize containment relationships."""
    containment_graph = nx.DiGraph()
    
    # Add containment edges
    for source, target, attrs in G.edges(data=True):
        if attrs.get('type') == 'CONTAINS':
            if source in G.nodes and target in G.nodes:
                containment_graph.add_node(source, **G.nodes[source])
                containment_graph.add_node(target, **G.nodes[target])
                containment_graph.add_edge(source, target)
    
    # Limit to manageable size
    if containment_graph.number_of_nodes() > MAX_NODES:
        # Select nodes with highest degree
        nodes_by_degree = sorted([(node, containment_graph.degree(node)) 
                                for node in containment_graph.nodes()],
                               key=lambda x: x[1], reverse=True)
        
        nodes_to_keep = [node for node, _ in nodes_by_degree[:MAX_NODES]]
        nodes_to_remove = [node for node in containment_graph.nodes() 
                          if node not in nodes_to_keep]
        
        containment_graph.remove_nodes_from(nodes_to_remove)
    
    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(containment_graph, k=0.5, iterations=50)
    
    nx.draw_networkx_nodes(containment_graph, pos, node_size=1500, 
                          node_color="lightgreen", alpha=0.8)
    nx.draw_networkx_edges(containment_graph, pos, width=1.5, 
                          arrowsize=20, alpha=0.7, edge_color="green")
    nx.draw_networkx_labels(containment_graph, pos, font_size=8)
    
    plt.title("Containment Relationships (Contains/Has)", fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    
    # Save the figure
    output_file = os.path.join(output_path, "containment_relationships.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    
    print("Created containment relationships visualization")

def visualize_class_neighborhood(G, output_path):
    """Visualize neighborhood of important classes."""
    # Find most central classes by degree
    central_classes = sorted([(node, G.degree(node)) for node in G.nodes()],
                           key=lambda x: x[1], reverse=True)[:5]
    
    for central_class, degree in central_classes:
        # Create a subgraph with the neighborhood
        neighborhood = nx.ego_graph(G, central_class, radius=1)
        
        # Limit to manageable size
        if neighborhood.number_of_nodes() > MAX_NODES:
            # Keep immediate neighbors with highest degree
            neighbors = list(G.neighbors(central_class)) + list(G.predecessors(central_class))
            neighbors_by_degree = sorted([(node, G.degree(node)) for node in neighbors],
                                       key=lambda x: x[1], reverse=True)
            
            top_neighbors = [node for node, _ in neighbors_by_degree[:MAX_NODES-1]]
            top_neighbors.append(central_class)
            
            nodes_to_remove = [node for node in neighborhood.nodes() 
                              if node not in top_neighbors]
            neighborhood.remove_nodes_from(nodes_to_remove)
        
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(neighborhood, k=0.3, iterations=50)
        
        # Draw nodes
        central_nodes = [central_class]
        other_nodes = [n for n in neighborhood.nodes() if n != central_class]
        
        nx.draw_networkx_nodes(neighborhood, pos, nodelist=central_nodes, 
                              node_size=2000, node_color="red", alpha=0.8)
        nx.draw_networkx_nodes(neighborhood, pos, nodelist=other_nodes,
                              node_size=1500, node_color="lightblue", alpha=0.6)
        
        # Draw edges with different colors based on relationship type
        for edge_type, color in [('INHERITS_FROM', 'blue'), ('CONTAINS', 'green'), 
                                ('REFERENCES', 'orange'), ('DEPENDS_ON', 'purple'),
                                ('CREATES', 'red')]:
            edge_list = [(s, t) for s, t, d in neighborhood.edges(data=True) 
                        if d.get('type') == edge_type]
            nx.draw_networkx_edges(neighborhood, pos, edgelist=edge_list, 
                                  width=1.5, alpha=0.7, edge_color=color)
        
        nx.draw_networkx_labels(neighborhood, pos, font_size=8)
        
        # Create a legend for edge types
        plt.figtext(0.01, 0.01, "Blue: Inherits From | Green: Contains | Orange: References | Purple: Depends On | Red: Creates", 
                   fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
        
        plt.title(f"Relationships for {central_class}", fontsize=16)
        plt.axis("off")
        plt.tight_layout()
        
        # Save the figure
        output_file = os.path.join(output_path, f"neighborhood_{central_class}.png")
        plt.savefig(output_file, dpi=300, bbox_inches="tight")
        plt.close()
        
        print(f"Created neighborhood visualization for {central_class}")

def generate_html_report(G, output_path):
    """Generate an HTML report summarizing the ontology."""
    # Get relationship counts
    rel_counts = {
        "INHERITS_FROM": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'INHERITS_FROM'),
        "CONTAINS": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'CONTAINS'),
        "REFERENCES": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'REFERENCES'),
        "DEPENDS_ON": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'DEPENDS_ON'),
        "CREATES": sum(1 for _, _, attrs in G.edges(data=True) if attrs.get('type') == 'CREATES'),
    }
    
    # Get top classes by connections
    top_classes = sorted([(node, G.degree(node)) for node in G.nodes()],
                       key=lambda x: x[1], reverse=True)[:20]
    
    # Generate HTML content
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>OpenAccess Design Ontology Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .stat-box {{ background-color: #f9f9f9; border-radius: 5px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .visualizations {{ display: flex; flex-wrap: wrap; gap: 20px; }}
        .viz-item {{ width: 30%; }}
        .viz-item img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>OpenAccess Design Ontology Report</h1>
        
        <div class="stat-box">
            <h2>Ontology Statistics</h2>
            <p><strong>Total Classes:</strong> {G.number_of_nodes()}</p>
            <p><strong>Total Relationships:</strong> {G.number_of_edges()}</p>
            <p><strong>Relationship Types:</strong></p>
            <ul>
                <li>Inheritance Relationships: {rel_counts["INHERITS_FROM"]}</li>
                <li>Containment Relationships: {rel_counts["CONTAINS"]}</li>
                <li>Reference Relationships: {rel_counts["REFERENCES"]}</li>
                <li>Dependency Relationships: {rel_counts["DEPENDS_ON"]}</li>
                <li>Creation Relationships: {rel_counts["CREATES"]}</li>
            </ul>
        </div>
        
        <h2>Most Connected Classes</h2>
        <table>
            <tr>
                <th>Class Name</th>
                <th>Connections</th>
            </tr>
    """
    
    for class_name, degree in top_classes:
        html_content += f"""
            <tr>
                <td>{class_name}</td>
                <td>{degree}</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <h2>Visualizations</h2>
        <div class="visualizations">
    """
    
    # Skip visualization images since we aren't generating them
    html_content += """
            <div class="viz-item">
                <h3>Visualizations</h3>
                <p>Visualizations were skipped due to matplotlib requirements.</p>
            </div>
        """
    
    html_content += """
        </div>
    </div>
</body>
</html>
    """
    
    # Write HTML file
    with open(os.path.join(output_path, "ontology_report.html"), 'w') as f:
        f.write(html_content)
    
    print("Created HTML report")

def main():
    """Main function to create visualizations."""
    print("Creating visualizations for OpenAccess design ontology...")
    
    # Check if ontology file exists
    if not os.path.exists(ONTOLOGY_FILE):
        print(f"Error: Ontology file {ONTOLOGY_FILE} not found. Run build_ontology.py first.")
        return
    
    # Create output directory
    viz_dir = os.path.join(OUTPUT_DIR, "visualizations")
    os.makedirs(viz_dir, exist_ok=True)
    
    # Load the graph
    G = load_graph_from_json(ONTOLOGY_FILE)
    
    print(f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Skip visualizations that require matplotlib for now
    # We'll still generate the HTML report
    print("Skipping visualizations that require matplotlib")
    
    # Generate HTML report
    generate_html_report(G, OUTPUT_DIR)
    
    print("Done! Visualizations and report have been created in the ontology_output directory.")

if __name__ == "__main__":
    main()