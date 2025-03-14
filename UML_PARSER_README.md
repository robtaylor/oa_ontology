# UML Schema Parser for OpenAccess Documentation

This tool attempts to extract class diagrams from UML schema images in the OpenAccess documentation and convert them to YAML format. The resulting YAML files can be integrated with the ontology for a more comprehensive understanding of the OpenAccess API.

## Installation

### Prerequisites

- Python 3.9 or higher
- Tesseract OCR installed on your system:
  - MacOS: `brew install tesseract`
  - Ubuntu: `apt-get install tesseract-ocr`
  - Windows: Download from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Install with PDM

```bash
# Install the package with UML parsing support
pdm install -G uml
```

## Usage

### Command-line Interface

Process a single schema diagram:

```bash
pdm run oa-schema --single html_source/schema/assignment.png
```

Process all schema diagrams in a directory:

```bash
pdm run oa-schema --schema_dir html_source/schema --output_dir yaml_output/schema
```

### Python API

```python
from oa_ontology.uml_parser import UMLParser

# Parse a single diagram
parser = UMLParser("html_source/schema/assignment.png")
uml_structure = parser.parse()

# Save to YAML
parser.save_as_yaml("output/assignment.yaml")
```

## Limitations

This is an experimental tool with several limitations:

1. **Accuracy**: OCR is not perfect, especially for complex diagrams with small text.
2. **Structure Recognition**: Identifying relationships between classes is challenging.
3. **Specialization**: The parser is tailored for OpenAccess UML diagrams and might not work well with other formats.

## Extending the Parser

To improve the parser, focus on these areas:

1. **Image Preprocessing**: Enhance contrast, remove noise, and correct orientation.
2. **Text Recognition**: Fine-tune OCR parameters or use deep learning models.
3. **Structure Detection**: Implement more sophisticated algorithms to identify boxes and connecting lines.

## Integration with Ontology

The parsed UML schemas can complement the API documentation by:

1. Providing visual representation of class relationships
2. Highlighting inheritance hierarchies
3. Clarifying the roles of different classes in the architecture

## Example Output

```yaml
classes:
  - name: oaAssignmentDef
    attributes:
      - assignmentName: oaString
      - defaultName: oaScalarName
    methods:
      - oaAssignmentDef()
      - oaAssignmentDef(assignmentName, defaultName)
      
  - name: oaAssignment
    attributes:
      - assignmentName: oaString
      - targetNet: oaNet
    methods:
      - create(block, name, net)
      - getNet()
      
relationships:
  - source: oaAssignmentDef
    target: oaAssignment
    type: uses
```

## Future Work

- Add support for extracting class attributes properly
- Improve relationship detection between classes
- Add validation against the API ontology 
- Generate GraphML visualizations of the parsed schemas