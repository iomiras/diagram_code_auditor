from diagrams.c4 import Container
from diagrams import Diagram, Cluster, Edge

graph_attr = {
    "splines": "polyline",
}

with Diagram("Class Relationships and Methods Python", direction="TB", show=False, graph_attr=graph_attr):
    
    with Cluster("Person Classes"):
        # Person class
        person = Container("Person")

        # Customer and Employee derived classes
        customer = Container("Customer")
        employee = Container("Employee")

        people = [customer, employee]
    
    # Explicitly listing methods for Person
    person_method = "introduce()"
    person >> Edge(label=person_method, style="dashed", color="blue") >> person
    person >> Edge(label="tell_name()", style="dashed", color="blue") >> person

    for _person in people:
        _person >> Edge(label="inherits", style="dashed", color="darkgreen") >> person

    # Order Class
    order = Container("Order")

    customer >> Edge(label="view_order_history()", style="dashed", color="blue") >> customer >> Edge(label="place_order()", style="solid", color="red") >> order
    # customer >> Edge(label="place_order()", style="solid", color="red") >> order

    # customer >> Edge(label="place_order()", style="solid", color="red") >> order
    customer >> Edge(label="cancel_order()", style="solid", color="red") >> order

    # customer >> Edge(label="places()", style="solid", color="red") >> order

    people = [customer, employee]

    # for _person in people:
    #     _person >> Edge(label="inherits", style="dashed", color="darkgreen") >> person
    # customer >> Edge(label="inherits", style="dashed", color="darkgreen") >> person
    # employee >> Edge(label="inherits", style="dashed", color="darkgreen") >> person

    product = Container("Product")

    # Inventory Class
    inventory = Container("Inventory")

    # Relationships between classes
    employee >> Edge(label="update_inventory()", style="solid", color="red") >> inventory

    # Explicitly listing methods for Employee
    employee_method = "update_inventory()"
    employee >> Edge(label=employee_method, style="dashed", color="blue") >> employee

    employee >> Edge(label="process_order()", style="solid", color="red") >> order

    # Explicitly listing methods for Product
    product_method = "update_price()"
    # for method in product_methods:
    product >> Edge(label=product_method, style="dashed", color="blue") >> product

    # Explicitly listing methods for Inventory
    inventory >> Edge(label="check_stock()", style="solid", color="red") >> product
    inventory >> Edge(label="add_product()", style="solid", color="red") >> product
    
    # inventory >> Edge(label="add_product()", style="solid", color="red") >> product

    # Explicitly listing methods for Order
    # for method in order_methods:
    order >> Edge(label="calculate_total()", style="dashed", color="blue") >> order
    order >> Edge(label="apply_discount()", style="dashed", color="blue") >> order