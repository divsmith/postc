#!/usr/bin/env python3

"""
PostC Bootstrap Compiler
Standalone compiler that compiles PostC source code to bytecode files.
"""

import sys
import os
import json
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Iterator

# Token types
class TokenType(Enum):
    # Literals
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    
    # Identifiers
    IDENTIFIER = "IDENTIFIER"
    
    # Operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    ASSIGN = "ASSIGN"
    EQUAL = "EQUAL"
    NOT_EQUAL = "NOT_EQUAL"
    LESS = "LESS"
    GREATER = "GREATER"
    LESS_EQUAL = "LESS_EQUAL"
    GREATER_EQUAL = "GREATER_EQUAL"
    
    # Stack operations
    DUP = "DUP"
    DROP = "DROP"
    SWAP = "SWAP"
    OVER = "OVER"
    ROT = "ROT"
    
    # Keywords
    LET = "LET"
    VAR = "VAR"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    DO = "DO"
    FOR = "FOR"
    FN = "FN"
    PARAM = "PARAM"
    RETURN = "RETURN"
    PRINT = "PRINT"
    
    # Delimiters
    COLON = "COLON"
    SEMICOLON = "SEMICOLON"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    COMMA = "COMMA"
    
    # Special
    COMMENT = "COMMENT"
    EOF = "EOF"
    NEWLINE = "NEWLINE"

# Token class
@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.value}, {self.value}, {self.line}:{self.column})"

# Lexer error
class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Lexer error at {line}:{column}: {message}")
        self.line = line
        self.column = column

