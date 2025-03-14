# OpenAccess Ontology Utility Scripts

This directory contains utility scripts for working with the OpenAccess ontology. These scripts use the core functionality in the `oa_ontology` package and are registered as PDM entry points for easy access.

## Visualization Scripts

- **Connected Classes Visualization**
  - Script: `visualize_connected_classes.py`
  - Command: `pdm run vis-connected`
  - Description: Creates an interactive visualization of the most connected classes without inheritance relationships
  - Options: `--limit` (number of nodes), `--domain` (filter by domain)

- **Enhanced Domain Visualization**
  - Script: `visualize_enhanced_domain.py`
  - Command: `pdm run vis-enhanced`
  - Description: Creates domain-specific visualizations of the ontology
  - Options: `--input`, `--output`, `--domain`, `--limit`

## UML Parser Scripts

- **Parse All Diagrams**
  - Script: `parse_all_diagrams.py`
  - Command: `pdm run parse-uml`
  - Description: Batch processor for parsing multiple UML diagrams using computer vision
  - Options: `--pattern`, `--output-dir`, `--no-debug`

- **Parse All Imagemaps**
  - Script: `parse_all_imagemaps.py`
  - Command: `pdm run parse-imagemap`
  - Description: Batch processor for parsing multiple HTML image maps
  - Options: `--pattern`, `--specific`, `--no-debug`

- **Test UML Parser**
  - Script: `test_improved_parser.py`
  - Command: `pdm run test-uml-parser`
  - Description: Test script for the improved UML parser

- **Test Structure Parser**
  - Script: `test_structure_parser.py`
  - Command: `pdm run test-structure-parser`
  - Description: Test script for the UML structure parser

## Data Fixing and Debugging Scripts

- **Debug Extraction**
  - Script: `debug_extraction.py`
  - Command: `pdm run debug-extraction`
  - Description: Diagnostic tool for troubleshooting HTML parsing issues
  - Usage: `pdm run debug-extraction <class_name>`

- **Fix Enhanced Ontology**
  - Script: `fix_enhanced_ontology.py`
  - Command: `pdm run fix-enhanced`
  - Description: Restructures ontology data for visualization

- **Fix BundleTerm Class**
  - Script: `fix_bundle_term.py`
  - Command: `pdm run fix-bundleterm`
  - Description: Fixes specific issues with oaBundleTerm class description

- **Process BusTerm Class**
  - Script: `process_busterm.py`
  - Command: `pdm run process-busterm`
  - Description: Extracts and verifies oaBusTerm class information

## Pipeline Scripts

- **Run Cross-Reference**
  - Script: `run_crossref.py`
  - Command: `pdm run crossref`
  - Description: Runs the cross-referencing between UML and API docs

- **Validate Cross-Reference**
  - Script: `validate_crossref.py`
  - Command: `pdm run validate-crossref`
  - Description: Validates the cross-referenced data

- **Generate Enhanced Domain Ontology**
  - Script: `run_enhanced_domain.py`
  - Command: `pdm run enhanced-domain`
  - Description: Generates the enhanced domain ontology

## Usage

All scripts are registered as PDM commands and can be run using:

```bash
pdm run <command>
```

For example:

```bash
pdm run vis-connected --limit 75
```

You can see a list of all available commands with:

```bash
pdm run --list
```

Many scripts include help text that can be accessed with:

```bash
pdm run <command> --help
```

Alternatively, you can run the scripts directly with:

```bash
pdm run python -m scripts.<script_name_without_extension>
```