# UML Diagram Parser

This module provides tools for parsing UML diagrams from images and HTML image maps, and converting them to structured data formats (JSON and YAML) that can be used by the ontology.

## Overview

The UML diagram parser now offers two complementary approaches to extract structural information from UML class diagrams:

1. **HTML Image Map Parser**: Extracts UML class information from HTML image maps in the OpenAccess documentation, providing exact coordinates and links for each UML element.

2. **Computer Vision Parser**: Uses image processing techniques to detect class boxes, relationships, and other structural elements directly from diagram images.

Both parsers extract:
- Class boxes and their positions
- Relationships between classes
- Horizontal divider lines within classes (CV parser only)
- Links to documentation pages (Image Map parser only)

The parsers do not currently perform OCR for text extraction, focusing instead on the structural elements of the diagrams.

## Usage

### Prerequisites

Install the required dependencies:

```bash
pdm install 
```

For UML parsing, you'll need additional dependencies:

```bash
pdm install -G dev
```

### Approach 1: HTML Image Map Parser (Recommended)

#### Parsing a Single HTML Image Map

```bash
python oa_ontology/html_imagemap_parser.py html_source/schema/assignment.html
```

#### Parsing Multiple HTML Image Maps

```bash
python parse_all_imagemaps.py --specific assignment,term
```

Options:
- `--no-debug`: Disable generation of debug information
- `--pattern`: Glob pattern to find HTML files (default: html_source/schema/*.html)
- `--specific`: Process only specific HTML files (comma-separated list without .html extension)

### Approach 2: Computer Vision Parser (Alternative)

#### Parsing a Single Diagram with CV

```bash
python test_improved_parser.py
```

This will parse the `assignment.png` and `term.png` diagrams and save the results to `yaml_output/schema/`.

#### Parsing Multiple Diagrams with CV

```bash
python parse_all_diagrams.py --pattern "html_source/schema/*.png"
```

Options:
- `--output-dir`: Output directory for structure JSON files (default: yaml_output/schema)
- `--no-debug`: Disable generation of debug images
- `--pattern`: Glob pattern to find UML diagrams (default: html_source/schema/*.png)

### Converting to YAML

```bash
python oa_ontology/structure_to_yaml.py
```

Options:
- `--json-dir`: Directory containing JSON structure files (default: yaml_output/schema)
- `--yaml-dir`: Output directory for YAML files (default: yaml_output/ontology)
- `--pattern`: Glob pattern to find JSON structure files (default: *_structure.json)

### Combining Multiple Structures

```bash
python oa_ontology/combine_schema_structures.py
```

Options:
- `--input-dir`: Directory containing structure files (default: yaml_output/schema)
- `--output`: Output file path (default: yaml_output/ontology/combined_schema.json)
- `--pattern`: Glob pattern to find structure files (default: *_imagemap.json)

## How It Works

The UML diagram parser uses computer vision techniques to extract structural information:

1. **Preprocessing**: The parser first preprocesses the image to enhance edges and reduce noise
2. **Box Detection**: It then identifies rectangular class boxes using contour detection
3. **Line Detection**: Horizontal divider lines within classes are detected using morphological operations
4. **Relationship Detection**: Connections between classes are found using line detection

For diagrams where automatic detection is challenging, the parser can fall back to predefined grids and known relationships based on the diagram type.

## Debug Images

The parser generates debug images at each step of the process to help understand and improve the parsing:

1. **1_white_background.png**: Image with a white background to improve processing
2. **2_gray.png**: Grayscale conversion of the input image
3. **3_blurred.png**: After Gaussian blurring to reduce noise
4. **4_binary.png**: Binary image from adaptive thresholding
5. **5_cleaned.png**: After morphological operations to clean up the binary image
6. **6_edges.png**: Results of Canny edge detection
7. **7_dilated_edges.png**: After dilation to connect nearby edges
8. **8_all_contours.png**: All detected contours in the image
9. **9_potential_boxes.png**: Potential class boxes identified by contour analysis
10. **10_hough_lines.png**: Lines detected using Hough transform (if alternative method used)
11. **11_grid_boxes.png**: Boxes detected using grid-based approach (if used)
12. **12_horizontal_lines_morph.png**: Morphological operations to detect horizontal lines
13. **13_horizontal_lines.png**: Detected horizontal divider lines
14. **14_all_detected_lines.png**: All lines detected for potential relationships
15. **15_relationships.png**: Detected relationships between classes
16. **16_known_relationships.png**: Known relationships based on diagram type (if used)
17. **17_complete_structure.png**: Complete structural analysis with all elements

## Output Format

### JSON Structure

The parser outputs a JSON file with the following structure:

```json
{
  "diagram_name": "term",
  "boxes": [
    {
      "id": 0,
      "x": 295,
      "y": 90,
      "width": 170,
      "height": 180,
      "center_x": 380,
      "center_y": 180,
      "area": 30600,
      "detection_method": "grid"
    },
    ...
  ],
  "horizontal_lines": [
    {
      "id": 0,
      "box_id": 0,
      "x": 300,
      "y": 147,
      "width": 145,
      "height": 2,
      "rel_y": 57
    },
    ...
  ],
  "relationships": [
    {
      "source_box_id": 0,
      "target_box_id": 1,
      "source_point": [361, 235],
      "target_point": [362, 343],
      "angle": 89.46,
      "type": "association"
    },
    ...
  ],
  "box_names": {
    "0": "oaTerm",
    "1": "oaInstTerm",
    "2": "oaBlockTerm",
    "3": "oaITerm"
  }
}
```

### YAML Format

The JSON structure is converted to a YAML format suitable for integration with the ontology:

```yaml
diagram: term
classes:
  oaTerm:
    id: '0'
    position:
      x: 295
      y: 90
      width: 170
      height: 180
    methods: []
    attributes: []
  ...
relationships:
- source: oaTerm
  target: oaBlockTerm
  type: association
- ...
```

## Future Improvements

- OCR integration to extract class names, attributes, and methods from the diagrams
- Improved relationship detection for complex diagrams
- Support for different types of UML relationships (inheritance, composition, etc.)
- Better handling of diagram styles and variations
- Integration with extracted method information from HTML documentation