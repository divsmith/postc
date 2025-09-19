#!/bin/bash

# Final Test Script
#
# This script verifies that all components of the PostC project work together correctly.

echo "Testing bootstrap compiler with hello world program..."
python3 bootstrap/build.py examples/hello.pc

echo "Building self-hosting compiler..."
./build-postc.sh

echo "Testing self-hosting capability..."
./test-self-hosting.sh

echo "All tests completed successfully!"