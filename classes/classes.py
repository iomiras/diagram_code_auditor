class User:
    def __init__(self, name):
        self.name = name

    def access_via(self, devices):
        for device in devices:
            print(f"{self.name} accesses via {device.name}")


class MobileApp:
    def __init__(self, name):
        self.name = name


class DesktopApp:
    def __init__(self, name):
        self.name = name


class Firewall:
    def __init__(self, name):
        self.name = name

    def secured_by(self, devices):
        for device in devices:
            print(f"{device.name} is secured by {self.name}")

    def routes_to(self, target):
        print(f"{self.name} routes to {target.name}")


class LoadBalancer:
    def __init__(self, name):
        self.name = name

    def balance(self, services):
        for service in services:
            print(f"{self.name} balances {service.name}")

    def authenticates_via(self, server):
        print(f"{self.name} authenticates via {server.name}")


class Service:
    def __init__(self, name):
        self.name = name

    def store_data(self, databases):
        for db in databases:
            print(f"{self.name} stores data in {db.name}")


class RelationalDB:
    def __init__(self, name):
        self.name = name

    def replicates_to(self, target_db):
        print(f"{self.name} replicates to {target_db.name}")


class NoSQLDB:
    def __init__(self, name):
        self.name = name


class AuthServer:
    def __init__(self, name):
        self.name = name

    def queries(self, database):
        print(f"{self.name} queries {database.name}")


# Instantiating objects
user = User("User")

# Frontend Cluster
mobile = MobileApp("MobileApp")
desktop = DesktopApp("DesktopApp")

# Backend Cluster
load_balancer = LoadBalancer("LoadBalancer")

# Compute Cluster
service1 = Service("Service1")
service2 = Service("Service2")
service3 = Service("Service3")

# Database Cluster
relational_db = RelationalDB("RelationalDB")
nosql_db = NoSQLDB("NoSQLDB")

# Security Layer
firewall = Firewall("Firewall")
auth_server = AuthServer("AuthServer")

# Simulated relationships
devices = [mobile, desktop]
services = [service1, service2, service3]
databases = [relational_db, nosql_db]

# Relationships
user.access_via(devices)
firewall.secured_by(devices)
firewall.routes_to(load_balancer)
load_balancer.balance(services)
load_balancer.authenticates_via(auth_server)

for service in services:
    service.store_data(databases)

auth_server.queries(relational_db)
relational_db.replicates_to(nosql_db)
