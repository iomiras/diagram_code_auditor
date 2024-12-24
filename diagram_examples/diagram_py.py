from diagrams.programming.flowchart import Action
from diagrams import Diagram, Cluster, Edge
from diagrams.generic.network import Firewall
from diagrams.generic.device import Mobile, Tablet
from diagrams.onprem.client import User
from diagrams.generic.compute import Rack
from diagrams.generic.database import SQL
from diagrams.generic.storage import Storage
from diagrams.onprem.compute import Server

graph_attr = {
    "splines": "curve",
}

with Diagram("Enhanced Class Relationships and Methods Python", direction="TB", show=False, graph_attr=graph_attr):
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

            # Parent methods
            service_parent >> Edge(label="restart_service()", style="dotted") >> service_parent
            service_parent >> Edge(label="store_data()", style="dotted") >> service_parent
            service_parent >> Edge(label="backup()", style="dotted") >> service_parent

            # Child classes inheriting from Service
            service1 = Server("Service1")
            service2 = Server("Service2")
            service3 = Server("Service3")

            # Inheritance relationships using a for loop
            services = [service1, service2, service3]
            inherit = "inherits"
            for service in services:
                service >> Edge(label=inherit, style="dotted", color="gray") >> service_parent

            # Additional services created by Service1
            additional_services = ["Service4", "Service5", "Service6"]
            connection_label = "creates()"
            for service_str in additional_services:
                service1 >> Edge(label=connection_label, color="pink") >> Server(service_str)

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

    # Explicitly listing methods for firewall
    firewall >> Edge(label="filter_traffic()", style="dotted") >> firewall
    firewall >> Edge(label="monitor_logs()", style="dotted") >> firewall
    firewall >> Edge(label="login()", style="dotted") >> firewall

    # Explicitly listing methods for load_balancer
    load_balancer >> Edge(label="check_health()", style="dotted") >> load_balancer
    load_balancer >> Edge(label="restart()", style="dotted") >> load_balancer

    # Connections between services and databases
    service1 >> Edge(label="store_data()", color="orange") >> [relational_db, nosql_db]
    service2 >> Edge(label="store_data()", color="orange") >> [relational_db, nosql_db]
    service3 >> Edge(label="store_data()", color="orange") >> [relational_db, nosql_db]

    auth_server >> Edge(label="queries()", color="brown") >> relational_db
    relational_db >> Edge(label="replicates_to()", color="darkgreen") >> nosql_db

    # Standalone methods for classes
    user >> Edge(label="login()", style="dotted") >> user
    user >> Edge(label="logout()", style="dotted") >> user
    user >> Edge(label="profile_view()", style="dotted") >> user
    user >> Edge(label="profile_update()", style="dotted") >> user

    mobile_app >> Edge(label="update_ui()", style="dotted") >> mobile_app
    desktop_app >> Edge(label="render_view()", style="dotted") >> desktop_app

    relational_db >> Edge(label="backup_data()", style="dotted") >> relational_db
    nosql_db >> Edge(label="clear_cache()", style="dotted") >> nosql_db

    auth_server >> Edge(label="validate_token()", style="dotted") >> auth_server

    #starts here
    auth_server >> Edge(label='lorem_ipsum_auth()', color='red') >> auth_server
    service2 >> Edge(label='test_rel_de()', color='red') >> service2
    # firewall >> Edge(label='lorem_ipsum_firewall()', color='red') >> firewall