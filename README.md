# Diagram and Code Alignment Tool `diagram-code-auditor`

**Table of Contents**

1. [Introduction](#introduction)
2. [Quick Start Guide](#quick-start-guide)
3. [Code-Diagram Mapping](#code-diagram-mapping)
4. [Key Features](#key-features)
5. [Limitations](#limitations)
6. [Error Messages](#error-messages)
7. [Diagram Requirements](#diagram-requirements)
8. [Workflow](#workflow)
9. [Common Output Examples](#common-output-examples)
10. [Adding the Pre-Commit Hook](#adding-the-pre-commit-hook)
11. [Libraries Used](#libraries-used)

---

## Introduction

The `diagram-code-auditor` ensures that **Python and PHP code** and diagrams remain synchronized by validating the consistency of class definitions and methods during the development workflow. It integrates with `pre-commit` to prevent discrepancies between code and diagram files from being committed.

It also has the capability to automatically generate diagrams for already existing **Python** code files. 

---

## Quick Start Guide

### Prerequisites

1. Python 3.8+
2. PHP 7.4+
3. Composer (for PHP dependencies)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/iomiras-diagram_code_auditor.git
   cd iomiras-diagram_code_auditor
   ```

2. Install Python dependencies (if any).

3. Install PHP dependencies using Composer:

   ```bash
   composer install
   ```

4. Verify the directory structure matches the provided template (see [Directory Structure](#directory-structure)).

5. Configure `code_diagram_mapping.json` to map your code files to diagram files.

6. (Optional) Add the pre-commit hook (see [Adding the Pre-Commit Hook](#adding-the-pre-commit-hook)).

7. Explore existing files in the repository to understand usage. You can run the project using these files to see how it works.

### Running the Tool
1. Diagram Code Auditor can be run in two modes:
    - **Automatic Mode**: Run the `diagram_code_auditor.py` script with the paths to your code file and diagram file.
    - **Manual Mode**: Run the `diagram_code_auditor.py` script with the paths to your code file and diagram file. The script will prompt you to add missing classes and methods to the diagram.
2. Diagram Generator can only be run in manual mode. Run the `diagram_generator.py` script with the path to your code file. The script will prompt you to generate a diagram for the code file.

---

## Code-Diagram Mapping

The `code_diagram_mapping.json` file is a crucial configuration file that maps code files to their corresponding diagram files. This ensures that the `diagram-code-auditor` knows which diagram to validate against each code file.

### Purpose

- **Automates Mapping**: Automatically links each code file to its associated diagram.
- **Simplifies Validation**: Ensures accurate validation during pre-commit or manual checks.
- **Supports Multiple Mappings**: Handles mappings for both Python and PHP code files.

### Structure

The file is a JSON object where each key-value pair represents a mapping:

```json
{
  "classes_examples/classes.py": "diagram_examples/diagram_py.py",
  "classes_examples/classes.php": "diagram_examples/diagram_php.py"
}
```

- **Key**: Path to the code file (relative to the repository root).
- **Value**: Path to the diagram file associated with the code file.

### How to Set It Up

1. Create a `code_diagram_mapping.json` file in the root of your repository.
2. Add mappings for each code file and its corresponding diagram file.
3. Ensure the paths are accurate and relative to the repository root.

### Example

For the following directory structure:

```
project-root/
├── classes_examples/
│   ├── classes.py
│   └── classes.php
├── diagram_examples/
│   ├── diagram_py.py
│   └── diagram_php.py
```

The `code_diagram_mapping.json` would look like:

```json
{
  "classes_examples/classes.py": "diagram_examples/diagram_py.py",
  "classes_examples/classes.php": "diagram_examples/diagram_php.py"
}
```

### Using Example Files

The repository contains example files for both code and diagrams under `classes_examples/` and `diagram_examples/`. You can use these files to:

- Understand how the tool works.
- Test its functionality.
- Explore different scenarios by modifying the example files.

---

## Key Features

### Language-Specific Parsing

Parses Python `.py` and PHP `.php` files to extract class definitions, methods, and relationships.

- **Examples**: Python: `ast`, PHP: `nikic/PHP-Parser`.

### Class and Method Validation

Ensures all classes and methods in the diagram are present in the code.

- **Examples**: Missing classes: `{Service6}`, Extra methods: `{restart_service()}`.

### Inheritance Handling

Propagates methods from parent to child classes for accurate validation.

- **Examples**: `classA >> Edge(label="inherits") >> classB`.

### Iteration in Diagrams

Supports relationships defined in loops within the diagram.

- **Examples**:
  ```python
  services = [service1, service2]
  for s in services:
      s >> Edge(label="method()") >> db
  ```

---
## Edge Styles and Use Cases

### Edge Styles

1. `style="solid", color="red"`: Interclass functions.

2. `style="dotted", color="black"`: Assumed connections.

3. `style="dashed", color="blue"`: Self-referential methods.

4. `style="dashed", color="darkgreen"`: Inheritance relationships.

### Use Cases

1. #### Diagram Creation:
   - Automatically generate diagrams from code files.
   - Define interclass relationships using function calls, attributes, or loops.

2. #### Diagram Auditing:
   - Validate diagrams against code to ensure alignment.

Highlight discrepancies in classes or methods.
---
## Limitations

| **Limitation**             | **Details**                                                                                                    |
| -------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Classes Defined as Strings | Classes initialized as strings in diagrams will be recreated as new nodes, not linked to existing definitions. |
| Method Connections         | New methods are self-referential in diagrams, as no relationship to other classes is specified.                |
| File Dependency            | Cross-file dependencies are not supported.                                                                     |
| Bidirectional Arrows       | Connections must be unidirectional (`>>`).                                                                     |
| Dynamic Method Iteration   | Iterating over dynamic lists of methods is not supported.                                                      |

---

## Error Messages

| **Error Message**                                  | **Cause**                                           | **Solution**                                                    |
| -------------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------- |
| `[Error] Unsupported file type.`                   | File is not `.py` or `.php`.                        | Use only supported file types for analysis.                     |
| `[Error] Invalid diagram syntax.`                  | Diagram file has a syntax error.                    | Correct the syntax in the diagram file.                         |
| `[Error] Validation failed for the updated file.`  | Updated diagram file failed validation.             | Review and fix the diagram file content.                        |
| `[Warning] Variable referenced before assignment.` | Class variable in diagram not properly initialized. | Ensure all class variables are assigned before use in diagrams. |

---

## Diagram Requirements

| **Requirement**              | **Description**                                                                      |
| ---------------------------- |--------------------------------------------------------------------------------------|
| Explicit Method Declarations | Methods must be explicitly declared before inheritance or relationships.             |
| Inheritance                  | Use `child >> Edge(label="inherits") >> parent` to define inheritance relationships. |
| Nested Clusters              | Supports hierarchical relationships using nested `with` blocks.                      |
| Iteration                    | Allows loops to declare multiple relationships.                                      |
| Assignments                  | Variables must map directly to classes or lists of classes.                          |

---

## Common Output Examples

## Potential Output Examples

### Example 1: Discrepancies Found

```bash
git commit -m "test"
****************************************************
Analyzing File Pair:
   File: classes_examples/classes.php
   Diagram: diagram_examples/diagram_php.py

===== Comparison Results =====
[Error] Extra Classes in Code classes_examples/classes.php:
{'ClassA'}

[Error] Extra Methods in Code classes_examples/classes.php:
{'ClassA': {'get_name()'}}

❌ Discrepancies found!

****************************************************
Analyzing File Pair:
   File: classes_examples/classes.py
   Diagram: diagram_examples/diagram_py.py

✅ Files are in sync!

****************************************************
⚠️ No diagram mapping found for diagram_code_auditor.py. Skipping.

Final Result:
❌ Discrepancies found! Commit aborted.
```

### Example 2: Successful Validation

```bash
git commit -m "all files synced"
****************************************************
Analyzing File Pair:
   File: classes_examples/classes.py
   Diagram: diagram_examples/diagram_py.py

✅ Files are in sync!

Final Result:
✅ All files are in sync! Proceeding with commit.
```

---

### Unsupported File Type

If the file type is unsupported:

```bash
[Error] Unsupported file type. Only .py and .php are supported.
```

### Invalid Diagram Syntax

If the diagram file contains syntax errors:

```bash
[Error] Invalid diagram syntax: unexpected EOF while parsing.
```

---

## Adding the Pre-Commit Hook

To integrate with `pre-commit`, follow these steps:

1. Save the script to `.git/hooks/pre-commit`:

```bash
files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|php)$')

if [ -z "$files" ]; then
    exit 0
fi

DIAGRAM_MAPPING="code_diagram_mapping.json"

discrepancies_found=0

for file in $files; do
    # Normalize path to match JSON keys (remove leading './')
    normalized_file=$(echo "$file" | sed 's|^\./||')

    diagram=$(python3 -c "import json; mapping = json.load(open('$DIAGRAM_MAPPING')); print(mapping.get('$normalized_file', ''))")

    if [ -n "$diagram" ]; then
        echo "Analyzing File Pair:"
        echo "   File: $normalized_file"
        echo "   Diagram: $diagram"

        python3 diagram_code_auditor.py "$normalized_file" "$diagram"
        status=$?
        if [ $status -ne 0 ]; then
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

2. Make the hook executable:

   ```bash
   chmod +x .git/hooks/pre-commit
   ```

3. Add `code_diagram_mapping.json` to define code-to-diagram mappings.

4. Committing staged files will trigger the validation.

---

## Libraries Used

| **Language**     | **Library**             | **Purpose**                                                         |
| ---------------- | ----------------------- | ------------------------------------------------------------------- |
| Python-Specific  | `ast`                   | Parses Python code to extract class and method definitions.         |
| PHP-Specific     | `nikic/PHP-Parser`      | Parses PHP code to generate an AST for class and method extraction. |
| Shared Libraries | `sys`, `pprint`, `json` | Handles command-line arguments, logging, and JSON operations.       |

---

### Use this tool to ensure code and diagrams are always in sync!