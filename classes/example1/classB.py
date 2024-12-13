class ClassB:
    def __init__(self, id_number, obj_c):
        self.id_number = id_number
        self.obj_c = obj_c

    def respond_to_a(self):
        return f"ClassB (ID: {self.id_number}) responding to ClassA"

    def use_class_c(self):
        return self.obj_c.provide_data()