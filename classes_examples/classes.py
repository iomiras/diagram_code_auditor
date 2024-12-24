class User:
    def __init__(self, name):
        self.name = name

    def login(self):
        print(f"{self.name} logged in")

    def logout(self):
        print(f"{self.name} logged out")

    def profile_view(self):
        print(f"{self.name} viewed profile")

    def profile_update(self):
        print(f"{self.name} updated profile")

    def access_via(self, devices):
        for device in devices:
            print(f"{self.name} accesses via {device.name}")


class MobileApp:
    def __init__(self, name):
        self.name = name

    def update_ui(self):
        print(f"{self.name} UI updated")
    
    def secured_by(self, firewall):
        print(f"{self.name} is secured by {firewall.name}")


class DesktopApp:
    def __init__(self, name):
        self.name = name

    def secured_by(self, firewall):
        print(f"{self.name} is secured by {firewall.name}")

    def render_view(self):
        print(f"{self.name} rendered view")


class Firewall:
    def __init__(self, name):
        self.name = name

    def routes_to(self, server):
        print(f"{self.name} routes to {server.name}")

    def filter_traffic(self):
        print(f"{self.name} is filtering traffic")

    def monitor_logs(self):
        print(f"{self.name} is monitoring logs")

    def login(self):
        print(f"{self.name} handled login")


class LoadBalancer:
    def __init__(self, name):
        self.name = name

    def authenticates_via(self, auth_server):
        print(f"{self.name} authenticates via {auth_server.name}")

    def check_health(self):
        print(f"{self.name} is checking health")

    def restart(self):
        print(f"{self.name} is restarting")

    def balance(self, services):
        for service in services:
            print(f"{self.name} balances {service.name}")


class Service:
    def __init__(self, name):
        self.name = name

    def restart_service(self):
        print(f"{self.name} is restarting")

    def store_data(self, databases):
        for db in databases:
            print(f"{self.name} stores data in {db.name}")

    def backup(self):
        print(f"{self.name} is backing up data")


class Service1(Service):
    def __init__(self):
        super().__init__("Service1")

    def creates(self, server):
        print(f"{self.name} creates new {server.name}")


class Service2(Service):
    def __init__(self):
        super().__init__("Service2")


class Service3(Service):
    def __init__(self):
        super().__init__("Service3")


class Service4:
    def __init__(self, name):
        self.name = name


class Service5:
    def __init__(self, name):
        self.name = name


class Service6:
    def __init__(self, name):
        self.name = name
        


class RelationalDB:
    def __init__(self, name):
        self.name = name

    def replicates_to(self, nosqldb):
        print(f"{self.name} replicates to {nosqldb.name}")

    def backup_data(self):
        print(f"{self.name} is backing up data")
    
    def test_rel_de(self):
        print(f"{self.name} has no store_data method")


class NoSQLDB:
    def __init__(self, name):
        self.name = name
        self.surname = name

    def clear_cache(self):
        print(f"{self.name} cache cleared")
    
    def lorem_ipsum_relational_db(self):
        print(f"{self.name} has no store_data method.")


class AuthServer:
    def __init__(self, name):
        self.name = name

    def validate_token(self):
        print(f"{self.name} is validating tokens")

    def queries(self, database):
        print(f"{self.name} queries {database.name}")
