# diagram1.py
from diagrams import Diagram, Cluster, Edge
from diagrams.generic.compute import Rack

graph_attr = {
    "splines": "polyline",
}

with Diagram("Diagram 1", direction="TB", show=False, graph_attr=graph_attr):
    load_balancer = Rack("LoadBalancer")
    load_balancer >> Edge(label="check_health()") >> load_balancer