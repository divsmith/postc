#!/usr/bin/env python3

"""
PostC Bootstrap Tool
Main entry point for the PostC bootstrap compiler, VM, and WASM target.
"""

import sys
import os

def show_help():
    """Show usage information."""
    print("PostC Bootstrap Tool")
    print("Usage:")
    print("  python3 postc.py compile <source_file> [output_file]     # Compile PostC source to bytecode")
    print("  python3 postc.py run <bytecode_file>                     # Run compiled PostC bytecode")
    print("  python3 postc.py wasm <bytecode_file> <output_file>      # Compile PostC bytecode to WASM")
    print("  python3 postc.py help                                    # Show this help message")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        show_help()
        return
        
    command = sys.argv[1]
    
    if command == "compile":
        if len(sys.argv) < 3:
            print("Error: Missing source file for compile command")
            show_help()
            return
            
        # Import and run compiler
        from compiler.compiler import main as compile_main
        sys.argv = [sys.argv[0]] + sys.argv[2:]  # Adjust argv for compiler
        compile_main()
        
    elif command == "run":
        if len(sys.argv) < 3:
            print("Error: Missing bytecode file for run command")
            show_help()
            return
            
        # Import and run VM
        from vm.vm import main as run_main
        sys.argv = [sys.argv[0]] + sys.argv[2:]  # Adjust argv for VM
        run_main()
        
    elif command == "wasm":
        if len(sys.argv) < 4:
            print("Error: Missing bytecode file or output file for wasm command")
            show_help()
            return
            
        # Import and run WASM compiler
        from wasm.wasm_target import compile_to_wasm
        bytecode_file = sys.argv[2]
        output_file = sys.argv[3]
        if not os.path.exists(bytecode_file):
            print(f"Error: File '{bytecode_file}' not found")
            return
        try:
            compile_to_wasm(bytecode_file, output_file)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        
    elif command == "help":
        show_help()
        
    else:
        print(f"Error: Unknown command '{command}'")
        show_help()

if __name__ == '__main__':
    main()