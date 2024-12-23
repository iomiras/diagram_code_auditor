<?php
require_once __DIR__ . '/vendor/autoload.php';

use PhpParser\Error;
use PhpParser\NodeDumper;
use PhpParser\ParserFactory;
use PhpParser\Node;
use PhpParser\Node\Stmt\ClassMethod_;
use PhpParser\NodeTraverser;
use PhpParser\NodeVisitorAbstract;

$file_name = './classes_examples/classes.php';

$code = file_get_contents($file_name);

$parser = (new ParserFactory())->createForNewestSupportedVersion();

// try {
//     $ast = $parser->parse($code);
// } catch (Error $error) {
//     echo "Parse error: {$error->getMessage()}\n";
//     return;
// }

// $dumper = new NodeDumper;
// // echo $dumper->dump($ast) . "\n";

// $traverser = new NodeTraverser();
// $traverser->addVisitor(new class extends NodeVisitorAbstract {
//     public function enterNode(Node $node) {
//         echo "entering node: {$node}\n";
//         // if ($node instanceof ClassMethod_) {
//         //     $node->stmts = [];
//         //     echo "Function found: {$node}\n";
//         // }
//     }
// });

// $ast = $traverser->traverse($ast);
// echo $dumper->dump($ast) . "\n";

try {
    $stmts = $parser->parse($code);
    $new_json = json_encode($stmts, JSON_PRETTY_PRINT);
    file_put_contents('./tmp/ast.json', $new_json);
} catch (PhpParser\Error $e) {
    echo 'Parse Error: ', $e->getMessage();
}
