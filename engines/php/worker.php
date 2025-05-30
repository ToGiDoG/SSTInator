#!/usr/bin/env php
<?php

while (ob_get_level()) { ob_end_flush(); }
ob_implicit_flush(true);

require_once __DIR__ . '/vendor/autoload.php';
$engineFns = require __DIR__ . '/engines.php';

$requested = isset($argv[1])
    ? explode(',', strtolower($argv[1]))
    : array_keys($engineFns);

fwrite(STDERR, "✅ " . count($requested) . " engine(s) ready: " . implode(', ', $requested) . "\n");

function render_engine(string $name, string $tpl, callable $fn): string {
    try {
        return $fn($tpl);
    } catch (Throwable $e) {
        return '❌ ' . $e->getMessage();
    }
}

while (($line = fgets(STDIN)) !== false) {
    $template = trim($line);
    $results = [];

    foreach ($requested as $name) {
        $fn = $engineFns[$name];
        $results[$name] = render_engine($name, $template, $fn);
    }

    fwrite(STDOUT, json_encode($results, JSON_UNESCAPED_UNICODE) . "\n");
    fwrite(STDOUT, "__END__\n");
    fflush(STDOUT);
}
