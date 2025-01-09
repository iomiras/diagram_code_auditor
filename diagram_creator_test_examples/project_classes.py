class Project:
    def __init__(self, title, deadline):
        self.title = title
        self.deadline = deadline
        self.tasks = []
        self.developers = []

    def add_task(self, task):
        self.tasks.append(task)
        print(f"Task '{task.name}' added to project '{self.title}'.")

    def assign_developer(self, developer):
        self.developers.append(developer)
        print(f"Developer '{developer.name}' assigned to project '{self.title}'.")

    def overview(self):
        print(f"Project '{self.title}' has {len(self.tasks)} tasks and {len(self.developers)} developers.")
        for task in self.tasks:
            print(f" - Task: {task.name} (Assignee: {task.assignee.name if task.assignee else 'None'})")


class Task:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.assignee = None
        self.completed = False

    def assign_to(self, developer):
        self.assignee = developer
        developer.tasks.append(self)
        print(f"Task '{self.name}' is assigned to developer '{developer.name}'.")

    def complete(self):
        if not self.completed:
            self.completed = True
            print(f"Task '{self.name}' is now completed.")
        else:
            print(f"Task '{self.name}' was already completed.")


class Developer:
    def __init__(self, name, specialty):
        self.name = name
        self.specialty = specialty
        self.tasks = []

    def take_task(self, task):
        self.tasks.append(task)
        task.assignee = self
        print(f"Developer '{self.name}' took task '{task.name}'.")

    def finish_task(self, task):
        if task in self.tasks:
            task.complete()
        else:
            print(f"Developer '{self.name}' cannot finish a task not assigned to them.")


class Manager:
    def __init__(self, name):
        self.name = name

    def create_project(self, title, deadline):
        project = Project(title, deadline)
        print(f"Manager '{self.name}' created project '{title}'.")
        return project

    def hire_developer(self, name, specialty):
        dev = Developer(name, specialty)
        print(f"Manager '{self.name}' hired developer '{name}'.")
        return dev

    def add_task_to_project(self, project, task):
        project.add_task(task)
        print(f"Manager '{self.name}' added task '{task.name}' to project '{project.title}'.")

    def assign_dev_to_project(self, project, developer):
        project.assign_developer(developer)
        print(f"Manager '{self.name}' assigned developer '{developer.name}' to project '{project.title}'.")
