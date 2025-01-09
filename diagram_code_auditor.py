import ast
import sys
from pprint import pprint
from utils.logging_utils import log_error
from utils.python_code_parser import PythonCodeVisitor
from utils.diagram_parser import DiagramVisitor
from utils.php_code_parser import extract_php_data

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
        class_methods = set(code_class_to_methods.get(cls, []))
        diagram_methods = set(diagram_class_to_methods.get(cls, []))

        missing = diagram_methods - class_methods
        extra = class_methods - diagram_methods

        if missing:
            missing_methods[cls] = missing
        if extra:
            extra_methods[cls] = extra

    return missing_methods, extra_methods


def parse_python(file_path: str) -> tuple:
    """
    Parse and analyze a code file's content.

    Args:
        file_path: File path to the code file.

    Returns:
        tuple: (classes, methods, attributes)
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        tree = ast.parse(content)
    except SyntaxError as e:
        log_error(f"Error parsing code: {e}")
        return [], {}

    code_visitor = PythonCodeVisitor()
    code_visitor.visit(tree)
    
    return code_visitor.get_results()


def parse_php(file_path: str) -> tuple:
    """
    Parse and analyze a PHP code file's content.

    Args:
        file_path: File path to the PHP code file.
    Returns:
         tuple: (classes, methods, attributes)
    """
    return extract_php_data(file_path)


def parse_diagram_file(diagram_file_name: str) -> tuple:
    """
    Parse and analyze a diagram file's content.

    Args:
        diagram_file_name: File path to the diagram file.

    Returns:
        tuple: (classes, methods, connections, variable_mappings)
    """
    try:
        with open(diagram_file_name, "r") as f:
            diagram_content = f.read()
            tree = ast.parse(diagram_content)
    except SyntaxError as e:
        log_error(f"Error parsing diagram: {e}")
        sys.exit(1)

    diagram_visitor = DiagramVisitor()
    diagram_visitor.visit(tree)

    return diagram_visitor.get_results()


def parse_code_file(file_path: str) -> tuple:
    if file_path.endswith('.py'):
        return parse_python(file_path)
    elif file_path.endswith('.php'):
        return parse_php(file_path)
    else:
        log_error("Unsupported file type. Only .py and .php are supported.")
        sys.exit(1)


def output_results(code_file_name, missing_classes, extra_classes, missing_methods, extra_methods):
    print("\n===== Comparison Results =====")
    if missing_classes:
        log_error(f"Missing Classes in Code {code_file_name}:")
        pprint(missing_classes)
        print()

    if extra_classes:
        log_error(f"Extra Classes in Code {code_file_name}:")
        pprint(extra_classes)
        print()

    if missing_methods:
        log_error(f"Missing Methods in Code {code_file_name}:")
        pprint(missing_methods)
        print()

    if extra_methods:
        log_error(f"Extra Methods in Code {code_file_name}:")
        pprint(extra_methods)
        print()


def main():
    code_file_name = sys.argv[1]
    diagram_file_name = sys.argv[2]
    discrepancies_found = False

    # Process the given code and diagram file pair
    try:
        
        code_classes, class_methods, class_attributes = parse_code_file(code_file_name)
    except FileNotFoundError:
        log_error(f"Error: Code file {code_file_name} not found.")
        discrepancies_found = True
        return

    # Analyze diagram
    diagram_classes, diagram_methods, *_ = parse_diagram_file(diagram_file_name)

    # Compare classes and methods
    missing_classes, extra_classes = compare_classes(code_classes, diagram_classes)
    missing_methods, extra_methods = compare_methods(class_methods, diagram_methods)

    # Show results for each file and track discrepancies
    if missing_classes or extra_classes or missing_methods or extra_methods:
        discrepancies_found = True
        output_results(code_file_name, missing_classes, extra_classes, missing_methods, extra_methods)

    # Exit based on discrepancies
    if discrepancies_found:
        print("\n❌ Discrepancies found!\n")
        sys.exit(1)
    else:
        print("\n✅ Files are in sync!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()