#!/usr/bin/env python3
"""
Dependencies module for the CLI commands.

This module defines the dependencies between commands and provides functions
to check and run prerequisite commands as needed.
"""

import os
import subprocess
import sys
from pathlib import Path
from oa_ontology.config import create_directories, REQUIRED_DIRECTORIES

# Define the command dependencies
# Format: {(command, subcommand): [(prerequisite_command, prerequisite_subcommand), ...]}
COMMAND_DEPENDENCIES = {
    # Process command dependencies
    ('process', 'build'): [('process', 'html')],
    ('process', 'domain'): [('process', 'build')],
    ('process', 'export'): [('process', 'build')],
    
    # UML command dependencies
    ('uml', 'combine'): [('uml', 'diagram'), ('uml', 'imagemap')],
    ('uml', 'to-yaml'): [('uml', 'diagram')],
    
    # Crossref command dependencies
    ('crossref', 'run'): [('process', 'html'), ('uml', 'diagram'), ('uml', 'imagemap')],
    ('crossref', 'validate'): [('crossref', 'run')],
    ('crossref', 'enhance'): [('process', 'domain'), ('crossref', 'run')],
    ('crossref', 'fix'): [('crossref', 'enhance')],
    
    # Visualize command dependencies
    ('visualize', 'basic'): [('process', 'build')],
    ('visualize', 'connected'): [('visualize', 'graph')],
    ('visualize', 'domain'): [('crossref', 'enhance')],
    ('visualize', 'graph'): [('crossref', 'enhance')],
}

# Define a mapping of output files for each command
# This helps us check if a command has been run successfully before
COMMAND_OUTPUT_FILES = {
    ('process', 'html'): ['yaml_output/design/classoaDesignObject.yaml'],
    ('process', 'build'): ['ontology_output/design_ontology.json'],
    ('process', 'domain'): ['ontology_output/domain_ontology.json'],
    ('process', 'export'): ['ontology_output/neo4j_import.cypher'],
    
    ('uml', 'diagram'): ['yaml_output/schema/design_structure.json'],
    ('uml', 'imagemap'): ['yaml_output/schema/design_imagemap.json'],
    ('uml', 'combine'): ['yaml_output/ontology/combined_schema.json'],
    ('uml', 'to-yaml'): ['yaml_output/ontology/design.yaml'],
    
    ('crossref', 'run'): ['ontology_output/crossref/oaDesignObject.json'],
    ('crossref', 'validate'): ['ontology_output/crossref/validation_report.md'],
    ('crossref', 'enhance'): ['outputs/enhanced_domain_ontology.json'],
    ('crossref', 'fix'): ['outputs/enhanced_domain_ontology_fixed.json'],
    
    ('visualize', 'basic'): ['ontology_output/visualizations/ontology_report.html'],
    ('visualize', 'connected'): ['outputs/connected_classes_visualization.html'],
    ('visualize', 'domain'): ['outputs/enhanced_domain_visualization.html'],
    ('visualize', 'graph'): ['outputs/visualization_graph.json'],
}

def get_command_description(command, subcommand):
    """Get a human-readable description of a command."""
    descriptions = {
        ('process', 'html'): "Parse HTML documentation into YAML",
        ('process', 'build'): "Build the software class ontology",
        ('process', 'domain'): "Extract domain concepts from class ontology",
        ('process', 'export'): "Export ontology to Neo4j-compatible format",
        
        ('uml', 'diagram'): "Process UML diagrams using computer vision",
        ('uml', 'imagemap'): "Parse HTML image maps for UML information",
        ('uml', 'combine'): "Combine multiple schema structures",
        ('uml', 'to-yaml'): "Convert UML structure to YAML format",
        
        ('crossref', 'run'): "Run the cross-referencing process",
        ('crossref', 'validate'): "Validate the cross-referenced data quality",
        ('crossref', 'enhance'): "Generate enhanced domain ontology from cross-referenced data",
        ('crossref', 'fix'): "Fix enhanced ontology structure for visualization",
        
        ('visualize', 'basic'): "Generate basic visualizations of the ontology",
        ('visualize', 'connected'): "Create visualization of most connected classes without inheritance",
        ('visualize', 'domain'): "Create domain-specific visualizations",
        ('visualize', 'graph'): "Create simplified graph for visualization",
    }
    return descriptions.get((command, subcommand), f"Run {command} {subcommand}")

