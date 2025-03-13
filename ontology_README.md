# OpenAccess Design Ontology

This directory contains scripts and data for building and exploring a graph ontology of the Cadence OpenAccess library, focusing on the design module.

## Overview

The OpenAccess API is a complex object-oriented library for IC design. This ontology project extracts class relationships and properties from the YAML documentation and represents them as a graph structure. This allows for better understanding of the codebase, exploration of relationships between classes, and discovery of design patterns.

## Files

- `build_ontology.py`: Extracts relationships from YAML files and builds the graph
- `visualize_ontology.py`: Generates an HTML report from the ontology
- `export_to_neo4j.py`: Exports the ontology to Neo4j-compatible formats

## Generated Outputs (in `ontology_output/`)

- `design_ontology.json`: The complete ontology in JSON format
- `ontology_metrics.json`: Statistics about the ontology
- `neo4j_import.cypher`: Cypher script for importing into Neo4j
- `example_queries.cypher`: Sample Neo4j queries for exploring the ontology
- `design_ontology.graphml`: GraphML format for visualization in tools like Gephi
- `visualizations/ontology_report.html`: HTML report of the ontology

## Ontology Structure

The ontology is structured as follows:

- **Nodes**: Class definitions with properties:
  - `name`: The class name
  - `description`: Brief description of the class
  - `methods_count`: Number of methods in the class
  - `enums_count`: Number of enumerations in the class

- **Relationships**:
  - `INHERITS_FROM`: Class inheritance relationships
  - `REFERENCES`: Class references other classes (through member references)
  - `DEPENDS_ON`: Class depends on another class (through method parameters)
  - `CREATES`: Class creates instances of another class (through factory methods)

## Key Ontology Metrics

- Total Classes: 336
- Total Relationships: 1733
- Inheritance Relationships: 1258
- Reference Relationships: 224
- Dependency Relationships: 150

## Most Connected Classes

The most central classes in the design hierarchy are:

1. oaDesignObject
2. oaObject
3. oaBlockObject
4. oaOccObject
5. oaBlock

## Using the Ontology

### With Neo4j

1. Install Neo4j Desktop or Neo4j Server
2. Create a new database
3. Run the contents of `neo4j_import.cypher` in the Neo4j Browser
4. Use the queries in `example_queries.cypher` to explore the ontology

### With Other Graph Tools

The ontology is also provided in GraphML format, which can be imported into:
- Gephi
- Cytoscape
- yEd Graph Editor

## Future Enhancements

Potential improvements to this ontology include:

1. Adding more relationship types based on method semantics
2. Extracting individual properties and methods as nodes
3. Incorporating data from other OpenAccess modules
4. Creating interactive visualizations
5. Implementing a domain-specific query language

## Requirements

- Python 3.6+
- NetworkX
- PyYAML
- tqdm

Optional:
- Neo4j (for database import)
- Gephi or similar (for advanced visualization)