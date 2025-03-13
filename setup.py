#!/usr/bin/env python3
"""
Setup script for OpenAccess Ontology Explorer.

This script:
1. Clones the HTML documentation repository
2. Sets up the directory structure for processing
3. Creates a configuration file
"""

import os
import subprocess
import sys
import json
from pathlib import Path

# Constants
OA_HTML_REPO = "https://github.com/oa22doc/oa22doc.github.io"
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "html_dir": "html_source",
    "yaml_dir": "yaml_output",
    "ontology_dir": "ontology_output",
    "modules": ["design", "base", "tech", "cms", "wafer", "block"]
}

def check_requirements():
    """Check for required tools."""
    print("Checking requirements...")
    
    # Check Git
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ Git is installed")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("✗ Git is required but not found")
        sys.exit(1)
    
    # Check Python packages
    required_packages = ["networkx", "pyyaml", "tqdm"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"✗ Missing Python packages: {', '.join(missing_packages)}")
        print(f"  Please install them with: pip install {' '.join(missing_packages)}")
        sys.exit(1)
    else:
        print("✓ All required Python packages are installed")

def clone_documentation_repo():
    """Clone the OpenAccess HTML documentation repository."""
    html_dir = DEFAULT_CONFIG["html_dir"]
    
    if os.path.exists(html_dir):
        print(f"The directory '{html_dir}' already exists.")
        choice = input("Do you want to remove it and clone again? (y/n): ")
        if choice.lower() == 'y':
            subprocess.run(["rm", "-rf", html_dir], check=True)
        else:
            print(f"Using existing '{html_dir}' directory")
            return
    
    print(f"Cloning documentation from {OA_HTML_REPO}...")
    subprocess.run(["git", "clone", OA_HTML_REPO, html_dir], check=True)
    print(f"✓ Documentation cloned to '{html_dir}'")

def create_directory_structure():
    """Create the necessary directory structure."""
    print("Creating directory structure...")
    
    # Create output directories if they don't exist
    for dir_name in [DEFAULT_CONFIG["yaml_dir"], DEFAULT_CONFIG["ontology_dir"]]:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ Created directory: {dir_name}")
    
    # Create subdirectories for each module
    for module in DEFAULT_CONFIG["modules"]:
        yaml_module_dir = os.path.join(DEFAULT_CONFIG["yaml_dir"], module)
        os.makedirs(yaml_module_dir, exist_ok=True)
        print(f"✓ Created directory: {yaml_module_dir}")

def create_config_file():
    """Create a configuration file."""
    print(f"Creating configuration file: {CONFIG_FILE}")
    
    # Add HTML directories to config
    html_dir = DEFAULT_CONFIG["html_dir"]
    module_dirs = {}
    
    for module in DEFAULT_CONFIG["modules"]:
        module_path = os.path.join(html_dir, module)
        if os.path.exists(module_path) and os.path.isdir(module_path):
            module_dirs[module] = module_path
    
    config = {**DEFAULT_CONFIG, "module_dirs": module_dirs}
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration written to {CONFIG_FILE}")

def print_next_steps():
    """Print instructions for next steps."""
    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Run parse_html.py to convert HTML to YAML:")
    print("   python parse_html.py")
    print("\n2. Run build_ontology.py to extract the software ontology:")
    print("   python build_ontology.py")
    print("\n3. Run extract_domain_ontology.py to extract the domain ontology:")
    print("   python extract_domain_ontology.py")
    print("\nFor more information, see README.md")
    print("="*50)

def main():
    """Main function."""
    print("Setting up OpenAccess Ontology Explorer...")
    
    check_requirements()
    clone_documentation_repo()
    create_directory_structure()
    create_config_file()
    print_next_steps()

if __name__ == "__main__":
    main()