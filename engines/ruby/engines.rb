# engines/ruby/engines.rb

require 'erb'
require 'erubi'
require 'erubis'
require 'haml'
require 'slim'
require 'liquid'
require 'mustache'

ENGINES = {
  'erb' => ->(tpl) {
    ERB.new(tpl).result(binding)
  },

  'erubi' => ->(tpl) {
    engine = Erubi::Engine.new(tpl, escape: false)
    eval(engine.src, binding)
  },

  'erubis' => ->(tpl) {
    Erubis::Eruby.new(tpl).result(binding)
  },

  'haml' => ->(tpl) {
    Haml::Template.new { tpl }.render(Object.new, {})
  },

  'slim' => ->(tpl) {
    Slim::Template.new { tpl }.render
  },

  'liquid' => ->(tpl) {
    Liquid::Template.parse(tpl).render
  },

  'mustache' => ->(tpl) {
    Mustache.render(tpl, {})
  }
}
