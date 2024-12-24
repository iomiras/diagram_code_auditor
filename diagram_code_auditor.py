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

class DiagramVisitor(ast.NodeVisitor):
    def __init__(self):
        self.all_classes = []
        self.variable_to_class = {}
        self.all_connections = []
        self.all_class_to_methods = {}
        self.variable_to_value = {}

    def visit_Assign(self, node):
        try:
            self._process_assignment(node)
        except Exception as e:
            log_error(f"Error processing assignment: {e}")
        self.generic_visit(node)

    def _process_assignment(self, node):
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

    def _handle_class_assignment(self, variable, value):
        for arg in value.args:
            if isinstance(arg, ast.Constant):
                class_name = arg.value
                self.all_classes.append(class_name)
                self.variable_to_class[variable] = class_name

    def _handle_list_assignment(self, variable, value):
        for elt in value.elts:
            if isinstance(elt, ast.Name):
                self._add_class_from_variable(variable, elt.id)
            elif isinstance(elt, ast.Constant):
                self._add_class_from_constant(variable, elt.value)

    def _add_class_from_variable(self, variable, class_var):
        class_name = self.variable_to_class.get(class_var)
        if class_name:
            self._store_class(variable, class_name)
        else:
            log_warning(f"Warning: {class_var} referenced before assignment.")

    def _add_class_from_constant(self, variable, class_name):
        self._store_class(variable, class_name)

    def _store_class(self, variable, class_name):
        self.all_classes.append(class_name)
        self.variable_to_value.setdefault(variable, []).append(class_name)

    def visit_BinOp(self, node):
        try:
            self._process_binop(node)
        except Exception as e:
            log_error(f"Error processing BinOp: {e}")
        self.generic_visit(node)

    def _process_binop(self, node):
        left_class_ids = self._resolve_left(node.left)
        method = extract_method_from_edge(node.right, self.variable_to_value)
        right_class_ids = self._resolve_right(node.right)
        self.add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def _resolve_left(self, node):
        if isinstance(node, ast.Name):
            return [node.id]
        elif isinstance(node, ast.List):
            return [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
        elif isinstance(node, ast.Call):
            return [node.args[0].value] if isinstance(node.args[0], ast.Constant) else []
        elif isinstance(node, ast.BinOp):
            return self._resolve_left(node.left)
        return []

    def _resolve_right(self, node):
        if isinstance(node, ast.Name):
            return [node.id]
        elif isinstance(node, ast.List):
            return [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
        elif isinstance(node, ast.Call):
            return [node.args[0].value] if isinstance(node.args[0], ast.Constant) else []
        return []

    def visit_For(self, node):
        try:
            self._process_for_loop(node)
        except Exception as e:
            log_error(f"Error processing For loop: {e}")
        self.generic_visit(node)

    def _process_for_loop(self, node):
        loop_var = node.target.id if isinstance(node.target, ast.Name) else None
        iteration_elements = self._get_iteration_elements(node.iter)
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.BinOp):
                self._process_binop_in_for(stmt.value, loop_var, iteration_elements)

    def _get_iteration_elements(self, iter_node):
        if isinstance(iter_node, ast.List):
            return [elt.id for elt in iter_node.elts if isinstance(elt, ast.Name)]
        if isinstance(iter_node, ast.Name):
            return self.variable_to_value.get(iter_node.id, [])
        return []

    def _process_binop_in_for(self, node, loop_var, iteration_elements):
        left_class_ids = iteration_elements if loop_var else []
        method = extract_method_from_edge(node.right, self.variable_to_value)
        right_class_ids = self._resolve_right(node.right)
        self.add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def add_to_connections(self, left_class_ids, method, right_class_ids, op):
        if method is None:
            return
        for left_id in left_class_ids:
            left_class = self.variable_to_class.get(left_id, left_id)
            for right_id in right_class_ids:
                right_class = self.variable_to_class.get(right_id, right_id)
                self._record_connection(left_class, method, right_class, op)

    def _record_connection(self, left_class, method, right_class, op):
        if isinstance(op, ast.RShift):
            self.all_connections.append([left_class, method, right_class])
        else:
            self.all_connections.append([right_class, method, left_class])

    def get_results(self):
        return self.all_classes, self.all_class_to_methods, self.all_connections, self.variable_to_class

class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.class_to_methods = {}
        self.class_to_parents = {}

    def visit_ClassDef(self, node):
        self.classes.append(node.name)
        self.class_to_methods[node.name] = []
        self.class_to_parents[node.name] = self._extract_parents(node)
        self.generic_visit(node)

    def _extract_parents(self, node):
        return [base.id for base in node.bases if isinstance(base, ast.Name)]

    def visit_FunctionDef(self, node):
        if node.name != "__init__":
            self.class_to_methods.setdefault(node.parent_class, []).append(node.name + "()")
        self.generic_visit(node)

    def resolve_inheritance(self):
        for class_name, parents in self.class_to_parents.items():
            for parent in parents:
                self.class_to_methods[class_name].extend(self.class_to_methods.get(parent, []))

    def get_results(self):
        self.resolve_inheritance()
        return self.classes, self.class_to_methods

def analyze_diagram(content):
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        log_error(f"Error parsing diagram: {e}")
        return [], {}, []

    visitor = DiagramVisitor()
    visitor.visit(tree)
    return visitor.get_results()

def analyze_code(content):
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        log_error(f"Error parsing code: {e}")
        return [], {}

    visitor = CodeVisitor()
    visitor.visit(tree)
    return visitor.get_results()

def compare_classes(code_classes, diagram_classes):
    return (
        set(diagram_classes) - set(code_classes),
        set(code_classes) - set(diagram_classes),
    )

def compare_methods(code_methods, diagram_methods):
    missing, extra = {}, {}
    all_classes = set(code_methods) | set(diagram_methods)
    for cls in all_classes:
        code = set(code_methods.get(cls, []))
        diagram = set(diagram_methods.get(cls, []))
        if missing_diff := diagram - code:
            missing[cls] = missing_diff
        if extra_diff := code - diagram:
            extra[cls] = extra_diff
    return missing, extra

def parse_code_file(file_path):
    if file_path.endswith(".py"):
        with open(file_path, "r") as f:
            return analyze_code(f.read())
    elif file_path.endswith(".php"):
        subprocess.run(["php", "php_parser.php"])
        with open("./tmp/ast.json", "r") as f:
            return parse_json(f.read())
    else:
        log_error("Unsupported file type. Only .py and .php are supported.")
        sys.exit(1)

def handle_updates(missing_classes, extra_classes, missing_methods, extra_methods, diagram_file, variable_to_classes):
    if not (missing_classes or extra_classes or missing_methods or extra_methods):
        return True

    create_backup(diagram_file)

    if not validate_diagram_syntax(diagram_file):
        return False

    with open(diagram_file, "a") as f:
        if extra_methods:
            for cls, methods in extra_methods.items():
                cls_var = next((var for var, value in variable_to_classes.items() if value == cls), f'Action("{cls}")')
                for method in methods:
                    if input(f"Add method {method} to {cls}? (yes/no): ").strip().lower() == "yes":
                        f.write(f"\n    {cls_var} >> Edge(label='{method}', color='red') >> {cls_var}")

        if extra_classes:
            for cls in extra_classes:
                if input(f"Add class {cls} to diagram? (yes/no): ").strip().lower() == "yes":
                    f.write(f"\n    {cls} = Action('{cls}')")

    return validate_update(diagram_file)

if __name__ == "__main__":
    code_file = sys.argv[1]
    diagram_file = sys.argv[2]

    code_classes, code_methods = parse_code_file(code_file)

    try:
        with open(diagram_file, "r") as f:
            diagram_content = f.read()
    except FileNotFoundError:
        log_error(f"Diagram file {diagram_file} not found.")
        sys.exit(1)

    diagram_classes, diagram_methods, _, variable_to_classes = analyze_diagram(diagram_content)

    missing_classes, extra_classes = compare_classes(code_classes, diagram_classes)
    missing_methods, extra_methods = compare_methods(code_methods, diagram_methods)

    if not (missing_classes or extra_classes or missing_methods or extra_methods):
        print(f"\n✅ Code {code_file} and its Diagram are in sync!\n")
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

    if input("Do you want to rewrite the diagram file? (yes/no): ").strip().lower() in ["yes", "y"]:
        if handle_updates(missing_classes, extra_classes, missing_methods, extra_methods, diagram_file, variable_to_classes):
            print("\nDiagram updated successfully.")
        else:
            print("\nFailed to update diagram. Commit aborted.")
    else:
        print("\n❌ Commit aborted.")
        sys.exit(1)