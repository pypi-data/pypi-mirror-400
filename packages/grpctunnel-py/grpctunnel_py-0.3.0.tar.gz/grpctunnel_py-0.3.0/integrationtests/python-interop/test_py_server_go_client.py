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
Integration test: Python server with Go client (reverse tunnel)

This test verifies that a Python server can receive reverse tunnel connections
from a Go client using jhump/grpctunnel and successfully make RPC calls to the
Go client over the reverse tunnel.
"""

import asyncio
import signal
import subprocess
from pathlib import Path

import grpc
import pytest
from grpctunnel import TunnelServiceHandler, TunnelServiceHandlerOptions
from grpctunnel.proto.v1 import add_TunnelServiceServicer_to_server

from proto import echo_pb2


class TestPythonServerGoClient:
    """Test Python server with Go client reverse tunnel."""

    @pytest.mark.asyncio
    async def test_python_server_go_client(self):
        """Test that Python server can call Go client over reverse tunnel."""
        # Path to Go client binary
        go_interop_dir = Path(__file__).parent.parent / "go-interop"
        client_binary = go_interop_dir / "client" / "go-client"

        if not client_binary.exists():
            pytest.skip(
                f"Go client binary not found at {client_binary}. "
                "Run 'go build' in go-interop directory first."
            )

        # Start Python server with tunnel support
        print("\nStarting Python server...")
        server = grpc.aio.server()

        # Create tunnel handler that supports reverse tunnels
        handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

        # Register tunnel service
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # Start server on port 50051
        port = server.add_insecure_port("[::]:50051")
        await server.start()
        print(f"Python server listening on port {port}")

        try:
            # Start Go client process
            print("Starting Go client...")
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

                # Check if channel is ready
                if not reverse_channel.ready():
                    # Wait a bit more for channel to be ready
                    await asyncio.sleep(1.0)
                    assert (
                        reverse_channel.ready()
                    ), "Reverse channel not ready after waiting"

                print("Reverse channel is ready, making RPC call to Go client...")

                # Create stub for calling Go client's Echo service
                stub_method = reverse_channel.unary_unary(
                    "test.EchoService/Echo",
                    request_serializer=lambda msg: msg.SerializeToString(),
                    response_deserializer=echo_pb2.EchoResponse.FromString,
                )

                # Make RPC call from Python server to Go client
                request = echo_pb2.EchoRequest(message="Hello from Python server!")
                print(f"Sending request: {request.message}")

                response = await stub_method(request)

                # Verify response
                assert response is not None, "No response received from Go client"
                assert (
                        response.message == "Hello from Python server!"
                ), f"Unexpected response: {response.message}"

                print(f"✓ Received response from Go client: {response.message}")

                # Wait for Go client to finish
                await asyncio.sleep(1.0)

                # Check Go client output
                client_process.send_signal(signal.SIGTERM)
                stdout, _ = client_process.communicate(timeout=3)

                print("\nGo client output:")
                print(stdout)

                # Verify that Go client reported success
                assert (
                        "INTEROP_SUCCESS" in stdout
                ), "Go client did not report success"

                print("\n✓ Interoperability test PASSED: Python server → Go client")

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


if __name__ == "__main__":
    # Allow running the test directly
    pytest.main([__file__, "-v"])
