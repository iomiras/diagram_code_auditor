<?php

// Base class for vehicles
abstract class Vehicle {
    protected $make;
    protected $model;
    protected $year;

    public function __construct($make, $model, $year) {
        $this->make = $make;
        $this->model = $model;
        $this->year = $year;
    }

    public function getDescription() {
        return "{$this->year} {$this->make} {$this->model}";
    }
}

// Derived class: Car
class Car extends Vehicle {
    private $doorCount;

    public function __construct($make, $model, $year, $doorCount) {
        parent::__construct($make, $model, $year);
        $this->doorCount = $doorCount;
    }

    public function getDescription() {
        return "{$this->year} {$this->make} {$this->model} with {$this->doorCount} doors.";
    }
}

// Derived class: Motorcycle
class Motorcycle extends Vehicle {
    private $type;

    public function __construct($make, $model, $year, $type) {
        parent::__construct($make, $model, $year);
        $this->type = $type;
    }

    public function getDescription() {
        return "{$this->year} {$this->make} {$this->model} ({$this->type} motorcycle).";
    }
}

// Intertwined class: Garage
class Garage {
    private $vehicles = [];

    public function addVehicle(Vehicle $vehicle) {
        $this->vehicles[] = $vehicle;
    }

    public function listVehicles() {
        foreach ($this->vehicles as $vehicle) {
            echo $vehicle->getDescription() . PHP_EOL;
        }
    }

    public function reportMaintenance() {
        echo "The following vehicles are done for maintenance:" . PHP_EOL;
    }

    public function stores($vehicle) {
        $this->vehicles[] = $vehicle;
    }
}

// Another intertwined class: Maintenance
class Maintenance {
    private $garage;

    public function __construct(Garage $garage) {
        $this->garage = $garage;
    }

    public function performMaintenance() {
        echo "Performing maintenance on all vehicles in the garage:" . PHP_EOL;
        $this->garage->listVehicles();
    }

    public function operatesIn($garage) {
        $this->garage = $garage;
    }
}