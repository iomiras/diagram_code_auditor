class Car:
    def __init__(self, model, engine):
        self.model = model
        self.engine = engine  # Engine object

    def start(self):
        return self.engine.start()

    def stop(self):
        return self.engine.stop()


class Engine:
    def __init__(self, type_):
        self.type_ = type_

    def start(self):
        return f"Engine of type {self.type_} started"

    def stop(self):
        return f"Engine of type {self.type_} stopped"

# [
#     ['Car', 'start()', 'Engine'],
#     ['Car', 'stop()', 'Engine']
# ]
