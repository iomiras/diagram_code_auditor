
# **Diagram-Code Auditor Presentation**

---

## **What Does It Do?**
1. **Validation**  
   - Ensures all classes and methods in diagrams are defined in the corresponding code files.

2. **Automatic Updates**  
   - Adds missing classes and methods from the code to the diagram:
     - **New Classes**: Automatically added as nodes with a default "Action" type.
     - **New Methods**: Added as self-referential edges (connected back to the same class).

3. **Pre-Commit Integration**  
   - Blocks commits if code and diagrams are inconsistent, maintaining alignment during development.

---

## **How It Works**

### **1. Mapping Code to Diagrams**
- **File**: `code_diagram_mapping.json`
- **Purpose**: Links code files to their respective diagrams to validate the correct relationships.
- **Example**:
   ```json
   {
     "classes_examples/classes.py": "diagram_examples/diagram_py.py",
     "classes_examples/classes.php": "diagram_examples/diagram_php.py"
   }
   ```

---

### **2. Parsing Code**
- **Python**: Uses the Abstract Syntax Tree (AST) module to extract classes and methods.
- **PHP**: 
  - Runs `nikic/PHP-Parser` to generate an AST in JSON format.
  - Python processes this JSON to extract classes and methods.

---

### **3. Handling Discrepancies**
- **New Classes**:  
  - Added as nodes with a default "Action" type.  
  - Example:  
    ```python
    Service6 = Action("Service6")
    ```

- **New Methods**:  
  - Added as self-referential edges since relationships are unknown.  
  - Example:  
    ```python
    Service6 >> Edge(label="new_method()") >> Service6
    ```

- **User Confirmation**:  
  - Prompts the user to approve updates. If unresolved discrepancies remain, the commit is blocked.

---

## **Limitations**
1. **String-Defined Classes in Diagrams**  
   - Classes initialized as strings are treated as new, even if they exist in the code.
   ```python
    Server("Service6") >>  Edge(label="filter_traffic()", style="dotted") >> Server("Service6")
    ```

2. **Default Relationships for Methods**  
   - New methods connect only to the same class due to the lack of inferred relationships.

3. **Diagram Conventions**  
   - Diagrams must follow specific structural and syntax rules to ensure compatibility.

---

## **Example Scenarios**

### **Validation Success**
```text
✅ Code and Diagram are in sync!
```

### **Validation Failure**
```text
===== Comparison Results =====

Missing Classes:
{ "Service6" }

Missing Methods:
{ "Service1": [ "restart_service()" ] }
```

### **Adding New Classes**
```python
# Added automatically to the diagram
Legend = Action("Legend")
```

### **Adding New Methods**
```python
# Added as a self-referential edge
auth >> Edge(label="restart()") >> auth
```

---

## **Try It Yourself**
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/diagram-code-auditor.git
   cd diagram-code-auditor
   ```

2. **Run the Tool**:
   ```bash
   python diagram_code_auditor.py classes_examples/classes.py diagram_examples/diagram_py.py
   ```

3. **Explore Examples**:
   - Existing files in `classes_examples/` and `diagram_examples/` demonstrate its functionality.

---
```