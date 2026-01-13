# Forward Tunnel Example

This example demonstrates how to create a **forward tunnel** from client to server.

## What is a Forward Tunnel?

A forward tunnel creates a persistent gRPC connection through which you can multiplex many RPC calls. This provides:

- **Session affinity**: All RPC calls through the tunnel go to the same server backend
- **Connection reuse**: Reduces connection overhead by reusing the same transport
- **Load balancer traversal**: Maintains connection to specific backend even through load balancers

## Architecture

```
┌─────────┐                              ┌─────────┐
│ Client  │                              │ Server  │
│         │                              │         │
│         │─── OpenTunnel ────────────>  │         │
│         │<── tunnel established ────   │         │
│         │                              │         │
│         │─── Echo("Hello") ────────>   │         │
│         │<── Echo: Hello ───────────   │         │
│         │                              │         │
│         │─── Echo("World") ────────>   │         │
│         │<── Echo: World ───────────   │         │
└─────────┘                              └─────────┘
```

All RPC calls go through the same tunnel connection.

## Files

- **server.py**: gRPC server with Echo service accessible through tunnels
- **client.py**: Client that creates a forward tunnel and makes RPC calls

## Running the Example

### Terminal 1: Start the Server

```bash
cd examples/forward_tunnel
python server.py
```

Output:
```
2024-01-14 10:00:00 - INFO - Starting Forward Tunnel Server...
2024-01-14 10:00:00 - INFO - Registered Echo service
2024-01-14 10:00:00 - INFO - ✓ Server listening on port 50051
2024-01-14 10:00:00 - INFO - Waiting for clients to connect...
```

### Terminal 2: Run the Client

```bash
cd examples/forward_tunnel
python client.py
```

Output:
```
2024-01-14 10:00:05 - INFO - Connecting to server at localhost:50051...
2024-01-14 10:00:05 - INFO - Creating forward tunnel...
2024-01-14 10:00:05 - INFO - ✓ Forward tunnel established

--- Making RPC calls through tunnel ---
2024-01-14 10:00:05 - INFO - Sending: Hello from client #1
2024-01-14 10:00:05 - INFO - Received: Echo: Hello from client #1
2024-01-14 10:00:05 - INFO - Sending: Hello from client #2
2024-01-14 10:00:05 - INFO - Received: Echo: Hello from client #2
...

✓ All calls completed successfully!
```

## Key Code Sections

### Server Side

```python
# Create tunnel handler
handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

# Register your service
handler.register_service(
    echo_service,
    "test.EchoService",
    {"Echo": {"is_client_stream": False, "is_server_stream": False}}
)

# Add tunnel service to gRPC server
add_TunnelServiceServicer_to_server(handler.service(), server)
```

### Client Side

```python
# Connect to server
channel = grpc.aio.insecure_channel(server_address)
tunnel_stub = TunnelServiceStub(channel)

# Create forward tunnel
pending = PendingChannel(tunnel_stub)
tunnel_channel = await pending.start()

# Use the tunnel channel for RPC calls
echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)
response = await echo_stub.Echo(request)
```

## Use Cases

### 1. Session Affinity
When you have stateful services behind a load balancer, forward tunnels ensure all requests go to the same backend:

```python
# Create tunnel once
tunnel_channel = await pending.start()

# All these calls go to the same server
await service.Login(credentials)
await service.GetUserData()
await service.UpdateProfile(data)
```

### 2. Connection Pooling
Reduce connection overhead by reusing the tunnel for many requests:

```python
# One tunnel, many concurrent requests
tasks = [service.GetData(id) for id in range(1000)]
results = await asyncio.gather(*tasks)
```

### 3. Long-lived Connections
Maintain a persistent connection for real-time applications:

```python
# Keep tunnel open for the lifetime of the application
async with create_tunnel() as tunnel:
    while running:
        await process_request(tunnel)
```

