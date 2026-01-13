#!/bin/bash
# Generate Python stubs from proto files

cd "$(dirname "$0")"

echo "Generating Python stubs from proto files..."
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/echo.proto

echo "✓ Proto stubs generated successfully"
echo "  - proto/echo_pb2.py"
echo "  - proto/echo_pb2_grpc.py"