def check_command_output(command, subcommand):
    """Check if the output files for a command exist."""
    if (command, subcommand) not in COMMAND_OUTPUT_FILES:
        return False  # If we don't know the output files, assume it hasn't been run
    
    output_files = COMMAND_OUTPUT_FILES[(command, subcommand)]
    result = all(os.path.exists(file) for file in output_files)
    if not result:
        missing_files = [file for file in output_files if not os.path.exists(file)]
        print(f"⚠️  Missing output files for {command} {subcommand}: {', '.join(missing_files)}")
    return result

def run_command(command, subcommand, verbose=False):
    """Run a command using the CLI."""
    print(f"Running prerequisite: {command} {subcommand} - {get_command_description(command, subcommand)}")
    
    # Use pdm run oa command structure for execution
    cmd = ["pdm", "run", "oa", command, subcommand]
    if verbose:
        cmd.append("--verbose")
    
    # Add --no-deps to prevent recursive dependency checking
    cmd.append("--no-deps")
    
    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=not verbose)
    if result.returncode != 0:
        print(f"❌ Error running {command} {subcommand}. Exit code: {result.returncode}")
        if not verbose and result.stderr:
            print(f"Error output: {result.stderr.decode('utf-8')}")
        return False
    
    # Verify that the command produced the expected output files
    if not check_command_output(command, subcommand):
        print(f"⚠️ Command {command} {subcommand} completed but didn't produce all expected output files.")
        return False
        
    return True

def ensure_prerequisites(command, subcommand, verbose=False, visit_history=None):
    """
    Recursively ensure all prerequisite commands have been run.
    
    Args:
        command: The main command (e.g., 'process', 'uml')
        subcommand: The specific subcommand (e.g., 'build', 'diagram')
        verbose: Whether to show verbose output
        visit_history: Track visited commands to prevent cycles
        
    Returns:
        bool: True if all prerequisites are satisfied, False otherwise
    """
    # Always ensure directories exist before checking prerequisites
    check_directories()
    
    # Initialize visit history on first call
    if visit_history is None:
        visit_history = set()
    
    # Check for circular dependencies
    command_key = (command, subcommand)
    if command_key in visit_history:
        print(f"❌ Circular dependency detected for {command} {subcommand}")
        return False
    
    # Add current command to visit history
    visit_history.add(command_key)
    
    # Check if this command has any prerequisites
    prerequisites = COMMAND_DEPENDENCIES.get(command_key, [])
    if not prerequisites:
        return True  # No prerequisites, we're good to go
    
    # First check if the command output already exists
    # If it does, we can skip checking prerequisites
    if check_command_output(command, subcommand):
        if verbose:
            print(f"✓ Command {command} {subcommand} output already exists")
        return True
    
    # Check each prerequisite
    for prereq_cmd, prereq_subcmd in prerequisites:
        prereq_key = (prereq_cmd, prereq_subcmd)
        
        # Check if prerequisite has already been completed
        if check_command_output(prereq_cmd, prereq_subcmd):
            if verbose:
                print(f"✓ Prerequisite {prereq_cmd} {prereq_subcmd} already completed")
            continue
            
        # Recursively ensure prereq's prerequisites
        if not ensure_prerequisites(prereq_cmd, prereq_subcmd, verbose, visit_history):
            return False
            
        # Run the prerequisite command
        if not run_command(prereq_cmd, prereq_subcmd, verbose):
            return False
    
    return True

def check_directories():
    """Ensure all required directories exist."""
    # Use the create_directories function from the config module
    create_directories()

if __name__ == "__main__":
    # Simple self-test
    check_directories()
    
    # Test the prerequisite checking for a few commands
    for cmd, subcmd in [
        ('process', 'build'),
        ('visualize', 'connected'),
        ('crossref', 'enhance')
    ]:
        print(f"\nTesting prerequisites for {cmd} {subcmd}:")
        deps = COMMAND_DEPENDENCIES.get((cmd, subcmd), [])
        print(f"  Direct dependencies: {deps}")
        all_deps = set()
        for dep_cmd, dep_subcmd in deps:
            ensure_prerequisites(dep_cmd, dep_subcmd, verbose=True)
            all_deps.add((dep_cmd, dep_subcmd))
        print(f"  All dependencies: {all_deps}")