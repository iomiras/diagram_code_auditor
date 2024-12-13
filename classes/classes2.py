class Employee:
    def __init__(self, emp_id, name, department):
        self.emp_id = emp_id
        self.name = name
        self.department = department

    def get_details(self):
        return f"Employee ID: {self.emp_id}, Name: {self.name}, Department: {self.department}"

    def report_to_manager(self, manager):
        return f"{self.name} reports to {manager.get_name()}"

class Manager:
    def __init__(self, name, team):
        self.name = name
        self.team = team  # List of Employee objects

    def get_name(self):
        return self.name

    def list_team(self):
        return [employee.get_details() for employee in self.team]

    def assign_task(self, employee, task):
        return f"Manager {self.name} assigned task '{task}' to {employee.name}"

class Task:
    def __init__(self, task_name, deadline):
        self.task_name = task_name
        self.deadline = deadline

    def get_task_info(self):
        return f"Task: {self.task_name}, Deadline: {self.deadline}"

    def assign_to_employee(self, employee):
        return f"Task '{self.task_name}' assigned to {employee.name}"

# Employee -> Manager:
# Via report_to_manager().
# Manager -> Employee:
# Via list_team() and assign_task().
# Task -> Employee:
# Via assign_to_employee().