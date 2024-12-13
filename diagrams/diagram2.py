from diagrams import Diagram, Edge
from diagrams.aws.media import ElementalServer
from diagrams.aws.database import Database
from diagrams.aws.storage import S3
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB
from diagrams.aws.analytics import Kinesis

graph_attr_1 = {"splines": "spline"}

with Diagram("Complex Multi-layered Cycles", show=False, graph_attr=graph_attr_1):
    class_a = ElementalServer("ClassA")
    class_b = Database("ClassB")
    class_c = S3("ClassC")
    class_d = EC2("ClassD")
    class_e = ELB("ClassE")

    class_a >> Edge(label="writes_to", color="blue") >> class_b
    class_b >> Edge(label="reads_from", color="green") >> class_c
    class_c >> Edge(label="triggers", color="orange") >> class_a  # Cycle
    class_d >> Edge(label="monitors", color="purple") >> class_a
    class_d >> Edge(label="fetches_data", color="red") >> class_c
    class_e >> Edge(label="balances", color="darkgreen") >> [class_a, class_d]
    class_a << Edge(label="receives_logs", color="brown") << class_c  # Cross Link