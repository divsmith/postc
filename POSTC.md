A toy programming language called PostC that uses reverse polish notation (RPN) for all operations. The language should be fully self-hosting, meaning it can compile itself.

Core Language Features:
- RPN syntax for all operations (e.g., '3 4 +' instead of '3 + 4')
- Data types: integers, floating-point numbers, strings, booleans
- Variables with mutable and immutable bindings using keywords like 'let' and 'var'
- Functions with first-class support (closures, higher-order functions)
- Control structures: conditionals (if/else), loops (while, for)
- Basic data structures: arrays, dictionaries/hashes
- Memory management (either garbage collection or manual allocation)
- Input/output operations (file and console)
- Error handling with exceptions or error codes
- Module system for code organization

RPN Syntax and Semantics:
- Operations follow postfix notation: operands first, then operator
- Function calls: arguments pushed to stack, then function name
- Example: '5 3 4 + *' means 5 * (3 + 4)
- Stack-based execution model with explicit stack manipulation operators:
  - dup (duplicate top element)
  - drop (remove top element)
  - swap (swap top two elements)
  - over (copy second element to top)
  - rot (rotate top three elements)
- Comments with # (to end of line)
- Whitespace-separated tokens
- Literals pushed directly to stack

Compilation Process:
1. Lexical analysis (tokenization) - convert source to token stream
2. Parsing RPN expressions into intermediate representation (bytecode)
3. Semantic analysis - type checking, scope resolution
4. Code generation - produce executable machine code for x86-64 or portable bytecode
5. Optimization passes - constant folding, dead code elimination
6. Linking - combine with standard library and other modules

Self-Hosting Requirements:
1. Bootstrap compiler written in a high-level language (Python/C) that can:
   - Parse PostC source files
   - Generate executable code or bytecode
   - Handle all language features
2. Reference implementation of PostC compiler written entirely in PostC
3. The bootstrap compiler must be able to compile the PostC compiler source
4. The compiled PostC compiler must be able to compile itself and other PostC programs
5. Standard library implemented in PostC with essential functions

Development Steps:
1. Design complete language specification with formal grammar
2. Implement bootstrap compiler in Python/C with all features
3. Write PostC compiler in PostC with equivalent functionality
4. Verify that bootstrap compiler can compile PostC compiler
5. Verify that compiled PostC compiler can compile itself
6. Create standard library in PostC (I/O, string operations, math functions)
7. Document language syntax, semantics, and provide examples

Additional Technical Details:
- Target architecture: x86-64 for native compilation or portable bytecode
- Executable format: ELF (Linux), PE (Windows), or custom bytecode
- Memory model: stack-based with heap allocation for complex data
- Calling conventions for function calls
- Runtime system requirements (GC, error handling)
- Debugging support (line number mapping, stack traces)

Example PostC Code:
```
# A simple function that adds two numbers
:add 2 param # Define function 'add' with 2 parameters
  +          # Add the two parameters
;            # End function definition

# Main program
5 3 add      # Call add with 5 and 3
print        # Print the result (8)
```

Final Deliverables:
1. Complete language specification document
2. Bootstrap compiler implementation in Python or C
3. Self-hosting PostC compiler written in PostC
4. Standard library in PostC
5. Examples and documentation
6. Build scripts and instructions for compiling the self-hosting compiler

With this specification, implement a complete self-hosting PostC compiler that can compile itself.