#!/usr/bin/env python3

"""
PostC Bootstrap Compiler - Lexer
Tokenizes PostC source code into a stream of tokens.
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Iterator

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

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.value}, {self.value}, {self.line}:{self.column})"

class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Lexer error at {line}:{column}: {message}")
        self.line = line
        self.column = column

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

def main():
    """Simple test function for the lexer."""
    import sys
    
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
    
    for token in tokens:
        print(token)

if __name__ == '__main__':
    main()