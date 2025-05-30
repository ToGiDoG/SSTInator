#!/usr/bin/env node
'use strict';

console.error("🔄 Loading NodeJS template engines...");

const { engines: allEngines } = require('./engines');

const enabled = process.argv[2]
  ? process.argv[2].split(',').map(e => e.trim().toLowerCase())
  : null;

const engines = enabled
  ? Object.fromEntries(Object.entries(allEngines).filter(([k]) => enabled.includes(k)))
  : allEngines;

// Force initialization of all engines with dummy input
async function preloadEngines() {
  const dummy = 'x';
  const preloadTasks = Object.entries(engines).map(async ([name, fn]) => {
    try {
      await fn(dummy);
    } catch (_) {
      // ignore errors during preloading
    }
  });
  await Promise.allSettled(preloadTasks);
}

(async () => {
  await preloadEngines();
  console.error(`✅ ${Object.keys(engines).length} engine(s) ready: ${Object.keys(engines).join(', ')}`);
})();

const readline = require('readline');
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', async (tpl) => {
  tpl = tpl.trim();

  const tasks = Object.entries(engines).map(async ([name, fn]) => {
    try {
      const result = await fn(tpl);
      return [name, result];
    } catch (err) {
      return [name, `❌ ${err.message}`];
    }
  });

  const resultsArray = await Promise.allSettled(tasks);
  const results = Object.fromEntries(resultsArray.map(p => p.value));

  console.log(JSON.stringify(results));
  console.log("__END__");
});
