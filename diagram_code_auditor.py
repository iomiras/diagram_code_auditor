import ast
import sys
from pprint import pprint
import json
import subprocess
import shutil


def log_error(message):
    print(f"[Error] {message}")

def log_warning(message):
    print(f"[Warning] {message}")

def log_info(message):
    print(f"[Info] {message}")

def create_backup(file_path):
    backup_path = f"{file_path}.bak"
    shutil.copy(file_path, backup_path)
    log_info(f"Backup created at {backup_path}")

# Validation Before Writing Updates
def validate_diagram_syntax(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        log_error(f"Invalid diagram syntax: {e}")
        return False

def validate_update(file_path):
    try:
        subprocess.run(['python3', file_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Validation failed for the updated file: {e}")
        return False

def extract_method_from_edge(node, variable_to_value={}):
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
                if isinstance(kw.value, ast.Name):
                    if kw.value.id in variable_to_value.keys():
                        return variable_to_value[kw.value.id][0]
                log_warning("Warning: Edge label is wrong:", ast.dump(kw.value))
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
    elif isinstance(node, ast.Call):
        if isinstance(node.args[0], ast.Constant):
            return [node.args[0].value]
    elif isinstance(node, ast.BinOp):
        # If the right node is a Name or a List of Names, extract them
        if isinstance(node.right, ast.Name):
            return [node.right.id]
        elif isinstance(node.right, ast.List):
            return [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]
        elif isinstance(node, ast.Call):
            if isinstance(node.args[0], ast.Constant):
                return [node.args[0].value]
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
        self.variable_to_value = {}

    def visit_Assign(self, node):
        """
        Visit assignment nodes to identify and track class variables and lists of class variables.
        """
        try:
            self._process_assignment(node)
        except Exception as e:
            log_error(f"Error processing assignment: {e}")
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
        elif isinstance(value, ast.Constant):
            if variable in self.variable_to_value.keys():
                self.variable_to_value[variable].append(value.value)
            else:
                self.variable_to_value[variable] = [value.value]


    def _handle_class_assignment(self, variable, value):
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
                    log_warning(f"Warning: {class_var} referenced before assignment.")
                    continue
                class_name = self.variable_to_class[class_var]
                self.all_classes.append(class_name)
                if variable in self.variable_to_value:
                    self.variable_to_value[variable].append(self.variable_to_class[class_var])
                else:
                    self.variable_to_value[variable] = [self.variable_to_class[class_var]]

            if isinstance(elt, ast.Constant):
                class_name = elt.value
                self.all_classes.append(class_name)
                if variable in self.variable_to_value:
                    self.variable_to_value[variable].append(class_name)
                else:
                    self.variable_to_value[variable] = [class_name]

    def visit_BinOp(self, node):
        """
        Visit binary operations to detect connections (edges).
        """
        try:
            self._process_binop(node)
        except Exception as e:
            log_error(f"Error processing BinOp: {e}")
        self.generic_visit(node)

    def _process_binop(self, node):
        if not isinstance(node.left, ast.Name):
            temp_node = node.left if not isinstance(node.left, ast.List) else node
            method = extract_method_from_edge(getattr(temp_node, 'right', None), self.variable_to_value)
        else:
            method = None
        if method is not None:
            # print("Method", method)
            # pprint(ast.dump(node, indent=4))
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
        elif isinstance(node, ast.Call):
            if isinstance(node.args[0], ast.Constant):
                return [node.args[0].value]
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
            log_error(f"Error processing For loop: {e}")
        self.generic_visit(node)

    def _process_for_loop(self, node):
        if not isinstance(node.target, ast.Name):
            log_warning("Warning: For loop target not supported.")
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

        if isinstance(iter_node, ast.Name) and iter_node.id in self.variable_to_value:
            return self.variable_to_value[iter_node.id]

        return []

    def _process_binop_in_for(self, node, loop_var, iteration_elements):
        """
        Process a binop inside a for loop. The loop variable may appear on the left side.
        """
        left_class_ids = []
        if (isinstance(node.left, ast.BinOp) and
            isinstance(node.left.left, ast.Name)):
            if node.left.left.id == loop_var:
                left_class_ids = iteration_elements
            else:
                left_class_ids = [node.left.left.id]

        method = None
        if (isinstance(node.left, ast.BinOp) and
            isinstance(node.left.right, ast.Call)):
            method = extract_method_from_edge(node.left.right, self.variable_to_value)
            
        right_class_ids = []

        if isinstance(node.right, ast.List):
            right_class_ids = [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]
        elif isinstance(node.right, ast.Name):
            right_class_ids = [node.right.id]
        elif isinstance(node.right, ast.Call):
            # Handle cases where node.right is a function call, such as Server(service_str)
            if isinstance(node.right.args[0], ast.Name) and node.right.args[0].id == loop_var:
                right_class_ids = iteration_elements
        # for el in right_class_ids:
        #     if el not in self.variable_to_class:
        #         self.all_classes.append(el)
        #         print("all classes updated", end=" ")
        # pprint(self.all_classes)
        #         self.all_class_to_methods[el] = []

        
        

        self.add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def add_to_connections(self, left_class_ids, method, right_class_ids, op):
        """
        Add connections from left classes to right classes based on the operator.
        For example, A >> Edge(label="method") >> B means A.method connects to B.
        """
        # print("right_class_ids", end=" ")
        # pprint(right_class_ids)
        # print("Method", method)
        for cls in right_class_ids:
            if cls not in self.all_class_to_methods and self.variable_to_class.get(cls) not in self.all_class_to_methods:
                if cls in self.variable_to_class:
                    self.all_class_to_methods[self.variable_to_class[cls]] = []
                else:
                    self.all_class_to_methods[cls] = []

        if method is None:
            return
        
        print(left_class_ids, method, right_class_ids)
        for left_id in left_class_ids:
            if left_id in self.all_classes:
                left_class = left_id
            elif left_id not in self.variable_to_class and left_id not in self.all_classes:
                log_warning(f"Warning: Left {left_id} not found in variable_to_class map.")
                continue
            else:
                left_class = self.variable_to_class[left_id]

            # Handle inheritance relationships explicitly
            if method == "inherits":
                for right_id in right_class_ids:
                    if right_id in self.all_classes:
                        right_class = right_id
                    elif right_id not in self.variable_to_class:
                        log_warning(f"Warning: Right {right_id} not found in variable_to_class map.")
                        continue
                    else:
                        right_class = self.variable_to_class[right_id]

                    # Add parent methods to child class
                    self.add_class_to_methods(left_class, method, right_class)
                continue

            # Handle other methods and connections
            for right_id in right_class_ids:
                if right_id in self.all_classes:
                    right_class = right_id
                elif right_id not in self.variable_to_class:
                    log_warning(f"Warning: Right {right_id} not found in variable_to_class map.")
                    continue
                else:
                    right_class = self.variable_to_class[right_id]

                # Add the method to the class or create a connection
                if left_class == right_class:
                    self.add_class_to_methods(left_class, method, right_class)
                    continue

                if isinstance(op, ast.RShift):
                    self.all_connections.append([left_class, method, right_class])
                    self.add_class_to_methods(left_class, method, right_class)
                else:
                    self.all_connections.append([right_class, method, left_class])
                    self.add_class_to_methods(right_class, method, left_class)

    def add_class_to_methods(self, class_name, method, another_class_name=None):
        """
        Add a method to a class in the internal mapping, ensuring no duplicates.
        """
        if method == 'inherits':
            if another_class_name and another_class_name in self.all_class_to_methods:
                inherited_methods = self.all_class_to_methods[another_class_name]
                self.all_class_to_methods.setdefault(class_name, []).extend(inherited_methods)
            return

        self.all_class_to_methods.setdefault(class_name, [])
        if method not in self.all_class_to_methods[class_name]:
            self.all_class_to_methods[class_name].append(method)

    def get_results(self):
        return self.all_classes, self.all_class_to_methods, self.all_connections, self.variable_to_class


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
        log_error(f"Error parsing diagram: {e}")
        return [], {}, []

    diagram_visitor = DiagramVisitor()
    diagram_visitor.visit(tree)

    all_classes, class_to_methods, all_connections, variable_to_classes = diagram_visitor.get_results()
    return all_classes, class_to_methods, all_connections, variable_to_classes


def analyze_code(code_content):
    """
    Parse and analyze a code file's content to extract classes and methods.
    """
    try:
        tree = ast.parse(code_content)
    except SyntaxError as e:
        log_error(f"Error parsing code: {e}")
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
    """
    Compare methods between classes in the code and the diagram.

    Args:
        code_class_to_methods (dict): Mapping of classes to methods in the code.
        diagram_class_to_methods (dict): Mapping of classes to methods in the diagram.

    Returns:
        tuple: (missing_methods, extra_methods)
            - missing_methods (dict): Methods present in the diagram but missing in the code.
            - extra_methods (dict): Methods present in the code but missing in the diagram.
    """
    missing_methods = {}
    extra_methods = {}

    # Iterate through all unique classes across both dictionaries
    all_classes = set(code_class_to_methods) | set(diagram_class_to_methods)

    for cls in all_classes:
        code_methods = set(code_class_to_methods.get(cls, []))
        diagram_methods = set(diagram_class_to_methods.get(cls, []))

        # Identify missing and extra methods
        missing = diagram_methods - code_methods
        extra = code_methods - diagram_methods

        if missing:
            missing_methods[cls] = missing
        if extra:
            extra_methods[cls] = extra

    return missing_methods, extra_methods



def parse_json(code_tree):
    code_classes = []
    code_methods = {}
    y = json.loads(code_tree)
    x = y[0]['stmts']
    for i in range(len(x)):
        if x[i]['nodeType'] == 'Stmt_Class':
            class_name = x[i]['name']['name']
            if x[i]['extends']:
                parent_class = x[i]['extends']['name']
                if parent_class in code_methods:
                    code_methods[class_name] = code_methods[parent_class].copy()
            code_classes.append(class_name)
            for j in range(len(x[i]['stmts'])):
                if x[i]['stmts'][j]['nodeType'] == 'Stmt_ClassMethod':
                    method_name = x[i]['stmts'][j]['name']['name']
                    if method_name == '__construct':
                        continue
                    method_name += '()'
                    if class_name in code_methods:
                        code_methods[class_name].append(method_name)
                    else:
                        code_methods[class_name] = [method_name]

    return code_classes, code_methods


# Unified Parser for Python and PHP
def parse_code_file(file_path):
    """Unified parser that handles both Python and PHP files."""
    if file_path.endswith('.py'):
        with open(file_path, 'r') as f:
            content = f.read()
        return analyze_code(content)
    elif file_path.endswith('.php'):
        subprocess.run(['php', 'php_parser.php'])
        with open('./tmp/ast.json', 'r') as f:
            content = f.read()
        return parse_json(content)
    else:
        log_error("Unsupported file type. Only .py and .php are supported.")
        sys.exit(1)

# Selective Updates Implementation
def handle_updates(missing_classes, extra_classes, missing_methods, extra_methods, diagram_file, variable_to_classes):
    """Handle selective updates to the diagram file."""
    if not (missing_classes or extra_classes or missing_methods or extra_methods):
        return True

    create_backup(diagram_file)
    
    if not validate_diagram_syntax(diagram_file):
        return False

    with open(diagram_file, "a") as f:
        if extra_methods:
            for cls, methods in extra_methods.items():
                value = [i for i in variable_to_classes if variable_to_classes[i]==cls]
                cls_var = value[0] if value else f'Action("{cls}")'
                for method in methods:
                    user_input = input(f"Add method {method} to {cls}? (yes/no): ").strip().lower()
                    if user_input == 'yes':
                        f.write(f"\n    {cls_var} >> Edge(label='{method}', color='red') >> {cls_var}")
        
        if extra_classes:
            for cls in extra_classes:
                user_input = input(f"Add class {cls} to diagram? (yes/no): ").strip().lower()
                if user_input == 'yes':
                    f.write(f"\n    {cls} = Action('{cls}')")

    return validate_update(diagram_file)

if __name__ == "__main__":
    # Example file names (override with command-line arguments if provided)
    code_file_name = "classes_examples/classes.py"
    code_file_name = "classes_examples/classes.php"
    diagram_file_names = ["diagram_examples/diagram.py"]

    # Override with command-line arguments
    code_file_name = sys.argv[1]
    diagram_file_name = sys.argv[2]

    code_classes, code_methods = parse_code_file(code_file_name)

    while True:
        # Analyze diagram file
        try:
            with open(diagram_file_name, "r") as f:
                diagram_content = f.read()
        except FileNotFoundError:
            log_error(f"Error: Diagram file {diagram_file_name} not found.")
            sys.exit(1)

        diagram_classes, diagram_methods, all_connections, variable_to_classes = analyze_diagram(diagram_content)
        print("Diagram Methods:", end=" ")
        pprint(diagram_methods)

        # Compare classes and methods
        missing_classes, extra_classes = compare_classes(code_classes, set(diagram_classes))
        missing_methods, extra_methods = compare_methods(code_methods, diagram_methods)

        if not (missing_classes or extra_classes or missing_methods or extra_methods):
            print(f"\n✅ Code {code_file_name} and its Diagram are in sync!\n")
            sys.exit(0)

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

        print("\n**************")
        try:
            sys.stdout.write("Do you want to rewrite the diagram file? (yes/no): ")
            sys.stdout.flush()

            ans = input().strip().lower()

            if ans not in ["yes", "no", "y", "n"]:
                print("Invalid input. Please enter 'yes' or 'no'.")
                continue

            if ans in ["no", "n"]:
                print("\n❌ Commit aborted.\n")
                sys.exit(1)

        except EOFError:
            log_error("Unexpected error while reading input. Exiting.")
            sys.exit(1)

        print("Updating the diagram file...")
        with open(diagram_file_name, "a") as f:
            if extra_methods:
                for cls, methods in extra_methods.items():
                    value = [i for i in variable_to_classes if variable_to_classes[i] == cls]
                    cls_var = value[0] if value else f'Action("{cls}")'
                    for method in methods:
                        f.write(f"\n    {cls_var} >> Edge(label='{method}', color='red') >> {cls_var}")
            if extra_classes:
                for cls in extra_classes:
                    f.write(f"\n    {cls} = Action('{cls}')")

        validate_diagram_syntax(diagram_file_name)
        print("\nRe-running checks...\n")