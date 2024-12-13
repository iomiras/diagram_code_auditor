import ast
from pprint import pprint

from torch.distributed.rpc.api import method_name

with open("classes/classes.py", "r") as f:
    code = f.read()

with open('diagrams/diagram.py', 'r') as f:
    diagram = f.read()


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.all_classes = []
        self.variable_to_class = {}
        self.all_connections = []
        self.last_left_classes = []

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
                method = next(
                    (kw.value.value for kw in temp_node.right.keywords if kw.arg == "label"),
                    None,
                )
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

            for left in left_class:
                _left = self.variable_to_class[left]
                for right in right_class:
                    _right = self.variable_to_class[right]
                    if isinstance(node.op, ast.RShift):
                        self.all_connections.append([_left, method, _right])
                    else:
                        self.all_connections.append([_right, method, _left])
            #         self.all_connections.append([left, method, right])
            # print('Left', left_class)
            # print('Node.op and method', ast.dump(node.op, indent=4), method)
            # print('Right', right_class)
            # print("===========")

        self.generic_visit(node)

    def get_results(self):
        return self.all_classes, self.variable_to_class, self.all_connections

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


def analyze_diagram(diagram):
    tree = ast.parse(diagram)
    visitor = Visitor()
    visitor.visit(tree)

    all_classes, variable_to_class, all_connections = visitor.get_results()

    # Print results for debugging
    print("All Classes:", all_classes)
    print("Variable to Class Mapping:", variable_to_class)
    print("All Connections:")
    pprint(all_connections)

    return all_classes, all_connections


def extract_attribute_chain(node):
    if isinstance(node, ast.Attribute):
        parent_chain = extract_attribute_chain(node.value)
        if parent_chain == 'self':
            return node.attr
        return f"{parent_chain}.{node.attr}"
    elif isinstance(node, ast.Name):
        return node.id
    return None

def analyze_code(code):
    tree = ast.parse(code)
    results = {}
    all_variables = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            results[class_name] = {}

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name + '()'
                    variables = []
                    calls = []

                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.Attribute):
                            attr_chain = extract_attribute_chain(stmt)
                            if attr_chain:
                                variables.append(attr_chain)
                                if attr_chain not in all_variables:
                                    all_variables.append(attr_chain)

                        if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute):
                            func_chain = extract_attribute_chain(stmt.func)
                            if func_chain:
                                calls.append(func_chain)

                    variables = set(variables)
                    results[class_name][method_name] = {
                        "variables": list(variables),
                        "calls": list(set(calls)),
                    }

    analysis_result = results
    method_var_to_class = {}

    for class_name in analysis_result.keys():
        for method_name in analysis_result[class_name]:
            if method_name == '__init__()':
                if analysis_result[class_name][method_name]:
                    for variable in analysis_result[class_name][method_name]['variables']:
                        if variable in method_var_to_class:
                            method_var_to_class[variable].append(class_name)
                        else:
                            method_var_to_class[variable] = [class_name]
            else:
                if method_name in method_var_to_class:
                    method_var_to_class[method_name].append(class_name)
                else:
                    method_var_to_class[method_name] = [class_name]

    variable_to_class = {}
    for variable in all_variables:
        if '.' in variable:
            v0, v1 = variable.split('.')
            if v1 + '()' in method_var_to_class:
                variable_to_class[v0] = method_var_to_class[v1 + '()'][0]
            elif v1 in method_var_to_class:
                variable_to_class[v0] = method_var_to_class[v1][0]
        else:
            variable_to_class[variable] = method_var_to_class[variable][0]

    all_connections = []
    all_classes = list(analysis_result.keys())

    for class_name in analysis_result.keys():
        for method_name in analysis_result[class_name]:
            for variable in analysis_result[class_name][method_name]['variables']:
                if '.' in variable:
                    v0, v1 = variable.split('.')
                    all_connections.append([class_name, method_name, variable_to_class[v0]])
    return all_classes, all_connections

all_diagram_classes, all_diagram_connections = analyze_diagram(diagram)
# print(all_diagram_classes)
# pprint(all_diagram_connections)
#
#
# print("============")
#
# all_code_classes, all_code_connections = analyze_code(code)
# print(all_code_classes)
# pprint(all_code_connections)