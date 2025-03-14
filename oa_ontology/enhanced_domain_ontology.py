#!/usr/bin/env python3
"""
Enhanced domain ontology extractor that incorporates cross-referenced UML and API data.

This script builds upon the original domain ontology extraction but uses the richer
cross-referenced data that combines API documentation with UML diagrams.
"""

import os
import json
import re
import glob
from pathlib import Path
from tqdm import tqdm
import networkx as nx
from collections import defaultdict

# Constants
CROSSREF_DIR = "ontology_output/crossref"
OUTPUT_DIR = "outputs"
ENHANCED_DOMAIN_FILE = os.path.join(OUTPUT_DIR, "enhanced_domain_ontology.json")
ENHANCED_DOMAIN_GRAPHML = os.path.join(OUTPUT_DIR, "enhanced_domain_ontology.graphml")
ENHANCED_DOMAIN_REPORT = os.path.join(OUTPUT_DIR, "enhanced_domain_ontology_report.md")

# Design domain concepts (same as original)
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

# UML to domain relationship mapping
UML_TO_DOMAIN = {
    "inheritance": "SPECIALIZES",
    "aggregation-many": "CONTAINS_MANY",
    "aggregation-single": "CONTAINS_ONE",
    "association-reference": "REFERENCES",
    "association-many": "ASSOCIATED_WITH_MANY",
    "association": "ASSOCIATED_WITH",
    "composition": "COMPOSED_OF",
    "usage": "USES"
}

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

