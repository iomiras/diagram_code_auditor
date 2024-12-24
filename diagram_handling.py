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
        Visit assignment nodes to identify d track class variables and lists of class variables.
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
            method = self.extract_method_from_edge(getattr(temp_node, 'right', None), self.variable_to_value)
        else:
            method = None

        if method is not None:
            left_class_ids = self.resolve_left(node.left)
            right_class_ids = self._resolve_right_classes(node.right)
            self.add_to_connections(left_class_ids, method, right_class_ids, node.op)
    
    def resolve_left(self, node):
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
            return self.resolve_left(node.left)
        return []

    def extract_method_from_edge(self, node, variable_to_value={}):
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

        self.add_to_connections(left_class_ids, method, right_class_ids, node.op)

    def add_to_connections(self, left_class_ids, method, right_class_ids, op):
        """
        Add connections from left classes to right classes based on the operator.
        For example, A >> Edge(label="method") >> B means A.method connects to B.
        """
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