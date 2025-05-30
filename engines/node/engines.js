'use strict';

// Preload all libraries
const ejs = require('ejs');
const pug = require('pug');
const handlebars = require('handlebars');
const nunjucks = require('nunjucks');
const mustache = require('mustache');
const artTemplate = require('art-template');
const dot = require('dot');
const squirrelly = require('squirrelly');
const { Liquid } = require('liquidjs');
const twig = require('twig');
const underscore = require('underscore');
const jsrender = require('jsrender');
const tjs = require('t.js');
const swig = require('swig');
const velocityjs = require('velocityjs');
const { Eta } = require('eta');
const hogan = require('hogan.js');
const dust = require('dustjs-linkedin');
const Ractive = require('ractive');
const jazz = require('jazz');
const LiquidNode = require('liquid-node').Engine;
const lodash = require('lodash');
const { createSSRApp } = require('vue');
const { renderToString } = require('@vue/server-renderer');

const liquidEngine = new Liquid();
const etaEngine = new Eta();
const liquidNodeEngine = new LiquidNode();

const engines = {
  ejs: async tpl => ejs.render(tpl),
  pug: async tpl => pug.render(tpl),
  handlebars: async tpl => handlebars.compile(tpl)(),
  nunjucks: async tpl => nunjucks.renderString(tpl),
  mustache_js: async tpl => mustache.render(tpl, {}),
  'art-template': async tpl => artTemplate.render(tpl),
  dot: async tpl => dot.template(tpl)({ safe: true }),
  squirrelly: async tpl => squirrelly.render(tpl),
  liquidjs: async tpl => liquidEngine.render(liquidEngine.parse(tpl), {}),
  twig_js: async tpl => twig.twig({ data: tpl }).render(),
  underscore: async tpl => underscore.template(tpl)(),
  jsrender: async tpl => jsrender.templates(tpl).render(),
  't.js': async tpl => tjs(tpl, {}),
  swig: async tpl => swig.render(tpl),
  velocityjs: async tpl => velocityjs.render(tpl),
  eta: async tpl => etaEngine.renderString(tpl, {}),
  hogan: async tpl => hogan.compile(tpl).render({}),
  dustjs: async tpl => {
    const name = `tpl_${Date.now()}`;
    dust.loadSource(dust.compile(tpl, name));
    return new Promise((resolve, reject) =>
      dust.render(name, {}, (err, out) => err ? reject(err) : resolve(out))
    );
  },
  ractive: async tpl => new Ractive({ template: tpl, data: {} }).toHTML(),
  jazz: async tpl => new Promise(resolve => {
    jazz.compile(tpl).eval({}, out => resolve(out));
  }),
  liquidnode: async tpl => liquidNodeEngine.parseAndRender(tpl, {}),
  lodash: async tpl => lodash.template(tpl)({}),
  vue3: async tpl => {
    const safeTpl = tpl.trim().startsWith('<') ? tpl : `<div>${tpl}</div>`;
    const app = createSSRApp({ template: safeTpl });
    return await renderToString(app);
  },
};

module.exports = { engines };
