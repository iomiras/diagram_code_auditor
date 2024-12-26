# Diagram and Code Alignment Tool `diagram-code-auditor`

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start Guide](#quick-start-guide)
3. [Code-Diagram Mapping](#code-diagram-mapping)
4. [Key Features](#key-features)
5. [Edge Styles and Use Cases](#edge-styles-and-use-cases)
6. [Potential Output Examples](#potential-output-examples)
7. [Adding the Pre-Commit Hook](#adding-the-pre-commit-hook)
8. [Libraries Used](#libraries-used)

---

## Introduction

The `diagram-code-auditor` ensures that **Python and PHP code** and diagrams remain synchronized by validating the consistency of class definitions and methods during the development workflow. It integrates with `pre-commit` hooks to prevent discrepancies between code and diagram files from being committed.

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

Run the `diagram_code_auditor.py` script with the paths to your code file and diagram file:

```bash
python diagram_code_auditor.py classes_examples/classes.py diagram_examples/diagram_py.py
```

---

## Code-Diagram Mapping

The `code_diagram_mapping.json` file is a crucial configuration file that maps code files to their corresponding diagram files. This ensures that the `diagram-code-auditor` knows which diagram to validate against each code file.

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

### Using Example Files

The repository contains example files for both code and diagrams under `classes_examples/` and `diagram_examples/`. These files demonstrate how the tool works and can be used for testing and exploration.

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

### Iteration in Diagrams

Supports relationships defined in loops within the diagram.

### Diagram Syntax Validation

Validates the syntax of the updated diagram before finalizing changes.

---

## Edge Styles and Use Cases

### Edge Styles

1. `style="solid", color="red"`: Interclass functions.
2. `style="dotted", color="black"`: Assumed connections.
3. `style="dashed", color="blue"`: Self-referential methods.
4. `style="dashed", color="darkgreen"`: Inheritance relationships.

### Use Cases

1. **Diagram Creation**:
   - Automatically generate diagrams from code files.
   - Define interclass relationships using function calls, attributes, or loops.

2. **Diagram Auditing**:
   - Validate diagrams against code to ensure alignment.
   - Highlight discrepancies in classes or methods.

---

## Potential Output Examples

### Example 1: Discrepancies Found

```bash
git commit -m "test"
****************************************************
Analyzing File Pair:
   File: classes_examples/classes.php
   Diagram: diagram_examples/diagram_php.py

[Warning] Warning: Left service not found in variable_to_class map.

===== Comparison Results =====
[Error] Extra Classes in Code classes_examples/classes.php:
{'Legent'}

[Error] Extra Methods in Code classes_examples/classes.php:
{'Legent': {'get_name()'}}

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

## Adding the Pre-Commit Hook

To integrate the `diagram-code-auditor` with `pre-commit`, follow these steps:

1. Save the following script to `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Get a list of staged Python and PHP files
files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|php)$')

if [ -z "$files" ]; then
    exit 0
fi

# Path to the diagram mapping file
DIAGRAM_MAPPING="code_diagram_mapping.json"

discrepancies_found=0

# Run the Python script for each file and its corresponding diagram
for file in $files; do
    # Normalize path to match JSON keys (remove leading './')
    normalized_file=$(echo "$file" | sed 's|^\./||')

    # Fetch corresponding diagram using the mapping
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

# Final exit based on discrepancies
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

---

## Libraries Used

| **Language**     | **Library**             | **Purpose**                                                         |
| ---------------- | ----------------------- | ------------------------------------------------------------------- |
| Python-Specific  | `ast`                   | Parses Python code to extract class and method definitions.         |
| PHP-Specific     | `nikic/PHP-Parser`      | Parses PHP code to generate an AST for class and method extraction. |
| Shared Libraries | `sys`, `pprint`, `json` | Handles command-line arguments, logging, and JSON operations.       |

---

Use this tool to ensure code and diagrams are always in sync!

