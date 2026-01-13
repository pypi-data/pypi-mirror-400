# Copyright 2024 Daniel Valdivia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Integration tests for streaming patterns in Go-Python interoperability.

This test file verifies that all four streaming patterns work correctly
between Go and Python implementations over reverse tunnels.
"""

import asyncio
import signal
import subprocess
from pathlib import Path

import grpc
import pytest
from grpctunnel import ReverseTunnelServer, TunnelServiceHandler, TunnelServiceHandlerOptions
from grpctunnel.proto.v1 import TunnelServiceStub, add_TunnelServiceServicer_to_server

from proto import echo_pb2, echo_pb2_grpc


class StreamingEchoServiceImpl:
    """Python implementation of streaming Echo service."""

    async def Echo(
            self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        print(f"Python received Echo: {request.message}")
        return echo_pb2.EchoResponse(message=request.message)

    async def EchoServerStream(
            self, request_bytes: bytes, stream: any, context: any
    ) -> None:
        """Server streaming: send multiple responses for one request."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        print(f"Python received EchoServerStream: {request.message}")

        # Send 3 responses
        for i in range(3):
            response = echo_pb2.EchoResponse(message=f"{request.message}-{i}")
            await stream.send_message(response)

    async def EchoClientStream(
            self, stream: any, context: any
    ) -> echo_pb2.EchoResponse:
        """Client streaming: receive multiple requests, send one response."""
        print("Python received EchoClientStream")
        messages = []

        try:
            while True:
                request_bytes = await stream.recv_message()
                request = echo_pb2.EchoRequest.FromString(request_bytes)
                messages.append(request.message)
        except StopAsyncIteration:
            pass

        combined = ",".join(messages)
        return echo_pb2.EchoResponse(message=combined)

    async def EchoBidiStream(self, stream: any, context: any) -> None:
        """Bidirectional streaming: receive and send concurrently."""
        print("Python received EchoBidiStream")

        try:
            while True:
                request_bytes = await stream.recv_message()
                request = echo_pb2.EchoRequest.FromString(request_bytes)

                # Echo back with prefix
                response = echo_pb2.EchoResponse(message=f"echo:{request.message}")
                await stream.send_message(response)
        except StopAsyncIteration:
            pass


