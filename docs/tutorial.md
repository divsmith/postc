# PostC Tutorial

Welcome to the PostC programming language tutorial! This guide will take you from basic concepts to advanced features through hands-on examples.

## Table of Contents

- [Getting Started](#getting-started)
- [Basic Concepts](#basic-concepts)
- [Variables and Functions](#variables-and-functions)
- [Control Structures](#control-structures)
- [Arrays](#arrays)
- [Dictionaries](#dictionaries)
- [String Operations](#string-operations)
- [File I/O](#file-io)
- [Building Complete Programs](#building-complete-programs)
- [Best Practices](#best-practices)

## Getting Started

### Your First PostC Program

Let's start with the traditional "Hello, World!" program:

```
# Hello World in PostC
"Hello, World!" print
```

**Explanation:**
- `"Hello, World!"` pushes the string onto the stack
- `print` consumes the string from the stack and prints it

**To run this program:**
```bash
echo '"Hello, World!" print' > hello.pc
python3 src/bootstrap/postc.py run hello.pc
```

### Basic Arithmetic

PostC uses Reverse Polish Notation (RPN) for all operations:

```
# Basic arithmetic: 3 + 4 * 5
3 4 5 * +
```

**Explanation:**
- `3` pushes 3 onto the stack
- `4` pushes 4 onto the stack
- `5` pushes 5 onto the stack
- `*` multiplies 4 and 5, leaving 20 on the stack
- `+` adds 3 and 20, leaving 23 on the stack

**Exercise:** Try different arithmetic expressions:
```
# Try these:
10 2 3 + *    # Should equal 50
15 3 / 2 +   # Should equal 7
```

## Basic Concepts

### The Stack

PostC is a stack-based language. Everything operates on a stack:

```
# Stack operations
5 dup         # Stack: [5, 5]
3 4 swap      # Stack: [4, 3]
1 2 3 rot     # Stack: [2, 3, 1]
```

### Data Types

PostC supports several data types:

```
# Integers
42
-17

# Floats
3.14
-2.5e10

# Strings
"Hello"
"World"

# Booleans
true
false
```

## Variables and Functions

### Variables

PostC has two types of variable bindings:

```
# Immutable variable (cannot be changed)
42 let answer

# Mutable variable (can be changed)
10 var counter
```

### Functions

Functions in PostC use RPN syntax:

```
# Define a function that adds two numbers
:add 2 param
  +
;

# Use the function
5 3 add print    # Prints: 8
```

**More complex function example:**
```
# Function to calculate square
:square 1 param
  dup *
;

# Use the function
5 square print   # Prints: 25
16 square print  # Prints: 256
```

## Control Structures

### Conditional Statements

```
# Basic if/else
x 10 > if
  "x is greater than 10" print
else
  "x is 10 or less" print
;
```

### Loops

```
# While loop - countdown from 5
5 var count
count 0 > while
  count print
  count 1 - var count
;

# For loop - also countdown
5 for
  dup print
;
```

## Arrays

Arrays in PostC are dynamic and can store any data type:

### Creating and Using Arrays

```
# Create an array of size 5
5 create_array

# Store values at specific indices
42 0 store_array
17 1 store_array
99 2 store_array

# Load and print values
0 load_array print    # Prints: 42
1 load_array print    # Prints: 17
2 load_array print    # Prints: 99

# Get array length
array_length print    # Prints: 5
```

### Array Example Program

```
# Array demonstration program
:create_and_use_array 0 param
  # Create array
  3 create_array

  # Store squares of indices
  0 dup dup * 0 store_array    # Store 0^2 = 0 at index 0
  1 dup dup * 1 store_array    # Store 1^2 = 1 at index 1
  2 dup dup * 2 store_array    # Store 2^2 = 4 at index 2

  # Print all values
  0 load_array print
  1 load_array print
  2 load_array print

  # Print array length
  array_length print
;

# Run the program
create_and_use_array
```

## Dictionaries

Dictionaries store key-value pairs and allow fast lookups:

### Creating and Using Dictionaries

```
# Create a dictionary
create_dict

# Store key-value pairs
"name" "PostC" store_dict
"version" "1.0" store_dict
"complete" "true" store_dict

# Load values by key
"name" load_dict print        # Prints: PostC
"version" load_dict print     # Prints: 1.0

# Check if keys exist
"turing_complete" dict_has_key print  # Prints: false
"name" dict_has_key print              # Prints: true

# Get dictionary size
dict_length print             # Prints: 3
```

### Dictionary Example Program

```
# Dictionary demonstration
:create_config_dict 0 param
  # Create configuration dictionary
  create_dict

  # Store configuration values
  "host" "localhost" store_dict
  "port" "8080" store_dict
  "debug" "true" store_dict

  # Print configuration
  "Configuration:" print
  "host" load_dict print
  "port" load_dict print
  "debug" load_dict print

  # Check if SSL is configured
  "ssl" dict_has_key print
;

# Run the program
create_config_dict
```

## String Operations

PostC provides comprehensive string manipulation:

### String Functions

```
# String concatenation
"Hello " "World!" string_concat print    # Prints: Hello World!

# String length
"Hello World!" string_length print       # Prints: 13

# Substring extraction
"Hello World!" 6 5 string_substring print  # Prints: World

# Find substring
"Hello World!" "World" string_indexof print  # Prints: 6
```

### String Processing Example

```
# String processing demonstration
:process_strings 0 param
  # Create and manipulate strings
  "Hello" " " "World" string_concat string_concat print

  # Analyze a string
  "Programming in PostC is fun!" var message
  message string_length print

  # Extract parts
  message 0 11 string_substring print    # "Programming"
  message 15 6 string_substring print    # "PostC"
  message 25 4 string_substring print    # "fun"
;

# Run the program
process_strings
```

## File I/O

PostC supports file input operations:

### Reading Files

```
# Read a file
"README.md" read_file print

# Read user input
"Enter your name: " print
read_stdin print
```

### File Processing Example

```
# File reading demonstration
:read_example_file 0 param
  # Try to read this source file
  "hello.pc" read_file print
;

# Run the program
read_example_file
```

## Building Complete Programs

Now let's build some complete programs that combine multiple features:

### Program 1: Simple Calculator

```
# Simple calculator that adds two numbers from user input
:calculator 0 param
  "Enter first number: " print
  read_stdin          # This would need actual input in real scenario

  "Enter second number: " print
  read_stdin          # This would need actual input in real scenario

  + print
;

# Run calculator
calculator
```

### Program 2: Array Statistics

```
# Calculate basic statistics for an array of numbers
:create_stats_array 0 param
  # Create array with some numbers
  5 create_array

  # Store values
  10 0 store_array
  20 1 store_array
  30 2 store_array
  15 3 store_array
  25 4 store_array

  # Sum all values
  0 load_array
  1 load_array +
  2 load_array +
  3 load_array +
  4 load_array +

  # Calculate average (sum / count)
  5 /

  "Average: " print
  print
;

# Run statistics program
create_stats_array
```

### Program 3: Student Gradebook (Dictionary-based)

```
# Simple gradebook using dictionary
:create_gradebook 0 param
  # Create gradebook dictionary
  create_dict

  # Add student grades
  "Alice" "95" store_dict
  "Bob" "87" store_dict
  "Charlie" "92" store_dict
  "Diana" "78" store_dict

  # Print all grades
  "Gradebook:" print
  "Alice" load_dict print
  "Bob" load_dict print
  "Charlie" load_dict print
  "Diana" load_dict print

  # Calculate class average
  "Alice" load_dict "87" +    # Alice + Bob
  "Charlie" load_dict +       # + Charlie
  "Diana" load_dict +         # + Diana
  4 /                         # Divide by 4 students

  "Class Average: " print
  print
;

# Run gradebook program
create_gradebook
```

### Program 4: Text File Analyzer

```
# Analyze a text file
:analyze_file 1 param
  # Load filename from parameter
  read_file

  # Count characters (approximate)
  string_length
  "File contains " print
  print
  " characters" print
;

# This would need a real filename parameter
"README.md" analyze_file
```

## Best Practices

### 1. Comment Your Code
```postc
# Calculate fibonacci number
:fib 1 param
  # Base case
  dup 2 < if
    drop
  else
    # Recursive case
    dup 1 - fib
    swap 2 - fib
    +
  ;
;
```

### 2. Use Descriptive Names
```postc
# Good
:calculate_average 1 param
:student_gradebook 0 param

# Avoid
:f 1 param
:x 0 param
```

### 3. Break Complex Programs into Functions
```postc
# Good - modular approach
:load_data 0 param
  # Load data into array
;

:calculate_stats 0 param
  # Calculate statistics
;

:display_results 0 param
  # Display results
;

# Bad - one large function
:main 0 param
  # Everything mixed together
;
```

### 4. Use Arrays and Dictionaries Appropriately
- Use arrays for ordered collections of similar items
- Use dictionaries for key-value associations
- Choose the right data structure for your problem

### 5. Test Your Programs
```postc
# Test your functions
:test_program 0 param
  # Test cases
  5 square 25 == if
    "Square test passed" print
  else
    "Square test failed" print
  ;
;
```

## Next Steps

Now that you've learned the basics:

1. **Practice**: Modify the examples and create your own programs
2. **Explore**: Look at the example programs in the `examples/` directory
3. **Reference**: Use the [Language Reference](language-reference.md) for detailed information
4. **Build**: Create more complex programs combining multiple features

## Common Patterns

### Input Processing
```postc
# Process user input
"Enter a number: " print
read_stdin          # Get input
# Process the input...
```

### Data Transformation
```postc
# Transform array data
array_length for
  i load_array square i store_array  # Square each element
;
```

### Conditional Logic
```postc
# Complex conditions
x 0 > y 10 < and if
  "x > 0 and y < 10" print
else
  "Other cases" print
;
```

Happy coding with PostC! 🎉