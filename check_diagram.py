import ast
import sys
from pprint import pprint

def extract_method_from_edge(node):
    """
    Extract the 'label' keyword (method name) from an Edge(...) call.
    Returns:
        str or None: The method label if found and is a string, otherwise None.
    """
    if not isinstance(node, ast.Call):
        return None

    if not (hasattr(node.func, 'id') and node.func.id == "Edge"):
        return None

    # Search for a keyword with arg='label'
    for kw in node.keywords:
        if kw.arg == "label":
            if isinstance(kw.value, ast.Constant):
                return kw.value.value
            else:
                # Label given but not as a string constant
                print("Warning: Edge label is not a constant string:", ast.dump(kw.value))
                return None
    return None


def resolve_left(node):
    """
    Resolve the left-hand side of a binary operation into a list of variable IDs to deal with nested Edge connections.
    These variable IDs correspond to classes or lists of classes as defined in the diagram.
    """
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.List):
        return [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
    elif isinstance(node, ast.BinOp):
        # If the right node is a Name or a List of Names, extract them
        if isinstance(node.right, ast.Name):
            return [node.right.id]
        elif isinstance(node.right, ast.List):
            return [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]
        # Otherwise, recurse left
        return resolve_left(node.left)
    return []


class DiagramVisitor(ast.NodeVisitor):
    """
    AST Visitor that extracts classes, class-to-variable mappings, and connections (edges)
    from the diagram.
    """

    def __init__(self):
        self.all_classes = []
        self.variable_to_class = {}
        self.all_connections = []
        self.all_class_to_methods = {}
        self.all_lists = {}

    def visit_Assign(self, node):
        """
        Visit assignment nodes to identify and track class variables and lists of class variables.
        """
        try:
            self._process_assignment(node)
        except Exception as e:
            print(f"Error processing assignment: {e}")
        self.generic_visit(node)

    def _process_assignment(self, node):
        if not isinstance(node, ast.Assign):
            return
        if not node.targets or not isinstance(node.targets[0], ast.Name):
            return

        variable = node.targets[0].id
        value = node.value

        if isinstance(value, ast.Call):
            self._handle_class_assignment(variable, value)
        elif isinstance(value, ast.List):
            self._handle_list_assignment(variable, value)

    def _handle_class_assignment(self, variable, value):
        # Expecting something like: variable = SomeClass("ClassName")
        for arg in value.args:
            if isinstance(arg, ast.Constant):
                class_name = arg.value
                self.all_classes.append(class_name)
                self.variable_to_class[variable] = class_name

    def _handle_list_assignment(self, variable, value):
        # Expecting: variable = [classVar1, classVar2, ...]
        for elt in value.elts:
            if isinstance(elt, ast.Name):
                class_var = elt.id
                if class_var not in self.variable_to_class:
                    print(f"Warning: {class_var} referenced before assignment.")
                    continue
                class_name = self.variable_to_class[class_var]
                self.all_classes.append(class_name)
                if variable in self.all_lists:
                    self.all_lists[variable].append(class_var)
                else:
                    self.all_lists[variable] = [class_var]

    def visit_BinOp(self, node):
        """
        Visit binary operations to detect connections (edges).
        """
        try:
            self._process_binop(node)
        except Exception as e:
            print(f"Error processing BinOp: {e}")
        self.generic_visit(node)

    def _process_binop(self, node):
        # Extract the method from the right part of the left node if present
        if not isinstance(node.left, ast.Name):
            # left might be a complex expression, attempt to find a method
            temp_node = node.left if not isinstance(node.left, ast.List) else node
            method = extract_method_from_edge(getattr(temp_node, 'right', None))
        else:
            method = None

        if method is not None:
            left_class_ids = resolve_left(node.left)
            right_class_ids = self._resolve_right_classes(node.right)
            self.add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def _resolve_right_classes(self, node):
        """
        Given a node on the right side of a binop, return the list of class variable IDs.
        """
        if isinstance(node, ast.Name):
            return [node.id]
        elif isinstance(node, ast.List):
            return [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
        return []

    def visit_For(self, node):
        """
        Visit a For loop node and extract connections from loops.
        E.g. for x in [classVar1, classVar2]:
                x >> Edge(...) >> [classVar3]
        """
        try:
            self._process_for_loop(node)
        except Exception as e:
            print(f"Error processing For loop: {e}")
        self.generic_visit(node)

    def _process_for_loop(self, node):
        if not isinstance(node.target, ast.Name):
            print("Warning: For loop target not supported.")
            return

        loop_var = node.target.id
        iteration_elements = self._get_iteration_elements(node.iter)

        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.BinOp):
                self._process_binop_in_for(stmt.value, loop_var, iteration_elements)

    def _get_iteration_elements(self, iter_node):
        """
        Extract iteration elements from something like: for var in [elt1, elt2] or for var in variableList
        """
        if isinstance(iter_node, ast.List):
            return [elt.id for elt in iter_node.elts if isinstance(elt, ast.Name)]

        if isinstance(iter_node, ast.Name) and iter_node.id in self.all_lists:
            return self.all_lists[iter_node.id]

        return []

    def _process_binop_in_for(self, node, loop_var, iteration_elements):
        """
        Process a binop inside a for loop. The loop variable may appear on the left side.
        """
        left_class_ids = []
        if (isinstance(node.left, ast.BinOp) and
            isinstance(node.left.left, ast.Name) and
            node.left.left.id == loop_var):
            left_class_ids = iteration_elements

        method = None
        if (isinstance(node.left, ast.BinOp) and
            isinstance(node.left.right, ast.Call)):
            method = extract_method_from_edge(node.left.right)

        right_class_ids = []
        if isinstance(node.right, ast.List):
            right_class_ids = [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]

        self.add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def add_to_connections(self, left_class_ids, method, right_class_ids, op):
        """
        Add connections from left classes to right classes based on the operator.
        For example, A >> Edge(label="method") >> B means A.method connects to B.
        """
        if method is None:
            # No method label found, skip adding a method connection
            return

        for left_id in left_class_ids:
            if left_id not in self.variable_to_class:
                print(f"Warning: {left_id} not found in variable_to_class map.")
                continue
            left_class = self.variable_to_class[left_id]

            for right_id in right_class_ids:
                if right_id not in self.variable_to_class:
                    print(f"Warning: {right_id} not found in variable_to_class map.")
                    continue
                right_class = self.variable_to_class[right_id]

                # If classes are the same, just add method to the class
                if left_class == right_class:
                    self.add_class_to_methods(left_class, method)
                    continue

                # Depending on the operator, decide the connection direction
                if isinstance(op, ast.RShift):
                    self.all_connections.append([left_class, method, right_class])
                    self.add_class_to_methods(left_class, method)
                else:
                    self.all_connections.append([right_class, method, left_class])
                    self.add_class_to_methods(right_class, method)

    def add_class_to_methods(self, class_name, method):
        """
        Add a method to a class in the internal mapping, ensuring no duplicates.
        """
        if method == 'inherits':  # ignore 'inherits' pseudo-methods
            return
        if class_name not in self.all_class_to_methods:
            self.all_class_to_methods[class_name] = []
        if method not in self.all_class_to_methods[class_name]:
            self.all_class_to_methods[class_name].append(method)

    def get_results(self):
        return self.all_classes, self.all_class_to_methods, self.all_connections


class CodeVisitor(ast.NodeVisitor):
    """
    Visitor to parse code classes and methods, including resolving inheritance.
    """
    def __init__(self):
        self.classes = []  # All class names
        self.current_class = None  # Currently visited class
        self.class_to_methods = {}  # Map of class names to methods
        self.class_to_parents = {}  # Map of class names to their parent classes

    def visit_ClassDef(self, node):
        # Initialize the current class
        self.current_class = node.name
        self.classes.append(node.name)
        self.class_to_methods[node.name] = []

        # Track base classes (parents)
        parents = self._extract_parents(node)
        self.class_to_parents[node.name] = parents

        # Visit class body to find methods
        self.generic_visit(node)
        self.current_class = None

    def _extract_parents(self, node):
        parents = []
        for base in node.bases:
            if isinstance(base, ast.Name):  # Simple parent class
                parents.append(base.id)
            elif isinstance(base, ast.Attribute):  # Parent with module path
                parents.append(base.attr)
        return parents

    def visit_FunctionDef(self, node):
        # Skip __init__
        if self.current_class and node.name != "__init__":
            self.class_to_methods[self.current_class].append(node.name + "()")
        self.generic_visit(node)

    def resolve_inheritance(self):
        resolved_methods = {}
        for class_name in self.classes:
            resolved_methods[class_name] = set(self.class_to_methods.get(class_name, []))

        # Propagate parent methods
        for class_name, parents in self.class_to_parents.items():
            for parent in parents:
                if parent not in resolved_methods:
                    # if Parent not found in local classes just skip
                    continue
                resolved_methods[class_name].update(resolved_methods[parent])

        # Convert methods back to lists
        for class_name in resolved_methods:
            self.class_to_methods[class_name] = list(resolved_methods[class_name])

    def get_results(self):
        self.resolve_inheritance()
        return self.classes, self.class_to_methods


def analyze_diagram(diagram_content):
    """
    Parse and analyze a diagram file's content to extract classes, methods, and connections.
    """
    try:
        tree = ast.parse(diagram_content)
    except SyntaxError as e:
        print(f"Error parsing diagram: {e}")
        return [], {}, []

    diagram_visitor = DiagramVisitor()
    diagram_visitor.visit(tree)

    all_classes, class_to_methods, all_connections = diagram_visitor.get_results()
    return all_classes, class_to_methods, all_connections


def analyze_code(code_content):
    """
    Parse and analyze a code file's content to extract classes and methods.
    """
    try:
        tree = ast.parse(code_content)
    except SyntaxError as e:
        print(f"Error parsing code: {e}")
        return [], {}

    code_visitor = CodeVisitor()
    code_visitor.visit(tree)

    classes, class_to_methods = code_visitor.get_results()
    return classes, class_to_methods


def compare_classes(code_classes, diagram_classes):
    missing_classes = set(diagram_classes) - set(code_classes)
    extra_classes = set(code_classes) - set(diagram_classes)
    return missing_classes, extra_classes

def compare_methods(code_class_to_methods, diagram_class_to_methods):
    missing_methods = {}
    extra_methods = {}
    for cls, methods in diagram_class_to_methods.items():
        if cls in code_class_to_methods:
            missing = set(methods) - set(code_class_to_methods[cls])
            extra = set(code_class_to_methods[cls]) - set(methods)
            if missing:
                missing_methods[cls] = missing
            if extra:
                extra_methods[cls] = extra
        else:
            # Class in diagram but not in code at all
            if methods:
                missing_methods[cls] = set(methods)
    return missing_methods, extra_methods


if __name__ == "__main__":
    # code_file_name = "classes/classes.py"
    # diagram_file_names = ["diagrams/
    #
    code_file_name = sys.argv[1]
    diagram_file_names = sys.argv[2:]

    # Analyze the code file
    try:
        with open(code_file_name, 'r') as f:
            code_file_content = f.read()
    except FileNotFoundError:
        print(f"Error: Code file {code_file_name} not found.")
        sys.exit(1)

    code_classes, code_methods = analyze_code(code_file_content)

    all_diagram_classes = set()
    aggregated_diagram_methods = {}

    # Analyze all diagram files
    for file_name in diagram_file_names:
        try:
            with open(file_name, "r") as f:
                diagram_content = f.read()
        except FileNotFoundError:
            print(f"Error: Diagram file {file_name} not found.")
            sys.exit(1)

        diagram_classes, diagram_methods, _ = analyze_diagram(diagram_content)
        all_diagram_classes.update(diagram_classes)
        for cls, methods in diagram_methods.items():
            aggregated_diagram_methods.setdefault(cls, set()).update(methods)

    # Compare classes and methods
    missing_classes, extra_classes = compare_classes(code_classes, all_diagram_classes)
    missing_methods, extra_methods = compare_methods(code_methods, aggregated_diagram_methods)

    # Determine exit code
    if missing_classes or extra_classes or missing_methods or extra_methods:
        print("===== Comparison Results =====")
        if missing_classes:
            print("\nMissing Classes in Code:")
            pprint(missing_classes)

        if extra_classes:
            print("\nExtra Classes in Code:")
            pprint(extra_classes)

        if missing_methods:
            print("\nMissing Methods in Code:")
            pprint(missing_methods)

        if extra_methods:
            print("\nExtra Methods in Code:")
            pprint(extra_methods)
        print("\n❌ Discrepancies found! Commit aborted.")
        sys.exit(1)

    else:
        print("\n✅ Code and Diagram are in sync!")
        sys.exit(0)
