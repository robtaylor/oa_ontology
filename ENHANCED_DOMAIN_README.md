# Enhanced Domain Ontology Extraction

This document describes the Enhanced Domain Ontology extraction process that combines information from both UML diagrams and API documentation to create a more comprehensive domain model.

## Overview

The Enhanced Domain Ontology builds on the original domain ontology extraction but incorporates cross-referenced data from UML diagrams and API documentation. This combined approach provides several key advantages:

1. More accurate relationship types derived from UML diagrams
2. Complete relationship coverage even for classes without detailed API documentation
3. Richer attribute information inferred from method signatures
4. Better representation of domain concepts with specialized relationship types

## Key Components

The enhanced domain ontology extraction consists of several components:

```
┌─────────────────────┐     ┌───────────────────┐
│ HTML Documentation  │     │  UML Diagrams     │
└──────────┬──────────┘     └─────────┬─────────┘
           │                          │
           ▼                          ▼
┌──────────────────────────────────────────────┐
│        Cross-Reference System                │
│        (crossref_api_uml.py)                 │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│     Enhanced Domain Ontology Extractor       │
│     (enhanced_domain_ontology.py)            │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              Output Files                    │
│  - JSON, GraphML, Reports, Neo4j scripts     │
└──────────────────────────────────────────────┘
```

### 1. Cross-Reference System

Located in `oa_ontology/crossref_api_uml.py`, this module combines information from UML diagrams and API documentation. Its key functions include:

- Merging method information from both sources
- Handling method overloads correctly
- Extracting relationships from UML diagrams
- Inferring attributes from getter/setter method patterns
- Cleaning descriptions for better readability

### 2. Enhanced Domain Ontology Extractor

Located in `oa_ontology/enhanced_domain_ontology.py`, this module uses the cross-referenced data to create a domain-focused ontology with richer relationship types. Key features:

- Maps UML relationship types to domain-specific relationship types (inheritance → SPECIALIZES, etc.)
- Extracts domain concepts from class names
- Tracks relationship sources (UML vs API-inferred)
- Generates comprehensive reports on the enhanced ontology

### 3. Runner Scripts

- `run_crossref.py`: Entry point for running the cross-referencing process
- `run_enhanced_domain.py`: Entry point for extracting the enhanced domain ontology
- `run_all.py`: Updated to include the enhanced domain extraction in the workflow

## Running the Enhanced Domain Extraction

You can run the enhanced domain extraction in two ways:

### Option 1: Full Pipeline

To run the complete pipeline, including cross-referencing and enhanced domain extraction:

```bash
python -m oa_ontology.run_all
```

### Option 2: Step by Step

To run individual steps:

1. First, run the cross-referencing process:
   ```bash
   python run_crossref.py
   ```

2. Then, extract the enhanced domain ontology:
   ```bash
   python run_enhanced_domain.py
   ```

3. Optionally, export to Neo4j or other graph databases:
   ```bash
   python -m oa_ontology.export_to_neo4j
   ```

## Output Files

The enhanced domain extraction produces several output files:

- `outputs/enhanced_domain_ontology.json`: The enhanced domain ontology in JSON format
- `outputs/enhanced_domain_ontology.graphml`: GraphML representation for visualization
- `outputs/enhanced_domain_ontology_report.md`: Detailed report with statistics and analysis
- `outputs/enhanced_neo4j_import.cypher`: Cypher script for importing into Neo4j
- `outputs/enhanced_queries.cypher`: Example queries for exploring the enhanced ontology

## Relationship Types

The enhanced domain ontology uses the following relationship types:

| UML Type | Domain Type | Description |
|----------|-------------|-------------|
| inheritance | SPECIALIZES | Class inheritance relationship |
| aggregation-many | CONTAINS_MANY | Container with multiple instances of another class |
| aggregation-single | CONTAINS_ONE | Container with a single instance of another class |
| association-reference | REFERENCES | Simple reference to another class |
| association-many | ASSOCIATED_WITH_MANY | Association with multiple instances |
| association | ASSOCIATED_WITH | General association between classes |
| composition | COMPOSED_OF | Strong ownership/composition |
| usage | USES | Usage dependency |

## Examples

### Finding Hub Classes

To find the most connected classes in the enhanced domain ontology:

```cypher
MATCH (c:Class)
RETURN c.name AS Class, size((c)--()) AS ConnectionCount
ORDER BY ConnectionCount DESC
LIMIT 10;
```

### Exploring Container Hierarchies

To explore container hierarchies in the enhanced domain:

```cypher
MATCH (c:Class)-[r:CONTAINS_ONE|CONTAINS_MANY]->(contained:Class)
RETURN c.name AS Container, 
       collect({class: contained.name, type: type(r)}) AS ContainedClasses
ORDER BY size(ContainedClasses) DESC
LIMIT 10;
```

### Comparing UML and API Information

To compare relationships sourced from UML vs API:

```cypher
MATCH (c:Class)-[r]->(other:Class)
WHERE r.source IS NOT NULL
RETURN r.source AS Source, count(r) AS Count
ORDER BY Count DESC;
```

## Technical Details

### Attribute Inference

The cross-referencing system infers attributes from getter/setter methods:

- `getFoo()` → Infers an attribute named `foo`
- `isEnabled()` → Infers a boolean attribute named `enabled` 
- `hasChildren()` → Infers a boolean attribute named `children`

### Relationship Source Tracking

Each relationship includes a `source` attribute indicating where it came from:

- `uml`: Extracted directly from UML diagrams
- `api_inferred`: Inferred from API method signatures

## Next Steps

Future improvements to the enhanced domain ontology could include:

1. Adding more specialized relationship types based on method name patterns
2. Integrating with additional documentation sources
3. Enhanced visualization capabilities for the domain ontology
4. Deeper analysis of class patterns and design patterns
5. Integration with code generation or documentation systems

## Troubleshooting

If you encounter issues:

- Make sure all dependencies are installed using `pdm install`
- Check that UML diagram files exist in the `yaml_output/schema` directory
- Verify that the API YAML files exist in the `yaml_output` directory
- Check the log output for specific error messages