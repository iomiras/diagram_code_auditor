import ast
import sys
from pprint import pprint

class DiagramVisitor(ast.NodeVisitor):
    def __init__(self):
        self.all_classes = []
        self.variable_to_class = {}
        self.all_connections = []
        self.last_left_classes = []
        self.all_class_to_methods = {}
        self.all_lists = {}

    def visit_Assign(self, node):
        if isinstance(node, ast.Assign):
            if isinstance(node.targets[0], ast.Name):
                variable = node.targets[0].id
                if isinstance(node.value, ast.Call):
                    for arg in node.value.args:
                        if isinstance(arg, ast.Constant):
                            class_name = arg.value
                            self.all_classes.append(class_name)
                            self.variable_to_class[variable] = class_name
                elif isinstance(node.value, ast.List):
                    for elt in node.value.elts:
                        if isinstance(elt, ast.Name):
                            self.all_classes.append(self.variable_to_class[elt.id])
                            if variable in self.all_lists:
                                self.all_lists[variable].append(elt.id)
                            else:
                                self.all_lists[variable] = [elt.id]
                            # self.all_lists[variable].append(self.variable_to_class[elt.id])

        self.generic_visit(node)

    def visit_BinOp(self, node):
        if not isinstance(node.left, ast.Name):
            if isinstance(node.left, ast.List):
                temp_node = node
            else:
                temp_node = node.left
            if isinstance(temp_node.right, ast.Call):
                method = extract_method_from_edge(temp_node.right)
            else:
                method = None
        else:
            method = None

        if method is not None:
            left_class = resolve_left(node.left)

            if isinstance(node.right, ast.Name):
                right_class = [node.right.id]
            elif isinstance(node.right, ast.List):
                right_class = [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]
            else:
                right_class = []

            self.add_to_connections(left_class, method, right_class, node.op)

        self.generic_visit(node)

    def visit_For(self, node):
        """
        Visit a For loop node and extract connections.
        """
        # Extract the loop variable (target)
        if isinstance(node.target, ast.Name):
            loop_var = node.target.id
        else:
            return  # Unsupported target type

        # Extract iteration elements (iter)
        iteration_elements = []
        if isinstance(node.iter, ast.List):
            iteration_elements = [
                elt.id for elt in node.iter.elts if isinstance(elt, ast.Name)
            ]
            # print("Iteration elements", iteration_elements)

        if isinstance(node.iter, ast.Name):
            iteration_elements = self.all_lists[node.iter.id]
            # print("iteration_elements", iteration_elements)

        # Process the loop body
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.BinOp):
                self.process_binop_in_for(stmt.value, loop_var, iteration_elements)

        # Continue visiting other nodes
        self.generic_visit(node)

    def process_binop_in_for(self, node, loop_var, iteration_elements):
        left_class = []
        if isinstance(node.left, ast.BinOp) and isinstance(node.left.left, ast.Name):
            if node.left.left.id == loop_var:
                left_class = iteration_elements

        # print("left_class", left_class)
        method = None
        if isinstance(node.left.right, ast.Call) and node.left.right.func.id == "Edge":
            method = extract_method_from_edge(node.left.right)

        right_class = []
        if isinstance(node.right, ast.List):
            right_class = [
                elt.id for elt in node.right.elts if isinstance(elt, ast.Name)
            ]

        # print(left_class, method, right_class)
        # Form connections
        self.add_to_connections(left_class, method, right_class, node.op)

    def add_to_connections(self, left_class, method, right_class, op):
        for left in left_class:
            if left not in self.variable_to_class:
                continue
            _left = self.variable_to_class[left]
            for right in right_class:
                _right = self.variable_to_class[right]
                if _left == _right:
                    self.add_class_to_methods(_left, method)
                    continue
                if isinstance(op, ast.RShift):
                    self.all_connections.append([_left, method, _right])
                    self.add_class_to_methods(_left, method)
                else:
                    self.all_connections.append([_right, method, _left])
                    self.add_class_to_methods(_right, method)
        # print("all_connections")
        # pprint(self.all_connections)

    def add_class_to_methods(self, class_name, method):
        if method == 'inherits':
            return
        if class_name in self.all_class_to_methods:
            self.all_class_to_methods[class_name].append(method)
        else:
            self.all_class_to_methods[class_name] = [method]
        return

    def get_results(self):
        return self.all_classes, self.all_class_to_methods, self.all_connections

