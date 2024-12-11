class ClassA:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello from {self.name}!"

    def interact_with_b(self, obj_b):
        return f"{self.name} says: {obj_b.respond_to_a()}"


class ClassB:
    def __init__(self, id_number, obj_c):
        self.id_number = id_number
        self.obj_c = obj_c

    def respond_to_a(self):
        return f"ClassB (ID: {self.id_number}) responding to ClassA"

    def use_class_c(self):
        return self.obj_c.provide_data()


class ClassC:
    def __init__(self, dataset):
        self.dataset = dataset

    def provide_data(self):
        return f"ClassC provides dataset: {self.dataset}"

    def interact_with_a(self, obj_a):
        return f"ClassC interacting with {obj_a.name}"

    def interact_with_b(self, obj_b):
        return f"ClassC sends data to ClassB (ID: {obj_b.id_number}): {self.dataset}"