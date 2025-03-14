#!/usr/bin/env python3
"""
Extract the domain ontology from OpenAccess design API.

This script analyzes the OpenAccess YAML documentation and extracts the underlying
conceptual domain model, focusing on IC design concepts rather than just code structure.
"""

import os
import yaml
import re
import json
from pathlib import Path
from tqdm import tqdm
import networkx as nx

# Load configuration
import json
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

# Constants
YAML_DIR = Path(CONFIG["yaml_dir"]) / "design"  # Default to design module
OUTPUT_DIR = Path(CONFIG["ontology_dir"])
DOMAIN_FILE = os.path.join(OUTPUT_DIR, "domain_ontology.json")
DOMAIN_GRAPHML = os.path.join(OUTPUT_DIR, "domain_ontology.graphml")
DOMAIN_REPORT = os.path.join(OUTPUT_DIR, "domain_ontology_report.md")

# Design domain concepts we want to extract
DOMAIN_CONCEPTS = {
    # Physical design concepts
    "Physical": ["Block", "Fig", "Shape", "Rect", "Path", "Via", "Pin", "Text", "Layer", "Design"],
    
    # Connectivity concepts
    "Connectivity": ["Net", "Term", "InstTerm", "Conn", "Route", "Guide", "Pin"],
    
    # Hierarchy concepts
    "Hierarchy": ["Module", "Design", "Block", "Inst", "ScalarInst", "VectorInst", "ArrayInst", "Occurrence"],
    
    # Layout concepts
    "Layout": ["Row", "Site", "Track", "GCell", "Boundary", "Blockage", "Halo", "Core"],
    
    # Device concepts 
    "Device": ["Device", "Resistor", "Capacitor", "Inductor", "Diode", "Transistor"]
}

# Common patterns for domain relationships
DOMAIN_RELATIONSHIPS = [
    # Format: (src_pattern, rel_pattern, tgt_pattern, relationship_type, weight)
    (r"(Inst|Array)", r"get(Term|Net)", r"(Term|Net)", "CONNECTS_TO", 5),
    (r"Net", r"get(Term|InstTerm|Pin|Shape|Fig|Via)", r"(Term|InstTerm|Pin|Shape|Fig|Via)", "CONNECTS", 5),
    (r"Block", r"get(Net|Inst|Term|Fig|Shape)", r"(Net|Inst|Term|Fig|Shape)", "CONTAINS", 5),
    (r"Design", r"get(Block|Module)", r"(Block|Module)", "CONTAINS", 5),
    (r"Module", r"get(ModNet|ModTerm|ModInst)", r"(ModNet|ModTerm|ModInst)", "CONTAINS", 5),
    (r"Occurrence", r"get(OccNet|OccTerm|OccInst)", r"(OccNet|OccTerm|OccInst)", "CONTAINS", 5),
    (r"Fig", r"get(Box|Net)", r"(Box|Net)", "HAS", 3),
    (r"(Rect|Path|Text|Via)", r"get(Layer|Net)", r"(Layer|Net)", "ASSOCIATED_WITH", 3),
    (r"(Shape|ConnFig)", r"get(Layer|Net)", r"(Layer|Net)", "ON", 4),
    (r"(Term|Inst)", r"get(Name|Net|InstTerm)", r"(Name|Net|InstTerm)", "HAS", 3),
    (r"(Net)", r"is(Global)", r"", "PROPERTY", 1)
]

def extract_domain_type(class_name):
    """Extract the domain type from a class name."""
    # Strip 'oa' prefix and any modifiers
    base_name = class_name.replace("oa", "").replace("Mod", "").replace("Occ", "")
    
    # Find which domain this class belongs to
    for domain, concepts in DOMAIN_CONCEPTS.items():
        for concept in concepts:
            if concept in base_name:
                return domain, concept
    
    return "Other", "Unknown"


def extract_domain_relationships(method, source_class, target_class):
    """Extract domain relationships from a method name and class names."""
    relationships = []
    method_name = method.get('name', '')
    
    # Strip 'oa' prefix for readability
    source_base = source_class.replace("oa", "")
    target_base = target_class.replace("oa", "") if target_class else ""
    
    # Check against domain relationship patterns
    for src_pattern, rel_pattern, tgt_pattern, rel_type, weight in DOMAIN_RELATIONSHIPS:
        if (re.search(src_pattern, source_base) and 
            (not tgt_pattern or re.search(tgt_pattern, target_base))):
            
            # Check if the method matches the relationship pattern
            if re.search(rel_pattern, method_name):
                # Extract concept specific part from the method name
                concept_match = re.search(r'get(\w+)', method_name)
                concept = concept_match.group(1) if concept_match else ""
                
                relationships.append((rel_type, target_class, {
                    'weight': weight,
                    'method': method_name,
                    'concept': concept
                }))
    
    return relationships

