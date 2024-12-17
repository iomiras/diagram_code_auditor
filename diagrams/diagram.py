from diagrams import Diagram, Cluster, Edge
from diagrams.generic.network import Firewall
from diagrams.generic.device import Mobile, Tablet
from diagrams.onprem.client import User
from diagrams.generic.compute import Rack
from diagrams.generic.database import SQL
from diagrams.generic.storage import Storage
from diagrams.onprem.compute import Server

graph_attr = {
    "splines": "polyline",
}

with Diagram("Class Relationships and Methods", direction="LR", show=False, graph_attr=graph_attr):
    # User class
    user = User("User")

    # Frontend Cluster: Classes representing frontend interfaces
    with Cluster("Frontend Classes"):
        mobile_app = Mobile("MobileApp")
        desktop_app = Tablet("DesktopApp")

    # Backend Cluster: Core processing classes
    with Cluster("Backend Classes"):
        load_balancer = Rack("LoadBalancer")

        with Cluster("Service Classes"):
            service1 = Server("Service1")
            service2 = Server("Service2")
            service3 = Server("Service3")

        load_balancer >> Edge(label="balance()") >> [service1, service2, service3]

    # Database Classes
    with Cluster("Database Classes"):
        relational_db = SQL("RelationalDB")
        nosql_db = Storage("NoSQLDB")

    # Security Layer: Security-related classes
    with Cluster("Security Classes"):
        firewall = Firewall("Firewall")
        auth_server = Server("AuthServer")

    # Class Relationships and Methods
    user >> Edge(label="access_via()", color="blue") >> [mobile_app, desktop_app]
    [mobile_app, desktop_app] >> Edge(label="secured_by()", color="red") >> firewall
    firewall >> Edge(label="routes_to()", color="green") >> load_balancer
    load_balancer >> Edge(label="authenticates_via()", color="purple") >> auth_server

    for service in [service1, service2, service3]:
        service >> Edge(label="store_data()", color="orange") >> [relational_db, nosql_db]

    auth_server >> Edge(label="queries()", color="brown") >> relational_db
    relational_db >> Edge(label="replicates_to()", color="darkgreen") >> nosql_db
