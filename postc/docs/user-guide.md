# PostC Programming Language Documentation

## Overview

PostC is a toy programming language that uses Reverse Polish Notation (RPN) for all operations. It is designed to be fully self-hosting, meaning it can compile itself.

## Syntax and Semantics

### Tokens

PostC source code consists of whitespace-separated tokens:
- Integer literals: `123`, `-456`
- Floating-point literals: `3.14`, `-2.5e10`
- String literals: `"hello world"`
- Boolean literals: `true`, `false`
- Identifiers: `variable_name`, `function_name`
- Operators: `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- Keywords: `let`, `var`, `if`, `else`, `while`, `for`, `fn`, `return`, `print`
- Comments: `#` to end of line
- Delimiters: `(`, `)`, `{`, `}`, `[`, `]`, `;`

### RPN Syntax

All operations in PostC follow postfix notation:
- Instead of `3 + 4`, write `3 4 +`
- Instead of `5 * (3 + 4)`, write `5 3 4 + *`
- Function calls push arguments to stack, then invoke function: `5 3 add`

### Stack Manipulation Operators

- `dup` - Duplicate the top element
- `drop` - Remove the top element
- `swap` - Swap the top two elements
- `over` - Copy the second element to top
- `rot` - Rotate the top three elements

### Data Types

1. **Integers** - Signed whole numbers
2. **Floats** - IEEE 754 double-precision floating-point numbers
3. **Strings** - Sequences of characters enclosed in double quotes
4. **Booleans** - `true` or `false`
5. **Arrays** - Ordered collections of values (planned)
6. **Dictionaries** - Key-value mappings (planned)

### Variables

- Immutable bindings: `let name value`
- Mutable bindings: `var name value`

### Functions

Functions are defined with the `:` keyword:
```
:func_name param_count param
  # function body
;
```

Example:
```
:add 2 param
  +
;
```

### Control Structures

#### Conditionals
```
condition if
  # then branch
else
  # else branch
;
```

#### Loops
```
# While loop
condition while
  # loop body
;
```

```
# For loop (countdown)
count for
  # loop body
;
```

### Comments

Single-line comments start with `#` and continue to the end of the line.

## Standard Library

PostC includes a standard library with basic functions:

### Arithmetic Functions
- `add` - Add two numbers
- `sub` - Subtract two numbers
- `mul` - Multiply two numbers
- `div` - Divide two numbers

### I/O Functions
- `print` - Print a value to stdout

### Stack Manipulation Functions
- `dup` - Duplicate the top element
- `drop` - Remove the top element
- `swap` - Swap the top two elements
- `over` - Copy the second element to top
- `rot` - Rotate the top three elements

## Example Code

### Hello World
```
"Hello, World!" print
```

### Fibonacci Sequence
```
# Function to calculate the nth Fibonacci number
:fib 1 param
  dup 2 < if
    # Base case: n < 2, return n
    drop
  else
    # Recursive case: fib(n-1) + fib(n-2)
    dup 1 - fib
    swap 2 - fib
    +
  ;
;

# Calculate and print 10th Fibonacci number
10 fib print
```

### Simple Calculator
```
# Add two numbers
:add 2 param
  +
;

# Multiply two numbers
:mul 2 param
  *
;

# Calculate (5 + 3) * 2
5 3 add 2 mul print  # Outputs: 16
```