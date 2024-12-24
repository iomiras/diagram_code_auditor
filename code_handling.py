import ast
import sys
from pprint import pprint
import json
import subprocess
import shutil

class CodeVisitor(ast.NodeVisitor):
    """
    Visitor to parse code classes and methods, including resolving inheritance.
    """
    def __init__(self):
        self.classes = []  # All class names
        self.current_class = None  # Currently visited class
        self.class_to_methods = {}  # Map of class names to methods
        self.class_to_parents = {}  # Map of class names to their parent classes

    def visit_ClassDef(self, node):
        # Initialize the current class
        self.current_class = node.name
        self.classes.append(node.name)
        self.class_to_methods[node.name] = []

        # Track base classes (parents)
        parents = self._extract_parents(node)
        self.class_to_parents[node.name] = parents

        # Visit class body to find methods
        self.generic_visit(node)
        self.current_class = None

    def _extract_parents(self, node):
        parents = []
        for base in node.bases:
            if isinstance(base, ast.Name):  # Simple parent class
                parents.append(base.id)
            elif isinstance(base, ast.Attribute):  # Parent with module path
                parents.append(base.attr)
        return parents

    def visit_FunctionDef(self, node):
        # Skip __init__
        if self.current_class and node.name != "__init__":
            self.class_to_methods[self.current_class].append(node.name + "()")
        self.generic_visit(node)

    def resolve_inheritance(self):
        resolved_methods = {}
        for class_name in self.classes:
            resolved_methods[class_name] = set(self.class_to_methods.get(class_name, []))

        # Propagate parent methods
        for class_name, parents in self.class_to_parents.items():
            for parent in parents:
                if parent not in resolved_methods:
                    # if Parent not found in local classes just skip
                    continue
                resolved_methods[class_name].update(resolved_methods[parent])

        # Convert methods back to lists
        for class_name in resolved_methods:
            self.class_to_methods[class_name] = list(resolved_methods[class_name])

    def get_results(self):
        self.resolve_inheritance()
        return self.classes, self.class_to_methods