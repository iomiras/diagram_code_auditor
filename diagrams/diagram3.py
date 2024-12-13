from diagrams import Diagram, Edge
from diagrams.aws.media import ElementalServer
from diagrams.aws.database import Database
from diagrams.aws.storage import S3
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB
from diagrams.aws.analytics import Kinesis

graph_attr_2 = {"splines": "ortho"}

with Diagram("Distributed System Architecture", show=False, graph_attr=graph_attr_2):
    load_balancer = ELB("LoadBalancer")
    worker_1 = EC2("Worker1")
    worker_2 = EC2("Worker2")
    analytics = Kinesis("Analytics")
    database = Database("Database")

    # Flow in a distributed system
    load_balancer >> Edge(label="distributes_to", color="purple") >> [worker_1, worker_2]
    [worker_1, worker_2] >> Edge(label="sends_to") >> analytics
    analytics >> Edge(label="stores_results", color="orange") >> database