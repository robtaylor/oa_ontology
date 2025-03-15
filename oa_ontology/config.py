#!/usr/bin/env python3
"""
Configuration module for the OpenAccess Ontology Explorer.

This module provides sensible defaults for all configuration settings,
eliminating the need for a separate config.json file.
"""

from pathlib import Path

# Directory structure
YAML_DIR = Path("yaml_output")
OUTPUT_DIR = Path("ontology_output")
UML_DIR = Path("yaml_output/schema")
ONTOLOGY_DIR = Path("ontology_output")
ENHANCED_DIR = Path("outputs")
CROSSREF_DIR = Path("ontology_output/crossref")
VISUALIZATION_DIR = Path("ontology_output/visualizations")

# Debug settings
DEBUG = False

# Default output files
DESIGN_ONTOLOGY_FILE = ONTOLOGY_DIR / "design_ontology.json"
DOMAIN_ONTOLOGY_FILE = ONTOLOGY_DIR / "domain_ontology.json"
DOMAIN_REPORT_FILE = ONTOLOGY_DIR / "domain_ontology_report.md"
ENHANCED_DOMAIN_FILE = ENHANCED_DIR / "enhanced_domain_ontology.json"
ENHANCED_DOMAIN_FIXED_FILE = ENHANCED_DIR / "enhanced_domain_ontology_fixed.json"
VISUALIZATION_GRAPH_FILE = ENHANCED_DIR / "visualization_graph.json"
NEO4J_EXPORT_FILE = ONTOLOGY_DIR / "neo4j_import.cypher"

# Module directories
DESIGN_MODULE_DIR = YAML_DIR / "design"
BASE_MODULE_DIR = YAML_DIR / "base"
TECH_MODULE_DIR = YAML_DIR / "tech"
CMS_MODULE_DIR = YAML_DIR / "cms"
WAFER_MODULE_DIR = YAML_DIR / "wafer"
BLOCK_MODULE_DIR = YAML_DIR / "block"

# Default HTML source directory
HTML_DIR = Path("html_source")

# Required directories that must exist
REQUIRED_DIRECTORIES = [
    YAML_DIR,
    UML_DIR, 
    YAML_DIR / "ontology",
    OUTPUT_DIR,
    CROSSREF_DIR,
    ENHANCED_DIR,
    VISUALIZATION_DIR,
    # Module directories
    DESIGN_MODULE_DIR,
    BASE_MODULE_DIR,
    TECH_MODULE_DIR,
    CMS_MODULE_DIR,
    WAFER_MODULE_DIR,
    BLOCK_MODULE_DIR
]

def load_config(config_file="config.json"):
    """
    Load configuration from config.json if it exists, otherwise use defaults.
    This function is provided for backward compatibility.
    
    Returns:
        dict: Configuration values with defaults filled in
    """
    import json
    import os
    
    # Start with default config
    config = {
        "yaml_dir": str(YAML_DIR),
        "output_dir": str(OUTPUT_DIR),
        "ontology_dir": str(ONTOLOGY_DIR),
        "uml_dir": str(UML_DIR),
        "debug": DEBUG
    }
    
    # Try to load from config.json for backward compatibility
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                # Update defaults with loaded values
                config.update(loaded_config)
        except Exception as e:
            print(f"Warning: Error loading {config_file}: {str(e)}")
            print(f"Using default configuration")
    
    return config

def create_directories():
    """Create all required directories if they don't exist."""
    for directory in REQUIRED_DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)

def get_config_as_dict():
    """
    Get all configuration as a dictionary.
    Useful for passing to template engines or serializing.
    """
    return {
        "yaml_dir": str(YAML_DIR),
        "output_dir": str(OUTPUT_DIR),
        "ontology_dir": str(ONTOLOGY_DIR),
        "uml_dir": str(UML_DIR),
        "enhanced_dir": str(ENHANCED_DIR),
        "crossref_dir": str(CROSSREF_DIR),
        "visualization_dir": str(VISUALIZATION_DIR),
        "design_ontology_file": str(DESIGN_ONTOLOGY_FILE),
        "domain_ontology_file": str(DOMAIN_ONTOLOGY_FILE),
        "domain_report_file": str(DOMAIN_REPORT_FILE),
        "enhanced_domain_file": str(ENHANCED_DOMAIN_FILE),
        "enhanced_domain_fixed_file": str(ENHANCED_DOMAIN_FIXED_FILE),
        "visualization_graph_file": str(VISUALIZATION_GRAPH_FILE),
        "neo4j_export_file": str(NEO4J_EXPORT_FILE),
        "debug": DEBUG
    }
    
# If this module is run directly, create the required directories
if __name__ == "__main__":
    create_directories()
    print("Configuration directories created:")
    for directory in REQUIRED_DIRECTORIES:
        print(f"- {directory}")