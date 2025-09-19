#!/usr/bin/env python3

"""
PostC Bootstrap Compiler - Code Generator
Generates bytecode from the AST.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

from parser import ASTNode, ASTNodeType
from lexer import Token, TokenType

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

@dataclass
class Instruction:
    opcode: Opcode
    operand: Optional[Union[int, float, str]] = None
    line: int = 0
    
    def __str__(self):
        if self.operand is not None:
            return f"{self.opcode.value} {self.operand}"
        return self.opcode.value

@dataclass
class Function:
    name: str
    param_count: int
    instructions: List[Instruction] = field(default_factory=list)
    
class CodeGeneratorError(Exception):
    def __init__(self, message: str, line: int = 0):
        super().__init__(f"Code generation error at line {line}: {message}")
        self.line = line

class CodeGenerator:
    def __init__(self):
        self.constants: List[Union[int, float, str, bool]] = []
        self.functions: Dict[str, Function] = {}
        self.current_function: Optional[Function] = None
        self.instructions: List[Instruction] = []
        
    def add_constant(self, value: Union[int, float, str, bool]) -> int:
        """Add a constant to the constant pool and return its index."""
        if value in self.constants:
            return self.constants.index(value)
        self.constants.append(value)
        return len(self.constants) - 1
        
    def generate_code(self, ast: ASTNode) -> List[Instruction]:
        """Generate bytecode from the AST."""
        if ast.type != ASTNodeType.PROGRAM:
            raise CodeGeneratorError("Expected PROGRAM node", ast.line)
            
        # Process all function declarations first
        for child in ast.children:
            if child.type == ASTNodeType.FUNCTION_DECL:
                self.generate_function(child)
                
        # Process the main program
        self.current_function = Function("main", 0)
        for child in ast.children:
            if child.type != ASTNodeType.FUNCTION_DECL:
                self.generate_statement(child)
                
        self.instructions.append(Instruction(Opcode.HALT))
        self.functions["main"] = self.current_function
        
        # For simplicity, we'll just return the main function's instructions
        # In a full implementation, we'd need to handle linking functions together
        return self.current_function.instructions
        
    def generate_function(self, node: ASTNode):
        """Generate code for a function declaration."""
        if not isinstance(node.value, dict):
            raise CodeGeneratorError("Function declaration missing metadata", node.line)
            
        func_name = node.value["name"]
        param_count = node.value["param_count"]
        
        func = Function(func_name, param_count)
        old_function = self.current_function
        self.current_function = func
        
        # Generate code for the function body
        if node.children:
            self.generate_block(node.children[0])  # The function body is the first child
            
        # Add a return instruction if not already present
        if not func.instructions or func.instructions[-1].opcode != Opcode.RETURN:
            func.instructions.append(Instruction(Opcode.RETURN))
            
        self.functions[func_name] = func
        self.current_function = old_function
        
    def generate_statement(self, node: ASTNode):
        """Generate code for a statement."""
        if node.type == ASTNodeType.VARIABLE_DECL:
            self.generate_variable_decl(node)
        elif node.type == ASTNodeType.BLOCK:
            self.generate_block(node)
        elif node.type == ASTNodeType.RPN_EXPRESSION:
            self.generate_rpn_expression_node(node)
        elif node.type == ASTNodeType.IF_EXPR:
            self.generate_if_expr(node)
        elif node.type == ASTNodeType.WHILE_LOOP:
            self.generate_while_loop(node)
        elif node.type == ASTNodeType.FOR_LOOP:
            self.generate_for_loop(node)
        else:
            # For other statements, treat as expressions
            self.generate_expression(node)
            
    def generate_variable_decl(self, node: ASTNode):
        """Generate code for a variable declaration."""
        if not isinstance(node.value, dict):
            raise CodeGeneratorError("Variable declaration missing metadata", node.line)
            
        var_name = node.value["name"]
        is_mutable = node.value["mutable"]
        
        # Generate code for the value expression
        if node.children:
            self.generate_expression(node.children[0])
        else:
            # Default to 0 for uninitialized variables
            self.emit(Instruction(Opcode.LOAD_CONST, self.add_constant(0), node.line))
            
        # Store the value in the variable
        const_idx = self.add_constant(var_name)
        self.emit(Instruction(Opcode.STORE_VAR, const_idx, node.line))
        
    def generate_block(self, node: ASTNode):
        """Generate code for a block of statements."""
        for child in node.children:
            self.generate_statement(child)
            
    def generate_rpn_expression_node(self, node: ASTNode):
        """Generate code for an RPN expression node."""
        if isinstance(node.value, str):
            self.generate_rpn_expression(node.value, node.line)
            
    def generate_if_expr(self, node: ASTNode):
        """Generate code for an if expression."""
        # In RPN, the condition is already on the stack
        # We need to evaluate the condition and jump if false
        
        # For simplicity in this bootstrap implementation, we'll just emit placeholder instructions
        # A full implementation would generate proper control flow
        
        # Condition is already evaluated (placeholder)
        # Jump if false to else branch or end
        self.emit(Instruction(Opcode.JUMP_IF_FALSE, 0, node.line))  # Placeholder jump target
        
        # Then branch
        if len(node.children) > 1:
            self.generate_block(node.children[1])
            
        # Else branch (if present)
        if len(node.children) > 2:
            # Jump over else branch
            self.emit(Instruction(Opcode.JUMP, 0, node.line))  # Placeholder jump target
            # Else branch
            self.generate_block(node.children[2])
            
    def generate_while_loop(self, node: ASTNode):
        """Generate code for a while loop."""
        # For simplicity in this bootstrap implementation, we'll just emit placeholder instructions
        # A full implementation would generate proper control flow
        
        # Condition evaluation
        # Jump if false to end of loop
        self.emit(Instruction(Opcode.JUMP_IF_FALSE, 0, node.line))  # Placeholder jump target
        
        # Loop body
        if len(node.children) > 1:
            self.generate_block(node.children[1])
            
        # Jump back to condition
        self.emit(Instruction(Opcode.JUMP, 0, node.line))  # Placeholder jump target
        
    def generate_for_loop(self, node: ASTNode):
        """Generate code for a for loop."""
        # For simplicity in this bootstrap implementation, we'll just emit placeholder instructions
        # A full implementation would generate proper control flow
        
        # Count is already on stack
        # Jump if false to end of loop
        self.emit(Instruction(Opcode.JUMP_IF_FALSE, 0, node.line))  # Placeholder jump target
        
        # Loop body
        if len(node.children) > 1:
            self.generate_block(node.children[1])
            
        # Decrement counter and jump back
        self.emit(Instruction(Opcode.LOAD_CONST, self.add_constant(1), node.line))
        self.emit(Instruction(Opcode.SUB, line=node.line))
        self.emit(Instruction(Opcode.JUMP, 0, node.line))  # Placeholder jump target
        
    def generate_expression(self, node: ASTNode):
        """Generate code for an expression."""
        if node.type == ASTNodeType.INTEGER_LITERAL:
            const_idx = self.add_constant(node.value)
            self.emit(Instruction(Opcode.LOAD_CONST, const_idx, node.line))
        elif node.type == ASTNodeType.FLOAT_LITERAL:
            const_idx = self.add_constant(node.value)
            self.emit(Instruction(Opcode.LOAD_CONST, const_idx, node.line))
        elif node.type == ASTNodeType.STRING_LITERAL:
            const_idx = self.add_constant(node.value)
            self.emit(Instruction(Opcode.LOAD_STRING, const_idx, node.line))
        elif node.type == ASTNodeType.BOOLEAN_LITERAL:
            if node.value:
                self.emit(Instruction(Opcode.LOAD_TRUE, line=node.line))
            else:
                self.emit(Instruction(Opcode.LOAD_FALSE, line=node.line))
        elif node.type == ASTNodeType.IDENTIFIER:
            # For now, assume all identifiers are variables
            # A full implementation would need to distinguish variables from functions
            const_idx = self.add_constant(node.value)
            self.emit(Instruction(Opcode.LOAD_VAR, const_idx, node.line))
        elif node.type == ASTNodeType.STACK_OP:
            op_map = {
                "dup": Opcode.DUP,
                "drop": Opcode.DROP,
                "swap": Opcode.SWAP,
                "over": Opcode.OVER,
                "rot": Opcode.ROT
            }
            opcode = op_map.get(node.value)
            if opcode:
                self.emit(Instruction(opcode, line=node.line))
        elif node.type == ASTNodeType.RPN_EXPRESSION:
            # For RPN expressions, we'll need to parse them properly
            # For now, we'll handle simple cases
            if isinstance(node.value, str):
                self.generate_rpn_expression(node.value, node.line)
        elif node.type == ASTNodeType.CALL:
            # Function call
            const_idx = self.add_constant(node.value)
            self.emit(Instruction(Opcode.CALL, const_idx, node.line))
        else:
            # For other node types, recursively generate code for children
            for child in node.children:
                self.generate_expression(child)
                
    def generate_rpn_expression(self, expression: str, line: int):
        """Generate code for an RPN expression."""
        # This is a simplified implementation
        # A full implementation would properly parse and compile RPN expressions
        
        # For now, we'll just split on whitespace, but we need to be careful with strings
        # Let's manually tokenize the expression to handle strings correctly
        tokens = self.tokenize_rpn_expression(expression)
        
        for token in tokens:
            if token.type == TokenType.INTEGER:
                const_idx = self.add_constant(int(token.value))
                self.emit(Instruction(Opcode.LOAD_CONST, const_idx, line))
            elif token.type == TokenType.FLOAT:
                const_idx = self.add_constant(float(token.value))
                self.emit(Instruction(Opcode.LOAD_CONST, const_idx, line))
            elif token.type == TokenType.STRING:
                # Remove the quotes from the string value
                string_value = token.value[1:-1] if len(token.value) >= 2 else token.value
                const_idx = self.add_constant(string_value)
                self.emit(Instruction(Opcode.LOAD_STRING, const_idx, line))
            elif token.type == TokenType.IDENTIFIER:
                # Check if it's an operator
                if token.value in ('+', '-', '*', '/'):
                    op_map = {'+': Opcode.ADD, '-': Opcode.SUB, '*': Opcode.MUL, '/': Opcode.DIV}
                    opcode = op_map.get(token.value)
                    if opcode:
                        self.emit(Instruction(opcode, line=line))
                elif token.value == 'print':
                    self.emit(Instruction(Opcode.PRINT, line=line))
                elif token.value in ('<', '>', '==', '!=', '<=', '>='):
                    op_map = {
                        '<': Opcode.LT, '>': Opcode.GT, '==': Opcode.EQ,
                        '!=': Opcode.NE, '<=': Opcode.LE, '>=': Opcode.GE
                    }
                    opcode = op_map.get(token.value)
                    if opcode:
                        self.emit(Instruction(opcode, line=line))
                elif token.value in ('dup', 'drop', 'swap', 'over', 'rot'):
                    op_map = {
                        'dup': Opcode.DUP, 'drop': Opcode.DROP, 'swap': Opcode.SWAP,
                        'over': Opcode.OVER, 'rot': Opcode.ROT
                    }
                    opcode = op_map.get(token.value)
                    if opcode:
                        self.emit(Instruction(opcode, line=line))
                else:
                    # Assume it's a function call or variable
                    # For now, we'll treat it as a variable load
                    const_idx = self.add_constant(token.value)
                    self.emit(Instruction(Opcode.LOAD_VAR, const_idx, line))
                        
    def tokenize_rpn_expression(self, expression: str) -> List[Token]:
        """Tokenize an RPN expression, handling strings correctly."""
        tokens = []
        i = 0
        line = 1
        col = 1
        
        while i < len(expression):
            # Skip whitespace
            if expression[i].isspace():
                i += 1
                col += 1
                continue
                
            # Handle strings
            if expression[i] == '"':
                start = i
                start_col = col
                i += 1
                col += 1
                while i < len(expression) and expression[i] != '"':
                    if expression[i] == '\\' and i + 1 < len(expression):
                        i += 2
                        col += 2
                    else:
                        i += 1
                        col += 1
                if i < len(expression):  # Found closing quote
                    i += 1
                    col += 1
                value = expression[start:i]
                tokens.append(Token(TokenType.STRING, value, line, start_col))
                continue
                
            # Handle numbers
            if expression[i].isdigit():
                start = i
                start_col = col
                while i < len(expression) and (expression[i].isdigit() or expression[i] == '.'):
                    i += 1
                    col += 1
                value = expression[start:i]
                if '.' in value:
                    tokens.append(Token(TokenType.FLOAT, value, line, start_col))
                else:
                    tokens.append(Token(TokenType.INTEGER, value, line, start_col))
                continue
                
            # Handle identifiers/keywords/operators
            start = i
            start_col = col
            while i < len(expression) and not expression[i].isspace():
                i += 1
                col += 1
            value = expression[start:i]
            tokens.append(Token(TokenType.IDENTIFIER, value, line, start_col))
            
        return tokens
        
    def emit(self, instruction: Instruction):
        """Add an instruction to the current function."""
        if self.current_function:
            self.current_function.instructions.append(instruction)
        else:
            self.instructions.append(instruction)

def main():
    """Simple test function for the code generator."""
    import sys
    from lexer import Lexer
    from parser import Parser
    
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    else:
        text = '''
:add 2 param
  +
;

5 3 add print
# This is a comment
"hello world" print
'''
    
    # Lexical analysis
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    
    # Parsing
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    # Code generation
    codegen = CodeGenerator()
    instructions = codegen.generate_code(ast)
    
    # Print the generated bytecode
    print("Constants:")
    for i, const in enumerate(codegen.constants):
        print(f"  {i}: {const}")
        
    print("\nFunctions:")
    for name, func in codegen.functions.items():
        print(f"  {name} ({func.param_count} params):")
        for i, instr in enumerate(func.instructions):
            print(f"    {i}: {instr}")
            
    print("\nMain instructions:")
    for i, instr in enumerate(instructions):
        print(f"  {i}: {instr}")

if __name__ == '__main__':
    main()