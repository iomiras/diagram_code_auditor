from diagrams import Diagram, Edge
from diagrams.c4 import Container
graph_attr = {'splines': 'polyline'}

with Diagram("diagram for animal classes.py", filename= "././diagrams_from_codes/diagram_for_animal_classes.py.png", direction="LR", show=False, graph_attr=graph_attr):
    animal = Container(name="Animal")
    dog = Container(name="Dog")
    cat = Container(name="Cat")
    person = Container(name="Person")
    vet = Container(name="Vet")
    kennel = Container(name="Kennel")

    dog >> Edge(label="inherits", style='dashed', color='darkgreen') >> animal
    cat >> Edge(label="inherits", style='dashed', color='darkgreen') >> animal
    person >> Edge(label="adopt_pet()", style='dotted', color='black') >> [animal, person, vet]
    person >> Edge(label="list_pets()", style='dotted', color='black') >> [animal, person, vet]
    vet >> Edge(label="treat_animal()", style='dotted', color='black') >> [animal, person, vet]
    kennel >> Edge(label="add_animal()", style='dotted', color='black') >> [animal, person, vet]
    animal >> Edge(label="speak()", style='dashed', color='blue') >> animal
    dog >> Edge(label="speak()", style='dashed', color='blue') >> dog
    cat >> Edge(label="speak()", style='dashed', color='blue') >> cat
    kennel >> Edge(label="list_animals()", style='dashed', color='blue') >> kennel
