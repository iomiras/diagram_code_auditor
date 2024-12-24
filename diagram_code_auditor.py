import ast
import sys
import json
import shutil
import subprocess
from pprint import pprint


def log_error(message: str) -> None:
    """Print an error message with proper formatting."""
    print(f"[Error] {message}")


def log_warning(message: str) -> None:
    """Print a warning message with proper formatting."""
    print(f"[Warning] {message}")


def log_info(message: str) -> None:
    """Print an info message with proper formatting."""
    print(f"[Info] {message}")


def create_backup(file_path: str) -> None:
    """Create a backup of the specified file."""
    backup_path = f"{file_path}.bak"
    shutil.copy(file_path, backup_path)
    log_info(f"Backup created at {backup_path}")

def restore_backup(file_path: str) -> None:
    """Restore the backup of the specified file."""
    backup_path = f"{file_path}.bak"
    shutil.copy(backup_path, file_path)
    log_info(f"Backup restored from {backup_path}")


def validate_diagram_syntax(file_path: str) -> bool:
    """
    Validate the syntax of a Python diagram file.
    
    Args:
        file_path: Path to the diagram file
        
    Returns:
        bool: True if syntax is valid, False otherwise
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        log_error(f"Invalid diagram syntax: {e}")
        return False


def validate_update(file_path: str) -> bool:
    """
    Validate that the updated file can be executed without errors.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        bool: True if validation passes, False otherwise
    """
    try:
        print(file_path)
        subprocess.run(['python3', file_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Validation failed for the updated file: {e}. Reverting changes...")
        restore_backup(file_path)
        return False


def extract_method_from_edge(node: ast.Call, variable_to_value: dict = {}) -> str:
    """
    Extract the method name (label) from an Edge(...) call in the AST.
    
    Args:
        node: AST node representing an Edge call
        variable_to_value: Dictionary mapping variable names to their values
        
    Returns:
        str or None: The extracted method label if found
    """
    if not isinstance(node, ast.Call):
        return None

    if not (hasattr(node.func, 'id') and node.func.id == "Edge"):
        return None

    for kw in node.keywords:
        if kw.arg == "label":
            if isinstance(kw.value, ast.Constant):
                return kw.value.value
            elif isinstance(kw.value, ast.Name):
                if kw.value.id in variable_to_value:
                    return variable_to_value[kw.value.id][0]
                log_warning(f"Warning: Edge label is wrong: {ast.dump(kw.value)}")
            return None
    return None


def resolve_left(node: ast.AST) -> list:
    """
    Resolve the left-hand side of a binary operation into a list of variable IDs.
    
    Args:
        node: AST node to resolve
        
    Returns:
        list: List of resolved variable IDs
    """
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.List):
        return [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
    elif isinstance(node, ast.Call):
        if isinstance(node.args[0], ast.Constant):
            return [node.args[0].value]
    elif isinstance(node, ast.BinOp):
        if isinstance(node.right, ast.Name):
            return [node.right.id]
        elif isinstance(node.right, ast.List):
            return [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]
        elif isinstance(node, ast.Call):
            if len(node.args) > 0:
                if isinstance(node.args[0], ast.Constant):
                    return [node.args[0].value]
        return resolve_left(node.left)
    return []


class DiagramVisitor(ast.NodeVisitor):
    """AST Visitor that extracts classes, class-to-variable mappings, and connections from the diagram."""
    
    def __init__(self):
        self.all_classes = []
        self.variable_to_class = {}
        self.all_connections = []
        self.all_class_to_methods = {}
        self.variable_to_value = {}

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignment nodes to track class variables and lists."""
        try:
            self._process_assignment(node)
        except Exception as e:
            log_error(f"Error processing assignment: {e}")
        self.generic_visit(node)

    def _process_assignment(self, node: ast.Assign) -> None:
        """Process an assignment node to update internal state."""
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
            self.variable_to_value.setdefault(variable, []).append(value.value)

    def _handle_class_assignment(self, variable: str, value: ast.Call) -> None:
        """Handle assignment of a class to a variable."""
        for arg in value.args:
            if isinstance(arg, ast.Constant):
                class_name = arg.value
                self.all_classes.append(class_name)
                self.variable_to_class[variable] = class_name

    def _handle_list_assignment(self, variable: str, value: ast.List) -> None:
        """Handle assignment of a list of classes to a variable."""
        for elt in value.elts:
            if isinstance(elt, ast.Name):
                class_var = elt.id
                if class_var not in self.variable_to_class:
                    log_warning(f"Warning: {class_var} referenced before assignment.")
                    continue
                class_name = self.variable_to_class[class_var]
                self.all_classes.append(class_name)
                self.variable_to_value.setdefault(variable, []).append(class_name)

            if isinstance(elt, ast.Constant):
                class_name = elt.value
                self.all_classes.append(class_name)
                self.variable_to_value.setdefault(variable, []).append(class_name)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        """Visit binary operations to detect connections (edges)."""
        try:
            self._process_binop(node)
        except Exception as e:
            log_error(f"Error processing BinOp: {e}")
        self.generic_visit(node)

    def _process_binop(self, node: ast.BinOp) -> None:
        """Process a binary operation node to extract connections."""
        if not isinstance(node.left, ast.Name):
            temp_node = node.left if not isinstance(node.left, ast.List) else node
            method = extract_method_from_edge(getattr(temp_node, 'right', None), self.variable_to_value)
        else:
            method = None
            
        if method is not None:
            left_class_ids = resolve_left(node.left)
            right_class_ids = self._resolve_right_classes(node.right)
            self.add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def _resolve_right_classes(self, node: ast.AST) -> list:
        """Resolve class IDs from the right side of a binary operation."""
        if isinstance(node, ast.Name):
            return [node.id]
        elif isinstance(node, ast.List):
            return [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
        elif isinstance(node, ast.Call):
            if len(node.args) > 0:
                if isinstance(node.args[0], ast.Constant):
                    return [node.args[0].value]
        return []

    def visit_For(self, node: ast.For) -> None:
        """Visit For loop nodes to extract connections from loops."""
        try:
            self._process_for_loop(node)
        except Exception as e:
            log_error(f"Error processing For loop: {e}")
        self.generic_visit(node)

    def _process_for_loop(self, node: ast.For) -> None:
        """Process a For loop node to extract connections."""
        if not isinstance(node.target, ast.Name):
            log_warning("Warning: For loop target not supported.")
            return

        loop_var = node.target.id
        iteration_elements = self._get_iteration_elements(node.iter)

        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.BinOp):
                self._process_binop_in_for(stmt.value, loop_var, iteration_elements)

    def _get_iteration_elements(self, iter_node: ast.AST) -> list:
        """Extract iteration elements from a For loop's iterable."""
        if isinstance(iter_node, ast.List):
            return [elt.id for elt in iter_node.elts if isinstance(elt, ast.Name)]

        if isinstance(iter_node, ast.Name) and iter_node.id in self.variable_to_value:
            return self.variable_to_value[iter_node.id]

        return []

    def _process_binop_in_for(self, node: ast.BinOp, loop_var: str, iteration_elements: list) -> None:
        """Process a binary operation inside a For loop."""
        left_class_ids = []
        if isinstance(node.left, ast.BinOp) and isinstance(node.left.left, ast.Name):
            if node.left.left.id == loop_var:
                left_class_ids = iteration_elements
            else:
                left_class_ids = [node.left.left.id]

        method = None
        if isinstance(node.left, ast.BinOp) and isinstance(node.left.right, ast.Call):
            method = extract_method_from_edge(node.left.right, self.variable_to_value)
            
        right_class_ids = []
        if isinstance(node.right, ast.List):
            right_class_ids = [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]
        elif isinstance(node.right, ast.Name):
            right_class_ids = [node.right.id]
        elif isinstance(node.right, ast.Call):
            if isinstance(node.right.args[0], ast.Name) and node.right.args[0].id == loop_var:
                right_class_ids = iteration_elements

        self.add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def add_to_connections(self, left_class_ids: list, method: str, right_class_ids: list, op: ast.operator) -> None:
        """Add connections between classes based on the operator and method."""
        for cls in right_class_ids:
            if cls not in self.all_class_to_methods and self.variable_to_class.get(cls) not in self.all_class_to_methods:
                if cls in self.variable_to_class:
                    self.all_class_to_methods[self.variable_to_class[cls]] = []
                else:
                    self.all_class_to_methods[cls] = []

        if method is None:
            return
        
        for left_id in left_class_ids:
            if left_id in self.all_classes:
                left_class = left_id
            elif left_id not in self.variable_to_class and left_id not in self.all_classes:
                log_warning(f"Warning: Left {left_id} not found in variable_to_class map.")
                continue
            else:
                left_class = self.variable_to_class[left_id]

            # Handle inheritance relationships
            if method == "inherits":
                for right_id in right_class_ids:
                    right_class = self._get_right_class(right_id)
                    if right_class is None:
                        continue
                    self.add_class_to_methods(left_class, method, right_class)
                continue

            # Handle other methods and connections
            for right_id in right_class_ids:
                right_class = self._get_right_class(right_id)
                if right_class is None:
                    continue

                if left_class == right_class:
                    self.add_class_to_methods(left_class, method, right_class)
                    continue

                if isinstance(op, ast.RShift):
                    self.all_connections.append([left_class, method, right_class])
                    self.add_class_to_methods(left_class, method, right_class)
                else:
                    self.all_connections.append([right_class, method, left_class])
                    self.add_class_to_methods(right_class, method, left_class)

    def _get_right_class(self, right_id: str) -> str:
        """Get the actual class name from a right-side ID."""
        if right_id in self.all_classes:
            return right_id
        elif right_id not in self.variable_to_class:
            log_warning(f"Warning: Right {right_id} not found in variable_to_class map.")
            return None
        return self.variable_to_class[right_id]

    def add_class_to_methods(self, class_name: str, method: str, another_class_name: str = None) -> None:
        """Add a method to a class in the internal mapping."""
        if method == 'inherits':
            if another_class_name and another_class_name in self.all_class_to_methods:
                inherited_methods = self.all_class_to_methods[another_class_name]
                self.all_class_to_methods.setdefault(class_name, []).extend(inherited_methods)
            return

        if method not in self.all_class_to_methods.setdefault(class_name, []):
            self.all_class_to_methods[class_name].append(method)

    def get_results(self) -> tuple:
        """Get the analysis results."""
        return self.all_classes, self.all_class_to_methods, self.all_connections, self.variable_to_class


