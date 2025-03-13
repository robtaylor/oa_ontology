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

def run_script(script_name, description):
    """Run a Python script and check its return code."""
    print(f"\n{'='*60}")
    print(f"Running: {script_name} - {description}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    elapsed = time.time() - start_time
    
    if result.returncode == 0:
        print(f"\n✓ {script_name} completed successfully in {elapsed:.1f} seconds")
        return True
    else:
        print(f"\n✗ {script_name} failed with return code {result.returncode}")
        return False

def main():
    """Run all scripts in sequence."""
    scripts = [
        ("setup.py", "Setup environment and download documentation"),
        ("parse_html.py", "Parse HTML documentation into YAML"),
        ("build_ontology.py", "Extract software ontology"),
        ("extract_domain_ontology.py", "Extract domain ontology"),
        ("visualize_ontology.py", "Generate visualizations and reports"),
        ("export_to_neo4j.py", "Export to Neo4j and GraphML formats")
    ]
    
    print("OpenAccess Ontology Explorer - Running All Scripts")
    print("="*60)
    
    start_time = time.time()
    success_count = 0
    
    for script, description in scripts:
        if run_script(script, description):
            success_count += 1
        else:
            print(f"\nExecution stopped due to failure in {script}")
            break
    
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print(f"Process completed: {success_count}/{len(scripts)} scripts successful")
    print(f"Total time: {total_time:.1f} seconds")
    print("="*60)
    
    # Check if we completed successfully
    if success_count == len(scripts):
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