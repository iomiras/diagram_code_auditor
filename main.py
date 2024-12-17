import ast
from pprint import pprint

with open('diagrams/diagram.py', 'r') as f:
    diagram = f.read()


class DiagramVisitor(ast.NodeVisitor):
    def __init__(self):
        self.all_classes = []
        self.variable_to_class = {}
        self.all_connections = []
        self.last_left_classes = []
        self.all_class_to_methods = {}

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

        method = None
        if isinstance(node.left.right, ast.Call) and node.left.right.func.id == "Edge":
            method = extract_method_from_edge(node.left.right)

        right_class = []
        if isinstance(node.right, ast.List):
            right_class = [
                elt.id for elt in node.right.elts if isinstance(elt, ast.Name)
            ]

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
                    self.add_class_to_methods(_left, method)

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

all_diagram_classes, diagram_class_to_methods, all_diagram_connections = analyze_diagram(diagram)
# pprint("All Diagram Classes:")
# pprint(all_diagram_classes)
# print("========================================")
# pprint("Diagram Class to Methods:")
# pprint(diagram_class_to_methods)
# print("========================================")
# print("All Connections:")
# pprint(all_diagram_connections)


with open("classes/classes.py", "r") as f:
    code = f.read()

import ast

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


all_code_classes, code_class_to_methods = analyze_code(code)
# pprint("All Code Classes:")
# pprint(all_code_classes)
# print("========================================")
# pprint("Code Class to Methods:")
# pprint(code_class_to_methods)
# print("========================================")

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

missing_classes, extra_classes = compare_classes(all_code_classes, all_diagram_classes)
missing_methods, extra_methods = compare_methods(code_class_to_methods, diagram_class_to_methods)

print('Missing Classes in Code, but in Diagram:')
pprint(missing_classes)
print("========================================")
print('Extra Classes in Code, but not in Diagram:')
pprint(extra_classes)
print("========================================")
print('Missing Methods in Code, but in Diagram:')
pprint(missing_methods)
print("========================================")
print('Extra Methods in Code, but not in Diagram:')
pprint(extra_methods)