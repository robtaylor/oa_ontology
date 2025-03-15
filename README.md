# OpenAccess Ontology Explorer

This repository contains tools for extracting, analyzing, and visualizing the ontology behind the Cadence OpenAccess API for IC design. The tools extract both the software class structure and the underlying domain concepts from the API documentation.

## Overview

The Cadence OpenAccess API is a complex C++ library that provides access to IC design data. This project aims to:

1. Extract the class structure and relationships from the API documentation
2. Identify the underlying domain concepts and relationships
3. Visualize the ontology for better understanding
4. Export the ontology to formats usable in graph databases and visualization tools

## Contents

### Packages and Scripts

- **oa_ontology**: Core library package with functionality for ontology extraction and processing
  - `build_ontology.py` - Extracts the software class structure from YAML documentation
  - `visualize_ontology.py` - Generates HTML reports and visualizations of the ontology
  - `export_to_neo4j.py` - Exports the ontology to Neo4j-compatible formats
  - `extract_domain_ontology.py` - Extracts the domain concepts and relationships
  - `enhanced_domain_ontology.py` - Creates enhanced domain ontology from cross-referenced data
  - And more specialized modules for different processing steps

- **scripts**: Utility scripts package with command-line tools
  - Visualization scripts (visualize_connected_classes.py, visualize_enhanced_domain.py)
  - UML parsing scripts (parse_all_diagrams.py, parse_all_imagemaps.py)
  - Data fixing and debugging scripts (debug_extraction.py, fix_enhanced_ontology.py)
  - Pipeline scripts (run_crossref.py, run_enhanced_domain.py, validate_crossref.py)

For a full list of available scripts and commands, see the [scripts README](scripts/README.md).

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

### Setup and Running the Unified CLI

First, install the project with PDM:

```bash
pdm install
```

The project provides a unified CLI tool that consolidates all functionality into a hierarchical command structure:

```bash
pdm run oa <command> <subcommand> [options]
```

To see all available commands:

```bash
pdm run oa --help
```

The CLI automatically checks and runs any prerequisite commands needed. For example, if you run `visualize connected` without having run the necessary data processing steps first, the CLI will run them for you. You can disable this behavior with the `--no-deps` flag:

```bash
pdm run oa --no-deps <command> <subcommand>  # Skip running prerequisites
```

#### Main Command Groups

1. **Process Commands**: Process data from OpenAccess documentation
   ```bash
   pdm run oa process --help
   ```
   - `html`: Parse HTML documentation into YAML format
   - `build`: Build the software class ontology
   - `domain`: Extract domain concepts from class ontology
   - `export`: Export ontology to Neo4j-compatible format

2. **UML Commands**: Process UML diagrams and image maps
   ```bash
   pdm run oa uml --help
   ```
   - `diagram`: Process UML diagrams using computer vision
   - `imagemap`: Parse HTML image maps for UML information
   - `combine`: Combine multiple schema structures
   - `to-yaml`: Convert UML structure to YAML format

3. **Cross-Reference Commands**: Cross-reference and enhance ontology data
   ```bash
   pdm run oa crossref --help
   ```
   - `run`: Run the cross-referencing process
   - `validate`: Validate the cross-referenced data quality
   - `enhance`: Generate enhanced domain ontology from cross-referenced data
   - `fix`: Fix enhanced ontology structure for visualization

4. **Visualization Commands**: Create visualizations of the ontology
   ```bash
   pdm run oa visualize --help
   ```
   - `basic`: Generate basic visualizations of the ontology
   - `connected`: Create visualization of most connected classes without inheritance
   - `domain`: Create domain-specific visualizations
   - `graph`: Create simplified graph for visualization

#### Common Workflows

**Basic Ontology Creation:**
```bash
# Setup and process the basic ontology
pdm run oa process html
pdm run oa process build
pdm run oa process domain

# Or use the workflow command
pdm run run-all
```

**UML Extraction and Processing:**
```bash
# Process UML diagrams
pdm run oa uml diagram
pdm run oa uml imagemap
pdm run oa uml combine
```

**Cross-Referencing and Enhancement:**
```bash
# Cross-reference and enhance the ontology
pdm run oa crossref run
pdm run oa crossref validate
pdm run oa crossref enhance
pdm run oa crossref fix
```

**Create Visualizations:**
```bash
# Create various visualizations
pdm run oa visualize graph  # Create simplified visualization graph
pdm run oa visualize connected --limit 75  # Most connected classes without inheritance
pdm run oa visualize domain --domain Physical  # Domain-specific visualization

# Visualize specific domains by filtering
pdm run oa visualize connected --domain Connectivity  # Show Connectivity domain classes
pdm run oa visualize connected --domain Physical --limit 50  # Top 50 Physical domain classes
pdm run oa visualize connected --domain Hierarchy  # Show Hierarchy domain classes
```

#### Legacy Command Support

A small set of legacy commands are still available for backward compatibility and special purposes:

```bash
# Core workflow commands
pdm run setup    # Set up the environment
pdm run run-all  # Run the full extraction pipeline

# Visualization shortcuts
pdm run vis-connected  # Connected classes visualization
pdm run vis-enhanced   # Domain-specific visualization

# Testing and debugging
pdm run test-uml-parser      # Test the UML parser
pdm run test-structure-parser  # Test the structure parser
pdm run debug-extraction     # Debug HTML extraction issues
```

You can view all available commands with:

```bash
pdm run --list
```

For all other functionality, use the unified CLI with the `oa` command as described above.

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

2. **Cross-reference Data Quality Issues**

   The cross-reference validation may show issues with data quality. These are expected and won't prevent the system from working but indicate areas where the data extraction could be improved. Common issues include:
   
   - Missing descriptions (50% of classes)
   - Classes with no methods (about half)
   - Missing relationships from UML diagrams

## License

This project is for educational and research purposes only. The OpenAccess API documentation is owned by Cadence Design Systems.
