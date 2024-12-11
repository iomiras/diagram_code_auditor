from click import style
from diagrams import Diagram, Edge
from diagrams.aws.media import ElementalServer
from diagrams.aws.database import Database
from diagrams.aws.storage import S3
from networkx.algorithms.bipartite.basic import color

graph_attr = {
    "splines":"polyline",
    # "layout":"dot",
}

# Create the diagram
with Diagram("Intertwined Classes Diagram", show=False, graph_attr=graph_attr):
    class_a = ElementalServer("ClassA")
    class_b = Database("ClassB")
    class_c = S3("ClassC")

    # Define relationships
    class_a >> Edge(label="interact_with_b()") >> class_b
    class_b >> Edge(label="use_class_c()", color="red") >> class_c
    class_c >> Edge(label="interact_with_a()") >> class_a
    class_c >> Edge(label="interact_with_b()", color="darkgreen") >> class_b