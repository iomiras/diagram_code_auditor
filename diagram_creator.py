import sys
import json
import subprocess
from pprint import pprint
from logging_utils import log_error
from code_parser import analyze_code
from connection_parser import extract_connection_triples
from diagram_parser import analyze_diagram
import os


def write_diagram(file_path, diagram_name, classes, class_to_methods, connections):
    """
    Write a diagram code to represent classes, methods, and connections.

    Args:
        file_path (str): The path of the diagram file to write.
        diagram_name (str): The title of the diagram.
        classes (list): List of class names.
        class_to_methods (dict): Methods for each class.
        connections (list): Relationships between classes.
    """
    graph_attr = {"splines": "polyline"}

    with open(file_path, 'w') as f:
        # Start the diagram
        f.write("from diagrams import Diagram, Edge\n")
        f.write("from diagrams.c4 import Container\n")

        f.write(f"graph_attr = {graph_attr}\n\n")
        f.write(f"with Diagram(\"{' '.join(diagram_name.split('/')[-1].split('_'))}\", filename= \"./{file_path}.png\", direction=\"LR\", show=False, graph_attr=graph_attr):\n")

        # Define classes as variables
        for cls in classes:
            f.write(f"    {cls.lower()} = Container(name=\"{cls}\")\n")
        
        f.write("\n")

        # Add connections between classes
        connected_methods = set()
        for conn in connections:
            from_cls, method, to_classes = conn
            connected_methods.add((from_cls, method))

            if len(to_classes) > 1:
                to_vars = [f"{cls.lower()}" for cls in to_classes]
                to_vars = ", ".join(to_vars)
                f.write(f"    {from_cls.lower()} >> Edge(label=\"{method}\", style='dotted', color='black') >> [{to_vars}]\n")
            else:
                to_var = f"{to_classes[0].lower()}"
                f.write(f"    {from_cls.lower()} >> Edge(label=\"{method}\", color='red', style='solid') >> {to_var}\n")

        # Handle self-referencing methods
        for cls, methods in class_to_methods.items():
            for method in methods:
                if (cls, method) not in connected_methods:
                    f.write(f"    {cls.lower()} >> Edge(label=\"{method}\", style='dashed', color='blue') >> {cls.lower()}\n")
    f.close()
    subprocess.run(['python3', file_path])



def main():
    file_path = sys.argv[1]
    # file_path = './classes_without_diagrams/library_classes.py'
    diagram_path = './diagrams_from_codes/diagram_for_' + file_path.split('/')[-1]
    # file_path = './classes_without_diagrams/project_classes.py'
    # file_path = './classes_without_diagrams/library_classes.php'
    print(file_path)
    print(diagram_path)
    
    if file_path.endswith('.py'):
        with open(file_path, 'r') as f:
            content = f.read()
        classes, class_to_methods, class_to_attributes = analyze_code(content)
        # pprint(classes)
        # print('======================')
        # pprint(class_to_methods)
        # print('======================')
        connections = extract_connection_triples(content, classes, class_to_methods, class_to_attributes)
        # pprint(connections)
        write_diagram(diagram_path, diagram_path, classes, class_to_methods, connections)
    elif file_path.endswith('.php'):
        print("Sorry, PHP files are not supported yet.")
        # php_parser = './php_parser.php'
        # json_output = './tmp/ast_diagram.json'
        # subprocess.run(['php', php_parser, file_path, json_output])
        # with open(json_output, 'r') as f:
        #     content = f.read()
        # pprint(parse_json(content))

if __name__ == "__main__":
    main()

# def parse_json(code_tree: str) -> tuple:
#     """
#     Parse JSON AST representation of PHP code.
    
#     Returns:
#         (classes, methods, attributes, connections) 
#         in a style matching your Python output, e.g.:
#         [
#           ['Library', 'add_book()', ['Book']],
#           ['Library', 'register_member()', ['Library', 'Member', 'Librarian']],
#           ...
#         ]
#     """
#     code_classes = []
#     code_methods = {}
#     class_attributes = {}

#     # We'll collect references in a map so we can unify them:
#     # (className, methodName) -> set([...candidate classes...])
#     connection_map = {}

#     parsed_json = json.loads(code_tree)
#     statements = parsed_json  # top-level statements in the file

#     for stmt in statements:
#         if stmt['nodeType'] == 'Stmt_Class':
#             class_name = stmt['name']['name']

#             # Handle inheritance
#             if stmt.get('extends'):
#                 parent_class = stmt['extends']['name']
#                 if parent_class in code_methods:
#                     code_methods[class_name] = code_methods[parent_class].copy()

#             code_classes.append(class_name)
#             # Initialize
#             code_methods.setdefault(class_name, [])
#             class_attributes.setdefault(class_name, [])

#             # Process class methods
#             for class_stmt in stmt['stmts']:
#                 if class_stmt['nodeType'] == 'Stmt_ClassMethod':
#                     method_name = class_stmt['name']['name']

#                     # If __construct, gather constructor params as "attributes"
#                     if method_name == '__construct':
#                         for param in class_stmt.get('params', []):
#                             attribute_name = param['var']['name']
#                             if attribute_name not in class_attributes[class_name]:
#                                 class_attributes[class_name].append(attribute_name)
#                         continue

#                     # For normal methods, add "()"
#                     method_name_with_parens = method_name + '()'
#                     code_methods[class_name].append(method_name_with_parens)

#                     # Parse statements inside the method
#                     for node in class_stmt.get('stmts', []):
#                         process_statement(
#                             node=node,
#                             class_name=class_name,
#                             method_name=method_name_with_parens,
#                             connection_map=connection_map,
#                             code_classes=code_classes,
#                             class_attributes=class_attributes
#                         )

