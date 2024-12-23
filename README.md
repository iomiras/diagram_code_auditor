# Diagram and Code Alignment Tool `diagram-code-auditor`

This tool ensures that  **Python and PHP code**  and diagrams remain synchronized by validating the consistency of class definitions and methods during the development workflow. It integrates with  `pre-commit`  to prevent discrepancies between code and diagram files from being committed.

---

## Libraries Used

### Python-Specific:

-   **`ast`**: The Python Abstract Syntax Tree library parses and analyzes Python code files, extracting class definitions, methods, and relationships in a structured manner.

### PHP-Specific:

-   **`nikic/PHP-Parser`**: Generates an Abstract Syntax Tree (AST) from PHP code, allowing the tool to extract class definitions, methods, and relationships for comparison.
-   **`subprocess`**: Executes the PHP script (`php_parser.php`) to generate an AST JSON file for PHP code.

### Shared Libraries:

-   **`sys`**: Handles command-line arguments to allow the script to dynamically process specified files during execution.
-   **`pprint`**: Provides clean, human-readable output for debug logs and comparison results.
-   **`json`**: Manages the mapping of diagram files to their corresponding code files, enabling seamless integration with the pre-commit script.

---

## Key Features
1. **Language-Specific Parsing**:
    
    -   Python: Processes Python  `.py`  files using the  `ast`  library.
    -   PHP: Parses PHP  `.php`  files using  `nikic/PHP-Parser`  and processes the generated AST JSON file.
    - 
2. **Class and Method Validation**:
   - Ensures all classes in the diagram are defined in the code.
   - Verifies that all methods in the diagram exist in their respective code classes.

3. **Inheritance Handling**:
   - Propagates methods from parent classes to children for accurate comparison.

4. **Cluster and Nested `with` Handling**:
   - Processes diagrams with hierarchical clusters defined using nested `with` blocks.

5. **Chain of Edges**:
   - Handles chains of relationships like:
     ```python
     classA >> Edge(label="method1()") >> classB >> Edge(label="method2()") >> classC
     ```

6. **Iteration in Diagrams**:
   - Extracts relationships defined using loops, e.g.:
     ```python
     services = [service1, service2]
     for service in services:
         service >> Edge(label="method()") >> target
     ```

7. **Assignment Parsing**:
   - Recognizes variables assigned to class definitions or lists of class definitions:
     ```python
     variable = SomeClass("ClassName")
     variable_list = [classVar1, classVar2]
     ```

8. **Unidirectional Connections**:
   - All diagram connections must be defined in a single direction (e.g., `>>`).

---

## Workflow

### Abstract description
1.  **Determine File Type**:
    
    -   Checks the file extension (`.py`  for Python or  `.php`  for PHP).
2.  **Handle Python Files**:
    
    -   Processes  `.py`  files using the  `ast`  library to extract classes and methods.
3.  **Handle PHP Files**:
    
    -   Runs the  `php_parser.php`  script to generate an AST JSON file.
    -   Parses the AST JSON file to extract PHP classes and methods.
4.  **Compare Code and Diagram**:
    
    -   Validates the extracted classes and methods from both the code and diagram files.

### Pre-Commit Integration
1. **Diagram Mapping**:
   - The  `code_diagram_mapping.json`  file maps  **code files**  (Python or PHP) to their corresponding  **diagrams**:
     ```json
     {
       "classes/classes.py": "diagrams/diagram.py",
       "classes/classes.php": "diagrams/diagram.php"
     }
     ```

2. **Pre-Commit Script**:
   -  Identifies staged Python or PHP files and validates them against their corresponding diagrams.
   - If discrepancies are found, the commit is aborted with detailed output.

---

## Diagram Requirements

1. **Explicit Method Declarations**:
   - All methods **must be declared explicitly before** inheritance or relationships.
   - Example:
     ```python
     service_parent >> Edge(label="restart_service()", style="dotted") >> service_parent
     ```

2. **Inheritance**:
   - Use `Edge(label="inherits")` to define inheritance relationships:
     ```python
     child_class >> Edge(label="inherits", style="dotted") >> parent_class
     ```

3. **Nested Clusters**:
   - Supports hierarchical relationships using nested `with` blocks:
     ```python
     with Cluster("Backend Classes"):
         with Cluster("Service Classes"):
             service1 = Server("Service1")
     ```

4. **Iteration**:
   - For loops can simplify the declaration of multiple relationships:
     ```python
     services = [service1, service2, service3]
     for service in services:
         service >> Edge(label="inherits", style="dotted") >> service_parent
     ```

