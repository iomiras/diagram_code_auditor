import ast
from pprint import pprint

with open("classes/classes1.py", "r") as f:
    code = f.read()

with open('diagrams/diagram.py', 'r') as f:
    diagram = f.read()

class Visitor(ast.NodeVisitor):
    def visit_Assign(self, node):
        self.generic_visit(node)
        print(f"Visiting {ast.dump(node, indent=4)}")

def analyze_diagram(diagram):
    tree = ast.parse(diagram)
    # print(ast.dump(tree, indent=4))
    variable_to_class = {}
    all_connections = []
    all_classes = []
    Visitor().visit_Assign(tree)

    for node in tree.body:
        if isinstance(node, ast.With):
            for _node in node.body:
                if isinstance(_node, ast.With):
                    # print("===== ITEM =====", ast.dump(_node, indent=4))
                    # print("item Body", _node.body)
                    items = _node.body
                    # while isinstance(_items, ast.With) for _items in items:
                    # TO-DO - Handle nested with statements
                else:
                    items = [_node]
                for item in items:
                    # print("====ITEM====\n", ast.dump(item, indent=4))
                    class_left = []
                    class_right = []
                    if isinstance(item, ast.Assign):
                        variable = item.targets[0].id
                        for arg in item.value.args:
                            class_name = arg.value
                            all_classes.append(class_name)
                            variable_to_class[variable] = class_name

                    if isinstance(item, ast.Expr):
                    # class1 = variable_to_class[item.value.left.left.id]
                    #     print("====ITEM====\n", ast.dump(item, indent=4))
                    #     print(variable_to_class)
                        if isinstance(item.value.left.left, ast.Name):
                            class_left.append(variable_to_class[item.value.left.left.id])
                        elif isinstance(item.value.left.left, ast.List):

                            class_left.append(variable_to_class[item.value.left.left.elts[0].id])
                            class_left.append(variable_to_class[item.value.left.left.elts[1].id])

                        method = item.value.left.right.keywords[0].value.value
                        right_direction = isinstance(item.value.left.op, ast.RShift)
                        if isinstance(item.value.right, ast.Name):
                            class_right.append(variable_to_class[item.value.right.id])
                        elif isinstance(item.value.right, ast.List):
                            class_right.append(variable_to_class[item.value.right.elts[0].id])
                            class_right.append(variable_to_class[item.value.right.elts[1].id])
                        for i in range(len(class_left)):
                            for j in range(len(class_right)):
                                if right_direction:
                                    all_connections.append([class_left[i], method, class_right[j]])
                                else:
                                    all_connections.append([class_right[i], method, class_left[j]])

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
print(all_diagram_classes)
pprint(all_diagram_connections)


print("============")

all_code_classes, all_code_connections = analyze_code(code)
print(all_code_classes)
pprint(all_code_connections)