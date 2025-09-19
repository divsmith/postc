# PostC Language Specification

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
5. **Arrays** - Ordered collections of values
6. **Dictionaries** - Key-value mappings

### Variables

- Immutable bindings: `let name value`
- Mutable bindings: `var name value`

### Functions

Functions are defined with the `fn` keyword:
```
:func_name param_count
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

## Formal Grammar

```
program         ::= (statement)* EOF

statement       ::= function_def
                 |  variable_decl
                 |  expression ";"

function_def    ::= ":" IDENTIFIER NUMBER "param" block ";"

variable_decl   ::= ("let" | "var") IDENTIFIER expression ";"

expression      ::= literal
                 |  identifier
                 |  expression expression operator
                 |  expression "if" block ("else" block)? ";"
                 |  expression "while" block ";"
                 |  expression "for" block ";"
                 |  stack_op

block           ::= (statement)*

literal         ::= INTEGER
                 |  FLOAT
                 |  STRING
                 |  "true"
                 |  "false"
                 |  array_literal
                 |  dict_literal

array_literal   ::= "[" (expression ("," expression)*)? "]"

dict_literal    ::= "{" (key_value ("," key_value)*)? "}"
key_value       ::= STRING ":" expression

identifier      ::= IDENTIFIER

operator        ::= "+" | "-" | "*" | "/" | "=" | "==" | "!=" | "<" | ">" | "<=" | ">="

stack_op        ::= "dup" | "drop" | "swap" | "over" | "rot"

INTEGER         ::= [0-9]+
FLOAT           ::= [0-9]+ "." [0-9]+
STRING          ::= """ .* """
IDENTIFIER      ::= [a-zA-Z_][a-zA-Z0-9_]*
```

## Example Code

```
# A simple function that adds two numbers
:add 2 param
  +
;

# Main program
5 3 add       # Call add with 5 and 3
print         # Print the result (8)

# Fibonacci function
:fib 1 param
  dup 2 < if
    drop
  else
    dup 1 - fib
    swap 2 - fib
    +
  ;
;

# Calculate and print 10th Fibonacci number
10 fib print
```