def clean_description(description, max_length=200):
    """Clean and truncate a description."""
    if not description:
        return ""
    
    # Remove excessive whitespace
    desc = re.sub(r'\s+', ' ', description).strip()
    
    # Truncate if too long
    if len(desc) > max_length:
        desc = desc[:max_length-3] + "..."
    
    return desc

def build_domain_ontology(yaml_dir):
    """Build a domain-focused ontology from the YAML files."""
    # First, build the software ontology like before
    sw_graph = nx.DiGraph()
    domain_graph = nx.DiGraph()
    
    # Get all class files (excluding member files)
    yaml_files = [f for f in os.listdir(yaml_dir)
                  if f.endswith('.yaml') and not f.endswith('-members.yaml')
                  and not f == 'classes.yaml']
    
    print(f"Processing {len(yaml_files)} class files...")
    
    # First pass: Load all classes and basic properties
    for filename in tqdm(yaml_files, desc="Loading classes"):
        try:
            with open(os.path.join(yaml_dir, filename), 'r') as f:
                data = yaml.safe_load(f)
            
            if 'name' not in data:
                continue
                
            class_name = data['name']
            domain_type, concept = extract_domain_type(class_name)
            
            # Add class node with domain info
            domain_graph.add_node(class_name, 
                                 type='Class',
                                 domain=domain_type,
                                 concept=concept,
                                 description=clean_description(data.get('description', '')),
                                 methods_count=len(data.get('methods', [])))
            
            # Store in SW graph for reference
            sw_graph.add_node(class_name, 
                             type='Class',
                             description=clean_description(data.get('description', '')),
                             methods_count=len(data.get('methods', [])))
            
            # Add inheritance relationships
            for parent in data.get('inheritance', []):
                sw_graph.add_edge(class_name, parent, type='INHERITS_FROM')
        
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    
    # Second pass: Add domain relationships
    for filename in tqdm(yaml_files, desc="Analyzing relationships"):
        try:
            with open(os.path.join(yaml_dir, filename), 'r') as f:
                data = yaml.safe_load(f)
            
            if 'name' not in data or 'methods' not in data:
                continue
                
            class_name = data['name']
            
            # Process methods to find domain relationships
            for method in data['methods']:
                method_name = method.get('name', '')
                return_type = method.get('return_type', '')
                
                # Skip methods that don't provide useful relationship info
                if not method_name.startswith('get') or 'Collection' in return_type:
                    continue
                
                # Extract target class from return type
                target_class = None
                if return_type and 'oa' in return_type and '*' in method.get('signature', ''):
                    target_class = return_type.replace('*', '').strip()
                    
                    # Check if both source and target are in our domain graph
                    if target_class in domain_graph and class_name in domain_graph:
                        # Extract domain relationships
                        relationships = extract_domain_relationships(method, class_name, target_class)
                        
                        for rel_type, target, attrs in relationships:
                            domain_graph.add_edge(class_name, target, type=rel_type, **attrs)
        
        except Exception as e:
            print(f"Error processing relationships in {filename}: {str(e)}")
    
    # Third pass: Infer additional domain relationships from inheritance
    for source, target, attrs in list(sw_graph.edges(data=True)):
        if attrs.get('type') == 'INHERITS_FROM':
            if source in domain_graph and target in domain_graph:
                # Inherit domain/concept from parent if not already set
                if not domain_graph.nodes[source].get('domain') and domain_graph.nodes[target].get('domain'):
                    domain_graph.nodes[source]['domain'] = domain_graph.nodes[target]['domain']
                    
                if not domain_graph.nodes[source].get('concept') and domain_graph.nodes[target].get('concept'):
                    domain_graph.nodes[source]['concept'] = domain_graph.nodes[target]['concept']
                
                # Add a generic domain relationship based on inheritance
                if not domain_graph.has_edge(source, target):
                    domain_graph.add_edge(source, target, type='SPECIALIZES', weight=2)
    
    return domain_graph

def export_domain_ontology(graph, output_path):
    """Export the domain ontology to JSON."""
    data = {
        "nodes": [],
        "links": []
    }
    
    # Add nodes
    for node, attrs in graph.nodes(data=True):
        node_data = {
            "id": node,
            "label": node.replace("oa", ""),  # More readable label
            **attrs
        }
        data["nodes"].append(node_data)
    
    # Add edges
    for source, target, attrs in graph.edges(data=True):
        edge_data = {
            "source": source,
            "target": target,
            **attrs
        }
        data["links"].append(edge_data)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Domain ontology exported to {output_path}")

