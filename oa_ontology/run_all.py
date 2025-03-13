#!/usr/bin/env python3
"""
Run all OpenAccess Ontology Explorer scripts in sequence.

This script:
1. Sets up the environment and downloads documentation
2. Parses HTML into YAML
3. Extracts software ontology
4. Extracts domain ontology
5. Generates visualizations and reports
6. Exports to Neo4j and GraphML formats
"""

import os
import sys
import time
from pathlib import Path
import importlib
import json

def run_module(module_name, description):
    """Run a Python module and check if it completes successfully."""
    print(f"\n{'='*60}")
    print(f"Running: {module_name} - {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Import the module
        module = importlib.import_module(f"oa_ontology.{module_name}")
        
        # Run the main function
        module.main()
        
        elapsed = time.time() - start_time
        print(f"\n✓ {module_name} completed successfully in {elapsed:.1f} seconds")
        return True
    except Exception as e:
        print(f"\n✗ {module_name} failed with error: {str(e)}")
        return False

def main():
    """Run all modules in sequence."""
    modules = [
        ("init", "Setup environment and download documentation"),
        ("parse_html", "Parse HTML documentation into YAML"),
        ("build_ontology", "Extract software ontology"),
        ("extract_domain_ontology", "Extract domain ontology"),
        ("visualize_ontology", "Generate visualizations and reports"),
        ("export_to_neo4j", "Export to Neo4j and GraphML formats")
    ]
    
    print("OpenAccess Ontology Explorer - Running All Modules")
    print("="*60)
    
    start_time = time.time()
    success_count = 0
    
    for module_name, description in modules:
        if run_module(module_name, description):
            success_count += 1
        else:
            print(f"\nExecution stopped due to failure in {module_name}")
            break
    
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print(f"Process completed: {success_count}/{len(modules)} modules successful")
    print(f"Total time: {total_time:.1f} seconds")
    print("="*60)
    
    # Check if we completed successfully
    if success_count == len(modules):
        config_file = Path("config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            ontology_dir = config.get("ontology_dir", "ontology_output")
            print(f"\nResults can be found in the {ontology_dir} directory:")
            print(f"- Software ontology: {ontology_dir}/design_ontology.json")
            print(f"- Domain ontology: {ontology_dir}/domain_ontology.json")
            print(f"- Domain report: {ontology_dir}/domain_ontology_report.md")
            
            # Check for visualization report
            viz_report = Path(ontology_dir) / "visualizations" / "ontology_report.html"
            if viz_report.exists():
                print(f"- Visualization report: {viz_report}")

if __name__ == "__main__":
    main()