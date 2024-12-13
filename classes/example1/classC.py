class ClassC:
    def __init__(self, dataset):
        self.dataset = dataset

    def provide_data(self):
        return f"ClassC provides dataset: {self.dataset}"

    def interact_with_a(self, obj_a):
        return f"ClassC interacting with {obj_a.name}"

    def interact_with_b(self, obj_b):
        return f"ClassC sends data to ClassB (ID: {obj_b.id_number}): {self.dataset}"