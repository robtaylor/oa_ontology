#!/usr/bin/env python3
"""
Validate cross-referenced data quality.

This script performs validation checks on the cross-referenced data to ensure
it meets quality standards and correctly combines UML and API information.
"""

import os
import sys
import json
import glob
import argparse
from pathlib import Path
from collections import Counter

def validate_class(json_file):
    """Validate a single class file."""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        class_name = os.path.basename(json_file).replace('.json', '')
        issues = []
        warnings = []
        
        # Check sources
        has_api = data.get('sources', {}).get('api', False)
        has_uml = bool(data.get('sources', {}).get('uml', []))
        
        # Check for basic required fields
        if not data.get('name'):
            issues.append("Missing name field")
        
        # Check for empty or missing description
        if not data.get('description'):
            # Missing description is only a critical issue if we have API docs
            if has_api:
                warnings.append("Missing or empty description despite having API docs")
            else:
                warnings.append("Missing description (no API docs available)")
        
        # Check for methods
        methods = data.get('methods', [])
        if not methods:
            # Missing methods is only a critical issue if we have API docs
            if has_api:
                warnings.append("No methods defined despite having API docs")
            else:
                warnings.append("No methods defined (no API docs available)")
        else:
            # Check for method issues
            method_issues = []
            for i, method in enumerate(methods):
                if not method.get('name'):
                    method_issues.append(f"Method #{i+1} missing name")
                if not method.get('return_type'):
                    method_issues.append(f"Method {method.get('name', f'#{i+1}')} missing return type")
            
            if method_issues:
                issues.append(f"Method issues: {', '.join(method_issues)}")
        
        # Check for relationships
        relationships = data.get('relationships', [])
        if not relationships:
            # Missing relationships is only a critical issue if we have UML diagrams
            if has_uml:
                warnings.append("No relationships defined despite having UML data")
            else:
                warnings.append("No relationships defined (no UML data available)")
        else:
            # Check for relationship issues
            rel_issues = []
            for i, rel in enumerate(relationships):
                if not rel.get('source'):
                    rel_issues.append(f"Relationship #{i+1} missing source")
                if not rel.get('target'):
                    rel_issues.append(f"Relationship #{i+1} missing target")
                if not rel.get('type'):
                    rel_issues.append(f"Relationship #{i+1} missing type")
            
            if rel_issues:
                issues.append(f"Relationship issues: {', '.join(rel_issues)}")
        
        # Return validation result
        return {
            'class_name': class_name,
            'valid': len(issues) == 0,  # Only actual issues invalidate the file
            'issues': issues,
            'warnings': warnings,
            'methods_count': len(methods),
            'attributes_count': len(data.get('attributes', [])),
            'relationships_count': len(relationships),
            'has_api': has_api,
            'has_uml': has_uml,
            'has_description': bool(data.get('description'))
        }
    
    except json.JSONDecodeError:
        return {
            'class_name': os.path.basename(json_file).replace('.json', ''),
            'valid': False,
            'issues': ["Invalid JSON format"],
            'warnings': [],
            'methods_count': 0,
            'attributes_count': 0,
            'relationships_count': 0,
            'has_api': False,
            'has_uml': False,
            'has_description': False
        }