def load_crossreferenced_data(crossref_dir):
    """Load all cross-referenced class data from JSON files."""
    crossref_data = {}
    
    # Find all JSON files in the crossref directory
    json_files = glob.glob(os.path.join(crossref_dir, "*.json"))
    
    print(f"Loading {len(json_files)} cross-referenced class files...")
    
    for json_file in tqdm(json_files, desc="Loading cross-referenced data"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'name' not in data:
                continue
                
            class_name = data['name']
            crossref_data[class_name] = data
        
        except Exception as e:
            filename = os.path.basename(json_file)
            print(f"Error loading {filename}: {str(e)}")
    
    return crossref_data

def build_enhanced_domain_ontology(crossref_dir):
    """Build an enhanced domain ontology using cross-referenced data."""
    # First, load all cross-referenced data
    crossref_data = load_crossreferenced_data(crossref_dir)
    
    # Create a new directed graph for the enhanced domain ontology
    domain_graph = nx.DiGraph()
    
    print(f"Building domain ontology from {len(crossref_data)} classes...")
    
    # First pass: Add all classes with domain information
    for class_name, data in tqdm(crossref_data.items(), desc="Adding classes"):
        domain_type, concept = extract_domain_type(class_name)
        
        # Add class node with domain info
        domain_graph.add_node(class_name, 
                             label=class_name.replace("oa", ""),
                             type='Class',
                             domain=domain_type,
                             concept=concept,
                             description=clean_description(data.get('description', '')),
                             methods_count=len(data.get('methods', [])))
    
    # Second pass: Add relationships from UML diagrams
    relationship_counts = defaultdict(int)
    source_counts = {
        'uml_only': 0,
        'api_inferred': 0,
        'crossref': 0
    }
    
    for class_name, data in tqdm(crossref_data.items(), desc="Adding relationships"):
        # Skip classes that aren't in the graph (shouldn't happen, but just in case)
        if class_name not in domain_graph:
            continue
        
        # Process UML relationships
        for rel in data.get('relationships', []):
            source = rel.get('source')
            target = rel.get('target')
            rel_type = rel.get('type')
            description = rel.get('description', '')
            member = rel.get('member', '')
            
            # Skip if source or target not in graph
            if source not in domain_graph or target not in domain_graph:
                continue
            
            # Map UML relationship type to domain relationship type
            domain_rel_type = UML_TO_DOMAIN.get(rel_type, "RELATED_TO")
            
            # Add edge with attributes
            domain_graph.add_edge(source, target, 
                                 type=domain_rel_type,
                                 description=description,
                                 member=member,
                                 source='uml')
            
            # Count the relationship type
            relationship_counts[domain_rel_type] += 1
            source_counts['uml_only'] += 1
        
        # Process inferred relationships from methods
        # Only if the class has methods and not too many UML relationships already
        if len(data.get('methods', [])) > 0 and class_name in domain_graph:
            # Look for methods that suggest relationships
            for method in data.get('methods', []):
                method_name = method.get('name', '')
                return_type = method.get('return_type', '')
                
                # Only consider getter methods that return OA classes
                if (method_name.startswith('get') and 
                    return_type and 
                    'oa' in return_type and 
                    '*' in return_type):
                    
                    # Extract target class from return type
                    target_class = return_type.replace('*', '').strip()
                    
                    # Skip if target class not in graph
                    if target_class not in domain_graph:
                        continue
                    
                    # Determine relationship type based on method name and return type
                    if 'Collection' in return_type or method_name.endswith('s'):
                        rel_type = "CONTAINS_MANY"
                    else:
                        rel_type = "CONTAINS_ONE"
                        
                    # Extract member name from method name (e.g., "getFoo" -> "foo")
                    member_match = re.match(r'get([A-Z][a-zA-Z0-9]*)', method_name)
                    member = ""
                    if member_match:
                        member = member_match.group(1)
                        # Convert to camelCase (first letter lowercase)
                        member = member[0].lower() + member[1:]
                    
                    # Skip if we already have a UML relationship with this member
                    has_existing = False
                    for _, _, edge_data in domain_graph.edges(class_name, data=True):
                        if edge_data.get('member') == member:
                            has_existing = True
                            break
                            
                    if not has_existing:
                        # Add the relationship
                        domain_graph.add_edge(class_name, target_class,
                                             type=rel_type,
                                             member=member,
                                             description=f"Inferred from method {method_name}",
                                             source='api_inferred')
                        
                        # Count the relationship
                        relationship_counts[rel_type] += 1
                        source_counts['api_inferred'] += 1
    
    # Count total relationships
    total_relationships = sum(relationship_counts.values())
    total_crossref = source_counts['uml_only'] + source_counts['api_inferred']
    source_counts['crossref'] = total_crossref
    
    print(f"Added {total_relationships} relationships to domain ontology")
    print(f"Relationship types:")
    for rel_type, count in relationship_counts.items():
        print(f"  - {rel_type}: {count} ({count/total_relationships:.1%})")
    
    print(f"Relationship sources:")
    print(f"  - UML: {source_counts['uml_only']} ({source_counts['uml_only']/total_crossref:.1%})")
    print(f"  - API inferred: {source_counts['api_inferred']} ({source_counts['api_inferred']/total_crossref:.1%})")
    
    return domain_graph, relationship_counts, source_counts

def save_domain_ontology(graph, output_file, graphml_file):
    """Save the domain ontology to JSON and GraphML formats."""
    # Convert NetworkX graph to JSON format
    nodes = []
    for node, attrs in graph.nodes(data=True):
        node_data = {'id': node}
        node_data.update(attrs)
        nodes.append(node_data)
    
    links = []
    for source, target, attrs in graph.edges(data=True):
        link_data = {'source': source, 'target': target}
        link_data.update(attrs)
        links.append(link_data)
    
    ontology_data = {'nodes': nodes, 'links': links}
    
    # Save as JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ontology_data, f, indent=2)
    
    print(f"Domain ontology saved to {output_file}")
    
    # Save as GraphML
    try:
        nx.write_graphml(graph, graphml_file)
        print(f"Domain ontology saved as GraphML to {graphml_file}")
    except Exception as e:
        print(f"Error saving GraphML: {str(e)}")

def generate_domain_report(graph, relationship_counts, source_counts, output_file):
    """Generate a detailed report about the domain ontology."""
    # Count classes by domain and concept
    domain_counts = defaultdict(int)
    concept_counts = defaultdict(int)
    
    for _, attrs in graph.nodes(data=True):
        domain = attrs.get('domain', 'Unknown')
        concept = attrs.get('concept', 'Unknown')
        
        domain_counts[domain] += 1
        concept_counts[concept] += 1
    
    # Generate report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Enhanced OpenAccess Domain Ontology Report\n\n")
        
        f.write("## Overview\n\n")
        f.write(f"Total classes: {graph.number_of_nodes()}\n")
        f.write(f"Total relationships: {graph.number_of_edges()}\n\n")
        
        # Classes by domain
        f.write("## Classes by Domain\n\n")
        for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{domain}** Domain: {count} classes ({count/graph.number_of_nodes():.1%})\n")
        f.write("\n")
        
        # Classes by concept
        f.write("## Top 10 Concepts\n\n")
        top_concepts = sorted(concept_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for concept, count in top_concepts:
            if concept != "Unknown":
                f.write(f"- **{concept}**: {count} classes\n")
        f.write("\n")
        
        # Relationship types
        f.write("## Relationship Types\n\n")
        for rel_type, count in sorted(relationship_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- **{rel_type}**: {count} relationships ({count/graph.number_of_edges():.1%})\n")
        f.write("\n")
        
        # Relationship sources
        f.write("## Relationship Sources\n\n")
        total_crossref = source_counts['crossref']
        f.write(f"- **UML Diagrams**: {source_counts['uml_only']} relationships ({source_counts['uml_only']/total_crossref:.1%})\n")
        f.write(f"- **API Inferred**: {source_counts['api_inferred']} relationships ({source_counts['api_inferred']/total_crossref:.1%})\n")
        f.write("\n")
        
        # Hub classes (most connected)
        f.write("## Top 10 Hub Classes\n\n")
        hub_classes = sorted(graph.degree(), key=lambda x: x[1], reverse=True)[:10]
        for class_name, degree in hub_classes:
            domain = graph.nodes[class_name].get('domain', 'Unknown')
            concept = graph.nodes[class_name].get('concept', 'Unknown')
            f.write(f"- **{class_name}** ({domain}/{concept}): {degree} connections\n")
    
    print(f"Domain ontology report saved to {output_file}")

def main():
    """Main function to extract the enhanced domain ontology."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Extracting enhanced domain ontology...")
    
    # Build the domain ontology
    graph, relationship_counts, source_counts = build_enhanced_domain_ontology(CROSSREF_DIR)
    
    # Save the domain ontology
    save_domain_ontology(graph, ENHANCED_DOMAIN_FILE, ENHANCED_DOMAIN_GRAPHML)
    
    # Generate domain report
    generate_domain_report(graph, relationship_counts, source_counts, ENHANCED_DOMAIN_REPORT)
    
    print("Domain ontology extraction complete!")

if __name__ == "__main__":
    main()