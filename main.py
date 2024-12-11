import ast

# The code snippet to analyze
with open("classes.py", "r") as f:
        code = f.read()

# Function to analyze classes and methods
def analyze_classes_and_methods(code):
    tree = ast.parse(code)
    results = {}

    def extract_attribute_chain(node):
        if isinstance(node, ast.Attribute):
            parent_chain = extract_attribute_chain(node.value)
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
                    method_name = item.name
                    variables = []
                    calls = []

                    for stmt in ast.walk(item):
                        if isinstance(stmt, ast.Attribute):
                            attr_chain = extract_attribute_chain(stmt)
                            if attr_chain:
                                variables.append(attr_chain)

                        if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Attribute):
                            func_chain = extract_attribute_chain(stmt.func)
                            if func_chain:
                                calls.append(func_chain)

                    results[class_name][method_name] = {
                        "variables": list(set(variables)),
                        "calls": list(set(calls)),
                    }

    return results


analysis_result = analyze_classes_and_methods(code)

import pprint
pprint.pprint(analysis_result)
