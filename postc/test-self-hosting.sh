#!/bin/bash

# Test script for self-hosting PostC compiler

echo "Testing self-hosting PostC compiler..."

# Compile the lexer with the PostC compiler
echo "Compiling lexer with PostC compiler..."
python3 bootstrap/build.py postc-compiler/lexer.pc > lexer.output

# Check if compilation was successful
if [ $? -eq 0 ]; then
    echo "Lexer compiled successfully with PostC compiler"
else
    echo "Failed to compile lexer with PostC compiler"
    exit 1
fi

echo "Self-hosting test complete!"