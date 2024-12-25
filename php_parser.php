<?php
require_once __DIR__ . '/vendor/autoload.php';

use PhpParser\Error;
use PhpParser\NodeDumper;
use PhpParser\ParserFactory;
use PhpParser\Node;
use PhpParser\Node\Stmt\ClassMethod_;
use PhpParser\NodeTraverser;
use PhpParser\NodeVisitorAbstract;

$file_name = $argv[1];
$json_output = $argv[2];

$code = file_get_contents($file_name);

$parser = (new ParserFactory())->createForNewestSupportedVersion();

try {
    $stmts = $parser->parse($code);
    $new_json = json_encode($stmts, JSON_PRETTY_PRINT);
    file_put_contents($json_output, $new_json);
} catch (PhpParser\Error $e) {
    echo 'Parse Error: ', $e->getMessage();
}