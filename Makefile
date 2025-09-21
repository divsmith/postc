# Makefile for PostC

.PHONY: all build test clean

all: build

# Build the self-hosting compiler
build:
	@echo "Building PostC compiler..."
	python3 src/bootstrap/postc.py src/compiler/lexer.pc
	python3 src/bootstrap/postc.py src/compiler/parser.pc
	python3 src/bootstrap/postc.py src/compiler/codegen.pc
	python3 src/bootstrap/postc.py src/compiler/compiler.pc
	@echo "PostC compiler build complete!"

# Run all tests
test:
	@echo "Testing self-hosting PostC compiler..."
	python3 src/bootstrap/postc.py src/compiler/lexer.pc > lexer.output
	@echo "Testing bootstrap compiler with hello world program..."
	python3 src/bootstrap/postc.py examples/hello.pc

# Run a specific example
run-example:
	@echo "Running example: $(EXAMPLE)..."
	python3 src/bootstrap/postc.py examples/$(EXAMPLE).pc

# Clean build artifacts
clean:
	@echo "Cleaning up..."
	rm -f lexer.output
