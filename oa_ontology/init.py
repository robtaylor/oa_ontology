#!/usr/bin/env python3
"""
Initialization script for OpenAccess Ontology Explorer.

This script:
1. Clones the HTML documentation repository
2. Sets up the directory structure for processing
3. Creates the necessary configuration
"""

import os
import subprocess
import sys
import json
import tomli
from pathlib import Path

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

def get_config():
    """Get configuration from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    if not pyproject_path.exists():
        print("✗ Could not find pyproject.toml")
        sys.exit(1)
    
    with open(pyproject_path, "rb") as f:
        pyproject = tomli.load(f)
    
    # Get settings from pyproject.toml
    config = pyproject.get("tool", {}).get("oa-ontology", {})
    
    # Set defaults if not provided
    if not config:
        config = {
            "html_repo": "https://github.com/oa22doc/oa22doc.github.io",
            "modules": ["design", "base", "tech", "cms", "wafer", "block"],
            "default_directories": {
                "html_dir": "html_source",
                "yaml_dir": "yaml_output",
                "ontology_dir": "ontology_output"
            }
        }
    
    # Ensure default_directories are set
    if "default_directories" not in config:
        config["default_directories"] = {
            "html_dir": "html_source",
            "yaml_dir": "yaml_output",
            "ontology_dir": "ontology_output"
        }
    
    return config

def clone_documentation_repo(html_repo, html_dir):
    """Clone the OpenAccess HTML documentation repository."""
    if os.path.exists(html_dir):
        print(f"The directory '{html_dir}' already exists.")
        choice = input("Do you want to remove it and clone again? (y/n): ")
        if choice.lower() == 'y':
            subprocess.run(["rm", "-rf", html_dir], check=True)
        else:
            print(f"Using existing '{html_dir}' directory")
            return
    
    print(f"Cloning documentation from {html_repo}...")
    subprocess.run(["git", "clone", html_repo, html_dir], check=True)
    print(f"✓ Documentation cloned to '{html_dir}'")

def create_directory_structure(directories, modules):
    """Create the necessary directory structure."""
    print("Creating directory structure...")
    
    # Create output directories if they don't exist
    for dir_name in [directories["yaml_dir"], directories["ontology_dir"]]:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ Created directory: {dir_name}")
    
    # Create subdirectories for each module
    for module in modules:
        yaml_module_dir = os.path.join(directories["yaml_dir"], module)
        os.makedirs(yaml_module_dir, exist_ok=True)
        print(f"✓ Created directory: {yaml_module_dir}")

def create_config_file(config):
    """Create a configuration file."""
    print("Creating configuration file: config.json")
    
    # Add HTML directories to config
    html_dir = config["default_directories"]["html_dir"]
    module_dirs = {}
    
    for module in config["modules"]:
        module_path = os.path.join(html_dir, module)
        if os.path.exists(module_path) and os.path.isdir(module_path):
            module_dirs[module] = module_path
    
    runtime_config = {
        **config["default_directories"],
        "modules": config["modules"],
        "module_dirs": module_dirs
    }
    
    with open("config.json", 'w') as f:
        json.dump(runtime_config, f, indent=2)
    
    print(f"✓ Configuration written to config.json")

def print_next_steps():
    """Print instructions for next steps."""
    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("1. Run parse_html.py to convert HTML to YAML:")
    print("   pdm run oa-parse")
    print("\n2. Run build_ontology.py to extract the software ontology:")
    print("   pdm run oa-build")
    print("\n3. Run extract_domain_ontology.py to extract the domain ontology:")
    print("   pdm run oa-domain")
    print("\nOr run the entire process with:")
    print("   pdm run oa-run-all")
    print("\nFor more information, see README.md")
    print("="*50)

def main():
    """Main function."""
    print("Setting up OpenAccess Ontology Explorer...")
    
    check_requirements()
    config = get_config()
    
    clone_documentation_repo(
        config.get("html_repo", "https://github.com/oa22doc/oa22doc.github.io"),
        config["default_directories"]["html_dir"]
    )
    
    create_directory_structure(
        config["default_directories"],
        config.get("modules", ["design", "base", "tech", "cms", "wafer", "block"])
    )
    
    create_config_file(config)
    print_next_steps()

if __name__ == "__main__":
    main()