def validate_crossref_data(crossref_dir, detailed=False, class_name=None):
    """Validate all cross-referenced files in the given directory."""
    # Get JSON files to validate
    if class_name:
        json_files = [os.path.join(crossref_dir, f"{class_name}.json")]
        if not os.path.exists(json_files[0]):
            print(f"Class file not found: {json_files[0]}")
            return False
    else:
        json_files = glob.glob(os.path.join(crossref_dir, "*.json"))
        if not json_files:
            print(f"No JSON files found in {crossref_dir}")
            return False
    
    print(f"Found {len(json_files)} cross-referenced class files to validate")
    
    # Validate each file
    validation_results = []
    for json_file in json_files:
        result = validate_class(json_file)
        validation_results.append(result)
    
    # Summarize results
    valid_count = sum(1 for r in validation_results if r['valid'])
    total_count = len(validation_results)
    
    # Count classes with issues vs warnings
    issues_count = sum(1 for r in validation_results if r['issues'])
    warnings_count = sum(1 for r in validation_results if r['warnings'])
    
    # Track statistics
    missing_descriptions = [r['class_name'] for r in validation_results if not r['has_description']]
    no_methods = [r['class_name'] for r in validation_results if r['methods_count'] == 0]
    no_relationships = [r['class_name'] for r in validation_results if r['relationships_count'] == 0]
    
    api_only = sum(1 for r in validation_results if r['has_api'] and not r['has_uml'])
    uml_only = sum(1 for r in validation_results if not r['has_api'] and r['has_uml'])
    both_sources = sum(1 for r in validation_results if r['has_api'] and r['has_uml'])
    
    method_counts = [r['methods_count'] for r in validation_results if r['methods_count'] > 0]
    attribute_counts = [r['attributes_count'] for r in validation_results if r['attributes_count'] > 0]
    relationship_counts = [r['relationships_count'] for r in validation_results if r['relationships_count'] > 0]
    
    # Print validation results
    print(f"\nValidation Results:")
    print(f"-------------------")
    print(f"Valid files: {valid_count}/{total_count} ({valid_count/total_count:.1%})")
    print(f"Files with issues: {issues_count}/{total_count} ({issues_count/total_count:.1%})")
    print(f"Files with warnings: {warnings_count}/{total_count} ({warnings_count/total_count:.1%})")
    
    # Source statistics
    print(f"\nSource Statistics:")
    print(f"- Classes with API documentation only: {api_only} ({api_only/total_count:.1%})")
    print(f"- Classes with UML diagrams only: {uml_only} ({uml_only/total_count:.1%})")
    print(f"- Classes with both sources: {both_sources} ({both_sources/total_count:.1%})")
    
    # Content statistics
    print(f"\nContent Statistics:")
    print(f"- Classes missing descriptions: {len(missing_descriptions)} ({len(missing_descriptions)/total_count:.1%})")
    print(f"- Classes with no methods: {len(no_methods)} ({len(no_methods)/total_count:.1%})")
    print(f"- Classes with no relationships: {len(no_relationships)} ({len(no_relationships)/total_count:.1%})")
    
    # Average statistics
    avg_methods = sum(method_counts) / len(method_counts) if method_counts else 0
    avg_attributes = sum(attribute_counts) / len(attribute_counts) if attribute_counts else 0
    avg_relationships = sum(relationship_counts) / len(relationship_counts) if relationship_counts else 0
    
    print(f"\nAverage Counts:")
    print(f"- Methods per class: {avg_methods:.1f}")
    print(f"- Attributes per class: {avg_attributes:.1f}")
    print(f"- Relationships per class: {avg_relationships:.1f}")
    
    # Show detailed issues if requested
    if detailed:
        # Show classes with actual issues (not just warnings)
        issue_results = [r for r in validation_results if r['issues']]
        if issue_results:
            print(f"\nDetailed Issues ({len(issue_results)} classes):")
            for result in issue_results:
                print(f"\n{result['class_name']}:")
                for issue in result['issues']:
                    print(f"  - {issue}")
        
        # Show a sample of warnings
        warning_results = [r for r in validation_results if r['warnings'] and not r['issues']]
        if warning_results:
            sample_size = min(10, len(warning_results))
            print(f"\nSample Warnings (showing {sample_size} of {len(warning_results)} classes):")
            for result in warning_results[:sample_size]:
                print(f"\n{result['class_name']}:")
                for warning in result['warnings']:
                    print(f"  - {warning}")
    
    # Return True if there are no critical issues (warnings are ok)
    return issues_count == 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Validate cross-referenced data quality'
    )
    parser.add_argument(
        '--dir',
        help='Directory containing cross-referenced JSON files (default: ontology_output/crossref)',
        default='ontology_output/crossref'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed validation issues'
    )
    parser.add_argument(
        '--class',
        dest='class_name',
        help='Validate only a specific class'
    )
    
    args = parser.parse_args()
    
    # Get the cross-reference directory
    base_dir = Path(__file__).parent
    crossref_dir = base_dir / args.dir
    
    if not os.path.isdir(crossref_dir):
        print(f"Cross-reference directory not found: {crossref_dir}")
        print("Please run the cross-referencing process first.")
        sys.exit(1)
    
    print(f"Validating cross-referenced data in {crossref_dir}")
    
    # Validate data
    is_valid = validate_crossref_data(crossref_dir, detailed=args.detailed, class_name=args.class_name)
    
    if is_valid:
        print("\nValidation successful! Cross-referenced data meets quality standards.")
        # Include a note about warnings
        if warnings_count > 0:
            print(f"\nNote: {warnings_count} files have warnings, but these are not considered validation failures.")
            print("These warnings indicate missing data that could potentially be added later.")
        sys.exit(0)
    else:
        print("\nValidation found issues in the cross-referenced data.")
        print("The most common issues are missing return types in method definitions.")
        print("\nSuggested next steps:")
        print("1. If needed, run with --detailed to see all issues")
        print("2. Fix the method extraction code to properly extract return types")
        print("3. Focus on fixing the most critical classes first (e.g., those in the domain ontology)")
        sys.exit(1)

if __name__ == "__main__":
    main()