# Lexer
class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.text else None
        
    def advance(self):
        """Advance the position pointer and update current character."""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            
    def peek(self, offset: int = 1) -> Optional[str]:
        """Peek at the next character without consuming it."""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
            
    def skip_whitespace(self):
        """Skip whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
            
    def skip_comment(self) -> Token:
        """Skip a comment and return a comment token."""
        start_pos = self.pos
        start_col = self.column
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        comment_text = self.text[start_pos:self.pos]
        return Token(TokenType.COMMENT, comment_text, self.line, start_col)
        
    def read_number(self) -> Token:
        """Read a number (integer or float)."""
        start_pos = self.pos
        start_col = self.column
        
        # Read integer part
        while self.current_char is not None and self.current_char.isdigit():
            self.advance()
            
        # Check for float
        if self.current_char == '.' and self.peek() and self.peek().isdigit():
            self.advance()  # consume '.'
            while self.current_char is not None and self.current_char.isdigit():
                self.advance()
            value = self.text[start_pos:self.pos]
            return Token(TokenType.FLOAT, value, self.line, start_col)
        else:
            value = self.text[start_pos:self.pos]
            return Token(TokenType.INTEGER, value, self.line, start_col)
            
    def read_string(self) -> Token:
        """Read a string literal."""
        start_pos = self.pos
        start_col = self.column
        self.advance()  # consume opening quote
        
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()  # consume escape character
            self.advance()
            
        if self.current_char is None:
            raise LexerError("Unterminated string", self.line, self.column)
            
        self.advance()  # consume closing quote
        value = self.text[start_pos:self.pos]
        return Token(TokenType.STRING, value, self.line, start_col)
        
    def read_identifier(self) -> Token:
        """Read an identifier or keyword."""
        start_pos = self.pos
        start_col = self.column
        
        while (self.current_char is not None and 
               (self.current_char.isalnum() or self.current_char == '_')):
            self.advance()
            
        value = self.text[start_pos:self.pos]
        token_type = self._get_keyword_token_type(value)
        return Token(token_type, value, self.line, start_col)
        
    def _get_keyword_token_type(self, value: str) -> TokenType:
        """Map identifier to keyword token type if applicable."""
        keywords = {
            'let': TokenType.LET,
            'var': TokenType.VAR,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'do': TokenType.DO,
            'for': TokenType.FOR,
            'fn': TokenType.FN,
            'param': TokenType.PARAM,
            'return': TokenType.RETURN,
            'print': TokenType.PRINT,
            'true': TokenType.BOOLEAN,
            'false': TokenType.BOOLEAN,
            'dup': TokenType.DUP,
            'drop': TokenType.DROP,
            'swap': TokenType.SWAP,
            'over': TokenType.OVER,
            'rot': TokenType.ROT,
        }
        return keywords.get(value, TokenType.IDENTIFIER)
        
    def get_next_token(self) -> Token:
        """Get the next token from the input."""
        while self.current_char is not None:
            # Skip whitespace
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
                
            # Handle comments
            if self.current_char == '#':
                return self.skip_comment()
                
            # Handle numbers
            if self.current_char.isdigit():
                return self.read_number()
                
            # Handle strings
            if self.current_char == '"':
                return self.read_string()
                
            # Handle identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()
                
            # Handle operators and delimiters
            start_col = self.column
            char = self.current_char
            
            if char == '+':
                self.advance()
                return Token(TokenType.PLUS, char, self.line, start_col)
                
            if char == '-':
                self.advance()
                return Token(TokenType.MINUS, char, self.line, start_col)
                
            if char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, char, self.line, start_col)
                
            if char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, char, self.line, start_col)
                
            if char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUAL, '==', self.line, start_col)
                return Token(TokenType.ASSIGN, char, self.line, start_col)
                
            if char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.NOT_EQUAL, '!=', self.line, start_col)
                raise LexerError(f"Unexpected character '{char}'", self.line, start_col)
                
            if char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.LESS_EQUAL, '<=', self.line, start_col)
                return Token(TokenType.LESS, char, self.line, start_col)
                
            if char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.GREATER_EQUAL, '>=', self.line, start_col)
                return Token(TokenType.GREATER, char, self.line, start_col)
                
            if char == ':':
                self.advance()
                return Token(TokenType.COLON, char, self.line, start_col)
                
            if char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, char, self.line, start_col)
                
            if char == '(':
                self.advance()
                return Token(TokenType.LPAREN, char, self.line, start_col)
                
            if char == ')':
                self.advance()
                return Token(TokenType.RPAREN, char, self.line, start_col)
                
            if char == '{':
                self.advance()
                return Token(TokenType.LBRACE, char, self.line, start_col)
                
            if char == '}':
                self.advance()
                return Token(TokenType.RBRACE, char, self.line, start_col)
                
            if char == '[':
                self.advance()
                return Token(TokenType.LBRACKET, char, self.line, start_col)
                
            if char == ']':
                self.advance()
                return Token(TokenType.RBRACKET, char, self.line, start_col)
                
            if char == ',':
                self.advance()
                return Token(TokenType.COMMA, char, self.line, start_col)
                
            raise LexerError(f"Unexpected character '{char}'", self.line, start_col)
            
        return Token(TokenType.EOF, '', self.line, self.column)
        
    def tokenize(self) -> List[Token]:
        """Tokenize the entire input text."""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens

# AST node types
class ASTNodeType(Enum):
    PROGRAM = "PROGRAM"
    FUNCTION_DECL = "FUNCTION_DECL"
    VARIABLE_DECL = "VARIABLE_DECL"
    ASSIGNMENT = "ASSIGNMENT"
    BINARY_OP = "BINARY_OP"
    UNARY_OP = "UNARY_OP"
    CALL = "CALL"
    IF_EXPR = "IF_EXPR"
    WHILE_LOOP = "WHILE_LOOP"
    FOR_LOOP = "FOR_LOOP"
    BLOCK = "BLOCK"
    INTEGER_LITERAL = "INTEGER_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    BOOLEAN_LITERAL = "BOOLEAN_LITERAL"
    IDENTIFIER = "IDENTIFIER"
    ARRAY_LITERAL = "ARRAY_LITERAL"
    DICT_LITERAL = "DICT_LITERAL"
    STACK_OP = "STACK_OP"
    RPN_EXPRESSION = "RPN_EXPRESSION"

# AST node
@dataclass
class ASTNode:
    type: ASTNodeType
    value: Optional[Union[str, int, float, dict]] = None
    children: List['ASTNode'] = field(default_factory=list)
    line: int = 0
    column: int = 0

# Parser error
class ParserError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Parser error at {line}:{column}: {message}")
        self.line = line
        self.column = column

# Parser
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        
    def advance(self):
        """Move to the next token."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
            
    def eat(self, token_type: TokenType):
        """Consume a token of the expected type."""
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            raise ParserError(
                f"Expected {token_type.value}, got {self.current_token.type.value if self.current_token else 'EOF'}",
                self.current_token.line if self.current_token else 0,
                self.current_token.column if self.current_token else 0
            )
            
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Peek at a token without consuming it."""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
        
    def parse_program(self) -> ASTNode:
        """Parse a complete program."""
        program = ASTNode(ASTNodeType.PROGRAM, line=1, column=1)
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.COMMENT:
                self.advance()
                continue
                
            statement = self.parse_statement()
            if statement:
                program.children.append(statement)
                
        return program
        
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement."""
        if not self.current_token:
            return None
            
        # Skip comments
        if self.current_token.type == TokenType.COMMENT:
            self.advance()
            return None
            
        # Function definition
        if self.current_token.type == TokenType.COLON:
            return self.parse_function_decl()
            
        # Variable declaration
        if self.current_token.type in (TokenType.LET, TokenType.VAR):
            return self.parse_variable_decl()
            
        # RPN expression
        return self.parse_rpn_expression()
        
    def parse_function_decl(self) -> ASTNode:
        """Parse a function declaration."""
        line, col = self.current_token.line, self.current_token.column
        self.eat(TokenType.COLON)
        
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            raise ParserError("Expected function name", line, col)
            
        func_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Parse parameter count
        if not self.current_token or self.current_token.type != TokenType.INTEGER:
            raise ParserError("Expected parameter count", line, col)
            
        param_count = int(self.current_token.value)
        self.eat(TokenType.INTEGER)
        
        if not self.current_token or self.current_token.type != TokenType.PARAM:
            raise ParserError("Expected 'param' keyword", line, col)
            
        self.eat(TokenType.PARAM)
        
        # Parse function body
        body = self.parse_block()
        
        # Expect semicolon at end of function
        # Only eat semicolon if it's actually there
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
        
        func_node = ASTNode(ASTNodeType.FUNCTION_DECL, func_name, [body], line, col)
        func_node.value = {"name": func_name, "param_count": param_count}
        return func_node
        
    def parse_variable_decl(self) -> ASTNode:
        """Parse a variable declaration."""
        line, col = self.current_token.line, self.current_token.column
        var_type = self.current_token.type
        self.eat(var_type)  # eat 'let' or 'var'
        
        if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
            raise ParserError("Expected variable name", line, col)
            
        var_name = self.current_token.value
        self.eat(TokenType.IDENTIFIER)
        
        # Parse the value expression
        value_expr = self.parse_rpn_expression()
        
        # Expect semicolon at end of declaration
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
        
        var_node = ASTNode(
            ASTNodeType.VARIABLE_DECL, 
            {"name": var_name, "mutable": var_type == TokenType.VAR}, 
            [value_expr] if value_expr else [],
            line, col
        )
        return var_node
        
    def parse_block(self) -> ASTNode:
        """Parse a block of statements."""
        line, col = self.current_token.line if self.current_token else 0, self.current_token.column if self.current_token else 0
        block = ASTNode(ASTNodeType.BLOCK, line=line, column=col)
        
        # Collect statements until we reach the end of the block
        while (self.current_token and 
               self.current_token.type not in (TokenType.SEMICOLON, TokenType.EOF, TokenType.RBRACE)):
            # If we encounter another function definition, it's not part of this block
            if self.current_token.type == TokenType.COLON:
                break
                
            statement = self.parse_statement()
            if statement:
                block.children.append(statement)
            # Special handling for 'else' - it's part of an if statement, not a separate statement
            elif self.current_token and self.current_token.type == TokenType.ELSE:
                break
                
        return block
        
    def parse_rpn_expression(self) -> Optional[ASTNode]:
        """Parse an RPN expression."""
        if not self.current_token:
            return None
            
        start_line = self.current_token.line
        start_col = self.current_token.column
        
        # Handle special constructs like if/else
        if self.current_token.type == TokenType.IF:
            return self.parse_if_expr()
            
        if self.current_token.type == TokenType.WHILE:
            return self.parse_while_loop()
            
        if self.current_token.type == TokenType.FOR:
            return self.parse_for_loop()
            
        # Collect tokens for a simple RPN expression
        expr_tokens = []
        while (self.current_token and 
               self.current_token.type not in (TokenType.SEMICOLON, TokenType.EOF, TokenType.ELSE, TokenType.IF, TokenType.WHILE, TokenType.FOR, TokenType.DO, TokenType.COLON, TokenType.RBRACE, TokenType.LET, TokenType.VAR)):
            if self.current_token.type == TokenType.COMMENT:
                self.advance()
                continue
            expr_tokens.append(self.current_token)
            self.advance()
            # Break if we've collected a reasonable number of tokens to avoid infinite loops
            if len(expr_tokens) > 100:  # Safety check
                break
                
        if not expr_tokens:
            return None
            
        # Create a simple representation of the RPN expression
        expr_values = [token.value for token in expr_tokens]
        return ASTNode(ASTNodeType.RPN_EXPRESSION, " ".join(expr_values), line=start_line, column=start_col)
        
    def parse_if_expr(self) -> ASTNode:
        """Parse an if expression."""
        line, col = self.current_token.line, self.current_token.column
        self.eat(TokenType.IF)
        
        # Parse condition
        condition = self.parse_rpn_expression()
        
        # Parse then branch
        then_branch = self.parse_block()
        
        # Parse else branch (optional)
        else_branch = None
        if self.current_token and self.current_token.type == TokenType.ELSE:
            self.eat(TokenType.ELSE)
            else_branch = self.parse_block()
            
        # Expect semicolon at end
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            
        children = [condition, then_branch]
        if else_branch:
            children.append(else_branch)
            
        return ASTNode(ASTNodeType.IF_EXPR, line=line, column=col, children=children)
        
    def parse_while_loop(self) -> ASTNode:
        """Parse a while loop."""
        line, col = self.current_token.line, self.current_token.column
        self.eat(TokenType.WHILE)
        
        # Parse condition
        condition = self.parse_rpn_expression()
        
        # Expect 'do' keyword
        if not self.current_token or self.current_token.type != TokenType.DO:
            raise ParserError("Expected 'do' keyword", self.current_token.line, self.current_token.column)
        self.eat(TokenType.DO)

        # Parse body
        body = self.parse_block()
        
        # Expect semicolon at end
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            
        return ASTNode(ASTNodeType.WHILE_LOOP, line=line, column=col, children=[condition, body])
        
    def parse_for_loop(self) -> ASTNode:
        """Parse a for loop."""
        line, col = self.current_token.line, self.current_token.column
        self.eat(TokenType.FOR)
        
        # Parse count expression (in RPN, the count is already on the stack)
        count_expr = ASTNode(ASTNodeType.RPN_EXPRESSION, "count", line=line, column=col)
        
        # Parse body
        body = self.parse_block()
        
        # Expect semicolon at end
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
            
        return ASTNode(ASTNodeType.FOR_LOOP, line=line, column=col, children=[count_expr, body])

