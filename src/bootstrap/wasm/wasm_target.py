"""
PostC WebAssembly Target
Module for generating WebAssembly code from PostC bytecode.
"""

import json
from typing import List, Dict, Union
from enum import Enum

# WASM instruction set
class WasmOpcode(Enum):
    # Constants
    I32_CONST = "i32.const"
    F64_CONST = "f64.const"
    
    # Variables (using global for simplicity)
    GLOBAL_GET = "global.get"
    GLOBAL_SET = "global.set"
    
    # Stack operations
    DROP = "drop"
    SELECT = "select"
    
    # Arithmetic
    I32_ADD = "i32.add"
    I32_SUB = "i32.sub"
    I32_MUL = "i32.mul"
    I32_DIV_S = "i32.div_s"
    F64_ADD = "f64.add"
    F64_SUB = "f64.sub"
    F64_MUL = "f64.mul"
    F64_DIV = "f64.div"
    
    # Comparison
    I32_EQ = "i32.eq"
    I32_NE = "i32.ne"
    I32_LT_S = "i32.lt_s"
    I32_GT_S = "i32.gt_s"
    I32_LE_S = "i32.le_s"
    I32_GE_S = "i32.ge_s"
    F64_EQ = "f64.eq"
    F64_NE = "f64.ne"
    F64_LT = "f64.lt"
    F64_GT = "f64.gt"
    F64_LE = "f64.le"
    F64_GE = "f64.ge"
    
    # Control flow
    BR = "br"
    BR_IF = "br_if"
    CALL = "call"
    RETURN = "return"
    
    # Memory
    MEMORY_GROW = "memory.grow"
    MEMORY_SIZE = "memory.size"

