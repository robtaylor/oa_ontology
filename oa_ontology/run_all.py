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
import subprocess
from pathlib import Path

def run_script(module_path, description):
    """Run a Python module and check its return code."""
    print(f"\n{'='*60}")
    print(f"Running: {module_path} - {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run([sys.executable, "-m", module_path], capture_output=False)
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"\n✓ {module_path} completed successfully in {elapsed:.1f} seconds")
        return True
    else:
        print(f"\n✗ {module_path} failed with return code {result.returncode}")
        return False

def main():
    """Run all scripts in sequence."""
    modules = [
        ("oa_ontology.init", "Setup environment and download documentation"),
        ("oa_ontology.parse_html", "Parse HTML documentation into YAML"),
        ("oa_ontology.build_ontology", "Extract software ontology"),
        ("oa_ontology.extract_domain_ontology", "Extract domain ontology"),
        ("oa_ontology.visualize_ontology", "Generate visualizations and reports"),
        ("oa_ontology.export_to_neo4j", "Export to Neo4j and GraphML formats")
    ]
    
    print("OpenAccess Ontology Explorer - Running All Scripts")
    print("="*60)
    
    start_time = time.time()
    success_count = 0
    
    for module, description in modules:
        if run_script(module, description):
            success_count += 1
        else:
            print(f"\nExecution stopped due to failure in {module}")
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
            import json
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