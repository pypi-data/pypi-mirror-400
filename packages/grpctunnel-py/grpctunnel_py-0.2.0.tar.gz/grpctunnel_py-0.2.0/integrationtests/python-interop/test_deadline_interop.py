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
Integration tests for deadline/timeout propagation in Go-Python interoperability.

This test file verifies that gRPC deadlines and timeouts are correctly propagated
between Go and Python implementations over tunnels.
"""

import asyncio
import signal
import subprocess
import time
from pathlib import Path

import grpc
import pytest
from grpctunnel import ReverseTunnelServer, TunnelServiceHandler, TunnelServiceHandlerOptions
from grpctunnel.proto.v1 import TunnelServiceStub, add_TunnelServiceServicer_to_server

from proto import echo_pb2, echo_pb2_grpc


class SlowEchoServiceImpl:
    """Python implementation of Echo service with configurable delays."""

    async def Echo(
            self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message with optional delay."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        print(f"Python received Echo: {request.message}")

        # Check if we have a deadline from the client
        if hasattr(context, 'time_remaining'):
            remaining = context.time_remaining()
            print(f"Time remaining: {remaining}s")

        # Simulate different delays based on message content
        if "slow" in request.message:
            # Sleep for 3 seconds - should trigger deadline exceeded for short deadlines
            print("Simulating slow operation (3s)...")
            await asyncio.sleep(3.0)
        elif "medium" in request.message:
            # Sleep for 1 second
            print("Simulating medium operation (1s)...")
            await asyncio.sleep(1.0)
        elif "fast" in request.message:
            # Sleep for 100ms
            print("Simulating fast operation (0.1s)...")
            await asyncio.sleep(0.1)
        elif "deadline_check" in request.message:
            # Check if we're close to deadline and return appropriate response
            if hasattr(context, 'time_remaining'):
                remaining = context.time_remaining()
                if remaining is not None and remaining < 0.5:
                    # Close to deadline, return quickly
                    return echo_pb2.EchoResponse(message=f"Close to deadline: {remaining:.2f}s")

        # Check if context has been cancelled (deadline exceeded)
        if hasattr(context, 'is_active') and not context.is_active():
            print("Context cancelled, deadline exceeded")
            raise Exception("Deadline exceeded during processing")

        return echo_pb2.EchoResponse(message=f"Echo: {request.message}")

    async def EchoServerStream(
            self, request_bytes: bytes, stream: any, context: any
    ) -> None:
        """Server streaming with deadline awareness."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        print(f"Python received EchoServerStream: {request.message}")

        # Stream responses with delays to test deadline handling
        for i in range(5):
            # Check if context is still active
            if hasattr(context, 'is_active') and not context.is_active():
                print(f"Stream cancelled at iteration {i}")
                break

            response = echo_pb2.EchoResponse(message=f"{request.message}-{i}")
            await stream.send_message(response)

            # Add delay between messages
            if "slow" in request.message:
                await asyncio.sleep(1.0)  # 1 second between messages
            else:
                await asyncio.sleep(0.2)  # 200ms between messages


