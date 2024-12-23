<?php

// $myDict = json_decode(file_get_contents('./tmp/mydict.json')); 
// $diagramClasses = json_decode(file_get_contents('./tmp/diagram_classes.json'));
// print("diagramClasses is " . gettype($diagramClasses) . "\n");
// print_r($diagramClasses);

// $diagramMethods = json_decode(file_get_contents('./tmp/diagram_methods.json'));
// print("diagramMethods is " . gettype($diagramMethods) . "\n");
// print_r($diagramMethods);

// $allConnections = json_decode(file_get_contents('./tmp/all_connections.json'));
// print("allConnections is " . gettype($allConnections) . "\n");
// print_r($allConnections);

namespace DiagramCodeAuditor;

use PHPat\Selector\Selector;
use PHPat\Test\Builder\Rule;
use PHPat\Test\PHPat;
use App\Domain\SuperForbiddenClass;

final class MyFirstTest
{
    public function test_domain_does_not_depend_on_other_layers(): Rule
    {
        error_log('Debugging MyFirstTest');
        return PHPat::rule()
            ->classes(Selector::namespace('classes_example'))
            ->because('this will break our architecture, implement it another way! see /docs/howto.md');
    }
}