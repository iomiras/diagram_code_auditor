<?php

class Library {
    private $name;
    private $address;
    private $books = [];
    private $members = [];

    public function __construct($name, $address) {
        $this->name = $name;
        $this->address = $address;
    }

    public function addBook($book) {
        $this->books[] = $book;
        echo "Book '{$book->getTitle()}' added to the library.\n";
    }

    public function registerMember($member) {
        $this->members[] = $member;
        echo "Member '{$member->getName()}' registered to the library.\n";
    }
}

class Book {
    private $title;
    private $author;
    private $isbn;
    private $borrower = null;

    public function __construct($title, $author, $isbn) {
        $this->title = $title;
        $this->author = $author;
        $this->isbn = $isbn;
    }

    public function borrow($member) {
        if ($this->borrower === null) {
            $this->borrower = $member;
            echo "'{$this->title}' is borrowed by {$member->getName()}.\n";
        } else {
            echo "'{$this->title}' is already borrowed by {$this->borrower->getName()}.\n";
        }
    }

    public function returnBook() {
        if ($this->borrower !== null) {
            echo "'{$this->title}' is returned by {$this->borrower->getName()}.\n";
            $this->borrower = null;
        } else {
            echo "'{$this->title}' is not currently borrowed.\n";
        }
    }

    public function getTitle() {
        return $this->title;
    }
}

class Member {
    private $name;
    private $membershipId;
    private $borrowedBooks = [];

    public function __construct($name, $membershipId) {
        $this->name = $name;
        $this->membershipId = $membershipId;
    }

    public function borrowBook($book) {
        if (count($this->borrowedBooks) < 5) {
            $book->borrow($this);
            $this->borrowedBooks[] = $book;
        } else {
            echo "{$this->name} has reached the borrowing limit.\n";
        }
    }

    public function returnBook($book) {
        $key = array_search($book, $this->borrowedBooks, true);
        if ($key !== false) {
            $book->returnBook();
            unset($this->borrowedBooks[$key]);
        } else {
            echo "{$this->name} doesn't have the book '{$book->getTitle()}' to return.\n";
        }
    }

    public function getName() {
        return $this->name;
    }
}

class Librarian {
    private $name;
    private $employeeId;

    public function __construct($name, $employeeId) {
        $this->name = $name;
        $this->employeeId = $employeeId;
    }

    public function catalogBook($library, $book) {
        $library->addBook($book);
        echo "Librarian '{$this->name}' cataloged '{$book->getTitle()}'.\n";
    }

    public function enrollMember($library, $member) {
        $library->registerMember($member);
        echo "Librarian '{$this->name}' enrolled member '{$member->getName()}'.\n";
    }
}
