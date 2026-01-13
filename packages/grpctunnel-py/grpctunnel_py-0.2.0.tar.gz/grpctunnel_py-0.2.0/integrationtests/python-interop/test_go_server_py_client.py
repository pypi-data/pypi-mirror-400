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
Integration test: Go server with Python client (reverse tunnel)

This test verifies that a Go server using jhump/grpctunnel can receive
reverse tunnel connections from a Python client and successfully make
RPC calls to the Python client over the reverse tunnel.
"""

import asyncio
import signal
import subprocess
from pathlib import Path

import grpc
import pytest
from grpctunnel import ReverseTunnelServer
from grpctunnel.proto.v1 import TunnelServiceStub

from proto import echo_pb2


class EchoServiceImpl:
    """Python implementation of Echo service."""

    async def Echo(
            self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        print(f"Python client received Echo request: {request.message}")
        response = echo_pb2.EchoResponse(message=request.message)
        return response


class TestGoServerPythonClient:
    """Test Go server with Python client reverse tunnel."""

    @pytest.mark.asyncio
    async def test_go_server_python_client(self):
        """Test that Go server can call Python client over reverse tunnel."""
        # Path to Go server binary
        go_interop_dir = Path(__file__).parent.parent / "go-interop"
        server_binary = go_interop_dir / "server" / "go-server"

        if not server_binary.exists():
            pytest.skip(
                f"Go server binary not found at {server_binary}. "
                "Run 'go build' in go-interop directory first."
            )

        # Start Go server
        print("\nStarting Go server...")
        server_process = subprocess.Popen(
            [str(server_binary), "--port", "50051"],
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
            async with grpc.aio.insecure_channel("localhost:50051") as channel:
                # Create tunnel stub
                tunnel_stub = TunnelServiceStub(channel)

                # Create reverse tunnel server on Python client side
                reverse_server = ReverseTunnelServer(tunnel_stub)

                # Register Echo service implementation
                reverse_server.register_method(
                    "test.EchoService/Echo",
                    EchoServiceImpl().Echo,
                    is_client_stream=False,
                    is_server_stream=False,
                )

                print("Starting reverse tunnel...")

                # Start reverse tunnel in background task
                async def run_reverse_tunnel():
                    started, err = await reverse_server.serve()
                    print(f"Reverse tunnel completed: started={started}, err={err}")
                    return started, err

                tunnel_task = asyncio.create_task(run_reverse_tunnel())

                # Wait for Go server to process (it waits 3 seconds, then calls Echo)
                # The Go server will:
                # 1. Wait for reverse tunnel to be established
                # 2. Call Echo on Python client
                # 3. Print "INTEROP_SUCCESS" if successful
                print("Waiting for Go server to make RPC call...")
                await asyncio.sleep(8.0)

                # Stop the reverse tunnel
                await reverse_server.stop()

                # Wait for tunnel to complete
                try:
                    started, err = await asyncio.wait_for(tunnel_task, timeout=2.0)
                    assert started, f"Reverse tunnel failed to start: {err}"
                except asyncio.TimeoutError:
                    pytest.fail("Reverse tunnel did not complete in time")

            # Check Go server output for success marker
            print("\nChecking Go server output...")
            server_process.send_signal(signal.SIGTERM)
            stdout, _ = server_process.communicate(timeout=3)

            print("Go server output:")
            print(stdout)

            # Verify that the interop was successful
            assert (
                    "INTEROP_SUCCESS" in stdout
            ), "Go server did not report success"
            assert (
                    "Hello from Go server!" in stdout
            ), "Go server did not send expected message"

            print("\n✓ Interoperability test PASSED: Go server → Python client")

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
    # Allow running the test directly
    pytest.main([__file__, "-v"])
