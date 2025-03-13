# OpenAccess Design Domain Ontology Summary

## Overview

We've extracted the underlying conceptual domain model from the OpenAccess design API, focusing on IC design concepts rather than just the software implementation structure. This ontology reveals the key design domains, concepts, and relationships that make up the OpenAccess physical design model.

## Key Design Domains

The analysis identified six main domains in the OpenAccess design API:

1. **Connectivity Domain (90 classes)**: Represents the electrical connectivity of the design
   - Key concepts: Net, Term, InstTerm, Pin, Route
   - Main function: Defining and managing the electrical connections between components

2. **Physical Domain (70 classes)**: Represents the physical implementation of the design
   - Key concepts: Shape, Rect, Line, Path, Text, Via, Fig
   - Main function: Defining the geometric objects that make up the layout

3. **Hierarchy Domain (42 classes)**: Represents the hierarchical structure of the design
   - Key concepts: Design, Block, Module, Inst, Occurrence
   - Main function: Managing design hierarchy and instantiation

4. **Layout Domain (15 classes)**: Represents the structured layout elements
   - Key concepts: Row, TrackPattern, GCellPattern, Boundary, Blockage
   - Main function: Managing the placement grid and routing resources

5. **Device Domain (6 classes)**: Represents the electronic devices in the design
   - Key concepts: Device, Resistor, Capacitor, Inductor
   - Main function: Modeling electronic components with specific behavior

6. **Other (83 classes)**: Utility and support classes that don't fit cleanly into the domains above

## Core Concepts and Relationships

The central concepts in the domain model are:

1. **DesignObject**: The base concept for all design elements
   - Highest centrality (0.718) - most connected concept
   - Core abstraction from which most other concepts derive

2. **BlockObject**: Container for physical design elements
   - Second highest centrality (0.436)
   - Key container for connectivity and geometric objects

3. **Fig (Figure)**: Base concept for all geometric objects
   - Represents physical shapes and objects in the design
   - Parent of ConnFig (connectable figures)

4. **Net**: Electrical connection between components
   - Various specialized forms: BusNet, BundleNet, ScalarNet
   - Connected to Terms, InstTerms, and geometric objects (ConnFig)

5. **Term**: Connection point for nets
   - Exists at the block level, module level, and occurrence level
   - Connected to Nets in various forms

6. **Inst (Instance)**: Instantiation of a design
   - Represents reuse of designs within a hierarchy
   - Various forms: ScalarInst, VectorInst, ArrayInst

## Key Relationship Types

The domain model identified these relationship types:

1. **SPECIALIZES**: Inheritance or specialization relationship (1051 relationships)
   - Most common relationship type, reflecting the OO structure

2. **HAS**: Containment or ownership (7 relationships)
   - E.g., Term HAS Net, Shape HAS Layer

3. **CONNECTS_TO**: Electrical connection (3 relationships)
   - E.g., InstTerm CONNECTS_TO Net

4. **ON**: Association with a layer (2 relationships)
   - E.g., Shape ON Layer

5. **CONNECTS**: Connects multiple elements (1 relationship)
   - E.g., Net CONNECTS Term

6. **CONTAINS**: Containment relationship (1 relationship)
   - E.g., Block CONTAINS Net

## Multi-Domain Structure

One of the most interesting aspects of the OpenAccess design is its multi-domain structure:

1. **Block Domain**: Physical implementation (oaBlock, oaNet, oaTerm, etc.)
2. **Module Domain**: Logical structure (oaModule, oaModNet, oaModTerm, etc.)
3. **Occurrence Domain**: Hierarchical instances (oaOccurrence, oaOccNet, oaOccTerm, etc.)

Each domain has parallel concepts that represent the same logical entity at different levels of the design hierarchy.

## Domain Model Applications

This domain ontology can be used for:

1. **Documentation**: Understanding the conceptual organization of OpenAccess
2. **Training**: Teaching new users about physical design concepts
3. **Tool Development**: Building tools that work with the OpenAccess data model
4. **Model Extension**: Identifying where to add new functionality
5. **Integration**: Mapping OpenAccess concepts to other EDA formats and tools

## Conclusion

The extracted domain ontology reveals the sophisticated conceptual model underlying the OpenAccess API. By identifying the key domains, concepts, and relationships, we gain a deeper understanding of how OpenAccess models IC design data beyond just the class structure.

This model shows that OpenAccess is organized around:
- Multiple hierarchical domains (block, module, occurrence)
- Rich connectivity representations
- Comprehensive geometric primitives
- Clear separation of concerns between domains

The ontology provides a foundation for understanding how OpenAccess represents and manages complex IC designs across multiple levels of abstraction.