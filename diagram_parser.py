import ast
from logging_utils import log_error, log_warning, log_info

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
