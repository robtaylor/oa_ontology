#!/usr/bin/env python3
"""
Export the OpenAccess design ontology to Neo4j-compatible formats.
This script generates Cypher commands that can be used to load the ontology into Neo4j.
"""

import os
import json
from pathlib import Path
import re

# Load configuration
import json
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

# Constants
ONTOLOGY_FILE = Path(CONFIG["ontology_dir"]) / "design_ontology.json"
DOMAIN_ONTOLOGY_FILE = Path(CONFIG["ontology_dir"]) / "domain_ontology.json"
ENHANCED_ONTOLOGY_FILE = Path("outputs") / "enhanced_domain_ontology.json"
OUTPUT_DIR = Path(CONFIG["ontology_dir"])

def clean_property_value(value):
    """Clean property values for Cypher queries."""
    if isinstance(value, str):
        # Escape quotes and newlines
        value = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        return f'"{value}"'
    return str(value)

def generate_neo4j_import_script(ontology_data):
    """Generate a Neo4j import script in Cypher."""
    script = """// OpenAccess Design Ontology Import Script
// This script will create a graph database of the OpenAccess class hierarchy
// Run this script in Neo4j Browser or through cypher-shell

// Clear existing database if needed
MATCH (n) DETACH DELETE n;

// Create constraints for faster lookups
CREATE CONSTRAINT class_name IF NOT EXISTS ON (c:Class) ASSERT c.name IS UNIQUE;

"""
    
    # Add nodes
    script += "// Create Class nodes\n"
    
    for node in ontology_data["nodes"]:
        node_props = []
        for key, value in node.items():
            if key not in ["id", "label"]:
                node_props.append(f"{key}: {clean_property_value(value)}")
        
        node_props_str = ", ".join(node_props)
        script += f"CREATE (:{node.get('type', 'Class')} {{name: \"{node['id']}\", {node_props_str}}});\n"
    
    script += "\n// Create relationships\n"
    
    # Add relationships
    for link in ontology_data["links"]:
        source = link["source"]
        target = link["target"]
        rel_type = link.get("type", "RELATED_TO")
        
        # Get additional properties for the relationship
        rel_props = []
        for key, value in link.items():
            if key not in ["source", "target", "type"]:
                rel_props.append(f"{key}: {clean_property_value(value)}")
        
        rel_props_str = ""
        if rel_props:
            rel_props_str = " {" + ", ".join(rel_props) + "}"
        
        script += f"MATCH (a:Class {{name: \"{source}\"}}), (b:Class {{name: \"{target}\"}}) CREATE (a)-[:{rel_type}{rel_props_str}]->(b);\n"
    
    return script

def generate_cypher_queries(ontology_data):
    """Generate common Cypher queries for exploring the ontology."""
    queries = """// Common Cypher Queries for Exploring the OpenAccess Design Ontology

// Find all base classes (classes that don't inherit from anything)
MATCH (c:Class)
WHERE NOT (c)-[:INHERITS_FROM]->()
RETURN c.name AS BaseClass
ORDER BY c.name;

// Find classes with the most relationships
MATCH (c:Class)
RETURN c.name AS Class, size((c)--()) AS RelationshipCount
ORDER BY RelationshipCount DESC
LIMIT 10;

// Get the complete inheritance hierarchy
MATCH p = (c:Class)-[:INHERITS_FROM*]->(base)
WHERE NOT (base)-[:INHERITS_FROM]->()
RETURN p
LIMIT 100;

// Find classes that contain other classes
MATCH (c:Class)-[r:CONTAINS]->(contained:Class)
RETURN c.name AS Container, collected(contained.name) AS ContainedClasses
ORDER BY size(ContainedClasses) DESC
LIMIT 20;

// Find all relationships for a specific class
// Replace 'oaDesign' with the class of interest
MATCH (c:Class {name: 'oaDesign'})-[r]->(other)
RETURN type(r) AS RelationshipType, other.name AS RelatedClass;

// Find all inheritance paths for a specific class
// Replace 'oaBlock' with the class of interest
MATCH p = (c:Class {name: 'oaBlock'})-[:INHERITS_FROM*]->(base)
RETURN [node IN nodes(p) | node.name] AS InheritancePath;

// Find circular references or dependencies
MATCH path = (c:Class)-[:DEPENDS_ON|REFERENCES*]->(c)
RETURN path;

// Find classes grouped by inheritance depth
MATCH path = (c:Class)-[:INHERITS_FROM*]->(base)
WHERE NOT (base)-[:INHERITS_FROM]->()
WITH c, length(path) AS depth
RETURN depth, collect(c.name) AS Classes
ORDER BY depth;

// Find the main containment structure
MATCH (c:Class)-[:CONTAINS]->(contained:Class)
WHERE NOT (c)<-[:CONTAINS]-()  // Only top-level containers
RETURN c.name AS Container, collect(contained.name) AS DirectlyContained
ORDER BY size(DirectlyContained) DESC;
"""
    return queries

def export_to_graphml(ontology_data, output_path):
    """Export the ontology to GraphML format."""
    # Create a basic GraphML structure
    graphml = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
     http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="d0" for="node" attr.name="description" attr.type="string"/>
  <key id="d1" for="node" attr.name="type" attr.type="string"/>
  <key id="d2" for="node" attr.name="methods_count" attr.type="int"/>
  <key id="d3" for="edge" attr.name="type" attr.type="string"/>
  <graph id="G" edgedefault="directed">
