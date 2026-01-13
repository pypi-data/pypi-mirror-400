# grpctunnel-py Examples

This directory contains simple, practical examples demonstrating how to use grpctunnel-py.

## What are gRPC Tunnels?

gRPC tunnels allow you to carry gRPC over gRPC. This enables two powerful patterns:

### Forward Tunnels
Create a persistent gRPC connection through which you can multiplex many RPC calls. This provides:
- **Session affinity**: Pin multiple RPC calls to a single server backend
- **Connection reuse**: Reduce connection overhead by reusing the same transport
- **Load balancer traversal**: Maintain connection to specific backend even through load balancers

### Reverse Tunnels
Allow servers to send RPC requests back to connected clients. This enables:
- **Server push**: Rich "server push" capabilities for real-time updates
- **NAT/Firewall traversal**: Access servers behind NAT or firewalls
- **Bidirectional communication**: True bidirectional RPC without websockets

## Examples

### [Forward Tunnel](./forward_tunnel/)
Demonstrates how to create a forward tunnel from client to server.

**Use case**: Multiple RPC calls through a single persistent connection

```bash
# Terminal 1: Start server
cd forward_tunnel
python server.py

# Terminal 2: Run client
python client.py
```

### [Reverse Tunnel](./reverse_tunnel/)
Demonstrates how to create a reverse tunnel allowing server to call client.

**Use case**: Server pushing data to clients, accessing clients behind NAT

```bash
# Terminal 1: Start server (waits for client)
cd reverse_tunnel
python server.py

# Terminal 2: Start client (connects and opens reverse tunnel)
python client.py
```

## Requirements

```bash
# Using pip
pip install grpcio grpcio-tools protobuf

# Using uv
uv add grpcio grpcio-tools protobuf

# Or install grpctunnel-py from source
pip install -e .
```

## Setup

The examples use a simple Echo service defined in `proto/echo.proto`. The Python stubs are already generated and included, but if you need to regenerate them:

```bash
cd examples
./generate_proto.sh
# Or manually:
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/echo.proto
```

## Running the Examples

### From the Repository Root

If running from the grpctunnel-py repository:

```bash
# Install dependencies
uv sync

# Run examples with uv
uv run python examples/forward_tunnel/server.py
uv run python examples/forward_tunnel/client.py
```

### As Standalone

If you've copied the examples folder separately:

```bash
cd examples

# Make sure grpctunnel is installed
pip install grpctunnel

# Run the examples
python forward_tunnel/server.py
python forward_tunnel/client.py
```

## Example Service

All examples use a simple Echo service that returns the message you send to it:

```protobuf
service EchoService {
  rpc Echo(EchoRequest) returns (EchoResponse);
}
```

This service is already compiled and available in the test proto files.

## Architecture Diagrams

### Forward Tunnel
```
Client                           Server
  |                                |
  |-- OpenTunnel (establish) ---->|
  |<---- tunnel connection -------|
  |                                |
  |-- RPC through tunnel -------->|
  |<----- response ---------------|
  |                                |
  |-- Another RPC -------------->|
  |<----- response ---------------|
```

### Reverse Tunnel
```
Client                           Server
  |                                |
  |-- OpenReverseTunnel --------->|
  |<---- reverse channel ---------|
  |                                |
  |<---- RPC from server ---------|
  |------ response -------------->|
  |                                |
  |<---- Another RPC -------------|
  |------ response -------------->|
```
