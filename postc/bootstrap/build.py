#!/usr/bin/env python3

"""
PostC Bootstrap Compiler - Build script
Compiles and runs PostC programs.
"""

import sys
import os

from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator
from vm import VM

def compile_and_run(filename):
    """Compile and run a PostC source file."""
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
    
    # Prepare functions for VM
    functions = {name: func.instructions for name, func in codegen.functions.items()}
    
    # Create VM and run
    print("Running program...")
    vm = VM(codegen.constants, functions)
    vm.run()
    
    print("Program finished.")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python3 build.py <source_file>")
        return
        
    filename = sys.argv[1]
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found")
        return
        
    try:
        compile_and_run(filename)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()