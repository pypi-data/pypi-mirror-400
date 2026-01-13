# Go-Python Interoperability Tests

This directory contains integration tests to verify interoperability between the Python grpctunnel implementation and the Go implementation from https://github.com/jhump/grpctunnel.

## Directory Structure

```
integrationtests/
├── go-interop/          # Go implementations (server/client)
│   ├── echopb/          # Generated protobuf code
│   ├── server/          # Go server with reverse tunnel support
│   ├── client/          # Go client that connects to Python server
│   └── echo.proto       # Echo service proto definition
└── python-interop/      # Python test scripts
    ├── test_go_server_py_client.py   # Python client → Go server
    └── test_py_server_go_client.py   # Python server ← Go client
```

## Test Scenarios

### Scenario 1: Go Server with Python Client (Reverse Tunnel)
1. Go server starts and exposes TunnelService
2. Python client connects and opens a reverse tunnel
3. Python client registers Echo service
4. Go server calls Echo service on Python client over reverse tunnel
5. Verify response is received correctly

### Scenario 2: Python Server with Go Client (Reverse Tunnel)
1. Python server starts and exposes TunnelService
2. Go client connects and opens a reverse tunnel
3. Go client registers Echo service
4. Python server calls Echo service on Go client over reverse tunnel
5. Verify response is received correctly

## Running the Tests

### Prerequisites
- Go 1.21+ installed
- Python 3.10+ installed with grpctunnel package
- protoc compiler with Go and Python plugins

### Build Go Components
```bash
cd integrationtests/go-interop
./generate.sh    # Generate protobuf code
go build -o server/go-server ./server/main.go
go build -o client/go-client ./client/main.go
```

### Generate Python Protobuf Code
```bash
cd integrationtests/go-interop
uv run python -m grpc_tools.protoc -I. \
  --python_out=../python-interop/proto \
  --grpc_python_out=../python-interop/proto \
  echo.proto
```

### Run Interoperability Tests
```bash
cd integrationtests/python-interop
uv run pytest -v

# Or run individual tests:
uv run pytest test_go_server_py_client.py -v     # Test Go server with Python client
uv run pytest test_py_server_go_client.py -v     # Test Python server with Go client
```

## Current Status

The Python implementation is feature-complete and all Python-to-Python tests pass:
- ✅ Forward tunnels (client → server RPCs)
- ✅ Reverse tunnels (server → client RPCs)
- ✅ All 4 streaming patterns (unary, client-stream, server-stream, bidi)
- ✅ Flow control (REVISION_ZERO and REVISION_ONE)
- ✅ Concurrent RPCs
- ✅ Error propagation

**Go-Python Interoperability Tests: ✅ COMPLETE**

Both interoperability test scenarios are now implemented and passing:
- ✅ Go server (jhump/grpctunnel) → Python client (grpctunnel-py)
- ✅ Python server (grpctunnel-py) → Go client (jhump/grpctunnel)

These tests confirm that:
- The Python implementation is wire-protocol compatible with the original Go implementation
- Reverse tunnels work correctly between Go and Python
- RPC calls can be made bidirectionally over reverse tunnels
- Both implementations follow the same gRPC tunneling protocol

## Notes

- The Python implementation follows the same protocol as the Go implementation
- Both use the same protobuf definitions from `proto/grpctunnel/v1/tunnel.proto`
- The wire protocol is fully compatible between implementations
- These tests validate that implementations can interoperate at the protocol level
