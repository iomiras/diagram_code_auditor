from diagrams import Diagram, Edge
from diagrams.c4 import Container
graph_attr = {'splines': 'polyline'}

with Diagram("diagram for classes.py", filename= ".//diagrams_from_codes/diagram_for_classes", direction="TB", show=False, graph_attr=graph_attr):
    person = Container(name="Person")
    customer = Container(name="Customer")
    employee = Container(name="Employee")
    product = Container(name="Product")
    inventory = Container(name="Inventory")
    order = Container(name="Order")

    customer >> Edge(label="inherits", style='dashed', color='darkgreen') >> person
    customer >> Edge(label="place_order()", style='solid', color='red') >> order
    customer >> Edge(label="cancel_order()", style='solid', color='red') >> order
    employee >> Edge(label="inherits", style='dashed', color='darkgreen') >> person
    employee >> Edge(label="process_order()", style='solid', color='red') >> order
    employee >> Edge(label="update_inventory()", style='solid', color='red') >> inventory
    employee >> Edge(label="update_inventory()", style='dotted', color='black') >> [person, product]
    inventory >> Edge(label="add_product()", style='solid', color='red') >> product
    inventory >> Edge(label="add_product()", style='dotted', color='black') >> [person, product]
    inventory >> Edge(label="check_stock()", style='solid', color='red') >> product
    inventory >> Edge(label="check_stock()", style='dotted', color='black') >> [person, product]
    order >> Edge(label="calculate_total()", style='solid', color='red') >> product
    person >> Edge(label="tell_name()", style='dashed', color='blue') >> person
    person >> Edge(label="introduce()", style='dashed', color='blue') >> person
    customer >> Edge(label="introduce()", style='dashed', color='blue') >> customer
    customer >> Edge(label="tell_name()", style='dashed', color='blue') >> customer
    customer >> Edge(label="view_order_history()", style='dashed', color='blue') >> customer
    employee >> Edge(label="tell_name()", style='dashed', color='blue') >> employee
    employee >> Edge(label="introduce()", style='dashed', color='blue') >> employee
    product >> Edge(label="update_price()", style='dashed', color='blue') >> product
    order >> Edge(label="apply_discount()", style='dashed', color='blue') >> order
