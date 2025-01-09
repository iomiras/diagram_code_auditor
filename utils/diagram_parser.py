import ast
from utils.logging_utils import log_error, log_warning

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

class DiagramVisitor(ast.NodeVisitor):
    """AST Visitor that extracts classes, class-to-variable mappings, and connections from the diagram."""
    
    def __init__(self):
        self.all_classes = []
        self.variable_to_class = {}
        self.all_connections = []
        self.all_class_to_methods = {}
        self.variable_to_value = {}
    
    def _add_class(self, class_name: str) -> None:
        """Add a class to the internal list of classes."""
        if class_name not in self.all_classes:
            self.all_classes.append(class_name)
    
    def _map_variable_to_class(self, variable: str, class_name: str) -> None:
        self._add_class(class_name)
        self.variable_to_class[variable] = class_name
    
    def _map_variable_to_value(self, variable: str, value: str) -> None:
        if variable not in self.variable_to_value:
            self.variable_to_value[variable] = []
        # If it's a list, extend it; otherwise just append
        if isinstance(value, list):
            for v in value:
                if v not in self.variable_to_value[variable]:
                    self.variable_to_value[variable].append(v)
        else:
            if value not in self.variable_to_value[variable]:
                self.variable_to_value[variable].append(value)

    def _ensure_class_has_methods_list(self, class_name: str) -> None:
        """Ensure the given class name has an entry in all_class_to_methods."""
        if class_name not in self.all_class_to_methods:
            self.all_class_to_methods[class_name] = []

    def _add_to_connections(self, left_class_ids: list, method: str, right_class_ids: list, op: ast.operator) -> None:
        """Add connections between classes based on the operator and method."""
        for cls in right_class_ids:
            if cls not in self.all_class_to_methods and self.variable_to_class.get(cls) not in self.all_class_to_methods:
                if cls in self.variable_to_class:
                    self.all_class_to_methods[self.variable_to_class[cls]] = []
                else:
                    self.all_class_to_methods[cls] = []
            if cls in self.variable_to_value and type(self.variable_to_value[cls]) == list:
                for current_class in self.variable_to_value[cls]:
                    for _method in self.all_class_to_methods[cls]:
                        self.all_class_to_methods[current_class] = [_method]
                        # self.add_class_to_methods(current_class, _method, cls)
                        # self.all_class_to_methods[current_class].append(_method)

        if method is None:
            return
        
        for left_id in left_class_ids:
            if left_id in self.all_classes or left_id in self.variable_to_value.keys():
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
                # print(f"RIGHT CLASS: {right_class}")
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


    def _map_class_to_methods(self, class_name, method: str, another_class_name) -> None:
        """
        Add a method to a class in the internal mapping or handle inheritance.
        If `method == 'inherits'`, we copy inherited methods from another class.
        """
        # Inheritance block
        if method == 'inherits':
            if another_class_name and another_class_name in self.all_class_to_methods:
                inherited_methods = self.all_class_to_methods[another_class_name]
                # If class_name is actually a variable containing multiple classes
                if class_name in self.variable_to_value:
                    # We assume self.variable_to_value[class_name] is a list
                    for current_class in self.variable_to_value[class_name]:
                        self._ensure_class_has_methods_list(current_class)
                        # Extend without duplicating
                        for im in inherited_methods:
                            if im not in self.all_class_to_methods[current_class]:
                                self.all_class_to_methods[current_class].append(im)
                else:
                    # Single class_name
                    self._ensure_class_has_methods_list(class_name)
                    for im in inherited_methods:
                        if im not in self.all_class_to_methods[class_name]:
                            self.all_class_to_methods[class_name].append(im)
            return

        # Non-inheritance: Just add the method to class_name
        # If the class_name is a variable containing multiple classes
        if class_name in self.variable_to_value:
            for current_class in self.variable_to_value[class_name]:
                self._ensure_class_has_methods_list(current_class)
                if method not in self.all_class_to_methods[current_class]:
                    self.all_class_to_methods[current_class].append(method)
        else:
            # Single class
            self._ensure_class_has_methods_list(class_name)
            if method not in self.all_class_to_methods[class_name]:
                self.all_class_to_methods[class_name].append(method)

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
            self._map_variable_to_value(variable, value.value)

    def _handle_class_assignment(self, variable: str, value: ast.Call) -> None:
        """Handle assignment of a class to a variable."""
        for arg in value.args:
            if isinstance(arg, ast.Constant):
                class_name = arg.value
                self._map_variable_to_class(variable, class_name)

    def _handle_list_assignment(self, variable: str, value: ast.List) -> None:
        """Handle assignment of a list of classes to a variable."""
        for elt in value.elts:
            if isinstance(elt, ast.Name):
                class_var = elt.id
                if class_var not in self.variable_to_class:
                    log_warning(f"Warning: {class_var} referenced before assignment.")
                    continue
                class_name = self.variable_to_class[class_var]

            elif isinstance(elt, ast.Constant):
                class_name = elt.value

            self._add_class(class_name)
            self._map_variable_to_value(variable, class_name)

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
            left_class_ids = self._resolve_node(node.left, 'left')
            right_class_ids = self._resolve_node(node.right, 'right')
            self._add_to_connections(left_class_ids, method, right_class_ids, node.op)
    
    def _resolve_node(self, node: ast.AST, type) -> str:
        if isinstance(node, ast.Name):
            return [node.id]
        elif isinstance(node, ast.List):
            return [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
        elif isinstance(node, ast.Call):
            if len(node.args) > 0:
                if isinstance(node.args[0], ast.Constant):
                    return [node.args[0].value]
        if type == 'left':
            if isinstance(node, ast.BinOp):
                if isinstance(node.right, ast.Name):
                    return [node.right.id]
                elif isinstance(node.right, ast.List):
                    return [elt.id for elt in node.right.elts if isinstance(elt, ast.Name)]
                elif isinstance(node, ast.Call):
                    if len(node.args) > 0:
                        if isinstance(node.args[0], ast.Constant):
                            return [node.args[0].value]
                return self._resolve_node(node.left, 'left')
        else:
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
        # print(f"LOOP VAR: {loop_var}")
        iteration_elements = self._get_iteration_elements(node.iter)
        # print(f"ITERATION ELEMENTS: {iteration_elements}")

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
            # print("Loop var: ", loop_var)
            # print("Right class ids: ", right_class_ids)
        elif isinstance(node.right, ast.Call):
            # print(f"LEFT CLASS IDS: {left_class_ids}")
            # print(f"RIGHT CLASS IDS PPP: {node.right.args[0].id}")
            # print(f"METHOD: {method}")
            if isinstance(node.right.args[0], ast.Name) and node.right.args[0].id == loop_var:
                right_class_ids = iteration_elements
        self._add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def _get_right_class(self, right_id: str) -> str:
        """Get the actual class name from a right-side ID."""
        if right_id in self.all_classes:
            return right_id
        elif right_id in self.variable_to_class:
            return self.variable_to_class[right_id]
        elif right_id in self.variable_to_value:
            # Handle multiple values; return the first one (or handle as needed)
            values = self.variable_to_value[right_id]
            return values[0] if isinstance(values, list) and values else None
        else:
            log_warning(f"Warning: Right {right_id} not found in variable_to_class map.")
            return None


    def add_class_to_methods(self, class_name, method: str, another_class_name) -> None:
        """Add a method to a class in the internal mapping."""
        if method == 'inherits':
            if another_class_name in self.all_class_to_methods:
                inherited_methods = self.all_class_to_methods[another_class_name]
                if class_name in self.variable_to_value:
                    # For multiple classes in variable_to_value
                    for current_class in self.variable_to_value[class_name]:
                        self._ensure_class_has_methods_list(current_class)
                        for inherited_method in inherited_methods:
                            if inherited_method not in self.all_class_to_methods[current_class]:
                                self.all_class_to_methods[current_class].append(inherited_method)
                else:
                    # Single class inheritance
                    self._ensure_class_has_methods_list(class_name)
                    for inherited_method in inherited_methods:
                        if inherited_method not in self.all_class_to_methods[class_name]:
                            self.all_class_to_methods[class_name].append(inherited_method)
            return

        # Non-inheritance case
        if class_name in self.variable_to_value:
            for current_class in self.variable_to_value[class_name]:
                self._ensure_class_has_methods_list(current_class)
                if method not in self.all_class_to_methods[current_class]:
                    self.all_class_to_methods[current_class].append(method)
        else:
            self._ensure_class_has_methods_list(class_name)
            if method not in self.all_class_to_methods[class_name]:
                self.all_class_to_methods[class_name].append(method)


    def get_results(self) -> tuple:
        """Get the analysis results."""
        return self.all_classes, self.all_class_to_methods, self.all_connections, self.variable_to_class