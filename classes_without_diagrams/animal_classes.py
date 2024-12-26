class Animal:
    """Base class for all animals."""
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound."

class Dog(Animal):
    """Dog class inheriting from Animal."""
    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

class Cat(Animal):
    """Cat class inheriting from Animal."""
    def __init__(self, name, color):
        super().__init__(name)
        self.color = color

    def speak(self):
        return f"{self.name}, the {self.color} cat, meows!"

class Person:
    """Person class that interacts with Animal classes."""
    def __init__(self, name):
        self.name = name
        self.pets = []

    def adopt_pet(self, pet):
        if isinstance(pet, Animal):
            self.pets.append(pet)
            print(f"{self.name} adopted a pet named {pet.name}.")
        else:
            print("This is not a valid pet!")

    def list_pets(self):
        if not self.pets:
            return f"{self.name} has no pets."
        return f"{self.name} owns: " + ", ".join([pet.name for pet in self.pets])

class Vet:
    """Vet class that provides services to animals."""
    def __init__(self, name):
        self.name = name

    def treat_animal(self, animal):
        if isinstance(animal, Animal):
            print(f"Vet {self.name} is treating {animal.name}.")
        else:
            print("This is not a valid animal!")

class Kennel:
    """Kennel class that manages a collection of animals."""
    def __init__(self):
        self.animals = []

    def add_animal(self, animal):
        if isinstance(animal, Animal):
            self.animals.append(animal)
            print(f"Added {animal.name} to the kennel.")
        else:
            print("Only animals are allowed in the kennel.")

    def list_animals(self):
        if not self.animals:
            return "The kennel is empty."
        return "Animals in the kennel: " + ", ".join([animal for animal in self.animals])
