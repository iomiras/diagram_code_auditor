import ast
import sys
import json
import glob
import subprocess
from pprint import pprint
from logging_utils import log_error
from code_parser import analyze_code
from diagram_parser import analyze_diagram

def compare_classes(code_classes: list, diagram_classes: list) -> tuple:
    """
    Compare classes between code and diagram.
    
    Returns:
        tuple: (missing_classes, extra_classes)
    """
    missing_classes = set(diagram_classes) - set(code_classes)
    extra_classes = set(code_classes) - set(diagram_classes)
    return missing_classes, extra_classes


def compare_methods(code_class_to_methods: dict, diagram_class_to_methods: dict) -> tuple:
    """
    Compare methods between classes in code and diagram.
    
    Returns:
        tuple: (missing_methods, extra_methods)
    """
    missing_methods = {}
    extra_methods = {}
    all_classes = set(code_class_to_methods) | set(diagram_class_to_methods)

    for cls in all_classes:
        code_methods = set(code_class_to_methods.get(cls, []))
        diagram_methods = set(diagram_class_to_methods.get(cls, []))

        missing = diagram_methods - code_methods
        extra = code_methods - diagram_methods

        if missing:
            missing_methods[cls] = missing
        if extra:
            extra_methods[cls] = extra

    return missing_methods, extra_methods


def parse_json(code_tree: str) -> tuple:
    """
    Parse JSON AST representation of PHP code.
    
    Args:
        code_tree: JSON string containing PHP AST
        
    Returns:
        tuple: (classes, methods)
    """
    code_classes = []
    code_methods = {}
    parsed_json = json.loads(code_tree)
    if len(parsed_json) == 0:
        statements = parsed_json[0]['stmts']
    else:
        statements = parsed_json
    
    for stmt in statements:
        if stmt['nodeType'] == 'Stmt_Class':
            class_name = stmt['name']['name']
            
            # Handle inheritance
            if stmt['extends']:
                parent_class = stmt['extends']['name']
                if parent_class in code_methods:
                    code_methods[class_name] = code_methods[parent_class].copy()
                    
            code_classes.append(class_name)
            
            # Process class methods
            for class_stmt in stmt['stmts']:
                if class_stmt['nodeType'] == 'Stmt_ClassMethod':
                    method_name = class_stmt['name']['name']
                    if method_name == '__construct':
                        continue
                    method_name += '()'
                    
                    if class_name in code_methods:
                        code_methods[class_name].append(method_name)
                    else:
                        code_methods[class_name] = [method_name]

    return code_classes, code_methods


def parse_code_file(file_path: str) -> tuple:
    """
    Parse a code file (Python or PHP).
    
    Args:
        file_path: Path to the code file
        
    Returns:
        tuple: (classes, methods)
    """
    php_parser = 'php_parser.php'

    if file_path.endswith('.py'):
        with open(file_path, 'r') as f:
            content = f.read()
        return analyze_code(content)
    elif file_path.endswith('.php'):
        json_output = './tmp/ast.json'
        subprocess.run(['php', php_parser, file_path, json_output])
        with open(json_output, 'r') as f:
            content = f.read()
        return parse_json(content)
    else:
        log_error("Unsupported file type. Only .py and .php are supported.")
        sys.exit(1)


def main():
    code_file_name = sys.argv[1]
    diagram_file_name = sys.argv[2]
    discrepancies_found = False

    # Process the given code and diagram file pair
    try:
        code_classes, code_methods = parse_code_file(code_file_name)
    except FileNotFoundError:
        log_error(f"Error: Code file {code_file_name} not found.")
        discrepancies_found = True
        return

    all_diagram_classes = set()
    aggregated_diagram_methods = {}

    try:
        with open(diagram_file_name, "r") as f:
            diagram_content = f.read()
    except FileNotFoundError:
        log_error(f"Error: Diagram file {diagram_file_name} not found.")
        discrepancies_found = True
        return

    # Analyze diagram
    diagram_classes, diagram_methods, all_connections, var_to_class = analyze_diagram(diagram_content)
    all_diagram_classes.update(diagram_classes)
    for cls, methods in diagram_methods.items():
        aggregated_diagram_methods.setdefault(cls, set()).update(methods)

    # Compare classes and methods
    missing_classes, extra_classes = compare_classes(code_classes, all_diagram_classes)
    missing_methods, extra_methods = compare_methods(code_methods, aggregated_diagram_methods)

    # Show results for each file and track discrepancies
    if missing_classes or extra_classes or missing_methods or extra_methods:
        discrepancies_found = True
        print("\n===== Comparison Results =====")
        if missing_classes:
            log_error(f"Missing Classes in Code {code_file_name}:")
            pprint(missing_classes)

        if extra_classes:
            log_error(f"Extra Classes in Code {code_file_name}:")
            pprint(extra_classes)

        if missing_methods:
            log_error(f"Missing Methods in Code {code_file_name}:")
            pprint(missing_methods)

        if extra_methods:
            log_error(f"Extra Methods in Code {code_file_name}:")
            pprint(extra_methods)

    # Exit based on discrepancies
    if discrepancies_found:
        print("\n❌ Discrepancies found!\n")
        sys.exit(1)
    else:
        print("\n✅ Files are in sync!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()