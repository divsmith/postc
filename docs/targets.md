# PostC Compilation Targets

PostC supports multiple compilation targets to generate code for different platforms and environments.

## Available Targets

### 1. Bytecode (Default)
The primary target is the PostC Virtual Machine bytecode. This target generates a JSON file containing the compiled program that can be executed by the PostC VM.

**Usage:**
```bash
python3 src/bootstrap/postc.py compile <source_file.pc> [output_file.pcc]
```

**Features:**
- Stack-based bytecode format
- JSON serialization for easy inspection
- Cross-platform execution
- Fast compilation and execution

### 2. WebAssembly (WASM)
PostC can compile to WebAssembly text format (.wat) for execution in web browsers or WASM runtimes.

**Usage:**
```bash
# First compile to bytecode
python3 src/bootstrap/postc.py compile <source_file.pc> <bytecode_file.pcc>

# Then compile bytecode to WASM
python3 src/bootstrap/postc.py wasm <bytecode_file.pcc> <output_file.wat>
```

**Features:**
- WebAssembly text format output
- Integration with WASI for I/O operations
- Near-native performance in WASM environments
- Browser compatibility

**Limitations:**
- Currently a prototype implementation
- Some PostC features not yet fully supported
- Requires further development for production use

### 3. Self-hosting Compiler Target
The self-hosting PostC compiler is written in PostC itself. The bootstrap compiler can compile the self-hosting compiler components.

**Usage:**
```bash
# Compile self-hosting compiler components
make build
```

**Features:**
- Written entirely in PostC
- Demonstrates the language's self-hosting capability
- Modular design with separate lexer, parser, and code generator
- Can compile other PostC programs

## Future Targets

### Native Machine Code
Planned support for compiling directly to native machine code for maximum performance.

### LLVM IR
Potential target to leverage LLVM's optimization passes and code generation for multiple architectures.

## Target Comparison

| Target | Performance | Portability | Ease of Implementation | Use Cases |
|--------|-------------|-------------|----------------------|-----------|
| Bytecode | Moderate | High | Easy | Development, cross-platform execution |
| WebAssembly | High | High | Moderate | Web applications, serverless functions |
| Self-hosting | Moderate | High | Moderate | Language development, bootstrapping |
| Native (Planned) | Very High | Low | Difficult | Performance-critical applications |

## Adding New Targets

To add a new compilation target:

1. Create a new module in `src/bootstrap/<target_name>/`
2. Implement translation from PostC bytecode to the target format
3. Add command-line support in `src/bootstrap/postc.py`
4. Update the Makefile with new build targets
5. Add documentation in `docs/targets.md`

The modular design of the bootstrap compiler makes it straightforward to add new targets by translating from the common bytecode format.