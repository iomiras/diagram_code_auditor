from diagrams import Diagram, Edge
from diagrams.aws.media import ElementalServer
from diagrams.aws.database import Database
from diagrams.aws.storage import S3
from diagrams.aws.compute import EC2
from diagrams.aws.network import ELB
from diagrams.aws.analytics import Kinesis
from diagrams.aws.integration import StepFunctions

# Complex Example 3: Hybrid System with Multi-source Interactions
graph_attr_3 = {"splines": "polyline"}

with Diagram("Hybrid Multi-source System", show=False, graph_attr=graph_attr_3):
    main_system = ElementalServer("MainSystem")
    auxiliary_system = EC2("AuxiliarySystem")
    data_lake = S3("DataLake")
    report_service = Kinesis("ReportService")
    state_machine = StepFunctions("StateMachine")

    main_system >> Edge(label="writes_data", color="green") >> data_lake
    auxiliary_system >> Edge(label="syncs_with", color="blue") >> data_lake
    data_lake >> Edge(label="feeds", color="red") >> report_service
    report_service >> Edge(label="triggers", color="purple") >> state_machine
    state_machine >> Edge(label="controls", color="orange") >> main_system
    auxiliary_system << Edge(label="logs_errors", color="darkred") << state_machine  # Cross Interaction