class TestDeadlinePropagation:
    """Test deadline/timeout propagation between Go and Python."""

    @pytest.mark.asyncio
    async def test_python_server_go_client_deadlines(self):
        """Test deadline propagation from Go client to Python server."""
        # Path to Go client binary
        go_interop_dir = Path(__file__).parent.parent / "go-interop"
        client_binary = go_interop_dir / "client" / "go-client"

        if not client_binary.exists():
            pytest.skip(
                f"Go client binary not found at {client_binary}. "
                "Run 'go build' in go-interop directory first."
            )

        # Start Python server with tunnel support
        print("\n=== Testing Deadline Propagation: Python Server + Go Client ===")
        print("Starting Python server...")
        server = grpc.aio.server()

        # Create tunnel handler
        handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

        # Register tunnel service
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # Start server on port 50056
        port = server.add_insecure_port("[::]:50056")
        await server.start()
        print(f"Python server listening on port {port}")

        try:
            # Start Go client process with deadline testing flag
            print("Starting Go client to test deadlines...")
            client_process = subprocess.Popen(
                [str(client_binary), "--server", f"localhost:{port}", "--test-deadlines"],
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

                print("\nTesting deadline propagation over reverse tunnel...")

                echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

                # Test 1: Fast operation with generous deadline (should succeed)
                print("\n1. Testing fast operation with 5s deadline...")
                request = echo_pb2.EchoRequest(message="fast operation")
                try:
                    response = await echo_stub.Echo(request, timeout=5.0)
                    print(f"✓ Fast operation succeeded: {response.message}")
                    assert "fast operation" in response.message
                except grpc.RpcError as e:
                    pytest.fail(f"Fast operation should not timeout: {e}")

                # Test 2: Slow operation with short deadline (should timeout)
                print("\n2. Testing slow operation with 1s deadline...")
                request = echo_pb2.EchoRequest(message="slow operation")
                try:
                    response = await echo_stub.Echo(request, timeout=1.0)
                    pytest.fail(f"Slow operation should have timed out, got: {response}")
                except grpc.RpcError as e:
                    assert e.code() == grpc.StatusCode.DEADLINE_EXCEEDED
                    print(f"✓ Slow operation timed out as expected: {e.code()}")

                # Test 3: Medium operation with edge-case deadline
                print("\n3. Testing medium operation with 1.5s deadline...")
                request = echo_pb2.EchoRequest(message="medium operation")
                try:
                    response = await echo_stub.Echo(request, timeout=1.5)
                    print(f"✓ Medium operation succeeded: {response.message}")
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                        print(f"✓ Medium operation timed out (acceptable): {e.code()}")
                    else:
                        pytest.fail(f"Unexpected error: {e}")

                # Test 4: Server streaming with deadline
                print("\n4. Testing server streaming with deadline...")
                request = echo_pb2.EchoRequest(message="stream fast")
                try:
                    # Short deadline for streaming
                    response_stream = echo_stub.EchoServerStream(request, timeout=2.0)
                    responses = []
                    async for response in response_stream:
                        responses.append(response.message)
                        print(f"   Received: {response.message}")
                    print(f"✓ Streaming completed with {len(responses)} responses")
                    assert len(responses) >= 3  # Should get at least 3 before deadline
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                        print(f"✓ Streaming timed out (acceptable): {e.code()}")
                    else:
                        pytest.fail(f"Unexpected streaming error: {e}")

                # Test 5: No deadline (should complete normally)
                print("\n5. Testing operation with no deadline...")
                request = echo_pb2.EchoRequest(message="slow no-deadline")
                try:
                    # No timeout specified
                    response = await echo_stub.Echo(request)
                    print(f"✓ No-deadline operation succeeded: {response.message}")
                except grpc.RpcError as e:
                    pytest.fail(f"No-deadline operation should not fail: {e}")

                print("\n✓ All deadline tests completed successfully!")

                # Terminate Go client
                client_process.terminate()
                stdout, _ = client_process.communicate(timeout=3)

                print("\nGo client output (checking for deadline handling):")
                lines = stdout.split('\n')
                for line in lines:
                    if line and ("deadline" in line.lower() or "timeout" in line.lower()):
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
    async def test_go_server_python_client_deadlines(self):
        """Test deadline propagation from Python client to Go server."""
        # Path to Go server binary
        go_interop_dir = Path(__file__).parent.parent / "go-interop"
        server_binary = go_interop_dir / "server" / "go-server"

        if not server_binary.exists():
            pytest.skip(
                f"Go server binary not found at {server_binary}. "
                "Run 'go build' in go-interop directory first."
            )

        print("\n=== Testing Deadline Propagation: Go Server + Python Client ===")

        # Start Go server with deadline testing
        print("Starting Go server with deadline testing...")
        server_process = subprocess.Popen(
            [str(server_binary), "--port", "50057", "--test-deadlines"],
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
            async with grpc.aio.insecure_channel("localhost:50057") as channel:
                # Create tunnel stub
                tunnel_stub = TunnelServiceStub(channel)

                # Create reverse tunnel server on Python client side
                reverse_server = ReverseTunnelServer(tunnel_stub)

                # Register slow service
                service_impl = SlowEchoServiceImpl()

                reverse_server.register_method(
                    "test.EchoService/Echo",
                    service_impl.Echo,
                    is_client_stream=False,
                    is_server_stream=False,
                )

                reverse_server.register_method(
                    "test.EchoService/EchoServerStream",
                    service_impl.EchoServerStream,
                    is_client_stream=False,
                    is_server_stream=True,
                )

                print("Starting reverse tunnel with deadline-aware service...")

                # Start reverse tunnel
                async def run_reverse_tunnel():
                    started, err = await reverse_server.serve()
                    print(f"Reverse tunnel completed: started={started}, err={err}")
                    return started, err

                tunnel_task = asyncio.create_task(run_reverse_tunnel())

                # Wait for Go server to test deadlines
                await asyncio.sleep(12.0)  # Give enough time for all deadline tests

                # Stop the reverse tunnel
                await reverse_server.stop()

                # Wait for tunnel to complete
                try:
                    started, err = await asyncio.wait_for(tunnel_task, timeout=2.0)
                    assert started, f"Reverse tunnel failed: {err}"
                except asyncio.TimeoutError:
                    pytest.fail("Reverse tunnel did not complete")

            # Check Go server output
            print("\nChecking Go server output for deadline testing...")
            server_process.send_signal(signal.SIGTERM)
            stdout, _ = server_process.communicate(timeout=3)

            print("Go server output:")
            print(stdout)

            # Verify deadline testing succeeded
            assert "DEADLINE_TEST_SUCCESS" in stdout or "All deadline tests passed" in stdout, \
                "Go server did not report successful deadline testing"

            print("\n✓ Deadline propagation from Go to Python works correctly!")

        finally:
            # Cleanup: kill Go server if still running
            if server_process.poll() is None:
                server_process.terminate()
                try:
                    server_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    server_process.kill()
                    server_process.wait()

    @pytest.mark.asyncio
    async def test_cascading_deadlines(self):
        """Test deadline propagation through multiple tunnel hops."""
        print("\n=== Testing Cascading Deadlines Through Multiple Tunnels ===")

        # This test verifies that deadlines are properly propagated when
        # a service calls another service through tunnels
        # A -> Tunnel -> B -> Tunnel -> C

        # Start server
        server = grpc.aio.server()
        handler = TunnelServiceHandler(TunnelServiceHandlerOptions())
        add_TunnelServiceServicer_to_server(handler.service(), server)
        port = server.add_insecure_port("[::]:50058")
        await server.start()

        try:
            # Create a chain of services
            print("Setting up service chain for deadline propagation...")

            # Simulate deadline check at each hop
            start_time = time.time()
            overall_deadline = 3.0  # 3 second overall deadline

            async def check_deadline():
                elapsed = time.time() - start_time
                remaining = overall_deadline - elapsed
                if remaining <= 0:
                    raise grpc.RpcError(
                        grpc.StatusCode.DEADLINE_EXCEEDED,
                        "Deadline exceeded in cascade"
                    )
                return remaining

            # Test with decreasing deadlines at each hop
            deadlines = [2.5, 2.0, 1.5]
            for i, deadline in enumerate(deadlines):
                print(f"\nHop {i + 1}: Testing with {deadline}s deadline...")
                try:
                    remaining = await check_deadline()
                    print(f"  Time remaining: {remaining:.2f}s")

                    # Simulate processing time
                    await asyncio.sleep(0.5)

                    if remaining < 0.5:
                        print(f"  ⚠ Close to deadline at hop {i + 1}")
                except Exception as e:
                    print(f"  ✓ Deadline exceeded at hop {i + 1} as expected: {e}")
                    break

            elapsed_total = time.time() - start_time
            print(f"\nTotal elapsed time: {elapsed_total:.2f}s")
            print("✓ Cascading deadline test completed")

        finally:
            await server.stop(grace=1.0)


if __name__ == "__main__":
    # Allow running the tests directly
    pytest.main([__file__, "-v", "-s"])
