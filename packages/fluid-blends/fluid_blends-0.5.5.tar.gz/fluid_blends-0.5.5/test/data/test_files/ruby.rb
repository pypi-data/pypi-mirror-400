# Imports and Libraries
require "json", "net/http", "uri"
require 'json'
require_relative 'another_file'
load 'script.rb'

# Constants and Variables
CONST = 42
$global_var = "Hello"
@instance_var = [1, 2, 3]
@@class_var = { key: :value }
local_var = /regex/

# Classes and Modules
module ExampleModule
  class ExampleClass < SuperClass
    include IncludedModule
    extend ExtendedModule

    def initialize(param1, param2 = 100, *args, **kwargs, &block)
      @param1 = param1
      @param2 = param2
      @args = args
      @kwargs = kwargs
      block.call if block_given?
    end

    def example_method(a, b: 2, **opts)
      result = a + b
      return result if result > 10
      raise "Error" unless opts[:allow]
    rescue StandardError => e
      puts e.message
    ensure
      puts "Finalizing"
    end

    def self.class_method
      yield if block_given?
    end
  end
end

# Expressions and Literals
lambda_func = ->(x) { x * 2 }
array = [1, "string", :symbol, nil, true, false]
hash = { key1: "value1", "key2" => 2 }

# Control Structures
if array.size > 3
  puts "Long"
elsif array.empty?
  puts "Empty"
else
  puts "Medium"
  hash = { key1: "value1", "key2" => 2 }
  range = (1...10)
  puts "Test else body"
end

while false; puts "Never"; end
for i in 1..5 do puts i end
5.times { |n| puts n }
case CONST
when 1 then puts "One"
when 42 then puts "Answer"
else puts "Other"
end

# Methods and Blocks
def with_block; yield "data" if block_given?; end
with_block { |x| puts x }

# Regular Expressions and Ranges
expression = /\d+/
range = (1...10)

# Pattern Matching
hash => { key1: extracted_value }
puts extracted_value

# Threads and Concurrency
thread = Thread.new { puts "Running in a thread" }
thread.join

# Fibers
fiber = Fiber.new do
  Fiber.yield "First pause"
  "Second execution"
end
puts fiber.resume
puts fiber.resume

# Refinements
module StringRefinement
  refine String do
    def shout
      upcase + "!!!"
    end
  end
end

using StringRefinement
puts "hello".shout

# Alias and Method Redefinition
class ExampleClass
  alias method_alias example_method
end

# Singleton Methods
obj = Object.new
def obj.unique_method
  puts "Only in this instance"
end
obj.unique_method

# Singleton class
a = Object.new
class << a; end

b = Object.new
class << b
  def hello
    puts "Hello from singleton class!"
  end
end

b.hello

# While Modifier
puts "Hello" while false

module SomeModule
  module InnerModule
      class MyClass
          CONSTANT = 4
      end
  end
end

# Scope resolution operator
SomeModule::InnerModule::MyClass::CONSTANT
