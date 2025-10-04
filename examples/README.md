# PostC Examples

This directory contains example programs written in PostC, organized by feature category.

## Basic Examples

- `hello.pc`: A "Hello, World!" program demonstrating basic output.
- `calculator.pc`: A simple calculator demonstrating arithmetic operations.
- `variables.pc`: Demonstrates the use of mutable and immutable variables.

## Mathematical Examples

- `factorial.pc`: Calculates the factorial of a number using recursive functions.
- `fibonacci.pc`: Calculates the nth Fibonacci number using recursive functions.

## Advanced Feature Examples

- `working-features.pc`: A collection of small programs testing various language features including control structures, functions, and stack operations.
- `turing-complete-features.pc`: **Comprehensive demonstration of PostC's Turing complete capabilities**, showcasing:
  - Array creation, storage, and retrieval operations
  - Dictionary key-value storage and lookup operations
  - File I/O operations for reading files
  - String manipulation functions (concatenation, length, substring, search)
  - Integration of all advanced features in a complete program

## Example Categories by Feature

### Basic I/O and Variables
- `hello.pc` - Basic string output
- `variables.pc` - Variable declarations and usage

### Arithmetic and Math
- `calculator.pc` - Basic arithmetic operations
- `factorial.pc` - Recursive mathematical functions
- `fibonacci.pc` - Recursive sequences

### Advanced Data Structures
- `turing-complete-features.pc` - Arrays, dictionaries, strings, file I/O

### Language Features
- `working-features.pc` - Control structures, functions, stack operations

## Running Examples

To run an example, use the `run-example` target in the `Makefile`:

```bash
make run-example EXAMPLE=hello
```

Available examples: `hello`, `calculator`, `factorial`, `fibonacci`, `variables`, `working-features`, `turing-complete-features`

## Learning Path

For new PostC programmers, we recommend following this learning sequence:

1. **Start with basics**: `hello.pc` → `variables.pc` → `calculator.pc`
2. **Learn functions**: `factorial.pc` → `fibonacci.pc`
3. **Explore features**: `working-features.pc`
4. **Master advanced features**: `turing-complete-features.pc`

Each example builds on previous concepts and demonstrates increasingly complex PostC features.
