from diagrams import Diagram, Edge
from diagrams.aws.media import ElementalServer
from diagrams.aws.database import Database
from diagrams.aws.storage import S3
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB
from diagrams.aws.analytics import Kinesis

# Complex Example 2: Distributed System with Failover and Cross Communication
graph_attr_2 = {"splines": "ortho"}

with Diagram("Distributed System with Failover", show=False, graph_attr=graph_attr_2):
    primary_lb = ELB("PrimaryLB")
    failover_lb = ELB("FailoverLB")
    worker_a = EC2("WorkerA")
    worker_b = EC2("WorkerB")
    analytics = Kinesis("Analytics")
    database_primary = Database("PrimaryDB")
    database_backup = Database("BackupDB")

    primary_lb >> Edge(label="routes_to", color="blue") >> [worker_a, worker_b]
    failover_lb >> Edge(label="routes_to", style="dashed", color="red") >> [worker_a, worker_b]
    worker_a >> Edge(label="sends_to") >> analytics
    worker_b >> Edge(label="sends_to") >> analytics
    analytics >> Edge(label="stores_to", color="orange") >> database_primary
    database_primary >> Edge(label="replicates_to", color="green") >> database_backup
    database_backup << Edge(label="failover_sync", color="purple") << worker_a  # Cross Communication
