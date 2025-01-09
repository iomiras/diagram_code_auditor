from diagrams.c4 import Container
from diagrams import Diagram, Cluster, Edge

graph_attr = {
    "splines": "curve",
}

with Diagram("Class Relationships and Methods Php", filename="./Class Relationships and Methods Php", direction="TB", show=False, graph_attr=graph_attr):
    # Vehicle Cluster
    with Cluster("Vehicle Classes"):
        vehicle = Container("Vehicle")

        # Explicitly listing methods for Vehicle
        vehicle_method = "getDescription()"
        # for method in vehicle_methods:
        vehicle >> Edge(label=vehicle_method, style="dashed", color="blue") >> vehicle

        # Derived vehicle classes
        car = Container("Car")
        motorcycle = Container("Motorcycle")
        vehicle_classes = [car, motorcycle]
        # derived_classes = 

        # for vehicle_cls in vehicle_classes:
            # derived = Container(cls)
        vehicle_classes >> Edge(label="inherits", style="dashed", color="darkgreen") << vehicle
            # derived_classes.append(derived)

    # Garage Class
    garage = Container("Garage")

    # Maintenance Class
    maintenance = Container("Maintenance")

    # Relationships between classes
    garage >> Edge(label="stores()", style="solid", color="red") >> vehicle_classes
    maintenance >> Edge(label="operatesIn()", style="solid", color="red") >> garage

    # Explicitly listing methods for Garage
    garage_method1 = "listVehicles()"
    garage_method2 = "reportMaintenance()"
    garage >> Edge(label=garage_method1, style="dashed", color="blue") >> garage
    garage >> Edge(label=garage_method2, style="dashed", color="blue") >> garage
    
    edge = "addVehicle()"
    garage >> Edge(label=edge, style="solid", color="red") >> vehicle

    # Explicitly listing methods for Maintenance
    maintenance_method = "performMaintenance()"
    maintenance >> Edge(label=maintenance_method, style="dashed", color="blue") >> maintenance