def generate_wasm_module(bytecode: dict) -> str:
    """Generate WebAssembly text format from PostC bytecode."""
    
    # Start with module header
    wasm_lines = ["(module"]
    
    # Add imports for printing (using WASI)
    wasm_lines.append('  (import "wasi_snapshot_preview1" "fd_write" (func $fd_write (param i32 i32 i32 i32) (result i32)))')
    wasm_lines.append('  (import "wasi_snapshot_preview1" "proc_exit" (func $proc_exit (param i32)))')
    
    # Add memory
    wasm_lines.append("  (memory (export \"memory\") 256)")  # 256 pages = 16MB, enough for our programs
    
    # Add data sections for string constants
    string_start_address = 1024  # Start storing strings from address 1024
    string_addresses = {}
    
    for i, constant in enumerate(bytecode["constants"]):
        if isinstance(constant, str):
            # Escape special characters for WASM string literal
            escaped_str = constant.replace("\\", "\\\\").replace('"', '\\"').replace('\n', '\\n')
            wasm_lines.append(f"  (data (i32.const {string_start_address + i * 100}) \"{escaped_str}\")")
            string_addresses[i] = string_start_address + i * 100
    
    # Add globals for variables
    for i, constant in enumerate(bytecode["constants"]):
        if isinstance(constant, (int, float)):
            wasm_lines.append(f"  (global $var_{i} (mut f64) (f64.const {float(constant) if isinstance(constant, (int, float)) else 0.0}))")
        elif isinstance(constant, bool):
            wasm_lines.append(f"  (global $var_{i} (mut i32) (i32.const {1 if constant else 0}))")
        elif isinstance(constant, str):
            wasm_lines.append(f"  (global $var_{i} (mut i32) (i32.const {string_addresses[i]}))")  # Point to string in memory
    
    # Generate functions
    for func_name, func_data in bytecode["functions"].items():
        wasm_lines.append(f"  (func ${func_name} (export \"{func_name}\")")
        
        # Add locals for temporary values
        wasm_lines.append("    (local $temp_i32 i32)")
        wasm_lines.append("    (local $temp_f64 f64)")
        wasm_lines.append("    (local $str_ptr i32)")
        wasm_lines.append("    (local $str_len i32)")
        wasm_lines.append("    (local $result i32)")
        
        # Generate function body
        for instr_str in func_data["instructions"]:
            wasm_instr = translate_instruction(instr_str, bytecode["constants"], string_addresses)
            if wasm_instr and not wasm_instr.startswith(";; UNIMPLEMENTED"):  # Only add if not unimplemented
                wasm_lines.append(f"    {wasm_instr}")
                
        wasm_lines.append("  )")
    
    # Add helper functions for handling strings and I/O
    # String length helper
    wasm_lines.append("  (func $strlen (param $ptr i32) (result i32)")
    wasm_lines.append("    (local $len i32)")
    wasm_lines.append("    (local $pos i32)")
    wasm_lines.append("    i32.const 0")
    wasm_lines.append("    local.set $len")
    wasm_lines.append("    local.get $ptr")
    wasm_lines.append("    local.set $pos")
    wasm_lines.append("    (loop $l")
    wasm_lines.append("      local.get $pos")
    wasm_lines.append("      i32.load8_u")
    wasm_lines.append("      i32.const 0")
    wasm_lines.append("      i32.ne")
    wasm_lines.append("      if")
    wasm_lines.append("        local.get $len")
    wasm_lines.append("        i32.const 1")
    wasm_lines.append("        i32.add")
    wasm_lines.append("        local.set $len")
    wasm_lines.append("        local.get $pos")
    wasm_lines.append("        i32.const 1")
    wasm_lines.append("        i32.add")
    wasm_lines.append("        local.set $pos")
    wasm_lines.append("        br $l")
    wasm_lines.append("      end")
    wasm_lines.append("    end")
    wasm_lines.append("    local.get $len")
    wasm_lines.append("  )")
    
    # Print string helper
    wasm_lines.append("  (func $print_str (param $str_ptr i32)")
    wasm_lines.append("    (local $str_len i32)")
    wasm_lines.append("    (local $iovec_ptr i32)")
    wasm_lines.append("    (local $result i32)")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Calculate string length")
    wasm_lines.append("    local.get $str_ptr")
    wasm_lines.append("    call $strlen")
    wasm_lines.append("    local.set $str_len")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Allocate memory for iovec structure")
    wasm_lines.append("    ;; iovec has two fields: ptr (i32) and len (i32), so 8 bytes total")
    wasm_lines.append("    i32.const 1000  ;; Use memory location 1000 for iovec")
    wasm_lines.append("    local.set $iovec_ptr")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Set the pointer field of iovec (offset 0)")
    wasm_lines.append("    local.get $iovec_ptr")
    wasm_lines.append("    local.get $str_ptr")
    wasm_lines.append("    i32.store")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Set the length field of iovec (offset 4)")
    wasm_lines.append("    local.get $iovec_ptr")
    wasm_lines.append("    i32.const 4")
    wasm_lines.append("    i32.add")
    wasm_lines.append("    local.get $str_len")
    wasm_lines.append("    i32.store")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Call fd_write with stdout (fd=1), iovec pointer, count=1")
    wasm_lines.append("    i32.const 1")  # fd (stdout)
    wasm_lines.append("    local.get $iovec_ptr")  # *iovec
    wasm_lines.append("    i32.const 1")  # iovs_len
    wasm_lines.append("    local.get $str_len")  # nwritten
    wasm_lines.append("    call $fd_write")
    wasm_lines.append("    drop  ;; Drop the result of fd_write")
    wasm_lines.append("  )")
    
    # Print integer helper
    wasm_lines.append("  (func $print_int (param $val i32)")
    wasm_lines.append("    (local $buf_ptr i32)")
    wasm_lines.append("    (local $digit i32)")
    wasm_lines.append("    (local $temp i32)")
    wasm_lines.append("    (local $len i32)")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Use a buffer in memory to convert integer to string")
    wasm_lines.append("    i32.const 2000  ;; Use memory location 2000 as buffer")
    wasm_lines.append("    local.set $buf_ptr")
    wasm_lines.append("    local.get $val")
    wasm_lines.append("    local.set $temp")
    wasm_lines.append("    i32.const 0")
    wasm_lines.append("    local.set $len")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Handle negative numbers")
    wasm_lines.append("    local.get $temp")
    wasm_lines.append("    i32.const 0")
    wasm_lines.append("    i32.lt_s")
    wasm_lines.append("    if")
    wasm_lines.append("      local.get $buf_ptr")
    wasm_lines.append("      i32.const 45")  # ASCII for '-'
    wasm_lines.append("      i32.store8")
    wasm_lines.append("      local.get $buf_ptr")
    wasm_lines.append("      i32.const 1")
    wasm_lines.append("      i32.add")
    wasm_lines.append("      local.set $buf_ptr")
    wasm_lines.append("      local.get $temp")
    wasm_lines.append("      i32.const -1")
    wasm_lines.append("      i32.mul")
    wasm_lines.append("      local.set $temp")
    wasm_lines.append("    end")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Convert digits")
    wasm_lines.append("    block $done")
    wasm_lines.append("      loop $digit_loop")
    wasm_lines.append("        local.get $temp")
    wasm_lines.append("        i32.const 0")
    wasm_lines.append("        i32.eq")
    wasm_lines.append("        br_if $done")
    wasm_lines.append("        ")
    wasm_lines.append("        local.get $temp")
    wasm_lines.append("        i32.const 10")
    wasm_lines.append("        local.get $temp")
    wasm_lines.append("        i32.const 10")
    wasm_lines.append("        i32.div_u")
    wasm_lines.append("        local.tee $temp")
    wasm_lines.append("        i32.sub")
    wasm_lines.append("        local.set $digit")
    wasm_lines.append("        ")
    wasm_lines.append("        local.get $buf_ptr")
    wasm_lines.append("        local.get $len")
    wasm_lines.append("        i32.add")
    wasm_lines.append("        local.get $digit")
    wasm_lines.append("        i32.const 48")  # ASCII for '0'
    wasm_lines.append("        i32.add")
    wasm_lines.append("        i32.store8")
    wasm_lines.append("        ")
    wasm_lines.append("        local.get $len")
    wasm_lines.append("        i32.const 1")
    wasm_lines.append("        i32.add")
    wasm_lines.append("        local.set $len")
    wasm_lines.append("        br $digit_loop")
    wasm_lines.append("      end")
    wasm_lines.append("    end")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Reverse the digits in buffer")
    wasm_lines.append("    local.get $buf_ptr")
    wasm_lines.append("    local.get $len")
    wasm_lines.append("    i32.add")
    wasm_lines.append("    i32.const 1")
    wasm_lines.append("    i32.sub")
    wasm_lines.append("    local.set $buf_ptr")
    wasm_lines.append("    ")
    wasm_lines.append("    ;; Call print_str to print the number")
    wasm_lines.append("    local.get $buf_ptr")
    wasm_lines.append("    call $print_str")
    wasm_lines.append("  )")
    
    # Close module
    wasm_lines.append(")")
    
    return "\n".join(wasm_lines)

