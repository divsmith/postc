#!/usr/bin/env python3

"""
PostC Virtual Machine
Standalone VM that executes compiled PostC bytecode files.
"""

import sys
import os
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

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
    
    # Halt
    HALT = "HALT"

# VM error
class VmError(Exception):
    def __init__(self, message: str):
        super().__init__(f"VM error: {message}")

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
            raise VmError(f"Unknown opcode: {opcode_str}")
        
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
        
        return cls(opcode, operand)

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

# Virtual Machine
class VM:
    def __init__(self, constants: List[Union[int, float, str, bool]], functions: Dict[str, Function]):
        self.constants = constants
        self.functions = functions
        self.stack: List[Union[int, float, str, bool]] = []
        self.call_stack: List[Frame] = []
        
    def push(self, value: Union[int, float, str, bool]):
        """Push a value onto the stack."""
        self.stack.append(value)
        
    def pop(self) -> Union[int, float, str, bool]:
        """Pop a value from the stack."""
        if not self.stack:
            raise VmError("Stack underflow")
        return self.stack.pop()
        
    def peek(self) -> Union[int, float, str, bool]:
        """Peek at the top value on the stack."""
        if not self.stack:
            raise VmError("Stack underflow")
        return self.stack[-1]
        
    def run(self):
        """Execute the program."""
        main_func = self.functions.get("main")
        if not main_func:
            raise VmError("Function 'main' not found")
            
        # Set up the initial frame for the main function
        self.call_stack.append(Frame(main_func.instructions))
        
        while self.call_stack:
            frame = self.call_stack[-1]
            
            if frame.pc >= len(frame.instructions):
                # End of function, pop the frame
                self.call_stack.pop()
                continue
                
            instruction = frame.instructions[frame.pc]
            frame.pc += 1
            self.execute_instruction(instruction)
            
    def execute_instruction(self, instruction: Instruction):
        """Execute a single instruction."""
        opcode = instruction.opcode
        
        if opcode == Opcode.LOAD_CONST:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid constant index")
            self.push(self.constants[instruction.operand])
            
        elif opcode == Opcode.LOAD_TRUE:
            self.push(True)
            
        elif opcode == Opcode.LOAD_FALSE:
            self.push(False)
            
        elif opcode == Opcode.LOAD_STRING:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid string index")
            self.push(self.constants[instruction.operand])
            
        elif opcode == Opcode.LOAD_VAR:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid variable index")
            var_name = self.constants[instruction.operand]
            # For now, we'll use a simple global variable model
            # A full implementation would use stack-based local variables
            if var_name not in self.get_current_frame_variables():
                raise VmError(f"Variable '{var_name}' not found")
            self.push(self.get_current_frame_variables()[var_name])
            
        elif opcode == Opcode.STORE_VAR:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid variable index")
            var_name = self.constants[instruction.operand]
            value = self.pop()
            self.get_current_frame_variables()[var_name] = value
            
        elif opcode == Opcode.DUP:
            value = self.peek()
            self.push(value)
            
        elif opcode == Opcode.DROP:
            self.pop()
            
        elif opcode == Opcode.SWAP:
            if len(self.stack) < 2:
                raise VmError("Not enough values on stack for SWAP")
            a = self.pop()
            b = self.pop()
            self.push(a)
            self.push(b)
            
        elif opcode == Opcode.OVER:
            if len(self.stack) < 2:
                raise VmError("Not enough values on stack for OVER")
            a = self.pop()
            b = self.peek()
            self.push(a)
            self.push(b)
            
        elif opcode == Opcode.ROT:
            if len(self.stack) < 3:
                raise VmError("Not enough values on stack for ROT")
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
                raise VmError("Invalid types for addition")
                
        elif opcode == Opcode.SUB:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a - b)
            else:
                raise VmError("Invalid types for subtraction")
                
        elif opcode == Opcode.MUL:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a * b)
            else:
                raise VmError("Invalid types for multiplication")
                
        elif opcode == Opcode.DIV:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                if b == 0:
                    raise VmError("Division by zero")
                self.push(a / b if isinstance(a, float) or isinstance(b, float) else a // b)
            else:
                raise VmError("Invalid types for division")
                
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
                raise VmError("Invalid types for comparison")
                
        elif opcode == Opcode.GT:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a > b)
            else:
                raise VmError("Invalid types for comparison")
                
        elif opcode == Opcode.LE:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a <= b)
            else:
                raise VmError("Invalid types for comparison")
                
        elif opcode == Opcode.GE:
            b = self.pop()
            a = self.pop()
            if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                self.push(a >= b)
            else:
                raise VmError("Invalid types for comparison")
                
        elif opcode == Opcode.PRINT:
            value = self.pop()
            print(value)
            
        elif opcode == Opcode.JUMP:
            if instruction.operand is None or not isinstance(instruction.operand, int):
                raise VmError("Invalid jump target")
            self.call_stack[-1].pc = instruction.operand
            
        elif opcode == Opcode.JUMP_IF_FALSE:
            if instruction.operand is None or not isinstance(instruction.operand, int):
                raise VmError("Invalid jump target")
            condition = self.pop()
            if not condition:
                self.call_stack[-1].pc = instruction.operand

        elif opcode == Opcode.CALL:
            if instruction.operand is None or not isinstance(instruction.operand, int) or instruction.operand >= len(self.constants):
                raise VmError("Invalid function index")
            func_name = self.constants[instruction.operand]
            if func_name not in self.functions:
                raise VmError(f"Function '{func_name}' not found")
                
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
            
        else:
            raise VmError(f"Unknown opcode: {opcode}")

    def get_current_frame_variables(self) -> Dict[str, Union[int, float, str, bool]]:
        """Get the variables for the current frame."""
        # This is a simplified approach. A full implementation would use a more robust
        # variable management system.
        if not hasattr(self, "_variables"):
            self._variables = {}
        return self._variables

def load_bytecode_from_file(filename: str) -> dict:
    """Load compiled bytecode from a file."""
    with open(filename, 'r') as f:
        return json.load(f)

def create_functions_from_bytecode(functions_data: dict) -> Dict[str, Function]:
    """Create Function objects from bytecode data."""
    functions = {}
    for name, func_data in functions_data.items():
        # Convert instruction strings to Instruction objects
        instructions = [
            Instruction.from_string(instr_str) 
            for instr_str in func_data["instructions"]
        ]
        
        functions[name] = Function(
            name=func_data["name"],
            param_count=func_data["param_count"],
            instructions=instructions
        )
    return functions

def run_bytecode_file(filename: str):
    """Load and run a compiled PostC bytecode file."""
    print(f"Loading bytecode from {filename}...")
    
    # Load bytecode from file
    bytecode = load_bytecode_from_file(filename)
    
    # Create functions from bytecode
    functions = create_functions_from_bytecode(bytecode["functions"])
    
    # Create VM and run
    print("Running program...")
    vm = VM(bytecode["constants"], functions)
    vm.run()
    
    print("Program finished.")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 vm.py <bytecode_file>")
        return
        
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return
        
    try:
        run_bytecode_file(filename)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()