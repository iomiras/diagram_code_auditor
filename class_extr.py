import ast
from pprint import pprint

with open("classes/classes.py", "r") as f:
    code = f.read()

class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []
        self.current_class = None
        self.class_to_methods = {}

    def visit_ClassDef(self, node):
        # print(f"Class: {node.name}")
        self.class_to_methods[node.name] = []
        self.current_class = node.name
        self.classes.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # print(f"Method: {node.name}")
        if node.name != "__init__":
            self.class_to_methods[self.current_class].append(node.name)
        self.generic_visit(node)

    def get_results(self):
        return self.classes, self.class_to_methods

def analyze_code(code):
    tree = ast.parse(code)
    code_visitor = CodeVisitor()
    code_visitor.visit(tree)

    classes, class_to_methods = code_visitor.get_results()
    return classes, class_to_methods


print("============")
all_code_classes, code_class_to_methods = analyze_code(code)
pprint("All Classes:")
pprint(all_code_classes)
print("========================================")
pprint("Class to Methods:")
pprint(code_class_to_methods)
print("========================================")