#!/usr/bin/env python3
"""
OpenAccess Ontology Explorer - CLI Tool

A unified command-line interface for working with the OpenAccess ontology.
"""

import argparse
import sys
import os
import importlib
from oa_ontology.cli_dependencies import ensure_prerequisites, check_directories


def setup_process_commands(subparsers):
    """Set up the 'process' subcommands for data processing."""
    process_parser = subparsers.add_parser(
        'process', 
        help='Process OpenAccess documentation data'
    )
    process_subparsers = process_parser.add_subparsers(
        dest='process_command',
        help='Processing command to run'
    )
    
    # HTML parsing command
    html_parser = process_subparsers.add_parser(
        'html', 
        help='Parse HTML documentation into YAML format'
    )
    html_parser.add_argument(
        '--html-dir',
        default='html_source',
        help='Directory containing HTML documentation (default: html_source)'
    )
    html_parser.add_argument(
        '--yaml-dir',
        default='yaml_output',
        help='Directory to output YAML files (default: yaml_output)'
    )
    
    # Build ontology command
    build_parser = process_subparsers.add_parser(
        'build', 
        help='Build the software class ontology'
    )
    build_parser.add_argument(
        '--yaml-dir',
        default='yaml_output',
        help='Directory containing YAML files (default: yaml_output)'
    )
    build_parser.add_argument(
        '--output-dir',
        default='ontology_output',
        help='Directory to output ontology files (default: ontology_output)'
    )
    
    # Extract domain command
    domain_parser = process_subparsers.add_parser(
        'domain', 
        help='Extract domain concepts from the class ontology'
    )
    domain_parser.add_argument(
        '--ontology-file',
        default='ontology_output/design_ontology.json',
        help='Path to the ontology file (default: ontology_output/design_ontology.json)'
    )
    domain_parser.add_argument(
        '--output-file',
        default='ontology_output/domain_ontology.json',
        help='Path to output domain ontology (default: ontology_output/domain_ontology.json)'
    )
    
    # Export to Neo4j command
    export_parser = process_subparsers.add_parser(
        'export', 
        help='Export ontology to Neo4j-compatible format'
    )
    export_parser.add_argument(
        '--ontology-file',
        default='ontology_output/design_ontology.json',
        help='Path to the ontology file (default: ontology_output/design_ontology.json)'
    )
    export_parser.add_argument(
        '--output-file',
        default='ontology_output/neo4j_import.cypher',
        help='Path to output Cypher script (default: ontology_output/neo4j_import.cypher)'
    )


def setup_uml_commands(subparsers):
    """Set up the 'uml' subcommands for UML diagram processing."""
    uml_parser = subparsers.add_parser(
        'uml', 
        help='Process UML diagrams and image maps'
    )
    uml_subparsers = uml_parser.add_subparsers(
        dest='uml_command',
        help='UML processing command to run'
    )
    
    # Process UML diagrams command
    diagram_parser = uml_subparsers.add_parser(
        'diagram', 
        help='Process UML diagrams using computer vision'
    )
    diagram_parser.add_argument(
        '--pattern',
        default='html_source/schema/*.png',
        help='Glob pattern to find UML diagrams (default: html_source/schema/*.png)'
    )
    diagram_parser.add_argument(
        '--output-dir',
        default='yaml_output/schema',
        help='Output directory for structure JSON files (default: yaml_output/schema)'
    )
    diagram_parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable generation of debug images'
    )
    
    # Process image maps command
    imagemap_parser = uml_subparsers.add_parser(
        'imagemap', 
        help='Parse HTML image maps for UML information'
    )
    imagemap_parser.add_argument(
        '--pattern',
        default='html_source/schema/*.html',
        help='Glob pattern to find HTML files (default: html_source/schema/*.html)'
    )
    imagemap_parser.add_argument(
        '--specific',
        help='Process only specific HTML files (comma-separated list without .html extension)'
    )
    imagemap_parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable generation of debug information'
    )
    
    # Combine UML structures command
    combine_parser = uml_subparsers.add_parser(
        'combine', 
        help='Combine multiple schema structures'
    )
    combine_parser.add_argument(
        '--input-dir',
        default='yaml_output/schema',
        help='Directory containing structure files (default: yaml_output/schema)'
    )
    combine_parser.add_argument(
        '--output',
        default='yaml_output/ontology/combined_schema.json',
        help='Output file path (default: yaml_output/ontology/combined_schema.json)'
    )
    combine_parser.add_argument(
        '--pattern',
        default='*_imagemap.json',
        help='Glob pattern to find structure files (default: *_imagemap.json)'
    )
    
    # UML to YAML conversion command
    yaml_parser = uml_subparsers.add_parser(
        'to-yaml', 
        help='Convert UML structure to YAML format'
    )
    yaml_parser.add_argument(
        '--json-dir',
        default='yaml_output/schema',
        help='Directory containing JSON structure files (default: yaml_output/schema)'
    )
    yaml_parser.add_argument(
        '--yaml-dir',
        default='yaml_output/ontology',
        help='Output directory for YAML files (default: yaml_output/ontology)'
    )
    yaml_parser.add_argument(
        '--pattern',
        default='*_structure.json',
        help='Glob pattern to find JSON structure files (default: *_structure.json)'
    )


