from diagrams import Diagram, Edge
from diagrams.c4 import Container
graph_attr = {'splines': 'polyline'}

with Diagram("diagram for project classes.py", filename= "././diagrams_from_codes/diagram_for_project_classes.py.png", direction="LR", show=False, graph_attr=graph_attr):
    project = Container(name="Project")
    task = Container(name="Task")
    developer = Container(name="Developer")
    manager = Container(name="Manager")

    project >> Edge(label="add_task()", style='dotted', color='black') >> [task, developer, manager]
    project >> Edge(label="assign_developer()", style='dotted', color='black') >> [task, developer, manager]
    project >> Edge(label="overview()", style='dotted', color='black') >> [task, developer, manager]
    project >> Edge(label="overview()", color='red', style='solid') >> task
    task >> Edge(label="assign_to()", style='dotted', color='black') >> [project, developer]
    task >> Edge(label="assign_to()", style='dotted', color='black') >> [task, developer, manager]
    developer >> Edge(label="take_task()", color='red', style='solid') >> task
    developer >> Edge(label="take_task()", style='dotted', color='black') >> [task, developer, manager]
    developer >> Edge(label="finish_task()", color='red', style='solid') >> task
    manager >> Edge(label="create_project()", color='red', style='solid') >> project
    manager >> Edge(label="hire_developer()", color='red', style='solid') >> developer
    manager >> Edge(label="add_task_to_project()", color='red', style='solid') >> project
    manager >> Edge(label="add_task_to_project()", style='dotted', color='black') >> [task, developer, manager]
    manager >> Edge(label="assign_dev_to_project()", color='red', style='solid') >> project
    manager >> Edge(label="assign_dev_to_project()", style='dotted', color='black') >> [task, developer, manager]
    task >> Edge(label="complete()", style='dashed', color='blue') >> task
