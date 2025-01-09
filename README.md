### Project Documentation: **`iomiras/diagram_code_auditor`**

#### Overview
This project facilitates the validation and visualization of class relationships and methods in Python and PHP projects by comparing source code against predefined diagrams. The system includes tools for generating diagrams from code and auditing the consistency between code and diagrams.

---

### Features
1. **Diagram Creation**: Automatically generates diagrams representing class relationships, methods, and connections in Python and PHP codebases.
2. **Code Diagram Auditing**: Compares code files against pre-defined diagrams to identify discrepancies in classes, methods, and relationships.
3. **Cross-Language Support**: Handles both Python and PHP code files.

---

### Workflow
#### Pre-Commit Integration
1. **File Identification**:
   - Detect staged `.py` or `.php` files.
   - Retrieve corresponding diagrams using `code_diagram_mapping.json`.
2. **Code Parsing**:
   - Python: Extract classes, methods, and attributes using the `ast` library.
   - PHP: Extract similar data using `nikic/php-parser` and custom scripts.
3. **Comparison**:
   - Validate classes and methods between code and diagrams.
   - Report missing or extra elements.
4. **Commit Enforcement**:
   - Prevent commits with discrepancies.

#### Diagram Creation
1. **Code Parsing**:
   - Parse code files to extract classes, methods, and attributes.
   - Identify relationships (e.g., method calls, property assignments).
   - If impossible to determine, assume connections.
   - **Edge Styling for Diagrams**:
     - **`style="solid", color="red"`**: Inter-class function calls.
     - **`style="dotted", color="black"`**: Assumed connections.
     - **`style="dashed", color="blue"`**: Self-referencing methods.
     - **`style="dashed", color="darkgreen"`**: Inheritance relationships.
2. **Diagram Generation**:
   - Create a visual representation of classes and relationships using the `diagrams` library.
   - Save diagrams as `.py` files.

---

### Project Structure
```
iomiras-diagram_code_auditor/
├── code_diagram_mapping.json               # Maps code files to corresponding diagram files.
├── diagram_code_auditor.py                 # Main script for auditing code against diagrams.
├── diagram_creator.py                      # Main script for generating diagrams from code.
├── diagram_code_auditor_test_examples/     # Example cases for the auditing workflow.
│   ├── classes.php                         # Example PHP classes code file.
│   ├── classes.py                          # Example Python classes code file.
│   ├── diagram_php.py                      # Corresponding diagram for `classes.php`.
│   └── diagram_py.py                       # Corresponding diagram for `classes.py`.
├── diagram_creator_test_examples/          # Example cases for diagram creation.
│   ├── animal_classes.py                   # Example Python code file.
│   ├── library_classes.py                  # Example Python code file.
│   ├── project_classes.php                 # Example PHP code file.
│   ├── project_classes.py                  # Example Python code file.
│   └── diagrams_from_codes/                # Generated diagrams from code files.
│       ├── diagram_for_animal_classes.py
│       └── diagram_for_project_classes.py
└── utils/                                  # Utility scripts for parsing and logging.
    ├── composer.json                       # PHP dependencies.
    ├── connection_parser.php               # Extracts connections from PHP code.
    ├── connection_parser.py                # Extracts connections from Python code.
    ├── diagram_parser.py                   # Parses diagram files.
    ├── logging_utils.py                    # Logging utilities.
    ├── php_code_parser.py                  # Parses PHP classes, methods, and attributes.
    ├── python_code_parser.py               # Parses Python classes, methods, and attributes.
    └── tmp/                                # Temporary storage for parsed PHP data in a JSON form.
```

---

### Limitations
1. **Cross-File Dependencies**: Relationships spanning multiple files are not supported.
2. **Dynamic Method Iteration in Diagrams**: Iterating over dynamic lists of methods is unsupported.
3. **Inheritance Representation**: Only supports `child >> Edge(label="inherits") >> parent`.
4. **Explicit Method Declarations**: Methods of the parent class must be explicitly declared before inheritance relationships.
5. **Unidirectional Connections**: All connections are represented as unidirectional (`>>`).
6. **No Support for Interfaces, Traits, or Abstract Classes**: Only standard classes are supported.
7. **Assumed Connections May Be Incorrect**: Assumed connections must be resolved manually.

---

### Input Values for Auditor and Creator

#### **Diagram Code Auditor**
The auditor compares code files with their corresponding diagram files to identify discrepancies in classes, methods, and relationships. It requires:
- **Code File**: A `.py` (Python) or `.php` (PHP) source code file containing class definitions, methods, and relationships.
- **Diagram File**: A diagram representation file generated using the `diagrams` library, containing expected class structures, methods, and connections.

#### **Diagram Creator**
The creator generates diagrams from code files to visually represent class relationships and method interactions. It requires:
- **Code File**: A `.py` or `.php` source code file from which classes, methods, attributes, and connections are extracted.

Both tools rely on:
- **Mapping File (`code_diagram_mapping.json`)**: A JSON file that maps code files to their corresponding diagram files. This ensures accurate pairing during auditing.

---

### Pre-Commit Script
```bash
#!/bin/bash

files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|php)$')

if [ -z "$files" ]; then
    exit 0
fi

DIAGRAM_MAPPING="code_diagram_mapping.json"
discrepancies_found=0

for file in $files; do
    normalized_file=$(echo "$file" | sed 's|^\./||')
    diagram=$(python3 -c "import json; mapping = json.load(open('$DIAGRAM_MAPPING')); print(mapping.get('$normalized_file', ''))")

    if [ -n "$diagram" ]; then
        python3 diagram_code_auditor.py "$normalized_file" "$diagram"
        if [ $? -ne 0 ]; then
            discrepancies_found=1
        fi
    else
        echo "⚠️ No diagram mapping found for $normalized_file. Skipping."
    fi
done

if [ $discrepancies_found -eq 1 ]; then
    echo "❌ Discrepancies found! Commit aborted."
    exit 1
else
    echo "✅ All files are in sync! Proceeding with commit."
    exit 0
fi
```

---

### Example Outputs
#### Successful Commit
```
git commit -m "all files synced"
****************************************************
Analyzing File Pair:
   File: diagram_code_auditor_test_examples/classes.py
   Diagram: diagram_code_auditor_test_examples/diagram_py.py

✅ Files are in sync!

Final Result:
✅ All files are in sync! Proceeding with commit.
```

#### Failed Commit
```
git commit -m "test"
****************************************************
Analyzing File Pair:
   File: diagram_code_auditor_test_examples/classes.php
   Diagram: diagram_code_auditor_test_examples/diagram_php.py

===== Comparison Results =====
[Error] Extra Classes in Code diagram_code_auditor_test_examples/classes.php:
{'ClassA'}

[Error] Extra Methods in Code diagram_code_auditor_test_examples/classes.php:
{'ClassA': {'methodB()'}}

❌ Discrepancies found!

****************************************************
Analyzing File Pair:
   File: diagram_code_auditor_test_examples/classes.py
   Diagram: diagram_code_auditor_test_examples/diagram_py.py

✅ Files are in sync!

****************************************************
⚠️ No diagram mapping found for diagram_code_auditor.py. Skipping.

Final Result:
❌ Discrepancies found! Commit aborted.
```