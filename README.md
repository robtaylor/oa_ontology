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
- `run_crossref.py` - Cross-references UML diagrams with API documentation
- `validate_crossref.py` - Validates the cross-referenced data quality
- `enhanced_domain_ontology.py` - Creates enhanced domain ontology from cross-referenced data
- `run_enhanced_domain.py` - Runs the enhanced domain ontology extraction

### Documentation

- `README.md` - This file
- `ontology_README.md` - Detailed documentation of the software ontology
- `domain_ontology_summary.md` - Analysis of the domain concepts and relationships
- `CROSSREF_README.md` - Documentation of the cross-referencing system
- `ENHANCED_DOMAIN_README.md` - Documentation of the enhanced domain ontology

### Outputs

- `outputs/design_ontology.json` - Software class ontology in JSON format
- `outputs/domain_ontology.json` - Domain concept ontology in JSON format
- `outputs/design_ontology.graphml` - Software ontology in GraphML format
- `outputs/domain_ontology.graphml` - Domain ontology in GraphML format
- `outputs/neo4j_import.cypher` - Neo4j import script
- `outputs/example_queries.cypher` - Example Neo4j queries
- `outputs/domain_ontology_report.md` - Detailed report on domain concepts
- `outputs/ontology_metrics.json` - Statistics about the ontology
- `ontology_output/crossref/*.json` - Cross-referenced class data
- `ontology_output/crossref/crossref_report.md` - Summary report of cross-referencing
- `outputs/enhanced_domain_ontology.json` - Enhanced domain ontology from cross-referenced data
- `outputs/enhanced_domain_ontology.graphml` - Enhanced domain ontology in GraphML format
- `outputs/enhanced_domain_ontology_report.md` - Report on the enhanced domain ontology

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

- Python >= 3.9
- [PDM](https://pdm-project.org/en/latest/)
- Required packages (automatically installed by PDM):
  - networkx
  - pyyaml
  - tqdm
  - beautifulsoup4
  - tomli
  - pyvis
  - lxml (for GraphML export)

### Setup and Running the Scripts

First, install the project with PDM:

```bash
pdm install
```

1. Setup the environment and download documentation:
```bash
pdm run oa-setup
```
This will:
- Clone the OpenAccess HTML documentation from GitHub
- Set up the directory structure
- Create a configuration file

2. Parse the HTML documentation into YAML:
```bash
pdm run oa-parse
```

3. Extract the software ontology:
```bash
pdm run oa-build
```

4. Generate reports and visualizations:
```bash
pdm run oa-visualize
```

5. Export to Neo4j:
```bash
pdm run oa-export
```

6. Extract the domain ontology:
```bash
pdm run oa-domain
```

You can also process all steps at once with:
```bash
pdm run oa-run-all
```

7. Cross-reference UML diagrams and API documentation:
```bash
pdm run oa-crossref
```

8. Validate the cross-referenced data:
```bash
pdm run oa-validate-crossref
```

9. Generate enhanced domain ontology from cross-referenced data:
```bash
pdm run oa-enhanced-domain
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

## Troubleshooting

### Common Issues

1. **Missing lxml Error**

   If you get an error about a missing lxml module when exporting to GraphML, make sure you have the lxml package installed:

   ```bash
   pdm add lxml
   ```

2. **NumPy 2.0 Compatibility Issue**

   If you encounter errors related to `np.float_` being removed in NumPy 2.0, you have two options:
   
   - Use an earlier version of NumPy: `pdm add "numpy<2.0"`
   - The code has been updated to handle this error gracefully, but GraphML export might not work with NumPy 2.0+

3. **Cross-reference Data Quality Issues**

   The cross-reference validation may show issues with data quality. These are expected and won't prevent the system from working but indicate areas where the data extraction could be improved. Common issues include:
   
   - Missing descriptions (50% of classes)
   - Classes with no methods (about half)
   - Missing relationships from UML diagrams

## License

This project is for educational and research purposes only. The OpenAccess API documentation is owned by Cadence Design Systems.
