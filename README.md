# Diagram and Code Alignment Tool

This tool ensures that Python code and diagrams remain synchronized by validating the consistency of class definitions and methods during the development workflow. It integrates with `pre-commit` to prevent discrepancies between code and diagram files from being committed.

---

## Key Features

1. **Class and Method Validation**:
   - Ensures all classes in the diagram are defined in the code.
   - Verifies that all methods in the diagram exist in their respective code classes.

2. **Inheritance Handling**:
   - Propagates methods from parent classes to children for accurate comparison.

3. **Cluster and Nested With Handling**:
   - Handles nested `with` statements to parse diagrams with hierarchical clusters.

4. **Chain of Edges**:
   - Processes diagrams with chains of edges, e.g., `classA >> Edge(label="method1()") >> classB >> Edge(label="method2()") >> classC`.

5. **Iteration in Diagrams**:
   - Extracts relationships from diagrams using loops like `for var in [elt1, elt2]`.

6. **Assignment Parsing**:
   - Recognizes assignments in diagrams, e.g., `variable = SomeClass("ClassName")` or `variable = [classVar1, classVar2, ...]`.

---

## Workflow

### Pre-Commit Integration

1. **Diagram Mapping**:
   - The `diagram_mapping.json` file maps code files to their corresponding diagrams:
     ```json
     {
       "classes/classes.py": "diagrams/diagram.py",
       "classes/classes1.py": "diagrams/diagram1.py"
     }
     ```

2. **Pre-Commit Script**:
   - The script identifies staged Python files and validates them against their corresponding diagrams.
   - If discrepancies are found, the commit is aborted with detailed output.

---

## Diagram Requirements

1. **Method Declarations**:
   - Methods must be **explicitly** declared as `Edge` connections before inheritance or relationships.
   - Example:
     ```python
     user >> Edge(label="login()", style="dotted") >> user
     user >> Edge(label="inherits", style="dotted", color="gray") >> parent_user
     ```

2. **Inheritance**:
   - Use `Edge(label="inherits")` to depict inheritance.
   - Example:
     ```python
     child_class >> Edge(label="inherits") >> parent_class
     ```

3. **Clusters and Chains**:
   - Supports nested `with` blocks to define hierarchical clusters.
   - Handles chains of relationships, e.g., `classA >> Edge(label="method1()") >> classB >> Edge(label="method2()") >> classC`.

4. **Iteration**:
   - Supports relationships defined using loops:
     ```python
     services = [service1, service2, service3]
     for service in services:
         service >> Edge(label="inherits", style="dotted", color="gray") >> service_parent
     ```

5. **Assignments**:
   - Recognizes variables assigned to class definitions, e.g., `variable = SomeClass("ClassName")`.

---

## Code Requirements

1. **Class Definitions**:
   - Classes must be fully defined in the same file (cross-file definitions are not supported).

2. **Inheritance Handling**:
   - Standard Python inheritance (`class ChildClass(ParentClass):`) must be used.

3. **Method Definitions**:
   - All methods in the diagram must exist in their respective classes.
   - Self-referential methods must be implemented.

4. **Connections**:
   - Connections in the diagram are not compared with connections in the code, as the tool focuses on class and method alignment.

---

## Limitations

1. **File Dependency**:
   - Classes must be defined within the same file; cross-file dependencies are not handled.

2. **Edge Labels**:
   - Labels must be constant strings. Dynamic variables or references, such as `Edge(label=some_label)`, are not supported.

3. **Arrow Direction**:
   - All arrows in the diagram must be unidirectional (e.g., `classA >> classB`). Bidirectional arrows like `classA >> classB << classC` are not supported.

4. **Connection Comparison**:
   - Only relationships defined in the diagram are extracted, not the connections in the code, so connections cannot be compared just yet.

---

## How `check_diagram.py` Works in Details

### Diagram Parsing `DiagramVisitor(ast.NodeVisitor)`

### **1. `visit_Assign()`**
Handles assignments to identify and track:
- Variables assigned to class instances.
  - Example: `variable = SomeClass("ClassName")`
- Lists of class variables.
  - Example: `variable = [classVar1, classVar2, ...]`

Key Helper Methods:
- **`_process_assignment()`**: Determines the type of assignment and delegates to specific handlers.
- **`_handle_class_assignment()`**: Processes assignments like `variable = SomeClass("ClassName")` and maps `variable` to `ClassName`.
- **`_handle_list_assignment()`**: Processes assignments like `variable = [classVar1, classVar2]` and tracks class lists.

---

