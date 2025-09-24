# PostC Virtual Machine

The PostC Virtual Machine (VM) is a stack-based virtual machine that executes compiled PostC bytecode. It has been separated from the bootstrap compiler to allow for independent execution of compiled programs.

## Architecture

The VM is designed as a stack-based machine with the following components:

1. **Stack**: A stack data structure that holds values during execution
2. **Call Stack**: Manages function calls using frames
3. **Constants Pool**: Stores constant values referenced by index
4. **Functions Table**: Maps function names to their compiled instructions

## Instruction Set

The VM supports a comprehensive set of opcodes for various operations:

### Constants
- `LOAD_CONST`: Load a constant value onto the stack
- `LOAD_TRUE`: Load boolean true onto the stack
- `LOAD_FALSE`: Load boolean false onto the stack
- `LOAD_STRING`: Load a string constant onto the stack

### Variables
- `LOAD_VAR`: Load a variable's value onto the stack
- `STORE_VAR`: Store the top stack value in a variable

### Stack Operations
- `DUP`: Duplicate the top element
- `DROP`: Remove the top element
- `SWAP`: Swap the top two elements
- `OVER`: Copy the second element to the top
- `ROT`: Rotate the top three elements

### Arithmetic Operations
- `ADD`: Add the top two elements
- `SUB`: Subtract the top element from the second element
- `MUL`: Multiply the top two elements
- `DIV`: Divide the second element by the top element

### Comparison Operations
- `EQ`: Check equality
- `NE`: Check inequality
- `LT`: Check less than
- `GT`: Check greater than
- `LE`: Check less than or equal
- `GE`: Check greater than or equal

### Control Flow
- `JUMP`: Unconditional jump to an instruction
- `JUMP_IF_FALSE`: Conditional jump if the top element is false
- `CALL`: Call a function
- `RETURN`: Return from a function
- `HALT`: Halt program execution

### I/O
- `PRINT`: Print the top stack element

## Usage

To run a compiled PostC program:

```bash
python3 src/bootstrap/postc.py run <bytecode_file>
```

The VM will load the bytecode file and execute the program, printing any output to stdout.

## Design Considerations

The VM was designed with the following principles:

1. **Simplicity**: The instruction set is minimal but complete enough to execute PostC programs
2. **Type Safety**: Operations perform type checking to prevent invalid operations
3. **Error Handling**: Clear error messages for common issues like stack underflow or division by zero
4. **Extensibility**: The modular design makes it easy to add new opcodes or features

This separation of the VM from the compiler allows for more flexible execution of PostC programs and makes it easier to implement additional targets like WebAssembly.