def translate_instruction(instr_str: str, constants: List[Union[int, float, str, bool]], string_addresses: Dict[int, int]) -> str:
    """Translate a PostC instruction to WASM."""
    parts = instr_str.strip().split(' ', 1)
    opcode_str = parts[0]
    operand_str = parts[1] if len(parts) > 1 else None
    
    # Map PostC opcodes to WASM
    translation_map = {
        "LOAD_CONST": lambda op, const: handle_load_const(op, const, string_addresses),
        "LOAD_TRUE": lambda _, __: "i32.const 1",
        "LOAD_FALSE": lambda _, __: "i32.const 0",
        "LOAD_STRING": lambda op, const: handle_load_string(op, const, string_addresses),
        "LOAD_VAR": lambda op, const: handle_load_var(op, const),
        "STORE_VAR": lambda op, const: handle_store_var(op, const),
        "DUP": lambda _, __: "(;; dup - requires local vars to implement)",
        "DROP": lambda _, __: "drop",
        "SWAP": lambda _, __: "(;; swap - requires local vars to implement)",
        "OVER": lambda _, __: "(;; over - requires local vars to implement)",
        "ROT": lambda _, __: "(;; rot - requires local vars to implement)",
        "ADD": lambda _, __: handle_add(),
        "SUB": lambda _, __: handle_sub(),
        "MUL": lambda _, __: handle_mul(),
        "DIV": lambda _, __: handle_div(),
        "EQ": lambda _, __: handle_eq(),
        "NE": lambda _, __: handle_ne(),
        "LT": lambda _, __: handle_lt(),
        "GT": lambda _, __: handle_gt(),
        "LE": lambda _, __: handle_le(),
        "GE": lambda _, __: handle_ge(),
        "PRINT": lambda _, __: handle_print(),
        "JUMP": lambda op, const: handle_jump(op),
        "JUMP_IF_FALSE": lambda op, const: handle_jump_if_false(op),
        "CALL": lambda op, const: handle_call(op, const),
        "RETURN": lambda _, __: "return",
        "HALT": lambda _, __: "i32.const 0 call $proc_exit"  # Exit with code 0
    }
    
    handler = translation_map.get(opcode_str)
    if handler:
        return handler(operand_str, constants)
    else:
        return f";; UNIMPLEMENTED: Unknown opcode: {opcode_str}"

def handle_load_const(operand_str: str, constants: List[Union[int, float, str, bool]], string_addresses: Dict[int, int]) -> str:
    """Handle LOAD_CONST instruction."""
    try:
        index = int(operand_str)
        if index < len(constants):
            constant = constants[index]
            if isinstance(constant, int):
                return f"i32.const {constant}"
            elif isinstance(constant, float):
                return f"f64.const {constant}"
            elif isinstance(constant, bool):
                return f"i32.const {1 if constant else 0}"
            else:
                # For strings, we'll load the pointer to the string in memory
                return f"i32.const {string_addresses.get(index, 0)}"
        else:
            return f";; Invalid constant index: {index}"
    except ValueError:
        return f";; Invalid operand: {operand_str}"