def resolve_left(node):
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.List):
        return [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
    elif isinstance(node, ast.BinOp):
        if isinstance(node.right, ast.Name):
            return [node.right.id]
        elif isinstance(node.right, ast.List):
            return [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]
        return resolve_left(node.left)
    return []

def extract_method_from_edge(node):
    """
    Extract the 'label' keyword (method) from an Edge call.
    """
    if isinstance(node, ast.Call) and node.func.id == "Edge":
        return next(
            (kw.value.value for kw in node.keywords if kw.arg == "label"),
            None,
        )
    return None

def analyze_diagram(diagram):
    tree = ast.parse(diagram)
    diagram_visitor = DiagramVisitor()
    diagram_visitor.visit(tree)

    all_classes, class_to_methods, all_connections = diagram_visitor.get_results()

    return all_classes, class_to_methods, all_connections

class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []  # All class names
        self.current_class = None  # Currently visited class
        self.class_to_methods = {}  # Map of class names to methods
        self.class_to_parents = {}  # Map of class names to their parent classes

    def visit_ClassDef(self, node):
        """
        Visit a class definition and record its methods and parents.
        """
        # Initialize the current class
        self.current_class = node.name
        self.classes.append(node.name)
        self.class_to_methods[node.name] = []

        # Track base classes (parents)
        parents = []
        for base in node.bases:
            if isinstance(base, ast.Name):  # Simple parent class
                parents.append(base.id)
            elif isinstance(base, ast.Attribute):  # Parent with module path
                parents.append(base.attr)
        self.class_to_parents[node.name] = parents

        # Visit class body to find methods
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """
        Visit a method definition and add it to the current class.
        Ignore constructors (__init__).
        """
        if node.name != "__init__":
            self.class_to_methods[self.current_class].append(node.name + "()")
        self.generic_visit(node)

    def resolve_inheritance(self):
        """
        Propagate parent methods to child classes.
        """
        resolved_methods = {}

        # Start with all classes
        for class_name in self.classes:
            resolved_methods[class_name] = set(self.class_to_methods.get(class_name, []))
        # Propagate parent methods
        for class_name, parents in self.class_to_parents.items():
            for parent in parents:
                if parent in resolved_methods:  # Only propagate if parent exists
                    resolved_methods[class_name].update(resolved_methods[parent])

        # Convert methods back to lists
        for class_name in resolved_methods:
            self.class_to_methods[class_name] = list(resolved_methods[class_name])

    def get_results(self):
        """
        Get the results: classes and methods, after resolving inheritance.
        """
        self.resolve_inheritance()
        return self.classes, self.class_to_methods


def analyze_code(code):
    tree = ast.parse(code)
    # print(ast.dump(tree, indent=4))
    code_visitor = CodeVisitor()
    code_visitor.visit(tree)

    classes, class_to_methods = code_visitor.get_results()
    return classes, class_to_methods


# all_code_classes, code_class_to_methods = analyze_code(code)

def compare_classes(code_classes, diagram_classes):
    missing_classes = set(diagram_classes) - set(code_classes)
    extra_classes = set(code_classes) - set(diagram_classes)
    return missing_classes, extra_classes

def compare_methods(code_class_to_methods, diagram_class_to_methods):
    missing_methods = {}
    extra_methods = {}
    for cls, methods in diagram_class_to_methods.items():
        if cls in code_class_to_methods:
            missing_methods[cls] = set(methods) - set(code_class_to_methods[cls])
            extra_methods[cls] = set(code_class_to_methods[cls]) - set(methods)
        else:
            missing_methods[cls] = set(methods)
            extra_methods[cls] = set()
    return missing_methods, extra_methods


if __name__ == "__main__":
    # Parse arguments
    code_file_name = "classes/classes.py"
    diagram_file_names = ["diagrams/diagram.py"]
    # code_file_name = sys.argv[1]
    # diagram_file_names = sys.argv[2:]

    # Analyze the code file
    with open(code_file_name, 'r') as f:
        code_file = f.read()
    code_classes, code_methods = analyze_code(code_file)

    # Analyze all diagram files and aggregate results
    all_diagram_classes = set()
    aggregated_diagram_methods = {}

    for file in diagram_file_names:
        with open(file, "r") as f:
            diagram_file = f.read()
        diagram_classes, diagram_methods, _ = analyze_diagram(diagram_file)
        all_diagram_classes.update(diagram_classes)
        for cls, methods in diagram_methods.items():
            aggregated_diagram_methods.setdefault(cls, set()).update(methods)

    # Compare classes and methods
    missing_classes, extra_classes = compare_classes(code_classes, all_diagram_classes)
    missing_methods, extra_methods = compare_methods(code_methods, aggregated_diagram_methods)

    # Report Results
    print("===== Comparison Results =====")

    if missing_classes:
        print("\nMissing Classes in Code:")
        pprint(missing_classes)

    if extra_classes:
        print("\nExtra Classes in Code:")
        pprint(extra_classes)

    if missing_methods:
        print("\nMissing Methods in Code:")
        pprint({cls: methods for cls, methods in missing_methods.items() if methods})

    if extra_methods:
        print("\nExtra Methods in Code:")
        pprint({cls: methods for cls, methods in extra_methods.items() if methods})

    # Exit with failure if discrepancies are found
    if missing_classes or extra_classes or any(missing_methods.values()) or any(extra_methods.values()):
        print("\n❌ Discrepancies found! Commit aborted.")
        sys.exit(1)
    else:
        print("\n✅ Code and Diagram are in sync!")
        sys.exit(0)