"""
    
    # Add nodes
    for node in ontology_data["nodes"]:
        node_id = re.sub(r'[^a-zA-Z0-9_]', '_', node["id"])  # Ensure valid XML ID
        graphml += f'    <node id="{node_id}">\n'
        
        # Add node attributes
        if "description" in node:
            description = node["description"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            graphml += f'      <data key="d0">{description}</data>\n'
        
        if "type" in node:
            graphml += f'      <data key="d1">{node["type"]}</data>\n'
        
        if "methods_count" in node:
            graphml += f'      <data key="d2">{node["methods_count"]}</data>\n'
        
        graphml += '    </node>\n'
    
    # Add edges
    for i, link in enumerate(ontology_data["links"]):
        source_id = re.sub(r'[^a-zA-Z0-9_]', '_', link["source"])
        target_id = re.sub(r'[^a-zA-Z0-9_]', '_', link["target"])
        graphml += f'    <edge id="e{i}" source="{source_id}" target="{target_id}">\n'
        
        if "type" in link:
            graphml += f'      <data key="d3">{link["type"]}</data>\n'
        
        graphml += '    </edge>\n'
    
    # Close GraphML
    graphml += """  </graph>
</graphml>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(graphml)
    
    print(f"Exported GraphML to {output_path}")

def main():
    """Main function to export the ontology to Neo4j formats."""
    print("Exporting OpenAccess ontologies to Neo4j formats...")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    # Export design ontology
    if os.path.exists(ONTOLOGY_FILE):
        print("Processing design ontology...")
        
        # Load the ontology data
        with open(ONTOLOGY_FILE, 'r') as f:
            ontology_data = json.load(f)
        
        # Generate Neo4j import script
        import_script = generate_neo4j_import_script(ontology_data)
        with open(os.path.join(OUTPUT_DIR, "neo4j_import.cypher"), 'w') as f:
            f.write(import_script)
        
        # Generate common Cypher queries
        queries = generate_cypher_queries(ontology_data)
        with open(os.path.join(OUTPUT_DIR, "example_queries.cypher"), 'w') as f:
            f.write(queries)
        
        # Export to GraphML
        export_to_graphml(ontology_data, os.path.join(OUTPUT_DIR, "design_ontology.graphml"))
    else:
        print(f"Warning: Design ontology file {ONTOLOGY_FILE} not found. Skipping design ontology export.")
    
    # Export enhanced domain ontology
    if os.path.exists(ENHANCED_ONTOLOGY_FILE):
        print("Processing enhanced domain ontology...")
        
        # Load the enhanced domain ontology data
        with open(ENHANCED_ONTOLOGY_FILE, 'r') as f:
            enhanced_data = json.load(f)
        
        # Generate Neo4j import script for enhanced domain ontology
        enhanced_import_script = generate_neo4j_import_script(enhanced_data)
        with open(os.path.join("outputs", "enhanced_neo4j_import.cypher"), 'w') as f:
            f.write(enhanced_import_script)
        
        # Generate specialized Cypher queries for enhanced domain ontology
        # These queries can leverage the richer relationship types in the enhanced ontology
        enhanced_queries = """// Enhanced Domain Ontology Cypher Queries
        
// Find classes with specific relationship types
MATCH (c:Class)-[r:SPECIALIZES]->(parent:Class)
RETURN c.name AS Class, parent.name AS ParentClass
LIMIT 20;

// Find composition relationships
MATCH (c:Class)-[r:COMPOSED_OF]->(part:Class)
RETURN c.name AS Whole, collect(part.name) AS Parts
ORDER BY size(Parts) DESC
LIMIT 10;

// Find classes that reference many other classes
MATCH (c:Class)-[r:REFERENCES]->(ref:Class)
RETURN c.name AS Class, count(r) AS ReferenceCount
ORDER BY ReferenceCount DESC
LIMIT 10;

// Find the container hierarchy
MATCH (c:Class)-[r:CONTAINS_ONE|CONTAINS_MANY]->(contained:Class)
RETURN c.name AS Container, 
       collect({class: contained.name, type: type(r)}) AS ContainedClasses
ORDER BY size(ContainedClasses) DESC
LIMIT 15;

// Find relationships by source
MATCH (c:Class)-[r]->(other:Class)
WHERE r.source IS NOT NULL
RETURN r.source AS Source, count(r) AS Count
ORDER BY Count DESC;

// Find classes with both UML and API relationships
MATCH (c:Class)-[r1]->(other1:Class)
WHERE r1.source = 'uml'
WITH c, count(r1) AS umlCount
MATCH (c)-[r2]->(other2:Class)
WHERE r2.source = 'api_inferred'
RETURN c.name AS Class, umlCount, count(r2) AS apiCount
ORDER BY (umlCount + count(r2)) DESC
LIMIT 20;
"""
        with open(os.path.join("outputs", "enhanced_queries.cypher"), 'w') as f:
            f.write(enhanced_queries)
        
        # Export to GraphML (already exported by enhanced_domain_ontology.py)
        print("Enhanced domain ontology GraphML already exported.")
    else:
        print(f"Warning: Enhanced domain ontology file {ENHANCED_ONTOLOGY_FILE} not found.")
        print("Run enhanced_domain_ontology.py first to generate the enhanced domain ontology.")
    
    print("Done! Neo4j files have been created in the output directories.")
    print("You can use these files to import the ontologies into Neo4j or other graph databases.")

if __name__ == "__main__":
    main()