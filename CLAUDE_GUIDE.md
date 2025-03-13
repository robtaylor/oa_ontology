## PDM

This project uses PDM (Python Development Master) for dependency management. Here's how to work with PDM:

### Setting Up PDM for the First Time

1. Install PDM if you haven't already:
   ```bash
   curl -sSL https://pdm-project.org/install-pdm.py | python3 -
   ```

2. Initialize the environment (when in the project directory):
   ```bash
   pdm install
   ```

### Common PDM Commands

- **Add a dependency**:
  ```bash
  pdm add package_name
  ```

- **Add a development dependency**:
  ```bash
  pdm add -d package_name
  ```

- **Update dependencies**:
  ```bash
  pdm update
  ```

- **Run a script defined in pyproject.toml**:
  ```bash
  pdm run script_name
  ```

- **Run within the managed enviroment **:
  ```bash
  pdm run script-or-program
  ```

- **Run python within the managed enviroment **:
  ```bash
  pdm run python
  ```

- **Activate the virtual environment**:
  ```bash
  eval $(pdm venv activate)
  ```

- **Create a new virtual environment**:
  ```bash
  pdm venv create
  ```

PDM automatically creates and manages virtual environments, making Python version and dependency management seamless.

## Effective Prompting Strategies

When working with Claude to refine the OpenAccess ontology, use these prompting strategies for best results:

### 1. Domain Understanding Prompts

```
Can you analyze the domain structure in our ontology and identify any missing key concepts or relationships that should be added to better represent IC design?
```

```
Based on the extracted domain_ontology.json, what are the most central concepts in the OpenAccess API, and how do they relate to traditional IC design concepts?
```

```
Examine the relationship types we've identified. What additional relationship types should we consider adding to better capture the semantics of IC design?
```

### 2. Ontology Enhancement Prompts

```
Can you help me enhance the extract_domain_ontology.py script to identify more nuanced relationships between the Connectivity and Physical domains?
```

```
Analyze domain_ontology_report.md and suggest how we might better categorize the concepts currently classified as "Other" into more specific domains.
```

```
What domain-specific rules should we add to our ontology to better capture the constraints of IC design?
```

### 3. Visualization Improvement Prompts

```
Can you enhance visualize_ontology.py to generate interactive D3.js visualizations that better show the hierarchical structure of the OpenAccess domains?
```

```
How could we modify our Neo4j export to include additional metadata that would make queries more effective for exploring design patterns?
```

```
Generate code to create a simplified view of the ontology that focuses specifically on the connectivity domain and its relationships to physical components.
```

### 4. Cross-Domain Analysis Prompts

```
Can you write a script that analyzes the relationships between the Block, Module, and Occurrence domains to better understand the parallel structures in OpenAccess?
```

```
Help me create a mapping between our extracted ontology and standard IC design concepts like netlists, layout, and parasitic extraction.
```

```
Generate code to identify potential design patterns in the API based on common relationships and concept clusters in our ontology.
```

## Sample Workflow with Claude

Here's a sample workflow for refining the domain categorization:

1. **Examine current domain categorization**:
   ```
   cat ontology_output/domain_ontology_report.md
   ```

2. **Ask Claude to analyze and suggest improvements**:
   ```
   I notice we have many "Other" concepts in our domain ontology. Can you analyze these and suggest a more refined categorization scheme that would better represent IC design concepts?
   ```

3. **Implement Claude's suggestions**:
   ```
   Can you modify extract_domain_ontology.py to implement your suggested domain categorization?
   ```

4. **Test the changes**:
   ```
   python oa_ontology/extract_domain_ontology.py
   ```

5. **Review and refine**:
   ```
   cat ontology_output/domain_ontology_report.md
   ```

6. **Ask for additional insights**:
   ```
   Based on this refined categorization, what new relationships should we consider adding to better represent IC design concepts?
   ```

## Advanced Ontology Analysis

For more advanced analysis, try these prompts:

```
Can you write a script that calculates the semantic distance between concepts based on their properties and relationships in the ontology?
```

```
Help me create a natural language query interface for the ontology that would allow designers to ask questions like "What objects are used to represent routing?" and get meaningful answers.
```

```
Generate code to compare our extracted OpenAccess ontology with other IC design ontologies or data models to identify similarities and differences.
```

## Best Practices for Ontology Refinement with Claude

1. **Iterative Approach**: Refine the ontology in small steps, reviewing results after each change.

2. **Domain-Specific Context**: Always include specific IC design terminology in your prompts to help Claude understand the domain.

3. **Concrete Examples**: When asking for improvements, provide concrete examples of what you're trying to achieve.

4. **Code Review**: Ask Claude to explain the changes it's making to ontology extraction code before implementing them.

5. **Visual Verification**: Use the visualization tools to verify that changes to the ontology structure make sense.

6. **Maintain Semantic Consistency**: Ensure that new relationships and categorizations maintain a consistent semantic model.

## Common Ontology Refinement Tasks

### Adding a New Domain

```
I'd like to add a "Verification" domain to our ontology to capture concepts related to design rule checking and verification. Can you modify extract_domain_ontology.py to include this domain and suggest concepts that might belong to it?
```

### Refining Relationship Detection

```
Our current relationship detection between classes doesn't capture the "IMPLEMENTS" relationship where one class implements a behavior defined by another. Can you enhance extract_domain_ontology.py to detect this pattern?
```

### Creating Domain-Specific Views

```
Can you write a script that extracts just the Physical domain concepts and their relationships to create a simplified view for layout engineers?
```

## Conclusion

Claude Code is a powerful tool for ontology refinement, especially when working with complex technical domains like IC design. By using these prompting strategies and workflows, you can effectively leverage Claude's capabilities to enhance and extend the OpenAccess ontology.

Remember that ontology development is an iterative process. Regular review and refinement will lead to a more accurate and useful representation of the domain knowledge embedded in the OpenAccess API.
