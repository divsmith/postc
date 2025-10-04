#!/usr/bin/env python3

"""
PostC Virtual Machine
Standalone VM that executes compiled PostC bytecode files.
"""

import sys
import os
import json
import traceback
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any

# Opcode definitions (duplicated for standalone VM)
class Opcode(Enum):
    # Constants
    LOAD_CONST = "LOAD_CONST"
    LOAD_TRUE = "LOAD_TRUE"
    LOAD_FALSE = "LOAD_FALSE"
    LOAD_STRING = "LOAD_STRING"
    
    # Variables
    LOAD_VAR = "LOAD_VAR"
    STORE_VAR = "STORE_VAR"
    
    # Stack operations
    DUP = "DUP"
    DROP = "DROP"
    SWAP = "SWAP"
    OVER = "OVER"
    ROT = "ROT"
    
    # Arithmetic
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    
    # Comparison
    EQ = "EQ"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LE = "LE"
    GE = "GE"
    
    # Control flow
    JUMP = "JUMP"
    JUMP_IF_FALSE = "JUMP_IF_FALSE"
    CALL = "CALL"
    RETURN = "RETURN"
    
    # I/O
    PRINT = "PRINT"
    READ_STDIN = "READ_STDIN"
    READ_FILE = "READ_FILE"

    # Arrays
    CREATE_ARRAY = "CREATE_ARRAY"
    LOAD_ARRAY = "LOAD_ARRAY"
    STORE_ARRAY = "STORE_ARRAY"
    ARRAY_LENGTH = "ARRAY_LENGTH"

    # Dictionaries
    CREATE_DICT = "CREATE_DICT"
    LOAD_DICT = "LOAD_DICT"
    STORE_DICT = "STORE_DICT"
    DICT_HAS_KEY = "DICT_HAS_KEY"
    DICT_LENGTH = "DICT_LENGTH"

    # Strings
    STRING_LENGTH = "STRING_LENGTH"
    STRING_CONCAT = "STRING_CONCAT"
    STRING_SUBSTRING = "STRING_SUBSTRING"
    STRING_INDEXOF = "STRING_INDEXOF"

    # Halt
    HALT = "HALT"

# VM error
class VmError(Exception):
    def __init__(self, message: str, line: int = 0):
        super().__init__(f"VM error at line {line}: {message}")
        self.line = line

# Instruction (simplified for execution)
@dataclass
class Instruction:
    opcode: Opcode
    operand: Optional[Union[int, float, str]] = None
    line: int = 0
    
    @classmethod
    def from_string(cls, instruction_str: str) -> 'Instruction':
        """Create an Instruction from its string representation."""
        parts = instruction_str.strip().split(' ', 1)
        opcode_str = parts[0]
        operand_str = parts[1] if len(parts) > 1 else None
        
        # Convert opcode string to enum
        try:
            opcode = Opcode(opcode_str)
        except ValueError:
            raise ValueError(f"Unknown opcode: {opcode_str}")
        
        # Convert operand if present
        operand = None
        if operand_str is not None:
            # Try to convert to int, then float, otherwise keep as string
            try:
                operand = int(operand_str)
            except ValueError:
                try:
                    operand = float(operand_str)
                except ValueError:
                    operand = operand_str
        
        # Extract line number from instruction string if available
        # For now, we'll just use 0 as default
        return cls(opcode, operand, 0)

# Function
@dataclass
class Function:
    name: str
    param_count: int
    instructions: List[Instruction] = field(default_factory=list)

# Frame
@dataclass
class Frame:
    """A frame on the call stack."""
    instructions: List[Instruction]
    pc: int = 0
    base_pointer: int = 0
    variables: Dict[str, Union[int, float, str, bool]] = field(default_factory=dict)