class CodeVisitor(ast.NodeVisitor):
    """AST Visitor to parse code classes and methods, including inheritance resolution."""
    
    def __init__(self):
        self.classes = []
        self.current_class = None
        self.class_to_methods = {}
        self.class_to_parents = {}

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to extract class information."""
        self.current_class = node.name
        self.classes.append(node.name)
        self.class_to_methods[node.name] = []

        parents = self._extract_parents(node)
        # Continuation of the CodeVisitor class from above...
        self.class_to_parents[node.name] = parents
        self.generic_visit(node)
        self.current_class = None

    def _extract_parents(self, node: ast.ClassDef) -> list:
        """Extract parent class names from a class definition."""
        parents = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                parents.append(base.id)
            elif isinstance(base, ast.Attribute):
                parents.append(base.attr)
        return parents

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to extract method information."""
        if self.current_class and node.name != "__init__":
            self.class_to_methods[self.current_class].append(node.name + "()")
        self.generic_visit(node)

    def resolve_inheritance(self) -> None:
        """Resolve inherited methods for all classes."""
        resolved_methods = {}
        for class_name in self.classes:
            resolved_methods[class_name] = set(self.class_to_methods.get(class_name, []))

        for class_name, parents in self.class_to_parents.items():
            for parent in parents:
                if parent not in resolved_methods:
                    continue
                resolved_methods[class_name].update(resolved_methods[parent])

        for class_name in resolved_methods:
            self.class_to_methods[class_name] = list(resolved_methods[class_name])

    def get_results(self) -> tuple:
        """Get the analysis results after resolving inheritance."""
        self.resolve_inheritance()
        return self.classes, self.class_to_methods


