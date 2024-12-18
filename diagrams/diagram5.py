# diagram5.py
from diagrams import Diagram, Cluster, Edge
from diagrams.generic.compute import Rack

with Diagram("Diagram 5", direction="TB", show=False):
    load_balancer = Rack("LoadBalancer")
    load_balancer >> Edge(label="check_health()") >> load_balancer