# Opcode definitions
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

    # String operations
    STRING_LENGTH = "STRING_LENGTH"
    STRING_CONCAT = "STRING_CONCAT"
    STRING_SUBSTRING = "STRING_SUBSTRING"
    STRING_INDEXOF = "STRING_INDEXOF"

    # Halt
    HALT = "HALT"

# Instruction
@dataclass
class Instruction:
    opcode: Opcode
    operand: Optional[Union[int, float, str]] = None
    line: int = 0
    
    def __str__(self):
        if self.operand is not None:
            return f"{self.opcode.value} {self.operand}"
        return self.opcode.value

# Function
@dataclass
class Function:
    name: str
    param_count: int
    instructions: List[Instruction] = field(default_factory=list)

# Code generator error
class CodeGeneratorError(Exception):
    def __init__(self, message: str, line: int = 0):
        super().__init__(f"Code generation error at line {line}: {message}")
        self.line = line

# Code generator
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
        self.functions[func_name] = func
        
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
        # Condition expression
        self.generate_rpn_expression_node(node.children[0])
        
        # Emit jump to else/end with a placeholder
        jump_if_false_instr = Instruction(Opcode.JUMP_IF_FALSE, 0, node.line)
        self.emit(jump_if_false_instr)
        
        # Generate code for the 'then' block
        if len(node.children) > 1:
            self.generate_block(node.children[1])
            
        # If there is an 'else' block, we need to jump over it
        jump_over_else_instr = None
        if len(node.children) > 2:
            jump_over_else_instr = Instruction(Opcode.JUMP, 0, node.line)
            self.emit(jump_over_else_instr)
            
        # The target for the JUMP_IF_FALSE is the current instruction count
        jump_if_false_instr.operand = len(self.current_function.instructions)
        
        # Generate code for the 'else' block
        if len(node.children) > 2:
            self.generate_block(node.children[2])
            # The target for the JUMP is the current instruction count
            if jump_over_else_instr:
                jump_over_else_instr.operand = len(self.current_function.instructions)
            
    def generate_while_loop(self, node: ASTNode):
        """Generate code for a while loop."""
        loop_start = len(self.current_function.instructions)

        # The condition expression
        self.generate_rpn_expression_node(node.children[0])

        # loop body
        if len(node.children) > 1:
            self.generate_block(node.children[1])

        # drop the condition result
        self.emit(Instruction(Opcode.DROP, line=node.line))

        # jump to start
        self.emit(Instruction(Opcode.JUMP, loop_start, node.line))
        
    def generate_for_loop(self, node: ASTNode):
        """Generate code for a for loop."""
        # The count is on the stack
        
        # Store the initial count in a temporary variable
        count_var = "_for_count_" + str(node.line) # Unique name for each loop
        self.emit(Instruction(Opcode.STORE_VAR, self.add_constant(count_var), node.line))
        
        loop_start = len(self.current_function.instructions)
        
        # Load the counter
        self.emit(Instruction(Opcode.LOAD_VAR, self.add_constant(count_var), node.line))
        
        # Check if count > 0
        self.emit(Instruction(Opcode.LOAD_CONST, self.add_constant(0), node.line))
        self.emit(Instruction(Opcode.GT, line=node.line))
        jump_to_end = Instruction(Opcode.JUMP_IF_FALSE, 0, node.line)
        self.emit(jump_to_end)
        
        # Generate the loop body
        if len(node.children) > 1:
            self.generate_block(node.children[1])
            
        # Decrement the counter
        self.emit(Instruction(Opcode.LOAD_VAR, self.add_constant(count_var), node.line))
        self.emit(Instruction(Opcode.LOAD_CONST, self.add_constant(1), node.line))
        self.emit(Instruction(Opcode.SUB, line=node.line))
        self.emit(Instruction(Opcode.STORE_VAR, self.add_constant(count_var), node.line))
        
        # Jump back to the start of the loop
        self.emit(Instruction(Opcode.JUMP, loop_start, node.line))
        
        # Patch the jump instruction
        jump_to_end.operand = len(self.current_function.instructions)
        
        # Drop the final counter value
        self.emit(Instruction(Opcode.DROP, line=node.line))
        
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
                elif token.value == 'read_stdin':
                    self.emit(Instruction(Opcode.READ_STDIN, line=line))
                elif token.value == 'read_file':
                    self.emit(Instruction(Opcode.READ_FILE, line=line))
                elif token.value == 'create_array':
                    self.emit(Instruction(Opcode.CREATE_ARRAY, line=line))
                elif token.value == 'load_array':
                    self.emit(Instruction(Opcode.LOAD_ARRAY, line=line))
                elif token.value == 'store_array':
                    self.emit(Instruction(Opcode.STORE_ARRAY, line=line))
                elif token.value == 'array_length':
                    self.emit(Instruction(Opcode.ARRAY_LENGTH, line=line))
                elif token.value == 'create_dict':
                    self.emit(Instruction(Opcode.CREATE_DICT, line=line))
                elif token.value == 'load_dict':
                    self.emit(Instruction(Opcode.LOAD_DICT, line=line))
                elif token.value == 'store_dict':
                    self.emit(Instruction(Opcode.STORE_DICT, line=line))
                elif token.value == 'dict_has_key':
                    self.emit(Instruction(Opcode.DICT_HAS_KEY, line=line))
                elif token.value == 'dict_length':
                    self.emit(Instruction(Opcode.DICT_LENGTH, line=line))
                elif token.value == 'string_length':
                    self.emit(Instruction(Opcode.STRING_LENGTH, line=line))
                elif token.value == 'string_concat':
                    self.emit(Instruction(Opcode.STRING_CONCAT, line=line))
                elif token.value == 'string_substring':
                    self.emit(Instruction(Opcode.STRING_SUBSTRING, line=line))
                elif token.value == 'string_indexof':
                    self.emit(Instruction(Opcode.STRING_INDEXOF, line=line))
                else:
                    # Check if it's a function call
                    if token.value in self.functions:
                        const_idx = self.add_constant(token.value)
                        self.emit(Instruction(Opcode.CALL, const_idx, line))
                    else:
                        # Assume it's a variable load
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

