class Person:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def introduce(self):
        print(f"My name is {self.name}, and you can reach me at {self.email}.")
    
    def tell_name(self):
        print(f"My name is {self.name}.")


class Customer(Person):
    def __init__(self, name, email, customer_id):
        super().__init__(name, email)
        self.customer_id = customer_id

    def place_order(self, order):
        print(f"Customer {self.name} placed order {order.order_id}.")

    def cancel_order(self, order):
        print(f"Customer {self.name} canceled order {order.order_id}.")

    def view_order_history(self):
        print(f"Customer {self.name} is viewing order history.")


class Employee(Person):
    def __init__(self, name, email, employee_id):
        super().__init__(name, email)
        self.employee_id = employee_id

    def process_order(self, order):
        print(f"Employee {self.name} is processing order {order.order_id}.")

    def update_inventory(self, inventory, product, quantity):
        inventory.add_product(product, quantity)
        print(f"Employee {self.name} updated inventory for {product.name}.")


class Product:
    def __init__(self, product_id, name, price):
        self.product_id = product_id
        self.name = name
        self.price = price

    def update_price(self, new_price):
        print(f"Price for {self.name} updated from {self.price} to {new_price}.")
        self.price = new_price


class Inventory:
    def __init__(self):
        self.products = {}

    def add_product(self, product, quantity):
        if product.product_id in self.products:
            self.products[product.product_id]["quantity"] += quantity
        else:
            self.products[product.product_id] = {"product": product, "quantity": quantity}
        print(f"Added {quantity} units of {product.name} to inventory.")

    def check_stock(self, product):
        if product.product_id in self.products:
            print(f"Stock for {product.name}: {self.products[product.product_id]['quantity']}")
            return self.products[product.product_id]["quantity"]
        print(f"{product.name} is out of stock.")
        return 0


class Order:
    def __init__(self, order_id, customer, products):
        self.order_id = order_id
        self.customer = customer
        self.products = products

    def calculate_total(self):
        total = sum(product.price for product in self.products)
        print(f"Total for order {self.order_id}: {total}")
        return total

    def apply_discount(self, discount):
        print(f"Order {self.order_id} received a discount of {discount}%.")