def setup_crossref_commands(subparsers):
    """Set up the 'crossref' subcommands for cross-referencing data."""
    crossref_parser = subparsers.add_parser(
        'crossref', 
        help='Cross-reference UML diagrams with API documentation'
    )
    crossref_subparsers = crossref_parser.add_subparsers(
        dest='crossref_command',
        help='Cross-reference operation to perform'
    )
    
    # Run cross-reference command
    run_parser = crossref_subparsers.add_parser(
        'run', 
        help='Run the cross-referencing process'
    )
    run_parser.add_argument(
        '--yaml-dir',
        default='yaml_output',
        help='Directory containing YAML parsed files (default: yaml_output)'
    )
    run_parser.add_argument(
        '--uml-dir',
        default='yaml_output/schema',
        help='Directory containing UML schema files (default: yaml_output/schema)'
    )
    run_parser.add_argument(
        '--output-dir',
        default='ontology_output/crossref',
        help='Output directory for cross-referenced data (default: ontology_output/crossref)'
    )
    run_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    run_parser.add_argument(
        '--class',
        dest='class_name',
        help='Process only a specific class'
    )
    
    # Validate cross-references command
    validate_parser = crossref_subparsers.add_parser(
        'validate', 
        help='Validate the cross-referenced data quality'
    )
    validate_parser.add_argument(
        '--crossref-dir',
        default='ontology_output/crossref',
        help='Directory containing cross-referenced data (default: ontology_output/crossref)'
    )
    validate_parser.add_argument(
        '--report',
        default='ontology_output/crossref/validation_report.md',
        help='Path to output validation report (default: ontology_output/crossref/validation_report.md)'
    )
    
    # Enhanced domain ontology command
    enhanced_parser = crossref_subparsers.add_parser(
        'enhance', 
        help='Generate enhanced domain ontology from cross-referenced data'
    )
    enhanced_parser.add_argument(
        '--crossref-dir',
        default='ontology_output/crossref',
        help='Directory containing cross-referenced data (default: ontology_output/crossref)'
    )
    enhanced_parser.add_argument(
        '--domain-file',
        default='ontology_output/domain_ontology.json',
        help='Path to domain ontology file (default: ontology_output/domain_ontology.json)'
    )
    enhanced_parser.add_argument(
        '--output-file',
        default='outputs/enhanced_domain_ontology.json',
        help='Path to output enhanced domain ontology (default: outputs/enhanced_domain_ontology.json)'
    )
    enhanced_parser.add_argument(
        '--report',
        default='outputs/enhanced_domain_ontology_report.md',
        help='Path to output report (default: outputs/enhanced_domain_ontology_report.md)'
    )
    
    # Fix enhanced ontology command
    fix_parser = crossref_subparsers.add_parser(
        'fix', 
        help='Fix enhanced ontology structure for visualization'
    )
    fix_parser.add_argument(
        '--input',
        default='outputs/enhanced_domain_ontology.json',
        help='Input JSON file path (default: outputs/enhanced_domain_ontology.json)'
    )
    fix_parser.add_argument(
        '--output',
        default='outputs/enhanced_domain_ontology_fixed.json',
        help='Output JSON file path (default: outputs/enhanced_domain_ontology_fixed.json)'
    )


