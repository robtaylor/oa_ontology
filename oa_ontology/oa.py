#!/usr/bin/env python3
"""
OpenAccess Ontology Explorer - Command Line Tool

This is the main entry point for the CLI application that consolidates 
all the scripts and tools in the OA Ontology Explorer.
"""

from oa_ontology.cli import main


if __name__ == '__main__':
    import sys
    sys.exit(main())