#!/bin/bash
set -e

# Create echopb directory if it doesn't exist
mkdir -p echopb

# Generate Go protobuf code
protoc --go_out=echopb --go_opt=paths=source_relative \
    --go-grpc_out=echopb --go-grpc_opt=paths=source_relative \
    echo.proto

echo "Proto code generated successfully"
