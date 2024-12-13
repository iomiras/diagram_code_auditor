import ast
from pprint import pprint

with open("classes/classes2.py", "r") as f:
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

def extract_attribute_chain(node):
    if isinstance(node, ast.Attribute):
        parent_chain = extract_attribute_chain(node.value)
        if parent_chain == 'self':
            return node.attr
        return f"{parent_chain}.{node.attr}"
    elif isinstance(node, ast.Name):
        return node.id
    return None

# def analyze_code(code):
#     tree = ast.parse(code)
#     results = {}
#     all_variables = []
#
#     for node in tree.body:
#         if isinstance(node, ast.ClassDef):
#             class_name = node.name
#             results[class_name] = {}
#
#             for item in node.body:
#                 if isinstance(item, ast.FunctionDef):
#                     method_name = item.name + '()'
#                     variables = []
#                     calls = []
#
#                     for stmt in ast.walk(item):
#                         if isinstance(stmt, ast.Attribute):
#                             attr_chain = extract_attribute_chain(stmt)
#                             if attr_chain:
#                                 variables.append(attr_chain)
#                                 if attr_chain not in all_variables:
#                                     all_variables.append(attr_chain)
#
#                         if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute):
#                             func_chain = extract_attribute_chain(stmt.func)
#                             if func_chain:
#                                 calls.append(func_chain)
#
#                     variables = set(variables)
#                     results[class_name][method_name] = {
#                         "variables": list(variables),
#                         "calls": list(set(calls)),
#                     }
#
#     analysis_result = results
#     method_var_to_class = {}
#
#     for class_name in analysis_result.keys():
#         for method_name in analysis_result[class_name]:
#             if method_name == '__init__()':
#                 if analysis_result[class_name][method_name]:
#                     for variable in analysis_result[class_name][method_name]['variables']:
#                         if variable in method_var_to_class:
#                             method_var_to_class[variable].append(class_name)
#                         else:
#                             method_var_to_class[variable] = [class_name]
#             else:
#                 if method_name in method_var_to_class:
#                     method_var_to_class[method_name].append(class_name)
#                 else:
#                     method_var_to_class[method_name] = [class_name]
#
#     variable_to_class = {}
#     for variable in all_variables:
#         if '.' in variable:
#             v0, v1 = variable.split('.')
#             if v1 + '()' in method_var_to_class:
#                 variable_to_class[v0] = method_var_to_class[v1 + '()'][0]
#             elif v1 in method_var_to_class:
#                 variable_to_class[v0] = method_var_to_class[v1][0]
#         else:
#             variable_to_class[variable] = method_var_to_class[variable][0]
#
#     all_connections = []
#     all_classes = list(analysis_result.keys())
#
#     for class_name in analysis_result.keys():
#         for method_name in analysis_result[class_name]:
#             for variable in analysis_result[class_name][method_name]['variables']:
#                 if '.' in variable:
#                     v0, v1 = variable.split('.')
#                     all_connections.append([class_name, method_name, variable_to_class[v0]])
#     return all_classes, all_connections

def analyze_code(code):
    tree = ast.parse(code)
    results = {}
    all_variables = []
    method_var_to_class = {}
    variable_context = {}
    debug_info = []  # Add debug information

    def extract_attribute_chain(node):
        if isinstance(node, ast.Attribute):
            parent_chain = extract_attribute_chain(node.value)
            if parent_chain == 'self':
                return node.attr
            return f"{parent_chain}.{node.attr}" if parent_chain else node.attr
        elif isinstance(node, ast.Name):
            return node.id
        return None

    # First pass: Collect class and method information
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            results[class_name] = {}

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name + '()'
                    variables = []
                    calls = []
                    method_ast = item

                    # Print AST for debugging
                    debug_info.append(f"Analyzing method {class_name}.{method_name}")
                    debug_info.append(ast.dump(method_ast, indent=2))

                    for stmt in ast.walk(method_ast):
                        # Detect method calls
                        if isinstance(stmt, ast.Call):
                            # Detailed method call tracking
                            if isinstance(stmt.func, ast.Attribute):
                                func_chain = extract_attribute_chain(stmt.func)
                                debug_info.append(f"Method call detected: {func_chain}")
                                if func_chain:
                                    calls.append(func_chain)
                            elif isinstance(stmt.func, ast.Name):
                                func_name = stmt.func.id
                                debug_info.append(f"Function call detected: {func_name}")
                                calls.append(func_name)

                        # Detect attribute references
                        if isinstance(stmt, ast.Attribute):
                            attr_chain = extract_attribute_chain(stmt)
                            debug_info.append(f"Attribute detected: {attr_chain}")

                            if attr_chain and '.' in attr_chain:
                                variables.append(attr_chain)
                                if attr_chain not in all_variables:
                                    all_variables.append(attr_chain)

                    # Store method information
                    results[class_name][method_name] = {
                        "variables": list(set(variables)),
                        "calls": list(set(calls)),
                    }

    # Connections detection
    all_connections = []
    all_classes = list(results.keys())

    # Cross-class interaction detection
    for class_name, class_methods in results.items():
        for method_name, method_details in class_methods.items():
            debug_info.append(f"Analyzing connections for {class_name}.{method_name}")

            # Check method calls
            for call in method_details['calls']:
                debug_info.append(f"Checking call: {call}")
                # Look for method calls that might indicate cross-class interaction
                for other_class in all_classes:
                    if other_class != class_name:
                        # Check if the call matches any method in the other class
                        for other_method in results[other_class].keys():
                            if call in other_method or call in results[other_class][other_method]['calls']:
                                debug_info.append(f"Connection found: {class_name} -> {other_class} via {call}")
                                all_connections.append([class_name, method_name, other_class])

            # Check variables (might indicate object references)
            for var in method_details['variables']:
                debug_info.append(f"Checking variable: {var}")
                for other_class in all_classes:
                    if other_class != class_name:
                        # Check if variable name matches other class methods or attributes
                        for other_method, other_method_details in results[other_class].items():
                            if var in other_method or any(var in v for v in other_method_details['variables']):
                                debug_info.append(f"Cross-class variable reference: {class_name} -> {other_class}")
                                all_connections.append([class_name, method_name, other_class])

    # Print debug information
    print("\n".join(debug_info))

    return all_classes, all_connections


all_diagram_classes, all_diagram_connections = analyze_diagram(diagram)
all_code_classes, all_code_connections = analyze_code(code)

print(all_diagram_classes)
pprint(all_diagram_connections)
print("============")
print(all_code_classes)
pprint(all_code_connections)