# Virtual Machine
class VM:
    def __init__(self, constants: List[Union[int, float, str, bool]], functions: Dict[str, Function]):
        self.constants = constants
        self.functions = functions
        self.stack: List[Union[int, float, str, bool]] = []
        self.call_stack: List[Frame] = []
        self.global_variables: Dict[str, Union[int, float, str, bool]] = {}
        self.debug_mode = False

        
    def push(self, value: Union[int, float, str, bool]):
        """Push a value onto the stack."""
        self.stack.append(value)
        
    def pop(self) -> Union[int, float, str, bool]:
        """Pop a value from the stack."""
        if not self.stack:
            raise VmError("Stack underflow", self.get_current_line())
        return self.stack.pop()
        
    def peek(self) -> Union[int, float, str, bool]:
        """Peek at the top value on the stack."""
        if not self.stack:
            raise VmError("Stack underflow", self.get_current_line())
        return self.stack[-1]
        
    def enable_debug_mode(self):
        """Enable debug mode which provides more detailed output."""
        self.debug_mode = True
        
    def get_current_line(self) -> int:
        """Get the line number of the current instruction."""
        if self.call_stack:
            frame = self.call_stack[-1]
            if frame.pc > 0 and frame.pc <= len(frame.instructions):
                return frame.instructions[frame.pc - 1].line
        return 0
        
    def run(self):
        """Execute the program."""
        main_func = self.functions.get("main")
        if not main_func:
            raise VmError("Function 'main' not found", 0)
            
        # Set up the initial frame for the main function
        self.call_stack.append(Frame(main_func.instructions))
        
        while self.call_stack:
            frame = self.call_stack[-1]
            
            if frame.pc >= len(frame.instructions):
                # End of function, pop the frame
                self.call_stack.pop()
                continue
                
            instruction = frame.instructions[frame.pc]
            if self.debug_mode:
                print(f"[DEBUG] Executing: {instruction.opcode.value} {instruction.operand if instruction.operand is not None else ''} at line {instruction.line}")
                
            frame.pc += 1
            self.execute_instruction(instruction)
            
    def execute_instruction(self, instruction: Instruction):
        """Execute a single instruction."""
        opcode = instruction.opcode
        line = instruction.line
        
        if opcode == Opcode.LOAD_CONST:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid constant index", line)
            self.push(self.constants[instruction.operand])
            
        elif opcode == Opcode.LOAD_TRUE:
            self.push(True)
            
        elif opcode == Opcode.LOAD_FALSE:
            self.push(False)
            
        elif opcode == Opcode.LOAD_STRING:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid string index", line)
            self.push(self.constants[instruction.operand])
            
        elif opcode == Opcode.LOAD_VAR:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid variable index", line)
            var_name = self.constants[instruction.operand]
            
            # Look for variable in current frame first, then global
            current_frame = self.call_stack[-1] if self.call_stack else None
            if current_frame and var_name in current_frame.variables:
                self.push(current_frame.variables[var_name])
            elif var_name in self.global_variables:
                self.push(self.global_variables[var_name])
            else:
                raise VmError(f"Variable '{var_name}' not found", line)
            
        elif opcode == Opcode.STORE_VAR:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid variable index", line)
            var_name = self.constants[instruction.operand]
            value = self.pop()
            
            # Store in current frame's local variables (for proper scoping)
            if self.call_stack:
                self.call_stack[-1].variables[var_name] = value
            else:
                # Fallback to global if no frames
                self.global_variables[var_name] = value
            
        elif opcode == Opcode.DUP:
            value = self.peek()
            self.push(value)
            
        elif opcode == Opcode.DROP:
            self.pop()
            
        elif opcode == Opcode.SWAP:
            if len(self.stack) < 2:
                raise VmError("Not enough values on stack for SWAP", line)
            a = self.pop()
            b = self.pop()
            self.push(a)
            self.push(b)
            
        elif opcode == Opcode.OVER:
            if len(self.stack) < 2:
                raise VmError("Not enough values on stack for OVER", line)
            a = self.pop()
            b = self.peek()
            self.push(a)
            self.push(b)
            
        elif opcode == Opcode.ROT:
            if len(self.stack) < 3:
                raise VmError("Not enough values on stack for ROT", line)
            a = self.pop()
            b = self.pop()
            c = self.pop()
            self.push(b)
            self.push(a)
            self.push(c)
            
        elif opcode == Opcode.ADD:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a + b)
            else:
                raise VmError(f"Invalid types for addition: {type(a).__name__} and {type(b).__name__}", line)
                
        elif opcode == Opcode.SUB:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a - b)
            else:
                raise VmError(f"Invalid types for subtraction: {type(a).__name__} and {type(b).__name__}", line)
                
        elif opcode == Opcode.MUL:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a * b)
            else:
                raise VmError(f"Invalid types for multiplication: {type(a).__name__} and {type(b).__name__}", line)
                
        elif opcode == Opcode.DIV:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                if b == 0:
                    raise VmError("Division by zero", line)
                self.push(a / b if isinstance(a, float) or isinstance(b, float) else a // b)
            else:
                raise VmError(f"Invalid types for division: {type(a).__name__} and {type(b).__name__}", line)
                
        elif opcode == Opcode.EQ:
            b = self.pop()
            a = self.pop()
            self.push(a == b)
            
        elif opcode == Opcode.NE:
            b = self.pop()
            a = self.pop()
            self.push(a != b)
            
        elif opcode == Opcode.LT:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a < b)
            else:
                raise VmError(f"Invalid types for comparison: {type(a).__name__} and {type(b).__name__}", line)
                
        elif opcode == Opcode.GT:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a > b)
            else:
                raise VmError(f"Invalid types for comparison: {type(a).__name__} and {type(b).__name__}", line)
                
        elif opcode == Opcode.LE:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a <= b)
            else:
                raise VmError(f"Invalid types for comparison: {type(a).__name__} and {type(b).__name__}", line)
                
        elif opcode == Opcode.GE:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a >= b)
            else:
                raise VmError(f"Invalid types for comparison: {type(a).__name__} and {type(b).__name__}", line)
                
        elif opcode == Opcode.PRINT:
            value = self.pop()
            print(value)
            
        elif opcode == Opcode.JUMP:
            if instruction.operand is None or not isinstance(instruction.operand, int):
                raise VmError("Invalid jump target", line)
            self.call_stack[-1].pc = instruction.operand
            
        elif opcode == Opcode.JUMP_IF_FALSE:
            if instruction.operand is None or not isinstance(instruction.operand, int):
                raise VmError("Invalid jump target", line)
            condition = self.pop()
            if not condition:
                self.call_stack[-1].pc = instruction.operand

        elif opcode == Opcode.CALL:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid function index", line)
            func_name = self.constants[instruction.operand]
            if func_name not in self.functions:
                raise VmError(f"Function '{func_name}' not found", line)

            func = self.functions[func_name]
            
            # Create a new frame for the function call
            base_pointer = len(self.stack) - func.param_count
            new_frame = Frame(func.instructions, base_pointer=base_pointer)
            self.call_stack.append(new_frame)
            
        elif opcode == Opcode.RETURN:
            # Pop the current frame
            frame = self.call_stack.pop()

            # Get the return value from the top of the stack
            return_value = self.pop()

            # Clean up the stack by removing arguments
            while len(self.stack) > frame.base_pointer:
                self.pop()

            # Push the return value back onto the stack
            self.push(return_value)
            
        elif opcode == Opcode.HALT:
            while self.call_stack:
                self.call_stack.pop()

        # Array operations
        elif opcode == Opcode.CREATE_ARRAY:
            size = self.pop()
            if not isinstance(size, int) or size < 0:
                raise VmError("Array size must be a non-negative integer", line)
            # Create array as a list of None values
            array = [None] * size
            self.push(array)

        elif opcode == Opcode.LOAD_ARRAY:
            index = self.pop()
            array = self.pop()
            if not isinstance(array, list):
                raise VmError("Expected array for LOAD_ARRAY", line)
            if not isinstance(index, int) or index < 0 or index >= len(array):
                raise VmError(f"Array index out of bounds: {index}", line)
            value = array[index]
            if value is None:
                raise VmError(f"Array element at index {index} is uninitialized", line)
            self.push(value)

        elif opcode == Opcode.STORE_ARRAY:
            if not isinstance(array, list):
                raise VmError("Expected array for STORE_ARRAY", line)
            if not isinstance(index, int) or index < 0 or index >= len(array):
                raise VmError(f"Array index out of bounds: {index}", line)
            array[index] = value
            # Push the array back onto the stack for further operations
            self.push(array)

        elif opcode == Opcode.ARRAY_LENGTH:
            array = self.pop()
            if not isinstance(array, list):
                raise VmError("Expected array for ARRAY_LENGTH", line)
            self.push(len(array))

        # Dictionary operations
        elif opcode == Opcode.CREATE_DICT:
            # Create empty dictionary
            dictionary = {}
            self.push(dictionary)

        elif opcode == Opcode.LOAD_DICT:
            key = self.pop()
            dictionary = self.pop()
            if not isinstance(dictionary, dict):
                raise VmError("Expected dictionary for LOAD_DICT", line)
            if key not in dictionary:
                raise VmError(f"Dictionary key not found: {key}", line)
            self.push(dictionary[key])

        elif opcode == Opcode.STORE_DICT:
            value = self.pop()
            key = self.pop()
            dictionary = self.pop()
            if not isinstance(dictionary, dict):
                raise VmError("Expected dictionary for STORE_DICT", line)
            dictionary[key] = value

        elif opcode == Opcode.DICT_HAS_KEY:
            key = self.pop()
            dictionary = self.pop()
            if not isinstance(dictionary, dict):
                raise VmError("Expected dictionary for DICT_HAS_KEY", line)
            self.push(key in dictionary)

        elif opcode == Opcode.DICT_LENGTH:
            dictionary = self.pop()
            if not isinstance(dictionary, dict):
                raise VmError("Expected dictionary for DICT_LENGTH", line)
            self.push(len(dictionary))

        # I/O operations
        elif opcode == Opcode.READ_STDIN:
            try:
                user_input = input()
                self.push(user_input)
            except EOFError:
                raise VmError("EOF reached while reading from stdin", line)
            except KeyboardInterrupt:
                raise VmError("Input interrupted by user", line)

        elif opcode == Opcode.READ_FILE:
            filename = self.pop()
            if not isinstance(filename, str):
                raise VmError("Expected string filename for READ_FILE", line)
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.push(content)
            except FileNotFoundError:
                raise VmError(f"File not found: {filename}", line)
            except PermissionError:
                raise VmError(f"Permission denied reading file: {filename}", line)
            except UnicodeDecodeError:
                raise VmError(f"Cannot decode file as UTF-8: {filename}", line)
            except Exception as e:
                raise VmError(f"Error reading file '{filename}': {str(e)}", line)

        # String operations
        elif opcode == Opcode.STRING_LENGTH:
            string = self.pop()
            if not isinstance(string, str):
                raise VmError("Expected string for STRING_LENGTH", line)
            self.push(len(string))

        elif opcode == Opcode.STRING_CONCAT:
            str2 = self.pop()
            str1 = self.pop()
            if not isinstance(str1, str) or not isinstance(str2, str):
                raise VmError("Expected strings for STRING_CONCAT", line)
            self.push(str1 + str2)

        elif opcode == Opcode.STRING_SUBSTRING:
            length = self.pop()
            start = self.pop()
            string = self.pop()
            if not isinstance(string, str):
                raise VmError("Expected string for STRING_SUBSTRING", line)
            if not isinstance(start, int) or not isinstance(length, int):
                raise VmError("Start and length must be integers for STRING_SUBSTRING", line)
            if start < 0 or start >= len(string):
                raise VmError(f"Start index out of bounds: {start}", line)
            if length < 0:
                raise VmError(f"Length cannot be negative: {length}", line)
            if start + length > len(string):
                raise VmError(f"Substring extends beyond string length: start={start}, length={length}", line)
            self.push(string[start:start + length])

        elif opcode == Opcode.STRING_INDEXOF:
            substring = self.pop()
            string = self.pop()
            if not isinstance(string, str) or not isinstance(substring, str):
                raise VmError("Expected strings for STRING_INDEXOF", line)
            index = string.find(substring)
            self.push(index)

        else:
            raise VmError(f"Unknown opcode: {opcode}", line)

