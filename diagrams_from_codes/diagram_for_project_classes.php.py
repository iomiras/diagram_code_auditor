from diagrams import Diagram, Edge
from diagrams.c4 import Container
graph_attr = {'splines': 'polyline'}

with Diagram("diagram for project classes.php", filename= ".//diagrams_from_codes/diagram_for_project_classes", direction="LR", show=False, graph_attr=graph_attr):
    project = Container(name="Project")
    task = Container(name="Task")
    developer = Container(name="Developer")
    manager = Container(name="Manager")

    project >> Edge(label="addTask()", style='solid', color='red') >> task
    project >> Edge(label="addTask()", style='solid', color='red') >> developer
    project >> Edge(label="addTask()", style='solid', color='red') >> project
    project >> Edge(label="addTask()", style='dotted', color='black') >> [task, developer]
    project >> Edge(label="assignDeveloper()", style='solid', color='red') >> developer
    project >> Edge(label="assignDeveloper()", style='solid', color='red') >> project
    project >> Edge(label="assignDeveloper()", style='dotted', color='black') >> [task, developer]
    project >> Edge(label="overview()", style='solid', color='red') >> project
    project >> Edge(label="overview()", style='dotted', color='black') >> [task, developer]
    task >> Edge(label="assignTo()", style='solid', color='red') >> developer
    task >> Edge(label="assignTo()", style='solid', color='red') >> task
    task >> Edge(label="assignTo()", style='dotted', color='black') >> [task, developer, project]
    task >> Edge(label="complete()", style='solid', color='red') >> task
    task >> Edge(label="complete()", style='dotted', color='black') >> [task, developer, project]
    task >> Edge(label="getName()", style='solid', color='red') >> task
    task >> Edge(label="getName()", style='dotted', color='black') >> [task, developer, project]
    task >> Edge(label="getAssignee()", style='solid', color='red') >> task
    task >> Edge(label="getAssignee()", style='dotted', color='black') >> [task, developer, project]
    developer >> Edge(label="takeTask()", style='solid', color='red') >> task
    developer >> Edge(label="takeTask()", style='solid', color='red') >> developer
    developer >> Edge(label="takeTask()", style='dotted', color='black') >> [task, developer, project]
    developer >> Edge(label="finishTask()", style='solid', color='red') >> task
    developer >> Edge(label="finishTask()", style='solid', color='red') >> developer
    developer >> Edge(label="finishTask()", style='dotted', color='black') >> [task, developer, project]
    developer >> Edge(label="addTask()", style='solid', color='red') >> task
    developer >> Edge(label="addTask()", style='solid', color='red') >> developer
    developer >> Edge(label="addTask()", style='dotted', color='black') >> [task, developer, project]
    developer >> Edge(label="getName()", style='solid', color='red') >> developer
    developer >> Edge(label="getName()", style='dotted', color='black') >> [task, developer, project]
    manager >> Edge(label="createProject()", style='solid', color='red') >> manager
    manager >> Edge(label="createProject()", style='dotted', color='black') >> [task, developer, project]
    manager >> Edge(label="hireDeveloper()", style='solid', color='red') >> manager
    manager >> Edge(label="hireDeveloper()", style='dotted', color='black') >> [task, developer, project]
    manager >> Edge(label="addTaskToProject()", style='solid', color='red') >> project
    manager >> Edge(label="addTaskToProject()", style='solid', color='red') >> task
    manager >> Edge(label="addTaskToProject()", style='solid', color='red') >> manager
    manager >> Edge(label="addTaskToProject()", style='dotted', color='black') >> [task, developer, project]
    manager >> Edge(label="assignDevToProject()", style='solid', color='red') >> project
    manager >> Edge(label="assignDevToProject()", style='solid', color='red') >> developer
    manager >> Edge(label="assignDevToProject()", style='solid', color='red') >> manager
    manager >> Edge(label="assignDevToProject()", style='dotted', color='black') >> [task, developer, project]
