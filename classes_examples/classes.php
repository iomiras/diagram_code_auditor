<?php

namespace classes_examples;

class User {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function login() {
        echo "$this->name logged in\n";
    }

    public function logout() {
        echo "$this->name logged out\n";
    }

    public function profile_view() {
        echo "$this->name viewed profile\n";
    }

    public function profile_update() {
        echo "$this->name updated profile\n";
    }

    public function access_via($devices) {
        foreach ($devices as $device) {
            echo "$this->name accesses via {$device->get_name()}\n";
        }
    }
}

class MobileApp {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function update_ui() {
        echo "$this->name UI updated\n";
    }

    public function secured_by($firewall) {
        echo "$this->name is secured by {$firewall->get_name()}\n";
    }
}

class DesktopApp {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function secured_by($firewall) {
        echo "$this->name is secured by {$firewall->get_name()}\n";
    }

    public function render_view() {
        echo "$this->name rendered view\n";
    }
}

class Firewall {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function routes_to($server) {
        echo "$this->name routes to {$server->get_name()}\n";
    }

    public function filter_traffic() {
        echo "$this->name is filtering traffic\n";
    }

    public function monitor_logs() {
        echo "$this->name is monitoring logs\n";
    }

    public function login() {
        echo "$this->name handled login\n";
    }
}

class LoadBalancer {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function authenticates_via($authServer) {
        echo "$this->name authenticates via {$authServer->get_name()}\n";
    }

    public function check_health() {
        echo "$this->name is checking health\n";
    }

    public function restart() {
        echo "$this->name is restarting\n";
    }

    public function balance($services) {
        foreach ($services as $service) {
            echo "$this->name balances {$service->get_name()}\n";
        }
    }
}

class Service {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function restart_service() {
        echo "$this->name is restarting\n";
    }

    public function store_data($databases) {
        foreach ($databases as $db) {
            echo "$this->name stores data in {$db->get_name()}\n";
        }
    }

    public function backup() {
        echo "$this->name is backing up data\n";
    }
}

class Service1 extends Service {
    public function __construct() {
        parent::__construct("Service1");
    }

    public function creates($server) {
        echo "$this->name creates new {$server->get_name()}\n";
    }
}

class Service2 extends Service {
    public function __construct() {
        parent::__construct("Service2");
    }
}

class Service3 extends Service {
    public function __construct() {
        parent::__construct("Service3");
    }
}

class Service4 {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }
}

class Service5 {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }
}

class Service6 {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }
}

class RelationalDB {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function replicates_to($nosqldb) {
        echo "$this->name replicates to {$nosqldb->get_name()}\n";
    }

    public function backup_data() {
        echo "$this->name is backing up data\n";
    }
}

class NoSQLDB {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function clear_cache() {
        echo "$this->name cache cleared\n";
    }
}

class AuthServer {
    private $name;

    public function __construct($name) {
        $this->name = $name;
    }

    public function validate_token() {
        echo "$this->name is validating tokens\n";
    }

    public function queries($database) {
        echo "$this->name queries all {$database->get_name()}\n.";
    }
}

// class Legent {
//     private $name;

//     public function __construct($name) {
//         $this->name = $name;
//     }

//     public function get_name() {
//         return $this->name;
//     }
// }