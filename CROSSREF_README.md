# Cross-Referencing UML and API Documentation

This directory contains tools to cross-reference UML diagrams with API documentation to create a more complete representation of the OpenAccess class structure.

## Overview

The cross-referencing system combines information from two sources:

1. **API Documentation**: Extracted from HTML files in the OpenAccess documentation
2. **UML Diagrams**: Extracted from image maps in the OpenAccess documentation

By combining these sources, we can create a more complete representation of the OpenAccess class structure, including:

- Class descriptions from API documentation
- Methods from both API and UML sources
- Attributes inferred from getter/setter methods
- Relationships extracted from UML diagrams

## Usage

### Running the Cross-Referencing Process

To run the cross-referencing process, use the following command:

```bash
python run_crossref.py
```

This will process all classes and save the results in `ontology_output/crossref/`.

Options:
- `--debug`: Enable debug output
- `--class CLASS`: Process only a specific class
- `--yaml-dir DIR`: Directory containing YAML parsed files (default: yaml_output)
- `--uml-dir DIR`: Directory containing UML schema files (default: yaml_output/schema)
- `--output-dir DIR`: Output directory for cross-referenced data (default: ontology_output/crossref)

Example to process a single class:

```bash
python run_crossref.py --class oaBusTerm --debug
```

### Validating the Cross-Referenced Data

To validate the cross-referenced data, use the following command:

```bash
python validate_crossref.py
```

This will validate all cross-referenced files and report any issues.

Options:
- `--detailed`: Show detailed validation issues
- `--class CLASS`: Validate only a specific class
- `--dir DIR`: Directory containing cross-referenced JSON files (default: ontology_output/crossref)

Example to validate a single class with detailed output:

```bash
python validate_crossref.py --class oaBusTerm --detailed
```

## Files

- `run_crossref.py`: Script to run the cross-referencing process
- `validate_crossref.py`: Script to validate the cross-referenced data
- `oa_ontology/crossref_api_uml.py`: Module containing the cross-referencing logic

## Output Format

The cross-referenced data is saved as JSON files in the output directory, with one file per class. The JSON structure includes:

- `name`: Class name
- `description`: Class description from API documentation
- `module`: Module containing the class (design, base, tech, etc.)
- `inheritance`: List of parent classes
- `methods`: List of methods with signatures, return types, and descriptions
- `attributes`: List of attributes (properties) inferred from methods
- `relationships`: List of relationships with other classes
- `enumerations`: Map of enumeration types and values
- `sources`: Information about where the data came from (API, UML)

## Known Issues

- Many classes are missing descriptions, especially those without API documentation
- Method return types are sometimes missing or incorrect
- Relationship information is only available for classes in UML diagrams
- Some class descriptions contain HTML markup or other artifacts

## Next Steps

1. Fix method extraction to properly handle return types
2. Enhance attribute extraction from UML diagrams
3. Generate more UML relationships from API documentation
4. Improve description extraction to remove HTML artifacts
5. Add support for extracting property types from API documentation

## License

Same as the main project.