class TestStreamingInterop:
    """Test streaming patterns between Go and Python."""

    @pytest.mark.asyncio
    async def test_streaming_python_server_go_client(self):
        """Test all streaming patterns with Python server and Go client."""
        # Path to Go client binary
        go_interop_dir = Path(__file__).parent.parent / "go-interop"
        client_binary = go_interop_dir / "client" / "go-client"

        if not client_binary.exists():
            pytest.skip(
                f"Go client binary not found at {client_binary}. "
                "Run 'go build' in go-interop directory first."
            )

        # Start Python server with tunnel support
        print("\n=== Testing Streaming: Python Server + Go Client ===")
        print("Starting Python server...")
        server = grpc.aio.server()

        # Create tunnel handler that supports reverse tunnels
        handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

        # Register tunnel service
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # Start server on port 50052 (different from other tests)
        port = server.add_insecure_port("[::]:50052")
        await server.start()
        print(f"Python server listening on port {port}")

        try:
            # Start Go client process
            print("Starting Go client with streaming support...")
            client_process = subprocess.Popen(
                [str(client_binary), "--server", f"localhost:{port}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            try:
                # Wait for Go client to establish reverse tunnel
                print("Waiting for Go client to establish reverse tunnel...")
                await asyncio.sleep(2.0)

                # Get reverse channel
                reverse_channel = handler.as_channel()
                assert reverse_channel is not None, "No reverse channel available"

                # Wait for channel to be ready
                if not reverse_channel.ready():
                    await asyncio.sleep(1.0)
                    assert reverse_channel.ready(), "Reverse channel not ready"

                print("\nTesting streaming patterns over reverse tunnel...")

                # Test 1: Unary (already tested, but include for completeness)
                print("\n1. Testing Unary RPC...")
                unary_method = reverse_channel.unary_unary(
                    "test.EchoService/Echo",
                    request_serializer=lambda msg: msg.SerializeToString(),
                    response_deserializer=echo_pb2.EchoResponse.FromString,
                )
                request = echo_pb2.EchoRequest(message="unary-test")
                response = await unary_method(request)
                assert response.message == "unary-test"
                print(f"✓ Unary: {response.message}")

                # Test 2: Server streaming
                print("\n2. Testing Server Streaming RPC...")
                server_stream_method = reverse_channel.unary_stream(
                    "test.EchoService/EchoServerStream",
                    request_serializer=lambda msg: msg.SerializeToString(),
                    response_deserializer=echo_pb2.EchoResponse.FromString,
                )
                request = echo_pb2.EchoRequest(message="server-stream")
                response_stream = await server_stream_method(request)

                responses = []
                async for response in response_stream:
                    responses.append(response.message)
                    print(f"   Received: {response.message}")

                assert len(responses) == 3
                assert responses == ["server-stream-0", "server-stream-1", "server-stream-2"]
                print("✓ Server streaming: Received 3 responses")

                # Test 3: Client streaming
                print("\n3. Testing Client Streaming RPC...")
                client_stream_method = reverse_channel.stream_unary(
                    "test.EchoService/EchoClientStream",
                    request_serializer=lambda msg: msg.SerializeToString(),
                    response_deserializer=echo_pb2.EchoResponse.FromString,
                )

                async def request_generator():
                    for i in range(3):
                        yield echo_pb2.EchoRequest(message=f"msg{i}")

                response = await client_stream_method(request_generator())
                assert response.message == "msg0,msg1,msg2"
                print(f"✓ Client streaming: {response.message}")

                # Test 4: Bidirectional streaming
                print("\n4. Testing Bidirectional Streaming RPC...")
                bidi_method = reverse_channel.stream_stream(
                    "test.EchoService/EchoBidiStream",
                    request_serializer=lambda msg: msg.SerializeToString(),
                    response_deserializer=echo_pb2.EchoResponse.FromString,
                )

                # Get the bidi stream
                bidi_stream = await bidi_method()

                # Send and receive messages
                bidi_responses = []
                for i in range(3):
                    await bidi_stream.write(echo_pb2.EchoRequest(message=f"bidi{i}"))
                    response = await bidi_stream.read()
                    bidi_responses.append(response.message)
                    print(f"   Sent: bidi{i}, Received: {response.message}")

                await bidi_stream.done_writing()

                assert len(bidi_responses) == 3
                assert bidi_responses == ["echo:bidi0", "echo:bidi1", "echo:bidi2"]
                print("✓ Bidirectional streaming: Completed")

                print("\n✓ All streaming patterns work correctly!")

                # Terminate Go client
                client_process.terminate()
                stdout, _ = client_process.communicate(timeout=3)

                print("\nGo client output (partial):")
                lines = stdout.split('\n')[:10]  # Show first 10 lines
                for line in lines:
                    if line:
                        print(f"  {line}")

            finally:
                # Cleanup: kill Go client if still running
                if client_process.poll() is None:
                    client_process.terminate()
                    try:
                        client_process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        client_process.kill()
                        client_process.wait()

        finally:
            # Stop Python server
            await server.stop(grace=1.0)

    @pytest.mark.asyncio
    async def test_streaming_go_server_python_client(self):
        """Test streaming patterns with Go server and Python client."""
        # Path to Go server binary
        go_interop_dir = Path(__file__).parent.parent / "go-interop"
        server_binary = go_interop_dir / "server" / "go-server"

        if not server_binary.exists():
            pytest.skip(
                f"Go server binary not found at {server_binary}. "
                "Run 'go build' in go-interop directory first."
            )

        # Note: This test would require updating the Go server to make streaming calls
        # to the Python client. Since the current Go server only makes a unary call,
        # we'll mark this as a known limitation.
        print("\n=== Testing Streaming: Go Server + Python Client ===")
        print("Note: Go server currently only tests unary calls.")
        print("Full streaming test would require Go server modifications.")

        # For now, we can test that Python client can handle streaming methods
        # when registered with the reverse tunnel

        # Start Go server
        print("\nStarting Go server...")
        server_process = subprocess.Popen(
            [str(server_binary), "--port", "50053"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        try:
            # Wait for server to start
            await asyncio.sleep(1.0)

            # Connect Python client to Go server
            print("Connecting Python client to Go server...")
            async with grpc.aio.insecure_channel("localhost:50053") as channel:
                # Create tunnel stub
                tunnel_stub = TunnelServiceStub(channel)

                # Create reverse tunnel server on Python client side
                reverse_server = ReverseTunnelServer(tunnel_stub)

                # Register all streaming methods
                service_impl = StreamingEchoServiceImpl()

                # Register unary
                reverse_server.register_method(
                    "test.EchoService/Echo",
                    service_impl.Echo,
                    is_client_stream=False,
                    is_server_stream=False,
                )

                # Register server streaming
                reverse_server.register_method(
                    "test.EchoService/EchoServerStream",
                    service_impl.EchoServerStream,
                    is_client_stream=False,
                    is_server_stream=True,
                )

                # Register client streaming
                reverse_server.register_method(
                    "test.EchoService/EchoClientStream",
                    service_impl.EchoClientStream,
                    is_client_stream=True,
                    is_server_stream=False,
                )

                # Register bidi streaming
                reverse_server.register_method(
                    "test.EchoService/EchoBidiStream",
                    service_impl.EchoBidiStream,
                    is_client_stream=True,
                    is_server_stream=True,
                )

                print("Starting reverse tunnel with streaming support...")

                # Start reverse tunnel
                async def run_reverse_tunnel():
                    started, err = await reverse_server.serve()
                    print(f"Reverse tunnel completed: started={started}, err={err}")
                    return started, err

                tunnel_task = asyncio.create_task(run_reverse_tunnel())

                # Wait for Go server to make its call
                await asyncio.sleep(8.0)

                # Stop the reverse tunnel
                await reverse_server.stop()

                # Wait for tunnel to complete
                try:
                    started, err = await asyncio.wait_for(tunnel_task, timeout=2.0)
                    assert started, f"Reverse tunnel failed: {err}"
                except asyncio.TimeoutError:
                    pytest.fail("Reverse tunnel did not complete")

            # Check Go server output
            print("\nChecking Go server output...")
            server_process.send_signal(signal.SIGTERM)
            stdout, _ = server_process.communicate(timeout=3)

            print("Go server output:")
            print(stdout)

            # Verify basic success (Go server currently only tests unary)
            assert "INTEROP_SUCCESS" in stdout, "Go server did not report success"

            print("\n✓ Basic interop with streaming methods registered succeeded!")
            print("  (Full streaming test requires Go server modifications)")

        finally:
            # Cleanup: kill Go server if still running
            if server_process.poll() is None:
                server_process.terminate()
                try:
                    server_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    server_process.kill()
                    server_process.wait()


if __name__ == "__main__":
    # Allow running the tests directly
    pytest.main([__file__, "-v", "-s"])
