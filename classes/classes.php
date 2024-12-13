<?php

class ClassA {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function greet() {
        return "Hello from {$this->name}!";
    }

    public function interactWithB($objB) {
        return "{$this->name} says: " . $objB->respondToA();
    }
}

class ClassB {
    private $idNumber;
    private $objC;

    public function __construct($idNumber, $objC) {
        $this->idNumber = $idNumber;
        $this->objC = $objC;
    }

    public function respondToA() {
        return "ClassB (ID: {$this->idNumber}) responding to ClassA";
    }

    public function useClassC() {
        return $this->objC->provideData();
    }
}

class ClassC {
    private $dataset;

    public function __construct($dataset) {
        $this->dataset = $dataset;
    }

    public function provideData() {
        return "ClassC provides dataset: {$this->dataset}";
    }

    public function interactWithA($objA) {
        return "ClassC interacting with {$objA->getName()}";
    }

    public function interactWithB($objB) {
        return "ClassC sends data to ClassB (ID: {$objB->getIdNumber()}): {$this->dataset}";
    }
}

// Utility methods for ClassA and ClassB to access private properties.
class ClassA {
    public function getName() {
        return $this->name;
    }
}

class ClassB {
    public function getIdNumber() {
        return $this->idNumber;
    }
}
?>
