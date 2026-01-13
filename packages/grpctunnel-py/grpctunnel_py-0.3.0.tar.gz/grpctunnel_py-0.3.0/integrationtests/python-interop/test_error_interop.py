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
Integration tests for error propagation in Go-Python interoperability.

This test file verifies that gRPC errors are correctly propagated
between Go and Python implementations over tunnels.
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


class ErrorEchoServiceImpl:
    """Python implementation of Echo service that returns errors."""

    async def Echo(
            self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message or return error based on message."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        print(f"Python received Echo: {request.message}")

        # Return different errors based on message content
        # For tunnel handlers, raise exceptions directly
        if "not_found" in request.message:
            raise Exception(f"grpc.StatusCode.NOT_FOUND: Resource not found")
        elif "permission_denied" in request.message:
            raise Exception(f"grpc.StatusCode.PERMISSION_DENIED: Access denied")
        elif "invalid" in request.message:
            raise Exception(f"grpc.StatusCode.INVALID_ARGUMENT: Invalid argument")
        elif "unavailable" in request.message:
            raise Exception(f"grpc.StatusCode.UNAVAILABLE: Service unavailable")
        elif "deadline" in request.message:
            raise Exception(f"grpc.StatusCode.DEADLINE_EXCEEDED: Deadline exceeded")
        elif "internal" in request.message:
            raise Exception(f"grpc.StatusCode.INTERNAL: Internal server error")

        return echo_pb2.EchoResponse(message=request.message)

    async def EchoError(
            self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Always returns an error with the specified code."""
        request = echo_pb2.ErrorRequest.FromString(request_bytes)
        print(f"Python received EchoError: code={request.code}, message={request.message}")

        # For tunnel handlers, raise exceptions directly
        # The error message format needs to match what grpctunnel expects
        raise Exception(f"Error code {request.code}: {request.message}")


class TestErrorPropagation:
    """Test error propagation between Go and Python."""

    @pytest.mark.asyncio
    async def test_python_server_go_client_errors(self):
        """Test error propagation from Python server to Go client."""
        # Path to Go client binary
        go_interop_dir = Path(__file__).parent.parent / "go-interop"
        client_binary = go_interop_dir / "client" / "go-client"

        if not client_binary.exists():
            pytest.skip(
                f"Go client binary not found at {client_binary}. "
                "Run 'go build' in go-interop directory first."
            )

        # Start Python server with tunnel support
        print("\n=== Testing Error Propagation: Python Server + Go Client ===")
        print("Starting Python server...")
        server = grpc.aio.server()

        # Create tunnel handler
        handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

        # Register tunnel service
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # Start server on port 50054
        port = server.add_insecure_port("[::]:50054")
        await server.start()
        print(f"Python server listening on port {port}")

        try:
            # Start Go client process with error testing flag
            print("Starting Go client to test errors...")
            client_process = subprocess.Popen(
                [str(client_binary), "--server", f"localhost:{port}", "--test-errors"],
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

                print("\nTesting error propagation over reverse tunnel...")

                # Test various error codes
                error_tests = [
                    (grpc.StatusCode.NOT_FOUND, "not_found_test"),
                    (grpc.StatusCode.PERMISSION_DENIED, "permission_denied_test"),
                    (grpc.StatusCode.INVALID_ARGUMENT, "invalid_test"),
                    (grpc.StatusCode.UNAVAILABLE, "unavailable_test"),
                    (grpc.StatusCode.DEADLINE_EXCEEDED, "deadline_test"),
                    (grpc.StatusCode.INTERNAL, "internal_test"),
                ]

                echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

                for expected_code, message in error_tests:
                    print(f"\nTesting {expected_code.name} error...")
                    request = echo_pb2.EchoRequest(message=message)

                    try:
                        response = await echo_stub.Echo(request)
                        pytest.fail(f"Expected error for {message}, got response: {response}")
                    except grpc.RpcError as e:
                        assert e.code() == expected_code, f"Expected {expected_code}, got {e.code()}"
                        print(f"✓ {expected_code.name}: Error correctly propagated")

                # Test EchoError method with specific error codes
                print("\nTesting EchoError method...")
                for code in [3, 5, 7, 13]:  # INVALID_ARGUMENT, NOT_FOUND, PERMISSION_DENIED, INTERNAL
                    error_request = echo_pb2.ErrorRequest(
                        code=code,
                        message=f"Error message for code {code}"
                    )

                    try:
                        response = await echo_stub.EchoError(error_request)
                        pytest.fail(f"Expected error for code {code}, got response: {response}")
                    except grpc.RpcError as e:
                        assert e.code().value[0] == code, f"Expected code {code}, got {e.code().value[0]}"
                        assert f"Error message for code {code}" in e.details()
                        print(f"✓ EchoError with code {code}: Error correctly propagated")

                print("\n✓ All error codes propagate correctly through tunnel!")

                # Terminate Go client
                client_process.terminate()
                stdout, _ = client_process.communicate(timeout=3)

                print("\nGo client output (checking for errors):")
                lines = stdout.split('\n')
                for line in lines:
                    if line and ("error" in line.lower() or "ERROR" in line):
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
    async def test_go_server_python_client_errors(self):
        """Test error propagation from Go server to Python client."""
        # Path to Go server binary
        go_interop_dir = Path(__file__).parent.parent / "go-interop"
        server_binary = go_interop_dir / "server" / "go-server"

        if not server_binary.exists():
            pytest.skip(
                f"Go server binary not found at {server_binary}. "
                "Run 'go build' in go-interop directory first."
            )

        print("\n=== Testing Error Propagation: Go Server + Python Client ===")

        # Start Go server with error testing
        print("Starting Go server with error testing...")
        server_process = subprocess.Popen(
            [str(server_binary), "--port", "50055", "--test-errors"],
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
            async with grpc.aio.insecure_channel("localhost:50055") as channel:
                # Create tunnel stub
                tunnel_stub = TunnelServiceStub(channel)

                # Create reverse tunnel server on Python client side
                reverse_server = ReverseTunnelServer(tunnel_stub)

                # Register error-returning service
                service_impl = ErrorEchoServiceImpl()

                reverse_server.register_method(
                    "test.EchoService/Echo",
                    service_impl.Echo,
                    is_client_stream=False,
                    is_server_stream=False,
                )

                reverse_server.register_method(
                    "test.EchoService/EchoError",
                    service_impl.EchoError,
                    is_client_stream=False,
                    is_server_stream=False,
                )

                print("Starting reverse tunnel...")

                # Start reverse tunnel
                async def run_reverse_tunnel():
                    started, err = await reverse_server.serve()
                    print(f"Reverse tunnel completed: started={started}, err={err}")
                    return started, err

                tunnel_task = asyncio.create_task(run_reverse_tunnel())

                # Wait for Go server to test error propagation
                await asyncio.sleep(10.0)

                # Stop the reverse tunnel
                await reverse_server.stop()

                # Wait for tunnel to complete
                try:
                    started, err = await asyncio.wait_for(tunnel_task, timeout=2.0)
                    assert started, f"Reverse tunnel failed: {err}"
                except asyncio.TimeoutError:
                    pytest.fail("Reverse tunnel did not complete")

            # Check Go server output
            print("\nChecking Go server output for error testing...")
            server_process.send_signal(signal.SIGTERM)
            stdout, _ = server_process.communicate(timeout=3)

            print("Go server output:")
            print(stdout)

            # Verify error testing succeeded
            assert "ERROR_TEST_SUCCESS" in stdout or "All errors propagated correctly" in stdout, \
                "Go server did not report successful error testing"

            print("\n✓ Error propagation from Python to Go works correctly!")

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
