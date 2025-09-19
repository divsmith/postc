#!/usr/bin/env python3

"""
PostC Bootstrap Compiler - Virtual Machine
Executes PostC bytecode.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

from codegen import Opcode, Instruction

class VmError(Exception):
    def __init__(self, message: str):
        super().__init__(f"VM error: {message}")

class VM:
    def __init__(self, constants: List[Union[int, float, str, bool]], functions: Dict[str, List[Instruction]]):
        self.constants = constants
        self.functions = functions
        self.stack: List[Union[int, float, str, bool]] = []
        self.variables: Dict[str, Union[int, float, str, bool]] = {}
        self.pc = 0  # Program counter
        self.current_function = "main"
        
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
        if self.current_function not in self.functions:
            raise VmError(f"Function '{self.current_function}' not found")
            
        instructions = self.functions[self.current_function]
        
        while self.pc < len(instructions):
            instruction = instructions[self.pc]
            self.execute_instruction(instruction)
            self.pc += 1
            
    def execute_instruction(self, instruction: Instruction):
        """Execute a single instruction."""
        opcode = instruction.opcode
        
        if opcode == Opcode.LOAD_CONST:
            if instruction.operand is None or instruction.operand >= len(self.constants):
                raise VmError("Invalid constant index")
            self.push(self.constants[instruction.operand])
            
        elif opcode == Opcode.LOAD_TRUE:
            self.push(True)
            
        elif opcode == Opcode.LOAD_FALSE:
            self.push(False)
            
        elif opcode == Opcode.LOAD_STRING:
            if instruction.operand is None or instruction.operand >= len(self.constants):
                raise VmError("Invalid string index")
            self.push(self.constants[instruction.operand])
            
        elif opcode == Opcode.LOAD_VAR:
            if instruction.operand is None or instruction.operand >= len(self.constants):
                raise VmError("Invalid variable index")
            var_name = self.constants[instruction.operand]
            if var_name not in self.variables:
                raise VmError(f"Variable '{var_name}' not found")
            self.push(self.variables[var_name])
            
        elif opcode == Opcode.STORE_VAR:
            if instruction.operand is None or instruction.operand >= len(self.constants):
                raise VmError("Invalid variable index")
            var_name = self.constants[instruction.operand]
            value = self.pop()
            self.variables[var_name] = value
            
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
            
        elif opcode == Opcode.CALL:
            if instruction.operand is None or instruction.operand >= len(self.constants):
                raise VmError("Invalid function index")
            func_name = self.constants[instruction.operand]
            if func_name not in self.functions:
                raise VmError(f"Function '{func_name}' not found")
            # In a full implementation, we would handle function calls properly
            # For now, we'll just print a message
            print(f"Calling function '{func_name}'")
            
        elif opcode == Opcode.HALT:
            self.pc = len(self.functions[self.current_function])  # Stop execution
            
        else:
            raise VmError(f"Unknown opcode: {opcode}")

def main():
    """Simple test function for the VM."""
    # Simple test program: push 5, push 3, add, print
    constants = [5, 3]
    functions = {
        "main": [
            Instruction(Opcode.LOAD_CONST, 0),
            Instruction(Opcode.LOAD_CONST, 1),
            Instruction(Opcode.ADD),
            Instruction(Opcode.PRINT),
            Instruction(Opcode.HALT)
        ]
    }
    
    vm = VM(constants, functions)
    vm.run()

if __name__ == '__main__':
    main()