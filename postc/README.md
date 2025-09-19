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
postc/
├── bootstrap/          # Bootstrap compiler (Python)
├── postc-compiler/     # Self-hosting compiler (PostC)
├── stdlib/             # Standard library
├── examples/           # Example programs
├── docs/               # Documentation
├── build-postc.sh      # Build script for self-hosting compiler
└── test-self-hosting.sh # Test script for self-hosting
```

## Getting Started

### Prerequisites

- Python 3.11 or later

### Building the Bootstrap Compiler

The bootstrap compiler is already implemented in Python and ready to use.

### Building the Self-Hosting Compiler

To build the self-hosting compiler:

```bash
./build-postc.sh
```

This will compile each component of the PostC compiler using the bootstrap compiler.

### Running PostC Programs

To run a PostC program with the bootstrap compiler:

```bash
python3 bootstrap/build.py <source_file>
```

### Testing Self-Hosting

To test that the self-hosting compiler works correctly:

```bash
./test-self-hosting.sh
```

## Language Syntax

PostC uses Reverse Polish Notation (RPN) for all operations:

```
# Instead of 3 + 4, write:
3 4 +

# Instead of 5 * (3 + 4), write:
5 3 4 + *

# Function calls push arguments to stack, then invoke function:
5 3 add
```

### Example Program

```
# A simple function that adds two numbers
:add 2 param
  +
;

# Main program
5 3 add      # Call add with 5 and 3
print        # Print the result (8)
```

## Documentation

- [Language User Guide](docs/user-guide.md) - Syntax, semantics, and examples
- [Compiler Implementation](docs/compiler.md) - Implementation details

## Standard Library

PostC includes a standard library with basic functions for arithmetic, I/O, and stack manipulation. See [stdlib/std.pc](stdlib/std.pc) for details.

## Examples

See the [examples/](examples/) directory for sample PostC programs.

## Future Improvements

- Implement proper error handling and reporting
- Add support for arrays and dictionaries
- Implement a garbage collector for memory management
- Add optimization passes to the compiler
- Add support for modules and imports