def analyze_diagram(diagram_content: str) -> tuple:
    """
    Parse and analyze a diagram file's content.
    
    Args:
        diagram_content: Content of the diagram file
        
    Returns:
        tuple: (classes, methods, connections, variable_mappings)
    """
    try:
        tree = ast.parse(diagram_content)
    except SyntaxError as e:
        log_error(f"Error parsing diagram: {e}")
        return [], {}, [], {}

    diagram_visitor = DiagramVisitor()
    diagram_visitor.visit(tree)
    return diagram_visitor.get_results()


def analyze_code(code_content: str) -> tuple:
    """
    Parse and analyze a code file's content.
    
    Args:
        code_content: Content of the code file
        
    Returns:
        tuple: (classes, methods)
    """
    try:
        tree = ast.parse(code_content)
    except SyntaxError as e:
        log_error(f"Error parsing code: {e}")
        return [], {}

    code_visitor = CodeVisitor()
    code_visitor.visit(tree)
    return code_visitor.get_results()


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
    statements = parsed_json[0]['stmts']
    
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


def handle_updates(extra_classes: set, extra_methods: dict, diagram_file: str, variable_to_classes: dict) -> bool:
    """
    Handle selective updates to the diagram file.
    
    Returns:
        bool: True if updates were successful
    """
    if not (extra_classes or extra_methods):
        return True

    create_backup(diagram_file)
    
    if not validate_diagram_syntax(diagram_file):
        return False
    
    
    with open(diagram_file, "a") as f:
        if extra_classes:
            for cls in extra_classes:
                user_input = input(f"Add class {cls} to diagram? (yes/no): ").strip().lower()
                if user_input == 'yes' or user_input == 'y':
                    f.write(f"\n    {cls} = Action('{cls}')")
                    variable_to_classes[cls] = cls
                else:
                    restore_backup(diagram_file)
        if extra_methods:
            for cls, methods in extra_methods.items():
                value = [i for i in variable_to_classes if variable_to_classes[i] == cls]
                cls_var = value[0] if value else f'Action("{cls}")'
                for method in methods:
                    user_input = input(f"Add method {method} to {cls}? (yes/no): ").strip().lower()
                    if user_input == 'yes' or user_input == 'y':
                        f.write(f"\n    {cls_var} >> Edge(label='{method}', color='red') >> {cls_var}")
                    else:
                        restore_backup(diagram_file)
        f.close()

    return validate_update(diagram_file)

