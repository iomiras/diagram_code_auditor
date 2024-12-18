# diagram1.py
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
    user = User("User")

    with Cluster("Frontend Classes"):
        mobile_app = Mobile("MobileApp")
        desktop_app = Tablet("DesktopApp")

    with Cluster("Backend Classes"):
        load_balancer = Rack("LoadBalancer")

        with Cluster("Service Classes"):
            service = Server("Service")  # Parent class
            service1 = Server("Service1")
            service2 = Server("Service2")
            service3 = Server("Service3")

            service >> Edge(label="restart_service()", style="dotted") >> service
            service >> Edge(label="store_data()", style="dotted") >> service

            service_list = [service1, service2, service3]

            for svc in service_list:
                svc >> Edge(label="inherits", style="dotted", color="gray") >> service

        load_balancer >> Edge(label="balance()") >> [service1, service2, service3]

    with Cluster("Database Classes"):
        relational_db = SQL("RelationalDB")
        nosql_db = Storage("NoSQLDB")

    with Cluster("Security Classes"):
        firewall = Firewall("Firewall")
        auth_server = Server("AuthServer")

    user >> Edge(label="access_via()") >> [mobile_app, desktop_app]
    [mobile_app, desktop_app] >> Edge(label="secured_by()") >> firewall
    firewall >> Edge(label="routes_to()") >> load_balancer
    load_balancer >> Edge(label="authenticates_via()") >> auth_server

    for _service in service_list:
        _service >> Edge(label="store_data()") >> [relational_db, nosql_db]

    auth_server >> Edge(label="queries()") >> relational_db
    relational_db >> Edge(label="replicates_to()") >> nosql_db

    # Standalone methods
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

    relational_db >> Edge(label="backup_data()", style="dotted") >> relational_db
    nosql_db >> Edge(label="clear_cache()", style="dotted") >> nosql_db

    auth_server >> Edge(label="validate_token()", style="dotted") >> auth_server