def compile_source_to_bytecode(filename: str) -> dict:
    """Compile a PostC source file to bytecode and return as a dictionary."""
    # Read the source file
    with open(filename, 'r') as f:
        source = f.read()
    
    print(f"Compiling {filename}...")
    
    # Lexical analysis
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    # Parsing
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    # Code generation
    codegen = CodeGenerator()
    codegen.generate_code(ast)
    
    # Return the compiled bytecode as a dictionary
    return {
        "constants": codegen.constants,
        "functions": {name: {
            "name": func.name,
            "param_count": func.param_count,
            "instructions": [str(instr) for instr in func.instructions]
        } for name, func in codegen.functions.items()}
    }

def save_bytecode_to_file(bytecode: dict, output_filename: str):
    """Save compiled bytecode to a file in JSON format."""
    with open(output_filename, 'w') as f:
        json.dump(bytecode, f, indent=2)
    print(f"Bytecode saved to {output_filename}")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 compiler.py <source_file> [output_file]")
        return
        
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return
        
    # Determine output filename
    if len(sys.argv) > 2:
        output_filename = sys.argv[2]
    else:
        # Replace .pc extension with .pcc (PostC Compiled)
        if filename.endswith('.pc'):
            output_filename = filename[:-3] + '.pcc'
        else:
            output_filename = filename + '.pcc'
    
    try:
        bytecode = compile_source_to_bytecode(filename)
        save_bytecode_to_file(bytecode, output_filename)
        print("Compilation finished.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()