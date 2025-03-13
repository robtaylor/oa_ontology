# OpenAccess Ontology Explorer

This repository contains tools for extracting, analyzing, and visualizing the ontology behind the Cadence OpenAccess API for IC design. The tools extract both the software class structure and the underlying domain concepts from the API documentation.

## Overview

The Cadence OpenAccess API is a complex C++ library that provides access to IC design data. This project aims to:

1. Extract the class structure and relationships from the API documentation
2. Identify the underlying domain concepts and relationships
3. Visualize the ontology for better understanding
4. Export the ontology to formats usable in graph databases and visualization tools

## Contents

### Scripts

- `build_ontology.py` - Extracts the software class structure from YAML documentation
- `visualize_ontology.py` - Generates HTML reports and visualizations of the ontology
- `export_to_neo4j.py` - Exports the ontology to Neo4j-compatible formats
- `extract_domain_ontology.py` - Extracts the domain concepts and relationships

### Documentation

- `README.md` - This file
- `ontology_README.md` - Detailed documentation of the software ontology
- `domain_ontology_summary.md` - Analysis of the domain concepts and relationships

### Outputs

- `outputs/design_ontology.json` - Software class ontology in JSON format
- `outputs/domain_ontology.json` - Domain concept ontology in JSON format
- `outputs/design_ontology.graphml` - Software ontology in GraphML format
- `outputs/domain_ontology.graphml` - Domain ontology in GraphML format
- `outputs/neo4j_import.cypher` - Neo4j import script
- `outputs/example_queries.cypher` - Example Neo4j queries
- `outputs/domain_ontology_report.md` - Detailed report on domain concepts
- `outputs/ontology_metrics.json` - Statistics about the ontology

## Key Findings

The analysis revealed several interesting aspects of the OpenAccess API:

1. **Multi-Domain Structure**: OpenAccess organizes design data into three parallel domains:
   - Block Domain (physical implementation)
   - Module Domain (logical structure)
   - Occurrence Domain (hierarchical instances)

2. **Domain Categories**:
   - Connectivity Domain (90 classes): Net, Term, InstTerm, etc.
   - Physical Domain (70 classes): Shape, Fig, Rect, etc.
   - Hierarchy Domain (42 classes): Design, Block, Module, etc.
   - Layout Domain (15 classes): Row, Boundary, Blockage, etc.
   - Device Domain (6 classes): Device, Resistor, Capacitor, etc.

3. **Core Concepts**:
   - DesignObject: Base class for all design elements
   - BlockObject: Container for physical design elements
   - Fig (Figure): Base concept for all geometric objects
   - Net: Electrical connection between components
   - Term: Connection point for nets
   - Inst (Instance): Instantiation of a design

## Usage

### Requirements

- Python 3.6+
- Required packages: networkx, pyyaml, tqdm

Install dependencies:
```
pip install networkx pyyaml tqdm
```

### Running the Scripts

To extract the software ontology:
```
python build_ontology.py
```

To generate reports and visualizations:
```
python visualize_ontology.py
```

To export to Neo4j:
```
python export_to_neo4j.py
```

To extract the domain ontology:
```
python extract_domain_ontology.py
```

### Visualizing with External Tools

The GraphML files can be imported into:
- [Gephi](https://gephi.org/)
- [Cytoscape](https://cytoscape.org/)
- [yEd Graph Editor](https://www.yworks.com/products/yed)

### Using with Neo4j

1. Install [Neo4j Desktop](https://neo4j.com/download/) or Neo4j Server
2. Create a new database
3. Run the contents of `outputs/neo4j_import.cypher` in the Neo4j Browser
4. Use the queries in `outputs/example_queries.cypher` to explore the ontology

## License

This project is for educational and research purposes only. The OpenAccess API documentation is owned by Cadence Design Systems.