# PostC Programming Language

PostC is a toy programming language that uses Reverse Polish Notation (RPN) for all operations. It is designed to be fully self-hosting, meaning it can compile itself.

## Features

- RPN syntax for all operations (e.g., `3 4 +` instead of `3 + 4`)
- Data types: integers, floating-point numbers, strings, booleans
- Variables with mutable and immutable bindings
- Functions with first-class support
- Control structures: conditionals (if/else), loops (while, for)
- Stack-based execution model with explicit stack manipulation operators
- Self-hosting compiler written in PostC

## Directory Structure

```
.
├── bootstrap/          # Bootstrap compiler (Python)
├── postc-compiler/     # Self-hosting compiler (PostC)
├── stdlib/             # Standard library
├── examples/           # Example programs
├── tests/              # Test programs
├── build-postc.sh      # Build script for self-hosting compiler
├── final-test.sh       # Final test script
├── test-self-hosting.sh # Test script for self-hosting
├── test.pc             # Simple test program
└── lexer.output        # Lexer output file
```

## Getting Started

### Prerequisites

- Python 3.11 or later

### Language Syntax

PostC uses Reverse Polish Notation (RPN) for all operations:

```
# Instead of 3 + 4, write:
3 4 +

# Instead of 5 * (3 + 4), write:
5 3 4 + *

# Function calls push arguments to stack, then invoke function:
5 3 add
```

### Data Types

1. **Integers** - Signed whole numbers (e.g., `123`, `-456`)
2. **Floats** - IEEE 754 double-precision floating-point numbers (e.g., `3.14`, `-2.5e10`)
3. **Strings** - Sequences of characters enclosed in double quotes (e.g., `"hello world"`)
4. **Booleans** - `true` or `false`

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

### Stack Manipulation Operators

- `dup` - Duplicate the top element
- `drop` - Remove the top element
- `swap` - Swap the top two elements
- `over` - Copy the second element to top
- `rot` - Rotate the top three elements

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

## Example Programs

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

## Building the Compiler

### Building the Self-Hosting Compiler

To build the self-hosting compiler:

```bash
./build-postc.sh
```

This will compile each component of the PostC compiler using the bootstrap compiler:
1. Compiling lexer
2. Compiling parser
3. Compiling code generator
4. Compiling main compiler

### Build Process Details

The PostC compiler is built in two stages:

**Stage 1: Bootstrap Compiler (Python)**
- Implemented in Python
- Can compile and run PostC programs
- Used to compile the self-hosting compiler

**Stage 2: Self-Hosting Compiler (PostC)**
- Implemented in PostC itself
- Compiled using the bootstrap compiler
- Can compile and run PostC programs

## Running PostC Programs

### Using the Bootstrap Compiler

To run a PostC program with the bootstrap compiler:

```bash
python3 bootstrap/postc.py <source_file>
```

### Using the Self-Hosting Compiler

After building the self-hosting compiler, you can use it to compile PostC programs.

## Testing

### Testing Self-Hosting Capability

To test that the self-hosting compiler works correctly:

```bash
./test-self-hosting.sh
```

### Final Verification

To run a complete test of the entire system:

```bash
./final-test.sh
```

## Compiler Implementation

The PostC compiler consists of the following components:

### Bootstrap Compiler (Python)

The bootstrap compiler is a complete implementation with the following components:

1. **Lexer** - Tokenizes PostC source code into a stream of tokens
2. **Parser** - Parses tokens into an Abstract Syntax Tree (AST)
3. **Code Generator** - Generates bytecode from the AST
4. **Virtual Machine** - Executes the generated bytecode

### Self-Hosting Compiler (PostC)

The self-hosting compiler is implemented in PostC itself and includes:

1. **Lexer** - Tokenizes PostC source code (`postc-compiler/lexer.pc`)
2. **Parser** - Parses tokens into an AST (`postc-compiler/parser.pc`)
3. **Code Generator** - Generates bytecode from the AST (`postc-compiler/codegen.pc`)

## Future Improvements

- Implement proper error handling and reporting
- Add support for arrays and dictionaries
- Implement a garbage collector for memory management
- Add optimization passes to the compiler
- Add support for modules and imports
- Expand the standard library with more functions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.