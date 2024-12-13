from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.onprem.client import User
from diagrams.onprem.database import PostgreSQL
from diagrams.generic.storage import Storage
from diagrams.aws.media import ElementalServer as Server
from diagrams.generic.network import Firewall
from diagrams.generic.device import Mobile, Tablet

graph_attr = {
    "splines":"polyline",
}

with Diagram("Complex Class Relationships", direction="LR", show=False, graph_attr=graph_attr):
    user = User("User")

    with Cluster("Frontend Cluster"):
        mobile = Mobile("MobileApp")
        desktop = Tablet("DesktopApp")

        # frontend_services = [mobile, desktop]

    with Cluster("Backend Cluster"):
        load_balancer = ELB("LoadBalancer")

        with Cluster("Compute Cluster"):
            service1 = EC2("Service1")
            service2 = EC2("Service2")
            service3 = EC2("Service3")

        load_balancer >> Edge(label="balance()") >> [service1, service2, service3]

    with Cluster("Database Cluster"):
        relational_db = RDS("RelationalDB")
        nosql_db = Storage("NoSQLDB")

    with Cluster("Security Layer"):
        firewall = Firewall("Firewall")
        auth_server = Server("AuthServer")

    user >> Edge(label="access_via()", color="blue") >> [mobile, desktop]
    [mobile, desktop] >> Edge(label="secured_by()", color="red") >> firewall >> Edge(label="routes_to()", color="green") >> load_balancer
    load_balancer >> Edge(label="authenticates_via()", color="purple") >> auth_server

    for service in [service1, service2, service3]:
        service1 >> Edge(label="store_data()", color="orange") >> [relational_db, nosql_db]

    auth_server >> Edge(label="queries()", color="brown") >> relational_db
    relational_db >> Edge(label="replicates_to()", color="darkgreen") >> nosql_db
