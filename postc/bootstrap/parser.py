#!/usr/bin/env python3

"""
PostC Bootstrap Compiler - Parser
Parses tokens into an Abstract Syntax Tree (AST).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Union

from lexer import Token, TokenType

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

@dataclass
class ASTNode:
    type: ASTNodeType
    value: Optional[Union[str, int, float, dict]] = None
    children: List['ASTNode'] = field(default_factory=list)
    line: int = 0
    column: int = 0

class ParserError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Parser error at {line}:{column}: {message}")
        self.line = line
        self.column = column

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
               self.current_token.type not in (TokenType.SEMICOLON, TokenType.EOF, TokenType.ELSE, TokenType.IF, TokenType.WHILE, TokenType.FOR, TokenType.COLON, TokenType.RBRACE, TokenType.LET, TokenType.VAR)):
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
        
        # Parse condition (in RPN, the condition is already on the stack)
        condition = ASTNode(ASTNodeType.RPN_EXPRESSION, "condition", line=line, column=col)
        
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
        
        # Parse condition (in RPN, the condition is already on the stack)
        condition = ASTNode(ASTNodeType.RPN_EXPRESSION, "condition", line=line, column=col)
        
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

def main():
    """Simple test function for the parser."""
    import sys
    from lexer import Lexer
    
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
    
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse_program()
    
    # Simple AST printer
    def print_ast(node, indent=0):
        prefix = "  " * indent
        if node.value is not None:
            print(f"{prefix}{node.type.value}: {node.value}")
        else:
            print(f"{prefix}{node.type.value}")
            
        for child in node.children:
            print_ast(child, indent + 1)
    
    print_ast(ast)

if __name__ == '__main__':
    main()