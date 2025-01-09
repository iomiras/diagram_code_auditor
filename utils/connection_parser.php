<?php

require_once __DIR__ . '/vendor/autoload.php';

require __DIR__ . '/php_parser.php';

use PhpParser\ParserFactory;
use PhpParser\Node;
use PhpParser\Node\Stmt\ClassMethod;
use PhpParser\NodeTraverser;
use PhpParser\NodeVisitorAbstract;
use PhpParser\Node\Stmt\Class_;


$connections = [];

$connectionsResultJson = './tmp/connections.json';

class ConnectionVisitor extends NodeVisitorAbstract {

    private $currentClass, $currentMethod, $classes;
    private $classesToMethods, $classesToAttributes, $allConnections;
    private $temporaryConnections;

    public function __construct($classes, $classToMethods, $classToAttributes)
    {
        global $connections;
        $this->classes = &$classes;
        $this->classesToMethods = &$classToMethods;
        $this->classesToAttributes = &$classToAttributes;
        $this->currentClass = null;
        $this->currentMethod = null;
        $this->allConnections = &$connections;
        $this->temporaryConnections = [];
    }

    public function enterNode(Node $node)
    {

        if ($node instanceof Class_) {
            $this->currentClass = $node->name;
        }
        if ($node instanceof ClassMethod) {
            $this->currentMethod = $node->name;

        }
        if ($node instanceof Node\Param && isset($this->currentClass)) {
            $this->processParam($node);
        }

        if ($node instanceof Node\Expr\MethodCall) {
            $this->processMethodCall($node);
        }

        if ($node instanceof Node\Expr\PropertyFetch) {
            $this->processPropertyFetch($node);
        }
    }

    public function leaveNode(Node $node)
    {
        if ($node instanceof Class_) {
            $this->addToConnections($this->currentClass, $this->currentMethod, $this->temporaryConnections);
            $this->currentClass = null;
        }
        if ($node instanceof ClassMethod) {
            $this->addToConnections($this->currentClass, $this->currentMethod, $this->temporaryConnections);
            $this->currentMethod = null;
        }
    }

    private function processMethodCall(Node $node)
    {
        if ($node->var->name === 'this') $this->addToConnections($this->currentClass, $this->currentMethod,[$this->currentClass]);
        else {
            foreach ($this->classesToMethods as $class => $methods) {
                if (in_array($node->name . '()', $methods)) {
                    $this->addToTempConnections($class);
                }
            }
        }
    }

    private function processPropertyFetch(Node $node)
    {
        if ($node->var->name === 'this') {
            $this->addToConnections($this->currentClass, $this->currentMethod,[$this->currentClass]);
        } else {
            foreach ($this->classesToAttributes as $class => $attributes) {
                if (in_array($node->var->name, $attributes)) {
                    $this->addToTempConnections($class);
                }
            }
        }
    }

    private function processParam(Node $node)
    {
        if (isset($node->type)) {
//                echo "Processing param\n";
            $assumedClass = $node->type->parts[0];
            if (in_array($assumedClass, $this->classes)) {
                $this->addToConnections($this->currentClass, $this->currentMethod, [$assumedClass]);
            }
        }
    }

    private function addToConnections($class, $method, $temporaryClasses) {
        if ($method !== '__construct' && $class !== null && $method !== null) {
            if (!in_array([$class, $method . '()', $temporaryClasses], $this->allConnections))
                $this->allConnections[] = [$class, $method . '()', $temporaryClasses];
//                $this->allConnections[] = [$class, $method . '()', $temporaryClasses];
        }
    }

    private function addToTempConnections($className) {
        if (!in_array($className, $this->temporaryConnections)) {
            $this->temporaryConnections[] = $className;
        }
    }
}

function parseConnection($file_name, $classes, $classToMethods, $classToAttributes)
{
    $code = file_get_contents($file_name);
    $parserFactory = new ParserFactory();
    $parser = $parserFactory->create(ParserFactory::PREFER_PHP7);

    $connectionVisitor = new ConnectionVisitor($classes, $classToMethods, $classToAttributes);
    $nodeTraverser = new NodeTraverser();
    $nodeTraverser->addVisitor($connectionVisitor);

    $stmts = $parser->parse($code);
    $nodeTraverser->traverse($stmts);
}

$file_name = $argv[1];
$classesDataFileNameJson = $argv[2];
$filenameToStoreConnectionsJson = $argv[3];

echo "Parsing connections for file: $file_name\n";
echo "Classes data file: $classesDataFileNameJson\n";
echo "Storing connections to: $filenameToStoreConnectionsJson\n";


try {
    $result = main($file_name, $classesDataFileNameJson);
    $classes = $result[0];
    $classToMethods = $result[1];
    $classToAttributes = $result[2];

    parseConnection($file_name, $classes, $classToMethods, $classToAttributes);
    $jsonString = json_encode($connections, JSON_PRETTY_PRINT);
    file_put_contents($filenameToStoreConnectionsJson, $jsonString);
} catch (PhpParser\Error $e) {
    echo 'Parse Error: ', $e->getMessage();
}