def setup_visualize_commands(subparsers):
    """Set up the 'visualize' subcommands for visualization."""
    visualize_parser = subparsers.add_parser(
        'visualize', 
        help='Create visualizations of the ontology'
    )
    visualize_subparsers = visualize_parser.add_subparsers(
        dest='visualize_command',
        help='Visualization to create'
    )
    
    # Create basic visualization command
    basic_parser = visualize_subparsers.add_parser(
        'basic', 
        help='Generate basic visualizations of the ontology'
    )
    basic_parser.add_argument(
        '--ontology-file',
        default='ontology_output/design_ontology.json',
        help='Path to the ontology file (default: ontology_output/design_ontology.json)'
    )
    basic_parser.add_argument(
        '--output-dir',
        default='ontology_output/visualizations',
        help='Directory to output visualizations (default: ontology_output/visualizations)'
    )
    
    # Connected classes visualization command
    connected_parser = visualize_subparsers.add_parser(
        'connected', 
        help='Create visualization of most connected classes without inheritance'
    )
    connected_parser.add_argument(
        '--input',
        default='outputs/visualization_graph.json',
        help='Path to the ontology data (default: outputs/visualization_graph.json)'
    )
    connected_parser.add_argument(
        '--output',
        default='outputs/connected_classes_visualization.html',
        help='Output HTML file path (default: outputs/connected_classes_visualization.html)'
    )
    connected_parser.add_argument(
        '--limit',
        type=int,
        default=75,
        help='Limit the visualization to the top N most connected nodes (default: 75)'
    )
    connected_parser.add_argument(
        '--domain',
        choices=["Physical", "Connectivity", "Hierarchy", "Layout", "Device", "Other"],
        help='Filter nodes by domain'
    )
    
    # Domain-specific visualization command
    domain_parser = visualize_subparsers.add_parser(
        'domain', 
        help='Create domain-specific visualizations'
    )
    domain_parser.add_argument(
        '--input',
        default='outputs/enhanced_domain_ontology.json',
        help='Path to the enhanced domain ontology (default: outputs/enhanced_domain_ontology.json)'
    )
    domain_parser.add_argument(
        '--output',
        default='outputs/enhanced_domain_visualization.html',
        help='Output HTML file path (default: outputs/enhanced_domain_visualization.html)'
    )
    domain_parser.add_argument(
        '--limit',
        type=int,
        help='Limit the visualization to the top N most connected nodes'
    )
    domain_parser.add_argument(
        '--domain',
        choices=["Physical", "Connectivity", "Hierarchy", "Layout", "Device", "Other"],
        help='Filter nodes by domain'
    )
    
    # Create visualization graph command
    graph_parser = visualize_subparsers.add_parser(
        'graph', 
        help='Create simplified graph for visualization'
    )
    graph_parser.add_argument(
        '--input',
        default='outputs/enhanced_domain_ontology.json',
        help='Input JSON file path (default: outputs/enhanced_domain_ontology.json)'
    )
    graph_parser.add_argument(
        '--output',
        default='outputs/visualization_graph.json',
        help='Output JSON file path (default: outputs/visualization_graph.json)'
    )


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='OpenAccess Ontology Explorer - CLI Tool'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--no-deps', '-n',
        action='store_true',
        help='Skip running prerequisites automatically'
    )
    
    # Create subparsers for main commands
    subparsers = parser.add_subparsers(
        dest='command',
        help='Command to run'
    )
    
    # Set up the command groups
    setup_process_commands(subparsers)
    setup_uml_commands(subparsers)
    setup_crossref_commands(subparsers)
    setup_visualize_commands(subparsers)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Ensure directories exist
    check_directories()
    
    # Handle command dispatching
    try:
        # Determine subcommand
        subcommand = None
        if args.command == 'process' and hasattr(args, 'process_command'):
            subcommand = args.process_command
        elif args.command == 'uml' and hasattr(args, 'uml_command'):
            subcommand = args.uml_command
        elif args.command == 'crossref' and hasattr(args, 'crossref_command'):
            subcommand = args.crossref_command
        elif args.command == 'visualize' and hasattr(args, 'visualize_command'):
            subcommand = args.visualize_command
        
        # Check prerequisites if we have a valid subcommand and not skipping deps
        if subcommand and not args.no_deps:
            print(f"Checking prerequisites for {args.command} {subcommand}...")
            if not ensure_prerequisites(args.command, subcommand, args.verbose):
                print(f"❌ Failed to satisfy prerequisites for {args.command} {subcommand}")
                return 1
            print(f"✓ All prerequisites for {args.command} {subcommand} are satisfied")
        
        # Dispatch to appropriate handler
        if args.command == 'process':
            dispatch_process_command(args)
        elif args.command == 'uml':
            dispatch_uml_command(args)
        elif args.command == 'crossref':
            dispatch_crossref_command(args)
        elif args.command == 'visualize':
            dispatch_visualize_command(args)
        else:
            parser.print_help()
            return 1
        
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def dispatch_process_command(args):
    """Dispatch process subcommands to the appropriate handlers."""
    if not args.process_command:
        raise ValueError("No process command specified")
    
    if args.process_command == 'html':
        from oa_ontology.parse_html import main as parse_html_main
        parse_html_main()
    elif args.process_command == 'build':
        from oa_ontology.build_ontology import main as build_ontology_main
        build_ontology_main()
    elif args.process_command == 'domain':
        from oa_ontology.extract_domain_ontology import main as extract_domain_main
        extract_domain_main()
    elif args.process_command == 'export':
        from oa_ontology.export_to_neo4j import main as export_to_neo4j_main
        export_to_neo4j_main()
    else:
        raise ValueError(f"Unknown process command: {args.process_command}")


