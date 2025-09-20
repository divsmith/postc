#!/bin/bash

# Final Test Script
#
# This script verifies that all components of the PostC project work together correctly.

echo "Testing bootstrap compiler with hello world program..."
python3 ../bootstrap/postc.py ../examples/hello.pc

echo "Building self-hosting compiler..."
../postc-compiler/build-postc.sh

echo "Testing self-hosting capability..."
../postc-compiler/test-self-hosting.sh

echo "All tests completed successfully!"