from diagrams import Diagram, Edge
from diagrams.aws.media import ElementalServer
from diagrams.aws.database import Database
from diagrams.aws.storage import S3
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB
from diagrams.aws.analytics import Kinesis
from diagrams.aws.security import IAM

# Complex Example 4: Security and Access Control with Feedback Loops
graph_attr_4 = {"splines": "curved"}
# graph_attr_4 = {"splines": "polyline"}

with Diagram("Access Control and Feedback", show=False, graph_attr=graph_attr_4):
    auth_service = IAM("AuthService")
    app_server = ElementalServer("AppServer")
    db_cluster = Database("DBCluster")
    analytics_service = Kinesis("AnalyticsService")
    storage = S3("Storage")

    auth_service >> Edge(label="grants_access", color="blue") >> app_server
    app_server >> Edge(label="reads_from", color="green") >> db_cluster
    app_server >> Edge(label="stores_logs", color="brown") >> storage
    db_cluster >> Edge(label="sends_data", color="orange") >> analytics_service
    auth_service >> Edge(label="feedback_to", color="purple") >> analytics_service
    storage >> Edge(label="archived_by", style="dashed", color="red") >> analytics_service  # Feedback Loop