def load_bytecode_from_file(filename: str) -> dict:
    """Load compiled bytecode from a file."""
    with open(filename, 'r') as f:
        return json.load(f)

def create_functions_from_bytecode(functions_data: dict) -> Dict[str, Function]:
    """Create Function objects from bytecode data."""
    functions = {}
    for name, func_data in functions_data.items():
        # Convert instruction strings to Instruction objects
        instructions = []
        for instr_str in func_data["instructions"]:
            try:
                instruction = Instruction.from_string(instr_str)
                instructions.append(instruction)
            except ValueError as e:
                print(f"Warning: {e}")
                continue

        functions[name] = Function(
            name=func_data["name"],
            param_count=func_data["param_count"],
            instructions=instructions
        )
        print(f"Loaded function: {name} with {len(instructions)} instructions")
    return functions

def run_bytecode_file(filename: str, debug: bool = False):
    """Load and run a compiled PostC bytecode file."""
    print(f"Loading bytecode from {filename}...")
    
    # Load bytecode from file
    bytecode = load_bytecode_from_file(filename)
    
    # Create functions from bytecode
    functions = create_functions_from_bytecode(bytecode["functions"])
    
    # Create VM and run
    print("Running program...")
    vm = VM(bytecode["constants"], functions)
    if debug:
        vm.enable_debug_mode()
    vm.run()
    
    print("Program finished.")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 vm.py <bytecode_file> [-d|--debug]")
        return
        
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return
        
    debug = "-d" in sys.argv or "--debug" in sys.argv
    
    try:
        run_bytecode_file(filename, debug)
    except Exception as e:
        print(f"Error: {e}")
        if debug:
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()