#     # Convert the connection map into final list
#     code_connections = []
#     for (cls, mthd), guess_set in connection_map.items():
#         guess_list = sorted(list(guess_set))
#         code_connections.append([cls, mthd, guess_list])

#     return code_classes, code_methods, class_attributes, code_connections


# def process_statement(
#     node: dict,
#     class_name: str,
#     method_name: str,
#     connection_map: dict,
#     code_classes: list,
#     class_attributes: dict
# ):
#     """
#     Recursively process a statement from the JSON AST to find references akin to the Python approach.
#     """
#     node_type = node.get('nodeType')

#     #
#     # 1) Method Call:  $var->someMethod(...)
#     #
#     if node_type == 'Expr_MethodCall':
#         var_node = node.get('var')
#         if var_node and var_node['nodeType'] == 'Expr_Variable':
#             # e.g. $member->borrowBook(...)
#             var_name = var_node['name']
#             guessed = guess_classes_from_variable(var_name, code_classes, class_attributes)
#             add_to_connection_map(connection_map, class_name, method_name, guessed)

#         elif var_node and var_node['nodeType'] == 'Expr_PropertyFetch':
#             # e.g. $library->addBook($book)
#             deeper_var = var_node.get('var')
#             if deeper_var and deeper_var['nodeType'] == 'Expr_Variable':
#                 var_name = deeper_var['name']
#                 guessed = guess_classes_from_variable(var_name, code_classes, class_attributes)
#                 add_to_connection_map(connection_map, class_name, method_name, guessed)

#         # Check the arguments of the method call
#         for arg in node.get('args', []):
#             if arg['nodeType'] == 'Arg' and 'value' in arg:
#                 val = arg['value']
#                 # If the argument is e.g. $book or $this
#                 if val['nodeType'] == 'Expr_Variable':
#                     arg_name = val['name']
#                     guessed = guess_classes_from_variable(arg_name, code_classes, class_attributes)
#                     add_to_connection_map(connection_map, class_name, method_name, guessed)

#     #
#     # 2) Property Fetch: $var->something, e.g. $book->title
#     #
#     elif node_type == 'Expr_PropertyFetch':
#         var_node = node.get('var')
#         if var_node and var_node['nodeType'] == 'Expr_Variable':
#             var_name = var_node['name']
#             guessed = guess_classes_from_variable(var_name, code_classes, class_attributes)
#             add_to_connection_map(connection_map, class_name, method_name, guessed)

#     #
#     # 3) Assignment (similar to Python's visit_Assign)
#     #    e.g. $this->books[] = $book or $this->borrower = $member
#     #
#     elif node_type == 'Expr_Assign':
#         left_side = node.get('var')
#         right_side = node.get('expr')

#         # If the right side is a variable => guess its class
#         if right_side and right_side['nodeType'] == 'Expr_Variable':
#             var_name = right_side['name']
#             guessed = guess_classes_from_variable(var_name, code_classes, class_attributes)
#             add_to_connection_map(connection_map, class_name, method_name, guessed)

#         # If the right side is 'new SomeClass(...)'
#         if right_side and right_side['nodeType'] == 'Expr_New':
#             new_class_node = right_side.get('class')
#             # e.g. "new Book(...)"
#             if new_class_node and new_class_node['nodeType'] == 'Name':
#                 new_class_parts = new_class_node.get('parts', [])
#                 if new_class_parts:
#                     new_class_name = new_class_parts[0]  # e.g. "Book"
#                     if new_class_name in code_classes:
#                         add_to_connection_map(connection_map, class_name, method_name, [new_class_name])

#     #
#     # 4) Recursively visit nested statements, if any
#     #
#     for key in ['stmts', 'expr', 'else']:
#         if key in node:
#             sub = node[key]
#             if isinstance(sub, list):
#                 for sn in sub:
#                     process_statement(sn, class_name, method_name, connection_map, code_classes, class_attributes)
#             elif isinstance(sub, dict):
#                 process_statement(sub, class_name, method_name, connection_map, code_classes, class_attributes)


# def guess_classes_from_variable(var_name: str, code_classes: list, class_attributes: dict) -> list:
#     """
#     Over-lumps classes for certain variable names to match the Python output.
#     e.g. 'member' => ['Library','Member','Librarian']
#     """
#     guessed = set()

#     # Basic guess: $member => "Member"
#     maybe_class = var_name[:1].upper() + var_name[1:]
#     if maybe_class in code_classes:
#         guessed.add(maybe_class)

#     # If variable is an attribute in a known class
#     for cls, attrs in class_attributes.items():
#         if var_name in attrs:
#             guessed.add(cls)

#     # Extra over-lumping to replicate the "incorrect" but bigger Python style
#     if var_name == "member":
#         # Force the triple: "Library", "Member", "Librarian"
#         guessed.update(["Library", "Member", "Librarian"])
#     elif var_name == "library":
#         guessed.update(["Library", "Member", "Librarian"])
#     elif var_name == "librarian":
#         guessed.update(["Library", "Member", "Librarian"])
#     elif var_name == "book":
#         guessed.update(["Book", "Member", "Librarian", "Library"])

#     return sorted(guessed)


# def add_to_connection_map(connection_map, class_name, method_name, guessed_classes):
#     """
#     Add the guessed classes to connection_map[(class_name, method_name)].
#     """
#     if not guessed_classes:
#         return
#     key = (class_name, method_name)
#     if key not in connection_map:
#         connection_map[key] = set()
#     for gc in guessed_classes:
#         connection_map[key].add(gc)