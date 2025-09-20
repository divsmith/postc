#!/bin/bash

# Build script for PostC compiler

echo "Building PostC compiler..."

# Compile each component
echo "Compiling lexer..."
python3 bootstrap/postc.py postc-compiler/lexer.pc

echo "Compiling parser..."
python3 bootstrap/postc.py postc-compiler/parser.pc

echo "Compiling code generator..."
python3 bootstrap/postc.py postc-compiler/codegen.pc

echo "Compiling main compiler..."
python3 bootstrap/postc.py postc-compiler/compiler.pc

echo "PostC compiler build complete!"