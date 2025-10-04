# PostC Programming Language

PostC is a toy programming language that uses Reverse Polish Notation (RPN) for all operations. It is designed to be fully self-hosting, meaning it can compile itself.

## Features

- **TURING COMPLETE** - Full computational power with arrays, dictionaries, and I/O operations
- RPN syntax for all operations (e.g., `3 4 +` instead of `3 + 4`)
- Data types: integers, floating-point numbers, strings, booleans, arrays, dictionaries
- Variables with mutable and immutable bindings
- Functions with first-class support
- Control structures: conditionals (if/else), loops (while, for)
- Stack-based execution model with explicit stack manipulation operators
- File I/O operations for reading and writing files
- String manipulation functions (concatenation, substring, length, search)
- Comprehensive standard library with arithmetic, comparison, and utility functions
- Self-hosting compiler written in PostC

## Directory Structure

```
.
├── src/
│   ├── bootstrap/      # Bootstrap compiler (Python)
│   │   ├── compiler/   # Compiler components
│   │   ├── vm/         # Virtual Machine
│   │   ├── wasm/       # WebAssembly target
│   │   └── postc.py    # Main entry point
│   └── compiler/       # Self-hosting compiler (PostC)
├── stdlib/             # Standard library
├── examples/           # Example programs
├── tests/              # Test programs
├── docs/               # Documentation
└── Makefile            # Build and test script
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- Make

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
5. **Arrays** - Dynamic arrays that can store multiple values (e.g., `[1, 2, 3, 4, 5]`)
6. **Dictionaries** - Key-value data structures for associative storage (e.g., `{"name": "PostC", "version": "1.0"}`)

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

PostC includes a comprehensive standard library with functions organized by category:

### Arithmetic Functions
- `add` - Add two numbers
- `sub` - Subtract two numbers
- `mul` - Multiply two numbers
- `div` - Divide two numbers
- `square` - Square a number
- `cube` - Cube a number
- `abs` - Absolute value
- `max` - Return the maximum of two numbers
- `min` - Return the minimum of two numbers

### Comparison Functions
- `eq` - Check equality
- `ne` - Check inequality
- `lt` - Less than comparison
- `gt` - Greater than comparison
- `le` - Less than or equal comparison
- `ge` - Greater than or equal comparison

### Stack Manipulation Functions
- `dup` - Duplicate the top element
- `drop` - Remove the top element
- `swap` - Swap the top two elements
- `over` - Copy the second element to top
- `rot` - Rotate the top three elements

### Boolean Logic Functions
- `not` - Logical negation
- `and` - Logical AND
- `or` - Logical OR

### String Functions
- `string_length` - Get string length
- `string_concat` - Concatenate two strings
- `string_substring` - Extract substring (start, length)
- `string_indexof` - Find index of substring

### Array Functions
- `create_array` - Create a new array with given size
- `store_array` - Store value at array index
- `load_array` - Load value from array index
- `array_length` - Get array length

### Dictionary Functions
- `create_dict` - Create a new dictionary
- `store_dict` - Store key-value pair in dictionary
- `load_dict` - Load value for given key from dictionary
- `dict_has_key` - Check if dictionary contains key
- `dict_length` - Get dictionary size

### I/O Functions
- `print` - Print a value to stdout
- `read_file` - Read contents of a file
- `read_stdin` - Read from standard input

### Control Flow Helpers
- `if_else` - Execute one of two branches based on condition
- `while_do` - Execute body while condition is true

### Utility Functions
- `identity` - Return input unchanged
- `const` - Return constant value
- `apply` - Apply function to argument

## Example Programs

See the `examples/` directory for sample PostC programs.

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

### Array Operations
```
# Create an array and store values
5 create_array
42 0 store_array
17 1 store_array
99 2 store_array

# Load and print values
0 load_array print  # Prints: 42
1 load_array print  # Prints: 17
2 load_array print  # Prints: 99
array_length print  # Prints: 5
```

### Dictionary Operations
```
# Create a dictionary
create_dict

# Store key-value pairs
"name" "PostC" store_dict
"version" "1.0" store_dict

# Load and print values
"name" load_dict print      # Prints: PostC
"version" load_dict print   # Prints: 1.0

# Check if keys exist
"turing_complete" dict_has_key print  # Prints: false
"name" dict_has_key print              # Prints: true
```

### String Operations
```
# Concatenate strings
"Hello " "World!" string_concat print  # Prints: Hello World!

# Get string length
"Hello World!" string_length print     # Prints: 13

# Extract substring
"Hello World!" 6 5 string_substring print  # Prints: World

# Find substring index
"Hello World!" "World" string_indexof print  # Prints: 6
```

### File I/O Operations
```
# Read and print file contents
"README.md" read_file print

# Read from standard input
read_stdin print
```

## Building and Testing

You can use the `Makefile` to build and test the compiler.

### Build the Self-Hosting Compiler

To build the self-hosting compiler:

```bash
make build
```

This will compile each component of the PostC compiler using the bootstrap compiler.

### Run Tests

To run the test suite:

```bash
make test
```

This will run a series of tests to ensure the compiler is working correctly.

### Run a Specific Example

To run a specific example, use the `run-example` target:

```bash
make run-example EXAMPLE=hello
```

This will run the `examples/hello.pc` program.

### Compile to Different Targets

The bootstrap compiler now supports multiple compilation targets:

1. **Bytecode** (default):
   ```bash
   python3 src/bootstrap/postc.py compile <source_file> [output_file]
   ```

2. **Run bytecode**:
   ```bash
   python3 src/bootstrap/postc.py run <bytecode_file>
   ```

3. **WebAssembly**:
   ```bash
   python3 src/bootstrap/postc.py compile <source_file> <bytecode_file>
   python3 src/bootstrap/postc.py wasm <bytecode_file> <wasm_output_file>
   ```

See `docs/targets.md` for more detailed information about compilation targets.

## Compiler Implementation

The PostC compiler consists of the following components:

### Bootstrap Compiler (Python)

The bootstrap compiler is now separated into distinct components:

1. **Lexer** - Tokenizes PostC source code into a stream of tokens
2. **Parser** - Parses tokens into an Abstract Syntax Tree (AST)
3. **Code Generator** - Generates bytecode from the AST
4. **Virtual Machine** - Executes the generated bytecode (now a separate component)
5. **WebAssembly Target** - Generates WebAssembly code from bytecode

All components are written in Python and located in `src/bootstrap/`.

### Self-Hosting Compiler (PostC)

The self-hosting compiler is implemented in PostC itself and includes:

1. **Lexer** - Tokenizes PostC source code (`src/compiler/lexer.pc`)
2. **Parser** - Parses tokens into an AST (`src/compiler/parser.pc`)
3. **Code Generator** - Generates bytecode from the AST (`src/compiler/codegen.pc`)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
