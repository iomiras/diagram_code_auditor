import ast
from logging_utils import log_error
from pprint import pprint


############################################################
# NEW FUNCTIONALITY: EXTRACTING CONNECTION TRIPLES (with attributes)
############################################################

class ConnectionFinder(ast.NodeVisitor):
    """
    A second-pass visitor that scans for:
      1) Method calls (e.g. `book.borrow(self)`)
      2) Assignments (`self.borrower = member`)
      3) Attribute usage (`book.title`)
    And infers connections like ["Member", "borrow_book()", "Book"].
    """

    def __init__(self, known_classes, class_to_methods=None, class_to_attrs=None):
        """
        :param known_classes: List of known class names (e.g. from CodeVisitor).
        :param class_to_methods: dict { "Book": ["borrow()", "return_book()", ...], ... }
        :param class_to_attrs:   dict { "Book": ["title", "author", ...], "Member": ["name", ...], ... }
        """
        super().__init__()
        self.known_classes = set(known_classes)

        self.class_to_methods = class_to_methods if class_to_methods else {}
        self.class_to_attrs = class_to_attrs if class_to_attrs else {}

        # pprint(known_classes)
        # pprint(class_to_methods)
        # pprint(class_to_attrs)
        # print('************')

        self.connections = []

        self.current_class = None
        self.current_method = None

        # Keep a map from variableName -> guessedClass
        # e.g., "book" -> "Book"
        self.variable_to_class_guess = {}

    def visit_ClassDef(self, node: ast.ClassDef):
        """
        Save the class name context (e.g. 'Library'), then visit methods.
        """
        self.current_class = node.name
        if len(node.bases) > 0:
            for base in node.bases:
                if isinstance(base, ast.Name):
                    self.known_classes.add(base.id)
                    self.current_method = 'inherits'
                    self._add_to_connections([base.id])
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Save the method name context (unless it's __init__) and gather param-based guesses.
        """

        self.current_method = node.name

        # Traverse function body
        self.generic_visit(node)

        self.current_method = None

    def visit_Call(self, node: ast.Call):
        """
        Detect calls: e.g. `book.borrow(self)`
        We'll see if the callee is `someVar.someMethod`.
        """
        if self.current_class and self.current_method:
            # print("Current Class:", self.current_class)
            # print("Current Method:", self.current_method)
            # print(ast.dump(node, indent=4))
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                var_name = node.func.value.id       # e.g. 'book'
                method_attr = node.func.attr        # e.g. 'borrow'
                self._refine_guess_from_method(var_name, method_attr)
            elif isinstance(node.func, ast.Call):
                self._add_to_connections([self.current_class])

        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        """
        Detect assignments like: 
            self.xyz = someVar
            or varName.attribute = something
        We'll do simple inference if possible.
        """
        if self.current_class and self.current_method:
            if isinstance(node.value, ast.Call):
                if isinstance(node.value.func, ast.Name):
                    if node.value.func.id in self.known_classes:
                        self._add_to_connections([node.value.func.id])

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        """
        Detect usage of `varName.attribute`, e.g. `book.title`.
        Then see if `attribute` belongs to exactly one known class -> guess `book` is that class.
        """
        if isinstance(node.value, ast.Name) and self.current_class and self.current_method:
            var_name = node.value.id
            if var_name == 'self':
                self.generic_visit(node)
                return
            attr = node.attr


            
            self._refine_guess_from_attribute(var_name, attr)

        self.generic_visit(node)

    ###########################################################
    # HELPER METHODS
    ###########################################################

    def _refine_guess_from_method(self, var_name: str, method_attr: str):
        """
        e.g., method_attr='borrow' => we look for 'borrow()' in class_to_methods 
        and see if exactly one class has it.
        If found, that's our guess. Otherwise, fall back to name-based guess.
        """
        method_str = method_attr + "()"
        candidate_classes = []
        for cls in self.class_to_methods.keys():
            method_list = self.class_to_methods[cls]
            if method_str in method_list:
                # print(cls)
                # print("Class", cls)
                # print("Method str:", method_str, "Method List:", method_list)
                candidate_classes.append(cls)
                # pprint(candidate_classes)
                # print('------')        
        
        # print("Candidate Classes:", candidate_classes)
        self._add_to_connections(candidate_classes)

    def _refine_guess_from_attribute(self, var_name: str, attribute_name: str):
        """
        e.g., if attribute_name='title', we see which classes define 'title' in class_to_attrs.
        If exactly one class has that attribute, guess var_name is that class.
        Otherwise, fall back to name-based guess or any existing guess.
        """

        candidate_classes = []
        for cls, attr_list in self.class_to_attrs.items():
            if attribute_name in attr_list:
                # print(var_name, "is an object of class", cls)
                # print("Class1:", self.current_class, "Method:", self.current_method, "Class2:", cls)
                # print('------')
                candidate_classes.append(cls)

        self._add_to_connections(candidate_classes)
    
    def _add_to_connections(self, candidate_classes):
        if len(candidate_classes) != 0 and [self.current_class, f"{self.current_method}()", candidate_classes] not in self.connections:
            return self.connections.append([
                self.current_class,
                self.current_method + '()' if self.current_method != 'inherits' else self.current_method,
                candidate_classes
            ])

def extract_connection_triples(code_content: str, classes: list, class_to_methods=None, class_to_attrs=None):
    """
    1. Parse the code into an AST.
    2. Run a ConnectionFinder pass to discover relationships like:
       ['Book', 'borrow()', 'Member'], etc.
    3. Return the list of discovered connections.
    """
    try:
        tree = ast.parse(code_content)
    except SyntaxError as e:
        log_error(f"Error parsing code for connection extraction: {e}")
        return []

    finder = ConnectionFinder(classes, class_to_methods, class_to_attrs)
    finder.visit(tree)
    # connections = list(set(finder.connections))
    print(finder.connections)
    return finder.connections