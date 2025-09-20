# PostC Programming Language Project

## Project Overview

PostC is a toy programming language that uses Reverse Polish Notation (RPN) for all operations. The language is designed to be fully self-hosting, meaning it can compile itself. It was created by Parker Smith and is distributed under the MIT License.

### Key Features

- RPN syntax for all operations (e.g., `3 4 +` instead of `3 + 4`)
- Data types: integers, floating-point numbers, strings, booleans
- Variables with mutable and immutable bindings
- Functions with first-class support
- Control structures: conditionals (if/else), loops (while, for)
- Stack-based execution model with explicit stack manipulation operators
- Self-hosting compiler written in PostC

### Project Structure

```
/app/
├── LICENSE                 # MIT License
├── POSTC.md                # Project specification and requirements
├── timeout.sh              # Timeout script (utility)
└── postc/                  # Main PostC project directory
    ├── BUILDING.md         # Build instructions
    ├── README.md           # Project documentation
    ├── build-postc.sh      # Build script for self-hosting compiler
    ├── final-test.sh       # Final test script
    ├── test-self-hosting.sh # Test script for self-hosting
    ├── test.pc             # Simple test program
    ├── bootstrap/          # Bootstrap compiler (Python)
    │   └── postc.py        # Main bootstrap compiler implementation
    ├── postc-compiler/     # Self-hosting compiler (PostC)
    │   ├── lexer.pc        # Lexer component
    │   ├── parser.pc       # Parser component
    │   ├── codegen.pc      # Code generator component
    │   └── compiler.pc     # Main compiler driver
    ├── stdlib/             # Standard library
    │   └── std.pc          # Standard library functions
    ├── examples/           # Example PostC programs
    ├── docs/               # Documentation
    │   ├── compiler.md     # Compiler implementation documentation
    │   ├── specification.md # Language specification
    │   └── user-guide.md   # User guide
    └── ...
```

## Language Syntax and Semantics

PostC uses Reverse Polish Notation (RPN) for all operations:
- Instead of `3 + 4`, write `3 4 +`
- Instead of `5 * (3 + 4)`, write `5 3 4 + *`
- Function calls push arguments to stack, then invoke function: `5 3 add`

### Data Types
1. Integers - Signed whole numbers
2. Floats - IEEE 754 double-precision floating-point numbers
3. Strings - Sequences of characters enclosed in double quotes
4. Booleans - `true` or `false`

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

## Building and Running

### Prerequisites
- Python 3.11 or later

### Building the Bootstrap Compiler
The bootstrap compiler is already implemented in Python and ready to use.

### Building the Self-Hosting Compiler
To build the self-hosting compiler:
```bash
./build-postc.sh
```

This script compiles each component of the PostC compiler using the bootstrap compiler:
1. Compiling lexer
2. Compiling parser
3. Compiling code generator
4. Compiling main compiler

### Running PostC Programs
To run a PostC program with the bootstrap compiler:
```bash
python3 bootstrap/postc.py <source_file>
```

### Testing Self-Hosting
To test that the self-hosting compiler works correctly:
```bash
./test-self-hosting.sh
```

## Development Components

### Bootstrap Compiler (Python)
Located in `postc/bootstrap/postc.py`, this is a complete compiler that can:
1. Lexical analysis (tokenization)
2. Parsing tokens into an Abstract Syntax Tree (AST)
3. Code generation from AST to bytecode
4. Virtual Machine execution of bytecode

### Self-Hosting Compiler (PostC)
The self-hosting compiler is written in PostC itself and consists of:
1. `lexer.pc` - Tokenizes PostC source code
2. `parser.pc` - Parses tokens into an AST
3. `codegen.pc` - Generates bytecode from the AST
4. `compiler.pc` - Main compiler driver

## Standard Library
PostC includes a standard library with basic functions in `postc/stdlib/std.pc`:
- Arithmetic: `add`, `sub`, `mul`, `div`
- I/O: `print`
- Stack manipulation: `dup`, `drop`, `swap`, `over`, `rot`

## Examples
See the `postc/examples/` directory for sample PostC programs:
- hello.pc - Simple "Hello, World!" program
- fibonacci.pc - Recursive Fibonacci implementation
- factorial.pc - Recursive factorial calculation
- calculator.pc - Simple calculator functions

## Development Process

The PostC compiler is built in two stages:

1. **Stage 1: Bootstrap Compiler (Python)**
   - Implemented in Python
   - Can compile and run PostC programs
   - Used to compile the self-hosting compiler

2. **Stage 2: Self-Hosting Compiler (PostC)**
   - Implemented in PostC itself
   - Compiled using the bootstrap compiler
   - Can compile and run PostC programs

## Future Improvements
- Implement proper error handling and reporting
- Add support for arrays and dictionaries
- Implement a garbage collector for memory management
- Add optimization passes to the compiler
- Add support for modules and imports