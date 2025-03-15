#!/usr/bin/env python3
"""
Utilities for visualization of the OpenAccess ontology.

This module provides utilities for creating visualizations with PyVis
using library files stored in the outputs directory.
"""

import os
import shutil
from pathlib import Path
from pyvis.network import Network
from oa_ontology.config import (
    ENHANCED_DIR, LIB_DIR, LIB_BINDINGS_DIR, 
    LIB_TOM_SELECT_DIR, LIB_VIS_DIR
)

def setup_visualization_libraries():
    """
    Configure the visualization environment and copy necessary library files.
    
    Returns:
        Path: The path to the lib directory
    """
    # Ensure lib directories exist
    os.makedirs(LIB_BINDINGS_DIR, exist_ok=True)
    os.makedirs(LIB_TOM_SELECT_DIR, exist_ok=True)
    os.makedirs(LIB_VIS_DIR, exist_ok=True)
    
    # Copy library files from project lib directory to outputs/lib if they exist
    source_lib = Path("lib")
    if source_lib.exists():
        # Copy utility files
        for src_dir, dest_dir in [
            (source_lib / "bindings", LIB_BINDINGS_DIR),
            (source_lib / "tom-select", LIB_TOM_SELECT_DIR),
            (source_lib / "vis-9.1.2", LIB_VIS_DIR)
        ]:
            if src_dir.exists():
                # Copy all files from the directory
                for file in src_dir.glob('*'):
                    if file.is_file():
                        dest_file = dest_dir / file.name
                        if not dest_file.exists():
                            shutil.copy2(file, dest_file)
                            print(f"Copied {file.name} to {dest_dir}")
    
    return LIB_DIR

def create_network(height="800px", width="100%", directed=True):
    """
    Create a pyvis Network with the correct configuration to use local library files.
    
    Args:
        height: Height of the visualization (default: "800px")
        width: Width of the visualization (default: "100%")
        directed: Whether the network is directed (default: True)
        
    Returns:
        Network: A configured pyvis Network instance
    """
    # Ensure library files are in place
    setup_visualization_libraries()
    
    # Create Network instance
    net = Network(height=height, width=width, directed=directed, notebook=False)
    
    # Use local resources from the outputs/lib directory
    # This tells pyvis to use local lib files instead of CDN resources
    net.cdn_resources = "local"
    
    # Configure network options
    net.toggle_hide_edges_on_drag(True)
    net.set_edge_smooth('dynamic')
    
    return net

if __name__ == "__main__":
    # Quick test to ensure the module works correctly
    setup_visualization_libraries()
    print(f"Visualization libraries configured in {LIB_DIR}")