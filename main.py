import re


def extract_classes_and_methods_from_code(code):
    instantiations = set(re.findall(r'class+\s+(\w+)', code))

    connections = re.findall(r'class+\s+(\w+)\((\w+)', code)
    for i in range(len(connections)):
        connection = connections[i]
        new_connection = (connection[1], connection[0])
        connections.remove(connection)
        connections.insert(i, new_connection)
    return instantiations, connections


def extract_diagrams_nodes_and_connections(diagram_code):
    nodes_dict = {}
    nodes = set()
    connections = []

    # Extract nodes from the diagram code
    instantiations = re.findall(r'(\w+)\s*=\s*(\w+)\("(\w+)', diagram_code)
    for var, cls, name in instantiations:
        nodes_dict[var] = name
        nodes.add(name)

    # Extract individual and chained connections
    direct_connections = re.findall(r'(\w+)\s*>>\s*(\w+)', diagram_code)
    reverse_connections = re.findall(r'(\w+)\s*<<\s*(\w+)', diagram_code)
    chained_connections = re.findall(r'(\w+(?:\s*>>\s*\w+)+)', diagram_code)
    reverse_chained_connections = re.findall(r'(\w+(?:\s*<<\s*\w+)+)', diagram_code)

    # Expand chained connections into individual pairs
    for chain in chained_connections:
        chain_nodes = re.split(r'\s*>>\s*', chain)
        for i in range(len(chain_nodes) - 1):
            connections.append((chain_nodes[i], chain_nodes[i + 1]))

    for chain in reverse_chained_connections:
        chain_nodes = re.split(r'\s*>>\s*', chain)
        for i in range(len(chain_nodes) - 1):
            connections.append((chain_nodes[i + 1], chain_nodes[i]))

    # Add direct connections
    connections += direct_connections

    # Add reverse connections (flip direction)
    connections += [(conn[1], conn[0]) for conn in reverse_connections]

    # Map variable names to node names using `nodes_dict`
    resolved_connections = []
    for conn in connections:
        if conn[0] in nodes_dict and conn[1] in nodes_dict:
            resolved_connections.append((nodes_dict[conn[0]], nodes_dict[conn[1]]))

    return nodes, resolved_connections



def compare_classes(existing_classes, diagram_nodes):
    if len(existing_classes - diagram_nodes) == 0:
        print("All classes are present in the diagram")
    else:
    # elif len(existing_classes - diagram_nodes) > 0:
        print("Classes in the code, but not in the diagram: ", existing_classes - diagram_nodes)
    # elif len(diagram_nodes - existing_classes) > 0:
        print("Classes in the diagram, but not in the code: ", diagram_nodes - existing_classes)

def compare_connections(code_connections, diagram_connections):
    if not set(code_connections) - set(diagram_connections):
        print("All connections are present in the diagram")
    else:
    # elif len(set(code_connections) - set(diagram_connections)) > 0:
        print("Connections in the code, but not in the diagram: ", set(code_connections) - set(diagram_connections))
    # elif len(set(diagram_connections) - set(code_connections)) > 0:
        print("Connections in the diagram, but not in the code: ", set(diagram_connections) - set(code_connections))

# Example Usage
if __name__ == "__main__":
    with open("uml.py", "r") as f:
        diagram_code = f.read()

    with open("classes.py", "r") as f:
        existing_code = f.read()

    code_classes, code_connections = extract_classes_and_methods_from_code(existing_code)
    diagram_nodes, diagram_connections = extract_diagrams_nodes_and_connections(diagram_code)

    compare_classes(code_classes, diagram_nodes)
    compare_connections(code_connections, diagram_connections)
