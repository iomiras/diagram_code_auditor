# diagram2.py
from diagrams import Diagram, Cluster, Edge
from diagrams.generic.compute import Rack

with Diagram("Diagram 2", direction="TB", show=False):
    load_balancer = Rack("LoadBalancer")
    missing_class = Rack("MissingClass")  # Missing in code
    load_balancer >> Edge(label="check_health()") >> missing_class
