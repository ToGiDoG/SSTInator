<?php
// engines/php/engines.php

use eftec\bladeone\BladeOne;
use Latte\Engine;
use Latte\Loaders\StringLoader;

require_once __DIR__ . '/vendor/autoload.php';

return [
    'twig_php' => function(string $tpl) {
        $loader = new \Twig\Loader\ArrayLoader(['tpl' => $tpl]);
        $twig   = new \Twig\Environment($loader);
        return $twig->render('tpl');
    },

    'smarty' => function(string $tpl) {
        $file = __DIR__ . '/_temp_smarty.tpl';
        file_put_contents($file, $tpl);
        $s = new \Smarty();
        $s->setTemplateDir(__DIR__)
          ->setCompileDir(__DIR__ . '/_smarty_cache');
        $out = $s->fetch('_temp_smarty.tpl');
        unlink($file);
        return $out;
    },

    'mustache' => function(string $tpl) {
        $m = new \Mustache_Engine();
        return $m->render($tpl, []);
    },

    'latte' => function(string $tpl) {
        $latte = new Engine();
        $latte->setLoader(new StringLoader());
        return $latte->renderToString($tpl, []);
    },

    'phptal' => function(string $tpl) {
        $file = __DIR__ . '/_temp_phptal.html';
        file_put_contents($file, $tpl);
        $p = new \PHPTAL($file);
        $out = $p->execute();
        unlink($file);
        return $out;
    },

    'blade' => function(string $tpl) {
        $views = __DIR__ . '/blade_views';
        $cache = __DIR__ . '/blade_cache';
        @mkdir($views);
        @mkdir($cache);
        $name = 'tpl_' . md5($tpl);
        $file = "$views/$name.blade.php";
        file_put_contents($file, $tpl);
        $blade = new BladeOne($views, $cache, BladeOne::MODE_AUTO);
        $out = $blade->run($name, []);
        unlink($file);
        return $out;
    },
];
