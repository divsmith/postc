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
    
    # Add memory
    wasm_lines.append("  (memory (export \"memory\") 1)")
    
    # Add globals for variables
    for i, constant in enumerate(bytecode["constants"]):
        if isinstance(constant, (int, float)):
            wasm_lines.append(f"  (global $var_{i} (mut f64) (f64.const 0.0))")
        elif isinstance(constant, str):
            wasm_lines.append(f"  (global $var_{i} (mut i32) (i32.const 0))")
        elif isinstance(constant, bool):
            wasm_lines.append(f"  (global $var_{i} (mut i32) (i32.const 0))")
    
    # Generate functions
    for func_name, func_data in bytecode["functions"].items():
        wasm_lines.append(f"  (func ${func_name} (export \"{func_name}\")")
        
        # Add locals (simplified)
        wasm_lines.append("    (local $temp i32)")
        
        # Generate function body
        for instr_str in func_data["instructions"]:
            wasm_instr = translate_instruction(instr_str, bytecode["constants"])
            if wasm_instr:
                wasm_lines.append(f"    {wasm_instr}")
                
        wasm_lines.append("  )")
    
    # Close module
    wasm_lines.append(")")
    
    return "\n".join(wasm_lines)

def translate_instruction(instr_str: str, constants: List[Union[int, float, str, bool]]) -> str:
    """Translate a PostC instruction to WASM."""
    parts = instr_str.strip().split(' ', 1)
    opcode_str = parts[0]
    operand_str = parts[1] if len(parts) > 1 else None
    
    # Map PostC opcodes to WASM
    translation_map = {
        "LOAD_CONST": handle_load_const,
        "LOAD_TRUE": lambda _: "i32.const 1",
        "LOAD_FALSE": lambda _: "i32.const 0",
        "LOAD_STRING": handle_load_string,
        "LOAD_VAR": handle_load_var,
        "STORE_VAR": handle_store_var,
        "DUP": lambda _: ";; dup (no direct equivalent, would need to implement with locals)",
        "DROP": lambda _: "drop",
        "SWAP": lambda _: ";; swap (no direct equivalent, would need to implement with locals)",
        "OVER": lambda _: ";; over (no direct equivalent, would need to implement with locals)",
        "ROT": lambda _: ";; rot (no direct equivalent, would need to implement with locals)",
        "ADD": handle_add,
        "SUB": handle_sub,
        "MUL": handle_mul,
        "DIV": handle_div,
        "EQ": handle_eq,
        "NE": handle_ne,
        "LT": handle_lt,
        "GT": handle_gt,
        "LE": handle_le,
        "GE": handle_ge,
        "PRINT": lambda _: ";; print (would need to implement with WASI)",
        "JUMP": handle_jump,
        "JUMP_IF_FALSE": handle_jump_if_false,
        "CALL": handle_call,
        "RETURN": lambda _: "return",
        "HALT": lambda _: "return"
    }
    
    handler = translation_map.get(opcode_str)
    if handler:
        return handler(operand_str, constants) if operand_str else handler(None)
    else:
        return f";; Unknown opcode: {opcode_str}"

def handle_load_const(operand_str: str, constants: List[Union[int, float, str, bool]]) -> str:
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
                return f";; String constant: {constant}"
        else:
            return f";; Invalid constant index: {index}"
    except ValueError:
        return f";; Invalid operand: {operand_str}"

def handle_load_string(operand_str: str, constants: List[Union[int, float, str, bool]]) -> str:
    """Handle LOAD_STRING instruction."""
    try:
        index = int(operand_str)
        if index < len(constants):
            constant = constants[index]
            if isinstance(constant, str):
                # For simplicity, just comment on what would be done
                return f";; Loading string: {constant}"
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
        return f"global.get $var_{index}"
    except ValueError:
        return f";; Invalid operand: {operand_str}"

def handle_store_var(operand_str: str, constants: List[Union[int, float, str, bool]]) -> str:
    """Handle STORE_VAR instruction."""
    try:
        index = int(operand_str)
        return f"global.set $var_{index}"
    except ValueError:
        return f";; Invalid operand: {operand_str}"

def handle_add(operand_str: str) -> str:
    """Handle ADD instruction."""
    # Simplified - would need type checking in a real implementation
    return ";; add (would need to determine if i32.add or f64.add)"

def handle_sub(operand_str: str) -> str:
    """Handle SUB instruction."""
    return ";; sub (would need to determine if i32.sub or f64.sub)"

def handle_mul(operand_str: str) -> str:
    """Handle MUL instruction."""
    return ";; mul (would need to determine if i32.mul or f64.mul)"

def handle_div(operand_str: str) -> str:
    """Handle DIV instruction."""
    return ";; div (would need to determine if i32.div_s or f64.div)"

def handle_eq(operand_str: str) -> str:
    """Handle EQ instruction."""
    return ";; eq (would need to determine if i32.eq or f64.eq)"

def handle_ne(operand_str: str) -> str:
    """Handle NE instruction."""
    return ";; ne (would need to determine if i32.ne or f64.ne)"

def handle_lt(operand_str: str) -> str:
    """Handle LT instruction."""
    return ";; lt (would need to determine if i32.lt_s or f64.lt)"

def handle_gt(operand_str: str) -> str:
    """Handle GT instruction."""
    return ";; gt (would need to determine if i32.gt_s or f64.gt)"

def handle_le(operand_str: str) -> str:
    """Handle LE instruction."""
    return ";; le (would need to determine if i32.le_s or f64.le)"

def handle_ge(operand_str: str) -> str:
    """Handle GE instruction."""
    return ";; ge (would need to determine if i32.ge_s or f64.ge)"

def handle_jump(operand_str: str, constants: List[Union[int, float, str, bool]]) -> str:
    """Handle JUMP instruction."""
    return f";; jump to {operand_str} (would need to implement with labels)"

def handle_jump_if_false(operand_str: str, constants: List[Union[int, float, str, bool]]) -> str:
    """Handle JUMP_IF_FALSE instruction."""
    return f";; jump_if_false to {operand_str} (would need to implement with labels)"

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