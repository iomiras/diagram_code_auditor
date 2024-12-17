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

with Diagram("Class Relationships and Methods", direction="TB", show=False, graph_attr=graph_attr):
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
            # Parent class (Service)
            service_parent = Server("Service")

            # Child classes inheriting from Service
            service1 = Server("Service1")
            service2 = Server("Service2")
            service3 = Server("Service3")

            services = [service1, service2, service3]
            # services_strs = ["Service1", "Service2", "Service3"]

            for service in services:
                service >> Edge(label="inherits", style="dotted", color="gray") >> service_parent

        # for service_str in services_strs:
        #     load_balancer >> Edge(label="balance()") >> service_str
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

    for service in services:
        service >> Edge(label="store_data()", color="orange") >> [relational_db, nosql_db]

    auth_server >> Edge(label="queries()", color="brown") >> relational_db
    relational_db >> Edge(label="replicates_to()", color="darkgreen") >> nosql_db

    # Standalone methods for each class (as connections to "self")
    user >> Edge(label="login()", style="dotted") >> user
    user >> Edge(label="logout()", style="dotted") >> user
    user >> Edge(label="profile_view()", style="dotted") >> user
    user >> Edge(label="profile_update()", style="dotted") >> user

    mobile_app >> Edge(label="update_ui()", style="dotted") >> mobile_app
    desktop_app >> Edge(label="render_view()", style="dotted") >> desktop_app

    firewall >> Edge(label="filter_traffic()", style="dotted") >> firewall
    firewall >> Edge(label="monitor_logs()", style="dotted") >> firewall
    firewall >> Edge(label="login()", style="dotted") >> firewall

    load_balancer >> Edge(label="check_health()", style="dotted") >> load_balancer
    load_balancer >> Edge(label="restart()", style="dotted") >> load_balancer

    service1 >> Edge(label="restart_service()", style="dotted") >> service1
    service2 >> Edge(label="restart_service()", style="dotted") >> service2
    service3 >> Edge(label="restart_service()", style="dotted") >> service3

    relational_db >> Edge(label="backup_data()", style="dotted") >> relational_db
    nosql_db >> Edge(label="clear_cache()", style="dotted") >> nosql_db

    auth_server >> Edge(label="validate_token()", style="dotted") >> auth_server
