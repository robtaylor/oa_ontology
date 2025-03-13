# OpenAccess Design Domain Ontology

## Overview

This report analyzes the domain concepts extracted from the OpenAccess Design API.
The ontology represents the underlying IC design concepts rather than just the code structure.

## Domain Statistics

Total classes: 306
Total relationships: 1065

### Classes by Domain

- **Connectivity**: 90 classes
- **Other**: 83 classes
- **Physical**: 70 classes
- **Hierarchy**: 42 classes
- **Layout**: 15 classes
- **Device**: 6 classes

### Relationship Types

- **SPECIALIZES**: 1051 relationships
- **HAS**: 7 relationships
- **CONNECTS_TO**: 3 relationships
- **ON**: 2 relationships
- **CONNECTS**: 1 relationships
- **CONTAINS**: 1 relationships

## Key Concepts

### DesignObject

**Domain**: Physical  
**Concept**: Design  
**Centrality**: 0.7180  
**Description**: There is a substantial tree of classes derived from oaDesignObject. For most of these classes, an oaDesignObject can be classified using itsoaTypevalu...  

**Relationships**:

- SPECIALIZES → AnalysisOpPoint
- SPECIALIZES → AnalysisPoint
- SPECIALIZES → BlockObject
- SPECIALIZES → Design
- SPECIALIZES → Device

### BlockObject

**Domain**: Physical  
**Concept**: Block  
**Centrality**: 0.4361  
**Description**: ...  

**Relationships**:

- SPECIALIZES → DesignObject
- SPECIALIZES → Assignment
- SPECIALIZES → Block
- SPECIALIZES → BusNetDef
- SPECIALIZES → BusTermDef

### Fig

**Domain**: Physical  
**Concept**: Fig  
**Centrality**: 0.2361  
**Description**: ...  

**Relationships**:

- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject
- SPECIALIZES → Blockage
- SPECIALIZES → Boundary
- SPECIALIZES → ConnFig

### ConnFig

**Domain**: Physical  
**Concept**: Fig  
**Centrality**: 0.1836  
**Description**: ...  

**Relationships**:

- ON → Net
- SPECIALIZES → Fig
- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject
- SPECIALIZES → Guide

### OccObject

**Domain**: Other  
**Concept**: Unknown  
**Centrality**: 0.1672  
**Description**: ...  

**Relationships**:

- SPECIALIZES → DesignObject
- SPECIALIZES → OccAssignment
- SPECIALIZES → OccBusNetDef
- SPECIALIZES → OccBusTermDef
- SPECIALIZES → OccConnectDef

### ModObject

**Domain**: Other  
**Concept**: Unknown  
**Centrality**: 0.1639  
**Description**: ...  

**Relationships**:

- SPECIALIZES → DesignObject
- SPECIALIZES → ModAssignment
- SPECIALIZES → ModBusNetDef
- SPECIALIZES → ModBusTermDef
- SPECIALIZES → ModConnectDef

### PinFig

**Domain**: Physical  
**Concept**: Fig  
**Centrality**: 0.1607  
**Description**: ...  

**Relationships**:

- SPECIALIZES → ConnFig
- SPECIALIZES → Fig
- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject
- SPECIALIZES → Ref

### Shape

**Domain**: Physical  
**Concept**: Shape  
**Centrality**: 0.1148  
**Description**: All shapes are placed on anoaLayerand anoaPurpose. The design API identifies these by the layer and purpose numbers. The corresponding names are found...  

**Relationships**:

- SPECIALIZES → PinFig
- SPECIALIZES → ConnFig
- SPECIALIZES → Fig
- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject

### OccShape

**Domain**: Physical  
**Concept**: Shape  
**Centrality**: 0.1049  
**Description**: oaOccArcoaOccDonutoaOccDotoaOccEllipseoaOccLineoaOccPathoaOccPathSegoaOccPolygonoaOccRectoaOccTextoaOccEvalTextoaOccTextDisplayoaOccPropDisplayoaOccAt...  

**Relationships**:

- ON → Net
- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject
- SPECIALIZES → OccArc
- SPECIALIZES → OccDonut

### OccInst

