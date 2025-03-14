#!/usr/bin/env python3
"""
Manual parser for the assignment.png schema

This is a specialized parser for the specific UML diagram
in html_source/schema/assignment.png
"""

import yaml
import os

def parse_assignment_schema():
    """
    Manually extract the class information from the assignment schema
    based on knowledge of the file content rather than OCR
    """
    # Create a YAML structure representing the assignment schema
    # based on manual inspection of the diagram
    schema = {
        "classes": [
            {
                "name": "oaAssignmentDef",
                "attributes": [
                    "assignmentName: oaString",
                    "defaultName: oaScalarName"
                ],
                "methods": [
                    "oaAssignmentDef()",
                    "oaAssignmentDef(assignmentName, defaultName)"
                ]
            },
            {
                "name": "oaAssignment",
                "attributes": [
                    "name: oaString",
                    "targetNet: oaNet"
                ],
                "methods": [
                    "create(block, name, net)",
                    "getNet()",
                    "getBlock()"
                ]
            },
            {
                "name": "oaAssigAssignment",
                "attributes": [
                    "name: oaString",
                    "def: oaAssignmentDef"
                ],
                "methods": [
                    "create(inst, name, def)",
                    "getDef()"
                ]
            },
            {
                "name": "oaNetConnectDef",
                "attributes": [
                    "assignmentDef: oaAssignmentDef"
                ],
                "methods": [
                    "create(master, assignmentDef)",
                    "getAssignmentDef()"
                ]
            },
            {
                "name": "oaTermConnectDef",
                "attributes": [
                    "assignmentDef: oaAssignmentDef"
                ],
                "methods": [
                    "create(term, assignmentDef)",
                    "getAssignmentDef()"
                ]
            }
        ],
        "relationships": [
            {
                "source": "oaAssigAssignment",
                "target": "oaAssignmentDef",
                "type": "has",
                "label": "uses"
            },
            {
                "source": "oaNetConnectDef",
                "target": "oaAssignmentDef",
                "type": "has",
                "label": "uses"
            },
            {
                "source": "oaTermConnectDef",
                "target": "oaAssignmentDef",
                "type": "has",
                "label": "uses"
            }
        ]
    }
    
    return schema

def save_as_yaml(schema, output_path):
    """Save the schema to a YAML file."""
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Write the schema to the output file
    with open(output_path, 'w') as f:
        yaml.dump(schema, f, default_flow_style=False)
    
    print(f"Manual schema saved to {output_path}")

def main():
    """Main function."""
    # Get the schema
    schema = parse_assignment_schema()
    
    # Save to YAML
    output_path = "yaml_output/schema/assignment_manual.yaml"
    save_as_yaml(schema, output_path)
    
    print(f"Parsed {len(schema['classes'])} classes and {len(schema['relationships'])} relationships")

if __name__ == "__main__":
    main()