import ast
from logging_utils import log_error
from pprint import pprint

class CodeVisitor(ast.NodeVisitor):
    """AST Visitor to parse code classes and methods, including inheritance resolution."""

    def __init__(self):
        self.classes = []
        self.current_class = None
        self.class_to_methods = {}
        self.class_to_parents = {}
        self.class_to_attributes = {}

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to extract class information."""
        self.current_class = node.name
        self.classes.append(node.name)
        self.class_to_methods[node.name] = []

        parents = self._extract_parents(node)
        self.class_to_parents[node.name] = parents
        self.generic_visit(node)
        self.current_class = None

    def _extract_parents(self, node: ast.ClassDef) -> list:
        """Extract parent class names from a class definition."""
        parents = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                parents.append(base.id)
            elif isinstance(base, ast.Attribute):
                parents.append(base.attr)
        return parents

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to extract method information."""
        if self.current_class and node.name != "__init__":
            self.class_to_methods[self.current_class].append(node.name + "()")
            # for expr in node.body:
            #     if isinstance(expr, ast.Expr):
            #         print(ast.dump(expr, indent=4))
            #         print("-----------------")
        else:
            for assign in node.body:
                if isinstance(assign, ast.Assign):
                    for target in assign.targets:
                        if isinstance(target, ast.Attribute):
                            if self.current_class in self.class_to_attributes:
                                self.class_to_attributes[self.current_class].append(target.attr)
                            else:
                                self.class_to_attributes[self.current_class] = [target.attr]
        self.generic_visit(node)

    def resolve_inheritance(self) -> None:
        """Resolve inherited methods for all classes."""
        resolved_methods = {}
        for class_name in self.classes:
            resolved_methods[class_name] = set(self.class_to_methods.get(class_name, []))

        for class_name, parents in self.class_to_parents.items():
            for parent in parents:
                if parent not in resolved_methods:
                    continue
                resolved_methods[class_name].update(resolved_methods[parent])

        for class_name in resolved_methods:
            self.class_to_methods[class_name] = list(resolved_methods[class_name])

    def get_results(self) -> tuple:
        """Get the analysis results after resolving inheritance."""
        self.resolve_inheritance()
        return self.classes, self.class_to_methods, self.class_to_attributes

def analyze_code(code_content: str) -> tuple:
    """
    Parse and analyze a code file's content.

    Args:
        code_content: Content of the code file

    Returns:
        tuple: (classes, methods)
    """
    try:
        tree = ast.parse(code_content)
    except SyntaxError as e:
        log_error(f"Error parsing code: {e}")
        return [], {}

    code_visitor = CodeVisitor()
    code_visitor.visit(tree)
    # print(code_visitor.get_results())
    return code_visitor.get_results()