class Library:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.books = []
        self.members = []

    def add_book(self, book):
        self.books.append(book)
        print(f"Book '{book.title}' added to the library.")

    def register_member(self, member):
        self.members.append(member)
        print(f"Member '{member.name}' registered to the library.")


class Book:
    def __init__(self, title, author, isbn):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.borrower = None

    def borrow(self, member):
        if self.borrower is None:
            self.borrower = member
            print(f"'{self.title}' is borrowed by {member.name}.")
        else:
            print(f"'{self.title}' is already borrowed by {self.borrower.name}.")

    def return_book(self):
        if self.borrower:
            print(f"'{self.title}' is returned by {self.borrower.name}.")
            self.borrower = None
        else:
            print(f"'{self.title}' is not currently borrowed.")


class Member:
    def __init__(self, name, membership_id):
        self.name = name
        self.membership_id = membership_id
        self.borrowed_books = []

    def borrow_book(self, book):
        if len(self.borrowed_books) < 5:
            book.borrow(self)
            self.borrowed_books.append(book)
        else:
            print(f"{self.name} has reached the borrowing limit.")

    def return_book(self, book):
        if book in self.borrowed_books:
            book.return_book()
            self.borrowed_books.remove(book)
        else:
            print(f"{self.name} doesn't have the book '{book.title}' to return.")


class Librarian:
    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id

    def catalog_book(self, library, book):
        library.add_book(book)
        print(f"Librarian '{self.name}' cataloged '{book.title}'.")

    def enroll_member(self, library, member):
        library.register_member(member)
        print(f"Librarian '{self.name}' enrolled member '{member.name}'.")
