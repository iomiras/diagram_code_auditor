class Node:
    def __init__(self, value):
        self.value = value
        self.children = []  # List of child Node objects

    def add_child(self, child_node):
        if child_node not in self.children:
            self.children.append(child_node)

    def get_children(self):
        return [child.value for child in self.children]


class Graph:
    def __init__(self):
        self.nodes = []

    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def find_node(self, value):
        for node in self.nodes:
            if node.value == value:
                return node
        return None

    def display_graph(self):
        return {node.value: node.get_children() for node in self.nodes}

# [
#     ['Node', 'add_child()', 'Node'],
#     ['Node', 'get_children()', 'Node'],
#     ['Graph', 'add_node()', 'Node'],
#     ['Graph', 'find_node()', 'Node'],
#     ['Graph', 'display_graph()', 'Node']
# ]