def main():
    php_parser = 'php_parser.php'

    code_file_name = sys.argv[1]
    diagram_file_name = sys.argv[2]
    # code_file_name = "classes_examples/classes.py"
    # code_file_name = "classes_examples/classes.php"
    # diagram_file_names = ["diagram_examples/diagram.py"]

    code_file_name = sys.argv[1]
    diagram_file_name = sys.argv[2]

    code_classes, code_methods = parse_code_file(code_file_name)

    all_diagram_classes = set()
    aggregated_diagram_methods = {}

    try:
        with open(file_name, "r") as f:
            diagram_content = f.read()
    except FileNotFoundError:
        print(f"Error: Diagram file {file_name} not found.")
        sys.exit(1)

    diagram_classes, diagram_methods, all_connections = analyze_diagram(diagram_content)
    print("Diagram methods:", diagram_methods)
    pprint("Diagram methods:", diagram_methods)
        # fp1 = open('./tmp/diagram_classes.json', 'w+')
        # json.dump(diagram_classes, fp1)

        # fp2 = open('./tmp/all_connections.json', 'w+')
        # json.dump(all_connections, fp2)

        # fp3 = open('./tmp/diagram_methods.json', 'w+')
        # json.dump(diagram_methods, fp3)
        # fp4 = open('./tmp/mydict.json', 'w+')
        # json.dump({"classes": diagram_classes, "diagram_methods": diagram_methods,"all_connections": all_connections}, fp4)
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
        print("\n❌ Discrepancies found! Commit aborted.\n")
        sys.exit(1)

    else:
        print(f"\n✅ Code {code_file_name} and its Diagram are in sync!\n")
        sys.exit(0)

if __name__ == "__main__":
    main()