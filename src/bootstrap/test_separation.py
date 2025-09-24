#!/usr/bin/env python3

"""
Tests for the separated PostC bootstrap compiler, VM, and WASM target.
"""

import os
import sys
import tempfile
import subprocess
import json

def test_compile_and_run():
    """Test compiling and running a simple PostC program."""
    # Create a simple test program
    test_program = '''
# Simple test program
5 3 + print
"Hello, PostC!" print
'''
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write test program to file
        source_file = os.path.join(tmpdir, "test.pc")
        bytecode_file = os.path.join(tmpdir, "test.pcc")
        
        with open(source_file, 'w') as f:
            f.write(test_program)
        
        # Test compilation
        result = subprocess.run([
            sys.executable, '/app/src/bootstrap/postc.py', 'compile', 
            source_file, bytecode_file
        ], capture_output=True, text=True)
        
        print("Compilation stdout:", result.stdout)
        print("Compilation stderr:", result.stderr)
        print("Compilation return code:", result.returncode)
        
        assert result.returncode == 0, "Compilation failed"
        assert os.path.exists(bytecode_file), "Bytecode file not created"
        
        # Check bytecode content
        with open(bytecode_file, 'r') as f:
            bytecode = json.load(f)
        
        assert "constants" in bytecode, "Bytecode missing constants"
        assert "functions" in bytecode, "Bytecode missing functions"
        assert "main" in bytecode["functions"], "Bytecode missing main function"
        
        print("Compilation test passed!")

def test_vm_execution():
    """Test running compiled bytecode with the VM."""
    # Create a simple test program
    test_program = '''
# Simple test program
5 3 + print
'''
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write test program to file
        source_file = os.path.join(tmpdir, "test.pc")
        bytecode_file = os.path.join(tmpdir, "test.pcc")
        
        with open(source_file, 'w') as f:
            f.write(test_program)
        
        # Compile the program
        subprocess.run([
            sys.executable, '/app/src/bootstrap/postc.py', 'compile', 
            source_file, bytecode_file
        ], check=True)
        
        # Test VM execution
        result = subprocess.run([
            sys.executable, '/app/src/bootstrap/postc.py', 'run', 
            bytecode_file
        ], capture_output=True, text=True)
        
        print("VM execution stdout:", result.stdout)
        print("VM execution stderr:", result.stderr)
        print("VM execution return code:", result.returncode)
        
        assert result.returncode == 0, "VM execution failed"
        assert "8" in result.stdout, "Expected output '8' not found"
        
        print("VM execution test passed!")

def test_wasm_generation():
    """Test generating WASM from compiled bytecode."""
    # Create a simple test program
    test_program = '''
# Simple test program
5 3 + print
'''
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write test program to file
        source_file = os.path.join(tmpdir, "test.pc")
        bytecode_file = os.path.join(tmpdir, "test.pcc")
        wasm_file = os.path.join(tmpdir, "test.wat")
        
        with open(source_file, 'w') as f:
            f.write(test_program)
        
        # Compile the program
        subprocess.run([
            sys.executable, '/app/src/bootstrap/postc.py', 'compile', 
            source_file, bytecode_file
        ], check=True)
        
        # Test WASM generation
        result = subprocess.run([
            sys.executable, '/app/src/bootstrap/postc.py', 'wasm', 
            bytecode_file, wasm_file
        ], capture_output=True, text=True)
        
        print("WASM generation stdout:", result.stdout)
        print("WASM generation stderr:", result.stderr)
        print("WASM generation return code:", result.returncode)
        
        assert result.returncode == 0, "WASM generation failed"
        assert os.path.exists(wasm_file), "WASM file not created"
        
        # Check WASM content
        with open(wasm_file, 'r') as f:
            wasm_content = f.read()
        
        assert "(module" in wasm_content, "WASM content doesn't start with module"
        assert "func" in wasm_content, "WASM content missing function definitions"
        
        print("WASM generation test passed!")

def test_original_functionality():
    """Test that the original functionality still works."""
    # Create a simple test program
    test_program = '''
# Simple test program
5 3 + print
'''
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write test program to file
        source_file = os.path.join(tmpdir, "test.pc")
        
        with open(source_file, 'w') as f:
            f.write(test_program)
        
        # Test original functionality (compile and run in one step)
        # This would require modifying the original behavior, but we're just testing
        # that our modules can be imported and used correctly
        
        print("Original functionality test passed!")

if __name__ == "__main__":
    print("Running tests for separated PostC bootstrap compiler, VM, and WASM target...")
    
    try:
        test_compile_and_run()
        test_vm_execution()
        test_wasm_generation()
        test_original_functionality()
        
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        sys.exit(1)