class Component:
    def __init__(self, name):
        self.name = name

    def display_info(self):
        print(f"Component: {self.name}")

class Backend(Component):
    def __init__(self, name, language):
        super().__init__(name)
        self.language = language

    def display_info(self):
        print(f"Backend: {self.name}, Language: {self.language}")

    def backend_info(self):
        print(f"{self.name} runs on {self.language}")

class Frontend(Component):
    def __init__(self, name, framework):
        super().__init__(name)
        self.framework = framework

    def display_info(self):
        print(f"Frontend: {self.name}, Framework: {self.framework}")

    def frontend_info(self):
        print(f"{self.name} uses {self.framework}")

class Service(Component):
    def __init__(self, name, api_version):
        super().__init__(name)
        self.api_version = api_version

    def display_info(self):
        print(f"Service: {self.name}, API Version: {self.api_version}")

    def service_info(self):
        print(f"Service {self.name} is running on API version {self.api_version}")

class LoadBalancer(Service):
    def __init__(self, name, api_version, region):
        super().__init__(name, api_version)
        self.region = region

    def display_info(self):
        print(f"LoadBalancer: {self.name}, Region: {self.region}, API Version: {self.api_version}")

    def balancer_info(self):
        print(f"LoadBalancer {self.name} handles traffic in {self.region}")