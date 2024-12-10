from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import APIGateway, ELB
from diagrams.programming.language import Javascript

with Diagram("Advanced System", direction="TB", show=False):
    backend = EC2("Backend")
    database = RDS("Database")
    api_gateway = APIGateway("Service")
    frontend = Javascript("Frontend")
    load_balancer = ELB("LoadBalancer")

    # Connections with different directions and chained logic
    backend << database
    frontend >> api_gateway >> backend
    frontend << api_gateway >> database
    load_balancer >> api_gateway
    database >> load_balancer