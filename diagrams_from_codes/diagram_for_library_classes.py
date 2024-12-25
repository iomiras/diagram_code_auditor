from diagrams import Diagram, Edge
from diagrams.c4 import Container
graph_attr = {'splines': 'spline'}

with Diagram("./diagrams_from_codes/diagram_for_library_classes.py", filename= "./diagram_for_library_classes.py", direction="TB", show=True, graph_attr=graph_attr):
    library = Container(name="Library")
    book = Container(name="Book")
    member = Container(name="Member")
    librarian = Container(name="Librarian")

    library >> Edge(label="add_book()", color='red', style='solid') >> book
    library >> Edge(label="register_member()", style='dotted', color='gray') >> [library, member, librarian]
    book >> Edge(label="borrow()", style='dotted', color='gray') >> [library, member, librarian]
    member >> Edge(label="borrow_book()", color='red', style='solid') >> book
    member >> Edge(label="return_book()", style='dotted', color='gray') >> [book, member]
    member >> Edge(label="return_book()", color='red', style='solid') >> book
    librarian >> Edge(label="catalog_book()", color='red', style='solid') >> library
    librarian >> Edge(label="catalog_book()", color='red', style='solid') >> book
    librarian >> Edge(label="enroll_member()", color='red', style='solid') >> library
    librarian >> Edge(label="enroll_member()", style='dotted', color='gray') >> [library, member, librarian]
    book >> Edge(label="return_book()", style='dotted', color='blue') >> book
