// Common Cypher Queries for Exploring the OpenAccess Design Ontology

// Find all base classes (classes that don't inherit from anything)
MATCH (c:Class)
WHERE NOT (c)-[:INHERITS_FROM]->()
RETURN c.name AS BaseClass
ORDER BY c.name;

// Find classes with the most relationships
MATCH (c:Class)
RETURN c.name AS Class, size((c)--()) AS RelationshipCount
ORDER BY RelationshipCount DESC
LIMIT 10;

// Get the complete inheritance hierarchy
MATCH p = (c:Class)-[:INHERITS_FROM*]->(base)
WHERE NOT (base)-[:INHERITS_FROM]->()
RETURN p
LIMIT 100;

// Find classes that contain other classes
MATCH (c:Class)-[r:CONTAINS]->(contained:Class)
RETURN c.name AS Container, collected(contained.name) AS ContainedClasses
ORDER BY size(ContainedClasses) DESC
LIMIT 20;

// Find all relationships for a specific class
// Replace 'oaDesign' with the class of interest
MATCH (c:Class {name: 'oaDesign'})-[r]->(other)
RETURN type(r) AS RelationshipType, other.name AS RelatedClass;

// Find all inheritance paths for a specific class
// Replace 'oaBlock' with the class of interest
MATCH p = (c:Class {name: 'oaBlock'})-[:INHERITS_FROM*]->(base)
RETURN [node IN nodes(p) | node.name] AS InheritancePath;

// Find circular references or dependencies
MATCH path = (c:Class)-[:DEPENDS_ON|REFERENCES*]->(c)
RETURN path;

// Find classes grouped by inheritance depth
MATCH path = (c:Class)-[:INHERITS_FROM*]->(base)
WHERE NOT (base)-[:INHERITS_FROM]->()
WITH c, length(path) AS depth
RETURN depth, collect(c.name) AS Classes
ORDER BY depth;

// Find the main containment structure
MATCH (c:Class)-[:CONTAINS]->(contained:Class)
WHERE NOT (c)<-[:CONTAINS]-()  // Only top-level containers
RETURN c.name AS Container, collect(contained.name) AS DirectlyContained
ORDER BY size(DirectlyContained) DESC;