def export_to_graphml(graph, output_path):
    """Export the graph to GraphML format."""
    # Create a copy of the graph for export
    export_graph = nx.DiGraph()
    
    # Copy nodes with simplified attributes
    for node, attrs in graph.nodes(data=True):
        export_attrs = {
            'name': node,
            'domain': attrs.get('domain', ''),
            'concept': attrs.get('concept', ''),
            'description': attrs.get('description', '')[:100]  # Truncate for GraphML
        }
        export_graph.add_node(node, **export_attrs)
    
    # Copy edges with simplified attributes
    for source, target, attrs in graph.edges(data=True):
        export_attrs = {
            'type': attrs.get('type', ''),
            'weight': attrs.get('weight', 1)
        }
        export_graph.add_edge(source, target, **export_attrs)
    
    try:
        # Write to GraphML
        nx.write_graphml(export_graph, output_path)
        print(f"Domain ontology exported to GraphML: {output_path}")
    except AttributeError as e:
        # Handle numpy float_ error
        if "float_" in str(e):
            print(f"Warning: Unable to export to GraphML due to NumPy 2.0 compatibility issue.")
            print(f"Error details: {str(e)}")
        else:
            raise

def generate_domain_report(graph, output_path):
    """Generate a markdown report summarizing the domain ontology."""
    # Count domains
    domains = {}
    for _, attrs in graph.nodes(data=True):
        domain = attrs.get('domain', 'Unknown')
        if domain not in domains:
            domains[domain] = 0
        domains[domain] += 1
    
    # Count relationship types
    relationships = {}
    for _, _, attrs in graph.edges(data=True):
        rel_type = attrs.get('type', 'Unknown')
        if rel_type not in relationships:
            relationships[rel_type] = 0
        relationships[rel_type] += 1
    
    # Prepare report
    report = f"""# OpenAccess Design Domain Ontology

## Overview

This report analyzes the domain concepts extracted from the OpenAccess Design API.
The ontology represents the underlying IC design concepts rather than just the code structure.

## Domain Statistics

Total classes: {graph.number_of_nodes()}
Total relationships: {graph.number_of_edges()}

### Classes by Domain

"""
    
    # Add domain counts
    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
        report += f"- **{domain}**: {count} classes\n"
    
    report += "\n### Relationship Types\n\n"
    
    # Add relationship counts
    for rel, count in sorted(relationships.items(), key=lambda x: x[1], reverse=True):
        report += f"- **{rel}**: {count} relationships\n"
    
    report += "\n## Key Concepts\n\n"
    
    # Find top classes by degree centrality
    centrality = nx.degree_centrality(graph)
    top_classes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:20]
    
    for class_name, score in top_classes:
        domain = graph.nodes[class_name].get('domain', 'Unknown')
        concept = graph.nodes[class_name].get('concept', 'Unknown')
        desc = graph.nodes[class_name].get('description', '')[:150] + "..."
        
        report += f"### {class_name.replace('oa', '')}\n\n"
        report += f"**Domain**: {domain}  \n"
        report += f"**Concept**: {concept}  \n"
        report += f"**Centrality**: {score:.4f}  \n"
        report += f"**Description**: {desc}  \n\n"
        
        # List key relationships
        out_edges = list(graph.out_edges(class_name, data=True))
        if out_edges:
            report += "**Relationships**:\n\n"
            for _, target, attrs in sorted(out_edges, key=lambda x: x[2].get('weight', 0), reverse=True)[:5]:
                rel_type = attrs.get('type', 'relates to')
                target_name = target.replace('oa', '')
                report += f"- {rel_type} → {target_name}\n"
            report += "\n"
    
    report += "\n## Domain Concept Map\n\n"
    report += "This ontology is available in GraphML format for visualization in tools like Gephi, Cytoscape, or yEd.\n"
    
    # Write report
    with open(output_path, 'w') as f:
        f.write(report)
    
    print(f"Domain report written to {output_path}")

def main():
    """Main function to extract the domain ontology."""
    print("Extracting OpenAccess design domain ontology...")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Build the domain ontology
    domain_graph = build_domain_ontology(YAML_DIR)
    
    print(f"Created domain ontology with {domain_graph.number_of_nodes()} concepts and {domain_graph.number_of_edges()} relationships")
    
    # Export to JSON
    export_domain_ontology(domain_graph, DOMAIN_FILE)
    
    # Export to GraphML
    export_to_graphml(domain_graph, DOMAIN_GRAPHML)
    
    # Generate report
    generate_domain_report(domain_graph, DOMAIN_REPORT)
    
    print("Done! The domain ontology has been extracted and exported.")

if __name__ == "__main__":
    main()