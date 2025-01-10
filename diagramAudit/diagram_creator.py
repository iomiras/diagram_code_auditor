import sys
import subprocess
from diagram_code_auditor import parse_code_file
from utils.php_code_parser import extract_connections
from utils.connection_parser import extract_connection_triples

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
    file_path = '.'.join(file_path.split('.')[:-1]) + '.py'
    graph_attr = {"splines": "polyline"}

    with open(file_path, 'w') as f:
        # Start the diagram
        f.write("from diagrams import Diagram, Edge\n")
        f.write("from diagrams.c4 import Container\n")

        f.write(f"graph_attr = {graph_attr}\n\n")
        f.write(f"with Diagram(\"{' '.join(diagram_name.split('/')[-1].split('_'))}\", filename= \"./{file_path.split('.')[0]}\", direction=\"LR\", show=False, graph_attr=graph_attr):\n")

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
                edge_attr = "style='dotted', color='black'"
            else:
                edge_attr = "style='solid', color='red'"
            if method == "inherits":
                edge_attr = "style='dashed', color='darkgreen'"

            if len(to_classes) > 1:
                to_vars = [f"{cls.lower()}" for cls in to_classes]
                to_vars = ", ".join(to_vars)
                f.write(f"    {from_cls.lower()} >> Edge(label=\"{method}\", {edge_attr}) >> [{to_vars}]\n")
            else:
                to_var = f"{to_classes[0].lower()}"
                f.write(f"    {from_cls.lower()} >> Edge(label=\"{method}\", {edge_attr}) >> {to_var}\n")

        # Handle self-referencing methods
        for cls, methods in class_to_methods.items():
            for method in methods:
                if (cls, method) not in connected_methods:
                    f.write(f"    {cls.lower()} >> Edge(label=\"{method}\", style='dashed', color='blue') >> {cls.lower()}\n")
    f.close()
    subprocess.run(['python3', file_path])

def extract_connection(file_path, classes, class_to_methods, class_to_attributes):
    """
    Extract connections from a code file.

    Args:
        file_path (str): The path of the code file.
        classes (list): List of class names.
        class_to_methods (dict): Methods for each class.
        class_to_attributes (dict): Attributes for each class.

    Returns:
        connections (list): A list of connections between classes.
    """
    connections = []
    if file_path.endswith('.py'):
        with open(file_path, 'r') as f:
            content = f.read()
        connections = extract_connection_triples(content, classes, class_to_methods, class_to_attributes)
    elif file_path.endswith('.php'):
        connections = extract_connections(file_path)
    return connections

def main():
    file_path = sys.argv[1]
    folder = ''
    diagram_path = folder + 'diagram_for_' + file_path.split('/')[-1]

    classes, class_to_methods, class_to_attributes = parse_code_file(file_path)

    connections = extract_connection(file_path, classes, class_to_methods, class_to_attributes)

    write_diagram(diagram_path, file_path, classes, class_to_methods, connections)

if __name__ == "__main__":
    main()