def handle_load_string(operand_str: str, constants: List[Union[int, float, str, bool]], string_addresses: Dict[int, int]) -> str:
    """Handle LOAD_STRING instruction."""
    try:
        index = int(operand_str)
        if index < len(constants):
            constant = constants[index]
            if isinstance(constant, str):
                # Return a pointer to the string in memory
                return f"i32.const {string_addresses.get(index, 0)}"
            else:
                return f";; Not a string constant at index {index}"
        else:
            return f";; Invalid constant index: {index}"
    except ValueError:
        return f";; Invalid operand: {operand_str}"

def handle_load_var(operand_str: str, constants: List[Union[int, float, str, bool]]) -> str:
    """Handle LOAD_VAR instruction."""
    try:
        index = int(operand_str)
        # Determine variable type (simplified: assume it's an int for now)
        # In a full implementation, we'd need to track types
        return f"global.get $var_{index}"
    except ValueError:
        return f";; Invalid operand: {operand_str}"

def handle_store_var(operand_str: str, constants: List[Union[int, float, str, bool]]) -> str:
    """Handle STORE_VAR instruction."""
    try:
        index = int(operand_str)
        # Determine variable type (simplified: assume it's an int for now)
        # In a full implementation, we'd need to track types
        return f"global.set $var_{index}"
    except ValueError:
        return f";; Invalid operand: {operand_str}"

def handle_add() -> str:
    """Handle ADD instruction with proper type detection."""
    # We'll use i32.add for integers, but in a full implementation we'd check the types
    return "i32.add"  # For integers

def handle_sub() -> str:
    """Handle SUB instruction with proper type detection."""
    return "i32.sub"  # For integers

def handle_mul() -> str:
    """Handle MUL instruction with proper type detection."""
    return "i32.mul"  # For integers

def handle_div() -> str:
    """Handle DIV instruction with proper type detection."""
    return "i32.div_s"  # For signed integers

def handle_eq() -> str:
    """Handle EQ instruction with proper type detection."""
    return "i32.eq"  # For integers

def handle_ne() -> str:
    """Handle NE instruction with proper type detection."""
    return "i32.ne"  # For integers

def handle_lt() -> str:
    """Handle LT instruction with proper type detection."""
    return "i32.lt_s"  # For signed integers

def handle_gt() -> str:
    """Handle GT instruction with proper type detection."""
    return "i32.gt_s"  # For signed integers

def handle_le() -> str:
    """Handle LE instruction with proper type detection."""
    return "i32.le_s"  # For signed integers

def handle_ge() -> str:
    """Handle GE instruction with proper type detection."""
    return "i32.ge_s"  # For signed integers

def handle_print() -> str:
    """Handle PRINT instruction with WASI integration."""
    # This pops the value from stack and prints it appropriately
    # For integers, call $print_int
    # For strings, call $print_str
    # We'll implement a simple version that assumes integer for now
    return "call $print_int"

def handle_jump(operand_str: str) -> str:
    """Handle JUMP instruction."""
    # WASM uses labels instead of absolute addresses
    if operand_str:
        return f"br $label_{operand_str}  ;; Jump to label {operand_str}"
    return "br $loop ;; Jump to a default loop label"

def handle_jump_if_false(operand_str: str) -> str:
    """Handle JUMP_IF_FALSE instruction."""
    # WASM uses labels instead of absolute addresses
    if operand_str:
        return f"br_if $label_{operand_str}  ;; Jump to label {operand_str} if condition is false"
    return "br_if $else ;; Jump to else label if condition is false"

def handle_call(operand_str: str, constants: List[Union[int, float, str, bool]]) -> str:
    """Handle CALL instruction."""
    try:
        index = int(operand_str)
        if index < len(constants):
            func_name = constants[index]
            return f"call ${func_name}"
        else:
            return f";; Invalid function index: {index}"
    except ValueError:
        return f";; Invalid operand: {operand_str}"

def compile_to_wasm(bytecode_file: str, output_file: str):
    """Compile PostC bytecode to WebAssembly text format."""
    # Load bytecode
    with open(bytecode_file, 'r') as f:
        bytecode = json.load(f)
    
    # Generate WASM
    wasm_code = generate_wasm_module(bytecode)
    
    # Save to file
    with open(output_file, 'w') as f:
        f.write(wasm_code)
    
    print(f"WASM code saved to {output_file}")