5. **Assignments**:
   - Variables must directly map to classes or class lists:
     ```python
     service_parent = Server("Service")
     services = [service1, service2, service3]
     ```

---

## Limitations

1. **File Dependency**:
   - Classes must be defined within the same file; cross-file dependencies are not handled.

2. **Dynamic Method Iteration**:
   - Iterating over dynamic lists of method names (e.g., `for method in methods_list`) is not supported.

3. **Bidirectional Arrows**:
   - Connections must be unidirectional (e.g., `>>`).

4. **Connection Validation**:
   - Relationships are only extracted from the diagram, but not compared to code as the connections within the code itself are not extracted.

---

## How `diagram_code_auditor.py` Works in Detail

### **1. Diagram Parsing (`DiagramVisitor`)**

#### **`visit_Assign()`**:
Handles assignments and tracks:
- Variables assigned to class definitions:
  ```python
  variable = SomeClass("ClassName")
  ```
- Lists of class variables:
  ```python
  variable = [classVar1, classVar2]
  ```

#### **`visit_BinOp()`**:
Processes binary operations representing connections:
```python
classA >> Edge(label="method1()") >> classB
```

#### **`visit_For()`**:
Extracts relationships from loops, such as:
```python
for service in services:
    service >> Edge(label="inherits") >> parent_service
```

#### Helper Methods:
- **`_process_binop()`**: Resolves and validates connections in binary operations.
- **`_get_iteration_elements()`**: Extracts elements from iterable variables in loops.

---

### **2. Code Parsing (`CodeVisitor`)**

#### Python Code Parsing (`CodeVisitor`):

-   **`visit_ClassDef()`**: Captures class definitions and their parent classes:
    
    ```python
    class ChildClass(ParentClass):
        ...
    ```
    
-   **`visit_FunctionDef()`**: Extracts methods from classes while excluding  `__init__`.
    
-   **`resolve_inheritance()`**: Propagates methods from parent classes to child classes.

#### PHP Code Parsing (`parse_json()`):

-   Processes the JSON AST output generated by  `nikic/PHP-Parser`.
-   Extracts class and method definitions from the parsed PHP code.

### Key Functionality:

1.  **Class Extraction**:
    
    -   Captures classes (`Stmt_Class`) and their parent classes (`extends`).
    -   Inherits methods from parent classes.
2.  **Method Extraction**:
    
    -   Ignores  `__construct()`  and adds method names with  `()`  suffix.
    -   Aggregates methods under their respective classes.
    Example:

    ```php
    class Service1 extends BaseService {
        public function restartService() {}
    }
    ```

    Generated output:

    ```python
    code_classes = ["Service1", "BaseService"]
    code_methods = {
        "BaseService": ["restartService()"],
        "Service1": ["restartService()"]
    }
    ```
---

### **3. Comparison**

#### **Class Comparison**:
Validates whether classes in the diagram exist in the code and vice versa.

#### **Method Comparison**:
Ensures methods in the diagram are defined in the corresponding code classes.

---

## Output Examples

### Fully Synchronized Code and Diagram
```text
✅ Code [Python or PHP code filename] and Diagram are in sync!
```

### Missing Classes or Methods
```text
===== Comparison Results =====

Missing Classes in Code:
{'Service'}

Missing Methods in Code:
{'Service1': {'restart_service()'}}

❌ Discrepancies found! Commit aborted.
```

### Extra Methods
```text
===== Comparison Results =====

Extra Methods in Code:
{'Firewall': {'filter_traffic()', 'login()'}}

❌ Discrepancies found! Commit aborted.
```

---

## Adding the Pre-Commit Hook

Follow these steps to integrate the tool with `pre-commit`:

1. Save the script to `.git/hooks/pre-commit`:
    ```bash
    files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|php)$')

    if [ -z "$files" ]; then
        exit 0
    fi
    DIAGRAM_MAPPING="code_diagram_mapping.json"
    for file in $files; do
        normalized_file=$(echo "$file" | sed 's|^\./||')

    diagram=$(python3 -c "import json; mapping = json.load(open('$DIAGRAM_MAPPING')); print(mapping.get('$normalized_file', ''))")

    if [ -n "$diagram" ]; then
        echo "File: $normalized_file"
        echo "Diagram: $diagram"
        echo "Checking $normalized_file against $diagram..."
        python3 diagram_code_auditor.py "$normalized_file" "$diagram"
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

2. Make the hook executable:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

3. Add the `code_diagram_mapping.json` file:
   ```json
   {
     "classes/classes.py": "diagrams/diagram.py"
   }
   ```

4. Staged files will be validated against their diagrams before committing.

--- 

Use this tool to ensure code and diagrams are always in sync!