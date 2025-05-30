#!/usr/bin/env ruby
STDOUT.sync = true

require 'json'
require 'thread'
require_relative './engines'

requested = ARGV[0] ? ARGV[0].split(',') : ENGINES.keys

STDERR.puts "✅ #{requested.size} engine(s) ready: #{requested.join(', ')}"

def render_engine(name, tpl)
  fn = ENGINES[name]
  begin
    [name, fn.call(tpl)]
  rescue => e
    [name, "❌ #{e.message}"]
  end
end

while input = STDIN.gets
  tpl = input.strip
  results = {}
  threads = []

  requested.each do |name|
    threads << Thread.new do
      engine, output = render_engine(name, tpl)
      results[engine] = output
    end
  end

  threads.each(&:join)

  puts results.to_json
  puts "__END__"
end
