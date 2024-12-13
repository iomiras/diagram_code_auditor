class ClassA:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello from {self.name}!"

    def interact_with_b(self, obj_b):
        return f"{self.name} says: {obj_b.respond_to_a()}"