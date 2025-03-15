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
        ("oa_ontology.crossref_api_uml", "Cross-reference UML diagrams with API documentation"),
        ("oa_ontology.enhanced_domain_ontology", "Extract enhanced domain ontology"),
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
        # Import configuration for output paths
        from oa_ontology.config import (
            ONTOLOGY_DIR, ENHANCED_DIR, 
            DESIGN_ONTOLOGY_FILE, DOMAIN_ONTOLOGY_FILE, DOMAIN_REPORT_FILE,
            ENHANCED_DOMAIN_FILE, ENHANCED_DOMAIN_FIXED_FILE
        )
        
        print(f"\nResults can be found in the {ONTOLOGY_DIR} directory:")
        print(f"- Software ontology: {DESIGN_ONTOLOGY_FILE}")
        print(f"- Domain ontology: {DOMAIN_ONTOLOGY_FILE}")
        print(f"- Domain report: {DOMAIN_REPORT_FILE}")
        
        # Check for enhanced domain ontology
        if ENHANCED_DIR.exists():
            enhanced_domain = ENHANCED_DOMAIN_FILE
            enhanced_report = ENHANCED_DIR / "enhanced_domain_ontology_report.md"
            if enhanced_domain.exists():
                print(f"- Enhanced domain ontology: {enhanced_domain}")
            if enhanced_report.exists():
                print(f"- Enhanced domain report: {enhanced_report}")
        
        # Check for visualization report
        viz_report = ONTOLOGY_DIR / "visualizations" / "ontology_report.html"
        if viz_report.exists():
            print(f"- Visualization report: {viz_report}")

if __name__ == "__main__":
    main()