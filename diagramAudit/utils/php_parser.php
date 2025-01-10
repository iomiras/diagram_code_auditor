<?php
require_once __DIR__ . '/vendor/autoload.php';

use PhpParser\Error;
use PhpParser\NodeDumper;
use PhpParser\ParserFactory;
use PhpParser\Node;
use PhpParser\Node\Stmt\ClassMethod;
use PhpParser\NodeTraverser;
use PhpParser\NodeVisitorAbstract;
use PhpParser\Node\Stmt\Class_;

$file_name = './classes_without_diagrams/project_classes.php';
$json_output = './tmp/output.json';

$classes = [];
$classToMethods = [];
$classToAttributes = [];

class ExtractorVisitor extends NodeVisitorAbstract {
    private $classes, $classToMethods, $classToAttributes, $currentClass;
    public function __construct()
    {
        global $classes, $classToMethods, $classToAttributes;
        $this->classes = &$classes;
        $this->classToMethods = &$classToMethods;
        $this->classToAttributes = &$classToAttributes;
        $this->currentClass = null;
    }
    public function enterNode(Node $node) {
        if ($node instanceof Class_) {
            $this->currentClass = $node->name;
            if (!in_array($this->currentClass, $this->classes))
                $this->classes[] = $this->currentClass;
            if ($node->extends) {
                foreach ($node->extends->parts as $part) {
                    foreach ($this->classToMethods[$part] as $method) {
                        if (isset($this->classToMethods[$this->currentClass])) {
                            if (!in_array($method, $this->classToMethods[$this->currentClass]))
                                $this->classToMethods[$this->currentClass] = $method . '()';
                        }
                    }
                    foreach ($this->classToAttributes[$part] as $attribute) {
                        if (isset($this->classToAttributes[$this->currentClass])) {
                            if (!in_array($attribute, $this->classToAttributes[$this->currentClass]))
                                $this->classToAttributes[$this->currentClass] = $attribute;

                        }
                    }
                }
            }
        }
        if ($node instanceof ClassMethod) {
            if ($node->name == "__construct") {
                foreach($node->params as $param) {
                    $this->classToAttributes[$this->currentClass][] = $param->name;
                }
            }
            else $this->classToMethods[$this->currentClass][] = $node->name . '()';
        }
    }
}

function extractData($filename){
    $code = file_get_contents($filename);
    $parserFactory = new ParserFactory();
    $parser = $parserFactory->create(ParserFactory::PREFER_PHP7);
    $stmts = $parser->parse($code);

    $nodeTraverser = new NodeTraverser();
    $extractVisitor = new ExtractorVisitor();
    $nodeTraverser->addVisitor($extractVisitor);

    $nodeTraverser->traverse($stmts);
}

function parseDataToJson($filename, $json_output): ?array
{
    try {
        global $classes, $classToMethods, $classToAttributes;

        extractData($filename);
        $resultJson = json_encode(["classes" => $classes, "classToMethods" => $classToMethods, "classToAttributes" => $classToAttributes], JSON_PRETTY_PRINT);
        file_put_contents($json_output, $resultJson);
        return [$classes, $classToMethods, $classToAttributes];
    } catch (PhpParser\Error $e) {
        echo 'Parse Error: ', $e->getMessage();
        return null;
    }
}

function main($filename, $json_output): ?array
{
    extractData($filename);
    return parseDataToJson($filename, $json_output);
}

$file_name = $argv[1];
$json_output = $argv[2];
main($file_name, $json_output);