import ast
from pprint import pprint

from imageio.config.plugins import class_name
from torch.autograd import variable
from torch.distributed.rpc.api import method_name

with open("classes/classes.py", "r") as f:
    code = f.read()

with open('diagrams/diagram.py', 'r') as f:
    diagram = f.read()

def analyze_diagram(diagram):
    tree = ast.parse(diagram)
    variable_to_class = {}
    all_connections = []
    all_classes = []

    for node in tree.body:
        if isinstance(node, ast.With):
            for item in node.body:
                # print(ast.dump(item, indent=4))
                if isinstance(item, ast.Assign):
                    variable = item.targets[0].id
                    for arg in item.value.args:
                        class_name = arg.value
                        all_classes.append(class_name)
                        variable_to_class[variable] = class_name

                if isinstance(item, ast.Expr):
                    class1 = variable_to_class[item.value.left.left.id]
                    class2 = variable_to_class[item.value.right.id]
                    method = item.value.left.right.keywords[0].value.value
                    right_direction = isinstance(item.value.left.op, ast.RShift)
                    if right_direction:
                        all_connections.append([class1, method, class2])
                    else:
                        all_connections.append([class2, method, class1])

                    # print(ast.dump(item.value, indent=4))
                    # print("left:", item.value.left.left.id)
                    # print("op is Rshift:", isinstance(item.value.left.op, ast.RShift))
                    # print("binding function:", item.value.left.right.keywords[0].value.value)
                    # print("right:", item.value.right.id)


                    # for operation in item.value:
                    #     if isinstance(operation, ast.BinOp):
                    #         print(ast.dump(operation, indent=4))

    return all_classes, all_connections

def analyze_code(code):
    def analyze_classes_and_methods(code):
        tree = ast.parse(code)
        results = {}
        all_variables = []

        def extract_attribute_chain(node):
            if isinstance(node, ast.Attribute):
                parent_chain = extract_attribute_chain(node.value)
                if parent_chain == 'self':
                    return node.attr
                return f"{parent_chain}.{node.attr}"
            elif isinstance(node, ast.Name):
                return node.id
            return None

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

                        # all_variables.append(variables)
                        variables = set(variables)
                        results[class_name][method_name] = {
                            "variables": list(variables),
                            "calls": list(set(calls)),
                        }

        return results, all_variables

    analysis_result, all_variables = analyze_classes_and_methods(code)
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

    # pprint(analysis_result)
    # pprint(method_var_to_class)
    #
    # print("all_variables", end=": ")
    # pprint(all_variables)

    variable_to_class = {}
    for variable in all_variables:
        if '.' in variable:
            v0, v1 = variable.split('.')
            if v1 + '()' in method_var_to_class:
                variable_to_class[v0] = method_var_to_class[v1 + '()'][0]
                # print(v0, method_var_to_class[v1 + '()'])
            elif v1 in method_var_to_class:
                variable_to_class[v0] = method_var_to_class[v1][0]
                # print(v0, method_var_to_class[v1])
        else:
            variable_to_class[variable] = method_var_to_class[variable][0]
    # print("variable_to_class", end=": ")
    # pprint(variable_to_class)

    all_connections = []
    all_classes = list(analysis_result.keys())

    for class_name in analysis_result.keys():
        for method_name in analysis_result[class_name]:
            for variable in analysis_result[class_name][method_name]['variables']:
                if '.' in variable:
                    v0, v1 = variable.split('.')
                    all_connections.append([class_name, method_name, variable_to_class[v0]])
    return all_classes, all_connections
    # pprint(all_connections)

all_diagram_classes, all_diagram_connections = analyze_diagram(diagram)
all_code_classes, all_code_connections = analyze_code(code)

print(all_diagram_classes)
print(all_diagram_connections)
print("============")
print(all_code_classes)
print(all_code_connections)