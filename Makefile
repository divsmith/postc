# Makefile for PostC

.PHONY: all build test clean

all: build

# Build the self-hosting compiler
build:
	@echo "Building PostC compiler..."
	python3 src/bootstrap/postc.py compile src/compiler/lexer.pc src/compiler/lexer.pcc
	python3 src/bootstrap/postc.py compile src/compiler/parser.pc src/compiler/parser.pcc
	python3 src/bootstrap/postc.py compile src/compiler/codegen.pc src/compiler/codegen.pcc
	python3 src/bootstrap/postc.py compile src/compiler/compiler.pc src/compiler/compiler.pcc
	@echo "PostC compiler build complete!"

# Run all tests
test:
	@echo "Testing self-hosting PostC compiler..."
	python3 src/bootstrap/postc.py compile src/compiler/lexer.pc lexer.output
	@echo "Testing bootstrap compiler with hello world program..."
	python3 src/bootstrap/postc.py compile examples/hello.pc examples/hello.pcc
	python3 src/bootstrap/postc.py run examples/hello.pcc

# Run a specific example
run-example:
	@echo "Running example: $(EXAMPLE)..."
	python3 src/bootstrap/postc.py compile examples/$(EXAMPLE).pc examples/$(EXAMPLE).pcc
	python3 src/bootstrap/postc.py run examples/$(EXAMPLE).pcc

# Compile a specific example to bytecode
compile-example:
	@echo "Compiling example: $(EXAMPLE)..."
	python3 src/bootstrap/postc.py compile examples/$(EXAMPLE).pc examples/$(EXAMPLE).pcc

# Generate WASM for a specific example
wasm-example:
	@echo "Generating WASM for example: $(EXAMPLE)..."
	python3 src/bootstrap/postc.py compile examples/$(EXAMPLE).pc examples/$(EXAMPLE).pcc
	python3 src/bootstrap/postc.py wasm examples/$(EXAMPLE).pcc examples/$(EXAMPLE).wat

# Clean build artifacts
clean:
	@echo "Cleaning up..."
	rm -f lexer.output
	rm -f src/compiler/*.pcc
	rm -f examples/*.pcc
	rm -f examples/*.wat
