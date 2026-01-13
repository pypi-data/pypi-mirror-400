# Reverse Tunnel Example

This example demonstrates how to create a **reverse tunnel** allowing a server to make RPC calls back to a client.

## What is a Reverse Tunnel?

A reverse tunnel allows the server to send RPC requests back to connected clients. This enables:

- **Server push**: Rich "server push" capabilities for real-time updates
- **NAT/Firewall traversal**: Server can call clients behind NAT or firewalls
- **Bidirectional communication**: True bidirectional RPC without websockets
- **Client hosting services**: Clients can host services accessible by the server

## Architecture

```
┌─────────┐                              ┌─────────┐
│ Client  │                              │ Server  │
│         │                              │         │
│ Hosts   │─── OpenReverseTunnel ─────>  │         │
│ Echo    │<── reverse tunnel ready ───  │         │
│ Service │                              │         │
│         │<── Echo("Hello") ──────────  │         │
│         │─── Echo: Hello ───────────>  │         │
│         │                              │         │
│         │<── Echo("World") ──────────  │         │
│         │─── Echo: World ───────────>  │         │
└─────────┘                              └─────────┘
```

The client hosts the service, but the server makes the RPC calls.

## Files

- **server.py**: Server that accepts reverse tunnels and calls the client
- **client.py**: Client that hosts Echo service and opens reverse tunnel

## Running the Example

### Terminal 1: Start the Server

```bash
cd examples/reverse_tunnel
python server.py
```

Output:
```
2024-01-14 10:00:00 - INFO - Starting Reverse Tunnel Server...
2024-01-14 10:00:00 - INFO - ✓ Server listening on port 50051
2024-01-14 10:00:00 - INFO - Waiting for client to connect with reverse tunnel...
```

### Terminal 2: Run the Client

```bash
cd examples/reverse_tunnel
python client.py
```

Output:
```
2024-01-14 10:00:05 - INFO - Connecting to server at localhost:50051...
2024-01-14 10:00:05 - INFO - Registered Echo service on client
2024-01-14 10:00:05 - INFO - Opening reverse tunnel to server...
2024-01-14 10:00:05 - INFO - ✓ Reverse tunnel established
2024-01-14 10:00:05 - INFO - Waiting for calls from server...
2024-01-14 10:00:05 - INFO - Client received request: Hello from server #1
2024-01-14 10:00:05 - INFO - Client received request: Hello from server #2
...
```

### Server Output After Client Connects

```
2024-01-14 10:00:05 - INFO - ✓ Reverse tunnel established

--- Making RPC calls to client ---
2024-01-14 10:00:05 - INFO - Sending to client: Hello from server #1
2024-01-14 10:00:05 - INFO - Client responded: Echo: Hello from server #1
2024-01-14 10:00:05 - INFO - Sending to client: Hello from server #2
2024-01-14 10:00:05 - INFO - Client responded: Echo: Hello from server #2
...

✓ All calls to client completed successfully!
```

## Key Code Sections

### Server Side

```python
# Create tunnel handler that accepts reverse tunnels
handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

# Add tunnel service to gRPC server
add_TunnelServiceServicer_to_server(handler.service(), server)

# Wait for reverse tunnel from client
await asyncio.sleep(2.0)

# Get the reverse channel to call the client
reverse_channel = handler.as_channel()

# Create stub to call client's service
echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

# Make RPC calls to the client
response = await echo_stub.Echo(request)
```

### Client Side

```python
# Connect to server
channel = grpc.aio.insecure_channel(server_address)
tunnel_stub = TunnelServiceStub(channel)

# Create reverse tunnel server (runs on client)
reverse_server = ReverseTunnelServer(tunnel_stub)

# Register service that server can call
reverse_server.register_service(
    echo_service,
    "test.EchoService",
    {"Echo": {"is_client_stream": False, "is_server_stream": False}}
)

# Open reverse tunnel
await reverse_server.serve()
```

## Use Cases

### 1. Server Push / Real-time Updates
Server pushes updates to clients in real-time:

```python
# Server side
async def push_update(client_id: str, data: dict):
    # Get reverse channel for specific client
    reverse_channel = get_client_channel(client_id)

    # Push update to client
    stub = UpdateServiceStub(reverse_channel)
    await stub.PushUpdate(UpdateRequest(data=data))
```

### 2. Callback Pattern
Server calls back to client after long-running operations:

```python
# Client registers callback service
class CallbackService:
    async def OnComplete(self, result):
        print(f"Server completed: {result}")

# Server calls back when done
await client_callback_stub.OnComplete(result)
```

### 3. IoT Device Management
Manage IoT devices behind NAT/firewalls:

```python
# Device opens reverse tunnel
reverse_server = ReverseTunnelServer(tunnel_stub)
reverse_server.register_service(device_control, "DeviceControl")

# Server can now control device
device_stub = DeviceControlStub(reverse_channel)
await device_stub.Restart()
await device_stub.UpdateFirmware(firmware)
```

### 4. Client-side Services
Expose client-side resources to server:

```python
# Client exposes local database
class LocalDBService:
    async def Query(self, sql):
        return local_db.execute(sql)

# Server queries client's local database
results = await db_stub.Query("SELECT * FROM users")
```

## Important Notes

### Single Reverse Channel
The current implementation tracks a single reverse channel per handler:

```python
# This returns the most recent reverse tunnel
reverse_channel = handler.as_channel()
```

For multiple clients, you'll need to manage multiple handlers or track channels differently.

### Connection Lifetime
Keep the client running as long as you want the server to be able to call it:

```python
# Client must stay alive to handle server requests
await asyncio.sleep(float('inf'))  # Run forever
```

### Error Handling
Handle disconnections gracefully:

```python
try:
    response = await echo_stub.Echo(request)
except grpc.aio.AioRpcError as e:
    if e.code() == grpc.StatusCode.UNAVAILABLE:
        logger.error("Client disconnected")
```