def dispatch_uml_command(args):
    """Dispatch UML subcommands to the appropriate handlers."""
    if not args.uml_command:
        raise ValueError("No UML command specified")
    
    if args.uml_command == 'diagram':
        import scripts.parse_all_diagrams
        scripts.parse_all_diagrams.main()
    elif args.uml_command == 'imagemap':
        import scripts.parse_all_imagemaps
        scripts.parse_all_imagemaps.main()
    elif args.uml_command == 'combine':
        from oa_ontology.combine_schema_structures import main as combine_schema_main
        combine_schema_main()
    elif args.uml_command == 'to-yaml':
        from oa_ontology.structure_to_yaml import main as structure_to_yaml_main
        structure_to_yaml_main()
    else:
        raise ValueError(f"Unknown UML command: {args.uml_command}")


def dispatch_crossref_command(args):
    """Dispatch crossref subcommands to the appropriate handlers."""
    if not args.crossref_command:
        raise ValueError("No crossref command specified")
    
    if args.crossref_command == 'run':
        import scripts.run_crossref
        scripts.run_crossref.main()
    elif args.crossref_command == 'validate':
        import scripts.validate_crossref
        scripts.validate_crossref.main()
    elif args.crossref_command == 'enhance':
        import scripts.run_enhanced_domain
        scripts.run_enhanced_domain.main()
    elif args.crossref_command == 'fix':
        import scripts.fix_enhanced_ontology
        scripts.fix_enhanced_ontology.main()
    else:
        raise ValueError(f"Unknown crossref command: {args.crossref_command}")


def dispatch_visualize_command(args):
    """Dispatch visualize subcommands to the appropriate handlers."""
    if not args.visualize_command:
        raise ValueError("No visualize command specified")
    
    if args.visualize_command == 'basic':
        from oa_ontology.visualize_ontology import main as visualize_ontology_main
        visualize_ontology_main()
    elif args.visualize_command == 'connected':
        import scripts.visualize_connected_classes
        # Create a new argument parser and namespace for the script
        parser = argparse.ArgumentParser()
        parser.add_argument("--input", default=args.input if hasattr(args, 'input') else "outputs/visualization_graph.json")
        parser.add_argument("--output", default=args.output if hasattr(args, 'output') else "outputs/connected_classes_visualization.html")
        parser.add_argument("--limit", type=int, default=args.limit if hasattr(args, 'limit') else 75)
        parser.add_argument("--domain", default=args.domain if hasattr(args, 'domain') else None)
        script_args = parser.parse_args([])  # Create empty namespace
        
        # Set the attributes from our CLI args
        if hasattr(args, 'input'):
            script_args.input = args.input
        if hasattr(args, 'output'):
            script_args.output = args.output
        if hasattr(args, 'limit'):
            script_args.limit = args.limit
        if hasattr(args, 'domain'):
            script_args.domain = args.domain
            
        # Monkey patch sys.argv to use our args
        import sys
        original_argv = sys.argv
        sys.argv = [sys.argv[0]]  # Keep just the script name
        
        # Run the script with our args
        try:
            # Pass the args object directly
            scripts.visualize_connected_classes.visualize_ontology(
                script_args.input,
                script_args.output, 
                script_args.limit, 
                script_args.domain
            )
            print(f"Visualization completed. Open {script_args.output} in a web browser to view.")
        finally:
            # Restore original args
            sys.argv = original_argv
    elif args.visualize_command == 'domain':
        import scripts.visualize_enhanced_domain
        scripts.visualize_enhanced_domain.main()
    elif args.visualize_command == 'graph':
        from oa_ontology.create_visualization_graph import main as create_vis_graph_main
        create_vis_graph_main()
    else:
        raise ValueError(f"Unknown visualize command: {args.visualize_command}")


if __name__ == '__main__':
    sys.exit(main())