### **2. `visit_BinOp()`**
Processes binary operations to detect connections:
- Example: `classA >> Edge(label="method1()") >> classB`.

Key Helper Methods:
- **`_process_binop()`**: Handles complex connections, extracts methods from `Edge` labels, and identifies participating classes.
- **`_resolve_right_classes()`**: Resolves the right-hand side of connections to class IDs.

---

### **3. `visit_For()`**
Extracts connections from loops in diagrams:
- Example:
  ```python
  for service in [service1, service2]:
      service >> Edge(label="method()") >> target
  ```

Key Helper Methods:
- **`_process_for_loop()`**: Extracts loop variables and elements.
- **`_get_iteration_elements()`**: Resolves iteration elements for loops using lists or pre-defined variables.
- **`_process_binop_in_for()`**: Handles `BinOp` inside loops and creates connections.

---

### **4. Helper Functions**
- **`extract_method_from_edge()`**:
  - Extracts method names from `Edge` labels.
  - Example: `Edge(label="method()")` → `"method()"`.
- **`resolve_left()`**:
  - Recursively resolves the left-hand side of connections to identify class variables.

---

### **5. Adding Connections**
- **`add_to_connections()`**:
  - Creates connections between classes using extracted methods.
  - Handles both `>>` (right arrow) and `<<` (left arrow) operators.
- **`add_class_to_methods()`**:
  - Maps methods to their respective classes and handles inheritance relationships.

---

## Code Parsing `CodeVisitor(ast.NodeVisitor)`

### **1. `visit_ClassDef()`**
Captures class definitions and their parent classes:
- Tracks class names, parent classes, and methods.

Key Helper Methods:
- **`_extract_parents()`**:
  - Extracts parent classes for inheritance.

---

### **2. `visit_FunctionDef()`**
Tracks methods within classes, excluding constructors (`__init__`):
- Example:
  ```python
  class MyClass:
      def my_method(self):
          pass
  ```

---

### **3. Inheritance Resolution**
Propagates parent class methods to child classes:
- **`resolve_inheritance()`**:
  - Ensures that methods inherited from parent classes are included in the child class.

---

### Comparison

1. **Class Comparison `compare_classes()`**:
   - Matches classes in the code with classes in the diagram.
   - Flags missing or extra classes.

2. **Method Comparison `compare_methods()`**:
   - Matches methods within each class.
   - Flags missing or extra methods.

---

## Output Examples

### Fully Synchronized Code and Diagram
```text
✅ Code and Diagram are in sync!
```

### Missing Classes
```text
===== Comparison Results =====

Missing Classes in Code:
{'Service'}

Missing Methods in Code:
{'Service1': {'store_data()'},
 'Service2': {'store_data()'},
 'Service3': {'store_data()'}}
 
❌ Discrepancies found! Commit aborted.
```

### Extra Methods
```text
===== Comparison Results =====

Extra Methods in Code:
{'Service1': {'restart_service()'}}

❌ Discrepancies found! Commit aborted.
```

---

## Adding the Pre-Commit Hook

1. Save the script to `.git/hooks/pre-commit`:
    ```bash
   #!/bin/bash
   
   # Get a list of staged Python files
   files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
   if [ -z "$files" ]; then
        exit 0
   fi
   
   # Path to the diagram mapping file
   DIAGRAM_MAPPING="diagram_mapping.json"
   
   # Run the Python script for each file and its corresponding diagram
   for file in $files; do
        # Normalize path to match JSON keys (remove leading './')
        normalized_file=$(echo "$file" | sed 's|^\./||')
        
        # Fetch corresponding diagram using the mapping
        diagram=$(python3 -c "import json; mapping = json.load(open('$DIAGRAM_MAPPING')); print(mapping.get('$normalized_file', ''))")
        
        if [ -n "$diagram" ]; then
            echo "File: $normalized_file"
            echo "Diagram: $diagram"
            echo "Checking $normalized_file against $diagram..."
            python3 check_diagram.py "$normalized_file" "$diagram"
            status=$?
            if [ $status -ne 0 ]; then
                exit 1
            fi
        else
            echo "⚠️ No diagram mapping found for $normalized_file. Skipping."
            echo
        fi
    done

    exit 0
    ```
   Then run to add the pre-commit hook:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

2. Add `diagram_mapping.json` to the root of the repository:
   ```json
   {
     "classes/classes.py": "diagrams/diagram.py",
     "classes/classes1.py": "diagrams/diagram1.py"
   }
   ```

3. Staged files are automatically checked before committing. 

Use this tool to ensure consistent documentation and implementation across your project!