**Domain**: Hierarchy  
**Concept**: Inst  
**Centrality**: 0.0852  
**Description**: An oaOccInst may correspond to anoaModInst, anoaInst, or both:If the occInst is an occurrence of anoaModModuleInst(it will be anoaOccModuleScalarInst,...  

**Relationships**:

- SPECIALIZES → OccObject
- SPECIALIZES → DesignObject
- SPECIALIZES → OccDesignInst
- SPECIALIZES → OccModuleInst
- SPECIALIZES → OccBitInst

### Ref

**Domain**: Other  
**Concept**: Unknown  
**Centrality**: 0.0820  
**Description**: ...  

**Relationships**:

- SPECIALIZES → PinFig
- SPECIALIZES → ConnFig
- SPECIALIZES → Fig
- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject

### RegionQuery

**Domain**: Other  
**Concept**: Unknown  
**Centrality**: 0.0787  
**Description**: A Region Query descends through a design hierarchy from the top design with which it is constructed, producing all objects of a specified type in the ...  

**Relationships**:

- SPECIALIZES → BlockageQuery
- SPECIALIZES → BoundaryQuery
- SPECIALIZES → FigGroupQuery
- SPECIALIZES → GuideQuery
- SPECIALIZES → InstQuery

### ModInst

**Domain**: Hierarchy  
**Concept**: Inst  
**Centrality**: 0.0754  
**Description**: oaModInst objects are always in the module domain. An oaModInst can have an equivalentoaInstin the block domain and will always have an equivalentoaOc...  

**Relationships**:

- SPECIALIZES → ModObject
- SPECIALIZES → DesignObject
- SPECIALIZES → ModDesignInst
- SPECIALIZES → ModModuleInst
- SPECIALIZES → ModBitInst

### TextDisplay

**Domain**: Physical  
**Concept**: Text  
**Centrality**: 0.0623  
**Description**: ...  

**Relationships**:

- SPECIALIZES → Shape
- SPECIALIZES → PinFig
- SPECIALIZES → ConnFig
- SPECIALIZES → Fig
- SPECIALIZES → BlockObject

### Inst

**Domain**: Hierarchy  
**Concept**: Inst  
**Centrality**: 0.0623  
**Description**: oaInst objects are always in the block domain. Thus they are contained in anoaBlockobject. An oaInst may have one or more equivalent module instances ...  

**Relationships**:

- SPECIALIZES → Ref
- SPECIALIZES → PinFig
- SPECIALIZES → ConnFig
- SPECIALIZES → Fig
- SPECIALIZES → BlockObject

### Net

**Domain**: Connectivity  
**Concept**: Net  
**Centrality**: 0.0557  
**Description**: oaNet objects are always in the block domain. Nets span the domains in a design. An oaNet may have one or more equivalent oaModNet's in the module hie...  

**Relationships**:

- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject
- SPECIALIZES → BitNet
- SPECIALIZES → BundleNet
- SPECIALIZES → BusNet

### Blockage

**Domain**: Physical  
**Concept**: Block  
**Centrality**: 0.0525  
**Description**: Note: LayerBlockages (bothoaLayerBlockageandoaLayerHalo) will never have a blockageType of oacPlacementBlockageType. AreaBlockages (bothoaAreaBlockage...  

**Relationships**:

- SPECIALIZES → Fig
- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject
- SPECIALIZES → AreaBlockage
- SPECIALIZES → AreaHalo

### Device

**Domain**: Device  
**Concept**: Device  
**Centrality**: 0.0525  
**Description**: Devices are managed objects, but they can be loaded from disk into memory (and unloaded from memory back to disk) on request as part of the parasitic ...  

**Relationships**:

- SPECIALIZES → DesignObject
- SPECIALIZES → MutualInductor
- SPECIALIZES → SeriesRL
- SPECIALIZES → StdDevice
- SPECIALIZES → CouplingCap

### Term

**Domain**: Connectivity  
**Concept**: Term  
**Centrality**: 0.0492  
**Description**: All terminals are required to have a net even if there is nothing else attached to that net.Multi-bit terminals represent a group of logical connectio...  

**Relationships**:

- HAS → Net
- SPECIALIZES → BlockObject
- SPECIALIZES → DesignObject
- SPECIALIZES → BitTerm
- SPECIALIZES → BundleTerm

### OccTerm

**Domain**: Connectivity  
**Concept**: Term  
**Centrality**: 0.0492  
**Description**: oaModTerm, oaOccTerm, andoaTermeach represent bus terminals on a different kind of master, where in each case the master represents a level of hierarc...  

**Relationships**:

- HAS → OccNet
- SPECIALIZES → OccObject
- SPECIALIZES → DesignObject
- SPECIALIZES → OccBitTerm
- SPECIALIZES → OccBundleTerm


## Domain Concept Map

This ontology is available in GraphML format for visualization in tools like Gephi, Cytoscape, or yEd.
