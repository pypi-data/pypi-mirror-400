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
Integration tests for reverse gRPC tunnels.

These tests verify that the Python server can send RPC requests back to
Python clients over reverse tunnel connections.
"""

import asyncio

import grpc
import pytest

from grpctunnel import (
    ReverseTunnelServer,
    TunnelServiceHandler,
    TunnelServiceHandlerOptions,
)
from grpctunnel.proto.v1 import (
    TunnelServiceStub,
    add_TunnelServiceServicer_to_server,
)
from tests.integration import echo_pb2, echo_pb2_grpc


class EchoServiceImpl:
    """Implementation of the Echo service for reverse tunnel testing."""

    async def Echo(
        self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        response = echo_pb2.EchoResponse(message=request.message)
        return response


@pytest.fixture
async def tunnel_server_with_reverse():
    """Create a gRPC server with reverse tunnel support."""
    server = grpc.aio.server()

    # Create tunnel handler that supports reverse tunnels
    handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

    # Register the tunnel service
    add_TunnelServiceServicer_to_server(handler.service(), server)

    # Start server on a random port
    port = server.add_insecure_port("[::]:0")
    await server.start()

    yield f"localhost:{port}", handler

    await server.stop(grace=1.0)


class TestReverseTunnel:
    """Integration tests for reverse tunnels."""

    @pytest.mark.asyncio
    async def test_reverse_tunnel_basic(self, tunnel_server_with_reverse):
        """Test basic reverse tunnel setup."""
        server_addr, handler = tunnel_server_with_reverse

        # Create a connection to the server
        async with grpc.aio.insecure_channel(server_addr) as transport_channel:
            stub = TunnelServiceStub(transport_channel)

            # Create reverse tunnel server on client side
            reverse_server = ReverseTunnelServer(stub)

            # Register echo service
            reverse_server.register_method(
                "test.EchoService/Echo",
                EchoServiceImpl().Echo,
                is_client_stream=False,
                is_server_stream=False,
            )

            # Start the reverse tunnel in a background task
            async def run_reverse_tunnel():
                started, err = await reverse_server.serve()
                return started, err

            tunnel_task = asyncio.create_task(run_reverse_tunnel())

            # Wait a bit for tunnel to establish
            await asyncio.sleep(0.1)

            # TODO: Get reverse channel and make RPC call from server to client
            # For now, just verify the tunnel starts
            assert not tunnel_task.done() or tunnel_task.result()[0]

            # Stop the tunnel
            await reverse_server.stop()

            # Wait for tunnel to complete
            try:
                started, err = await asyncio.wait_for(tunnel_task, timeout=1.0)
                assert started
            except asyncio.TimeoutError:
                pytest.fail("Reverse tunnel did not complete")

    @pytest.mark.asyncio
    async def test_handler_creation(self):
        """Test that TunnelServiceHandler can be created with various options."""
        # Default options
        handler1 = TunnelServiceHandler()
        assert handler1 is not None

        # With options
        options = TunnelServiceHandlerOptions(
            no_reverse_tunnels=False,
            disable_flow_control=False,
        )
        handler2 = TunnelServiceHandler(options)
        assert handler2 is not None

        # Verify we can register methods
        handler2.register_method(
            "test.Service/Method",
            lambda req, ctx: None,
            is_client_stream=False,
            is_server_stream=False,
        )

    @pytest.mark.asyncio
    async def test_reverse_tunnel_server_creation(self):
        """Test that ReverseTunnelServer can be created."""
        # Create a mock stub (we won't actually use it)
        async with grpc.aio.insecure_channel("localhost:50051") as channel:
            stub = TunnelServiceStub(channel)
            reverse_server = ReverseTunnelServer(stub)
            assert reverse_server is not None

            # Verify we can register methods
            reverse_server.register_method(
                "test.Service/Method",
                lambda req, ctx: None,
                is_client_stream=False,
                is_server_stream=False,
            )

    @pytest.mark.asyncio
    async def test_reverse_tunnel_channel_tracking(self, tunnel_server_with_reverse):
        """Test that reverse tunnel channels are properly tracked."""
        server_addr, handler = tunnel_server_with_reverse

        # Create a connection to the server
        async with grpc.aio.insecure_channel(server_addr) as transport_channel:
            stub = TunnelServiceStub(transport_channel)

            # Create reverse tunnel server on client side
            reverse_server = ReverseTunnelServer(stub)

            # Register echo service
            reverse_server.register_method(
                "test.EchoService/Echo",
                EchoServiceImpl().Echo,
                is_client_stream=False,
                is_server_stream=False,
            )

            # Start the reverse tunnel in a background task
            async def run_reverse_tunnel():
                started, err = await reverse_server.serve()
                return started, err

            tunnel_task = asyncio.create_task(run_reverse_tunnel())

            # Wait for tunnel to establish
            await asyncio.sleep(0.2)

            # Check that a reverse tunnel is tracked
            tunnels = await handler.all_reverse_tunnels()
            assert len(tunnels) > 0, "Expected at least one reverse tunnel"

            # Get reverse channel
            reverse_channel = handler.as_channel()
            assert reverse_channel is not None
            assert reverse_channel.ready()

            # Stop the tunnel
            await reverse_server.stop()

            # Wait for tunnel to complete
            try:
                started, err = await asyncio.wait_for(tunnel_task, timeout=1.0)
                assert started
            except asyncio.TimeoutError:
                pytest.fail("Reverse tunnel did not complete")

    @pytest.mark.asyncio
    async def test_reverse_tunnel_rpc_call(self, tunnel_server_with_reverse):
        """Test that server can send RPC to client over reverse tunnel."""
        server_addr, handler = tunnel_server_with_reverse

        # Create a connection to the server
        async with grpc.aio.insecure_channel(server_addr) as transport_channel:
            stub = TunnelServiceStub(transport_channel)

            # Create reverse tunnel server on client side
            reverse_server = ReverseTunnelServer(stub)

            # Register echo service on client
            reverse_server.register_method(
                "test.EchoService/Echo",
                EchoServiceImpl().Echo,
                is_client_stream=False,
                is_server_stream=False,
            )

            # Start the reverse tunnel in a background task
            async def run_reverse_tunnel():
                started, err = await reverse_server.serve()
                return started, err

            tunnel_task = asyncio.create_task(run_reverse_tunnel())

            # Wait for tunnel to establish
            await asyncio.sleep(0.3)

            # Get reverse channel from handler
            reverse_channel = handler.as_channel()
            assert reverse_channel.ready(), "Reverse channel should be ready"

            # Create a stub for making RPC calls to the client
            # Use the echo service stub
            stub_method = reverse_channel.unary_unary(
                "test.EchoService/Echo",
                request_serializer=lambda msg: msg.SerializeToString(),
                response_deserializer=echo_pb2.EchoResponse.FromString,
            )

            # Make RPC call from server to client
            request = echo_pb2.EchoRequest(message="Hello from server!")
            response = await stub_method(request)

            # Verify response
            assert response is not None
            assert response.message == "Hello from server!"

            # Stop the tunnel
            await reverse_server.stop()

            # Wait for tunnel to complete
            try:
                started, err = await asyncio.wait_for(tunnel_task, timeout=1.0)
                assert started
            except asyncio.TimeoutError:
                pytest.fail("Reverse tunnel did not complete")

    @pytest.mark.asyncio
    async def test_reverse_tunnel_server_streaming(self, tunnel_server_with_reverse):
        """Test server streaming RPC over reverse tunnel."""
        server_addr, handler = tunnel_server_with_reverse

        async with grpc.aio.insecure_channel(server_addr) as transport_channel:
            stub = TunnelServiceStub(transport_channel)
            reverse_server = ReverseTunnelServer(stub)

            # Register server streaming method
            async def echo_server_stream(request_bytes: bytes, stream: any, context: any) -> None:
                request = echo_pb2.EchoRequest.FromString(request_bytes)
                for i in range(3):
                    response = echo_pb2.EchoResponse(message=f"{request.message}-{i}")
                    await stream.send_message(response)

            reverse_server.register_method(
                "test.EchoService/EchoServerStream",
                echo_server_stream,
                is_client_stream=False,
                is_server_stream=True,
            )

            async def run_reverse_tunnel():
                started, err = await reverse_server.serve()
                return started, err

            tunnel_task = asyncio.create_task(run_reverse_tunnel())
            await asyncio.sleep(0.3)

            reverse_channel = handler.as_channel()
            assert reverse_channel.ready()

            stub_method = reverse_channel.unary_stream(
                "test.EchoService/EchoServerStream",
                request_serializer=lambda msg: msg.SerializeToString(),
                response_deserializer=echo_pb2.EchoResponse.FromString,
            )

            request = echo_pb2.EchoRequest(message="test")
            response_stream = await stub_method(request)

            responses = []
            async for response in response_stream:
                responses.append(response.message)

            assert len(responses) == 3
            assert responses == ["test-0", "test-1", "test-2"]

            # Small delay to allow gRPC stream cleanup before stopping
            await asyncio.sleep(0.1)
            await reverse_server.stop()
            try:
                started, err = await asyncio.wait_for(tunnel_task, timeout=1.0)
                assert started
            except asyncio.TimeoutError:
                pytest.fail("Reverse tunnel did not complete")

    @pytest.mark.asyncio
    async def test_reverse_tunnel_client_streaming(self, tunnel_server_with_reverse):
        """Test client streaming RPC over reverse tunnel."""
        server_addr, handler = tunnel_server_with_reverse

        async with grpc.aio.insecure_channel(server_addr) as transport_channel:
            stub = TunnelServiceStub(transport_channel)
            reverse_server = ReverseTunnelServer(stub)

            # Register client streaming method
            async def echo_client_stream(stream: any, context: any) -> echo_pb2.EchoResponse:
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

            reverse_server.register_method(
                "test.EchoService/EchoClientStream",
                echo_client_stream,
                is_client_stream=True,
                is_server_stream=False,
            )

            async def run_reverse_tunnel():
                started, err = await reverse_server.serve()
                return started, err

            tunnel_task = asyncio.create_task(run_reverse_tunnel())
            await asyncio.sleep(0.3)

            reverse_channel = handler.as_channel()
            assert reverse_channel.ready()

            stub_method = reverse_channel.stream_unary(
                "test.EchoService/EchoClientStream",
                request_serializer=lambda msg: msg.SerializeToString(),
                response_deserializer=echo_pb2.EchoResponse.FromString,
            )

            async def request_generator():
                for i in range(3):
                    yield echo_pb2.EchoRequest(message=f"msg{i}")

            response = await stub_method(request_generator())

            assert response is not None
            assert response.message == "msg0,msg1,msg2"

            # Small delay to allow gRPC stream cleanup before stopping
            await asyncio.sleep(0.1)
            await reverse_server.stop()
            try:
                started, err = await asyncio.wait_for(tunnel_task, timeout=1.0)
                assert started
            except asyncio.TimeoutError:
                pytest.fail("Reverse tunnel did not complete")

    @pytest.mark.asyncio
    async def test_reverse_tunnel_bidi_streaming(self, tunnel_server_with_reverse):
        """Test bidirectional streaming RPC over reverse tunnel."""
        server_addr, handler = tunnel_server_with_reverse

        async with grpc.aio.insecure_channel(server_addr) as transport_channel:
            stub = TunnelServiceStub(transport_channel)
            reverse_server = ReverseTunnelServer(stub)

            # Register bidi streaming method
            async def echo_bidi_stream(stream: any, context: any) -> None:
                try:
                    while True:
                        request_bytes = await stream.recv_message()
                        request = echo_pb2.EchoRequest.FromString(request_bytes)
                        response = echo_pb2.EchoResponse(message=f"echo:{request.message}")
                        await stream.send_message(response)
                except StopAsyncIteration:
                    pass

            reverse_server.register_method(
                "test.EchoService/EchoBidiStream",
                echo_bidi_stream,
                is_client_stream=True,
                is_server_stream=True,
            )

            async def run_reverse_tunnel():
                started, err = await reverse_server.serve()
                return started, err

            tunnel_task = asyncio.create_task(run_reverse_tunnel())
            await asyncio.sleep(0.3)

            reverse_channel = handler.as_channel()
            assert reverse_channel.ready()

            stub_method = reverse_channel.stream_stream(
                "test.EchoService/EchoBidiStream",
                request_serializer=lambda msg: msg.SerializeToString(),
                response_deserializer=echo_pb2.EchoResponse.FromString,
            )

            # Call without request_iterator to get the bidi stream
            bidi_stream = await stub_method()

            # Manually send requests and read responses
            responses = []
            for i in range(3):
                await bidi_stream.write(echo_pb2.EchoRequest(message=f"msg{i}"))
                response = await bidi_stream.read()
                responses.append(response.message)

            # Signal we're done writing
            await bidi_stream.done_writing()

            assert len(responses) == 3
            assert responses == ["echo:msg0", "echo:msg1", "echo:msg2"]

            # Small delay to allow cleanup
            await asyncio.sleep(0.1)
            await reverse_server.stop()
            try:
                started, err = await asyncio.wait_for(tunnel_task, timeout=1.0)
                assert started
            except asyncio.TimeoutError:
                pytest.fail("Reverse tunnel did not complete")

    @pytest.mark.asyncio
    async def test_concurrent_reverse_rpcs(self, tunnel_server_with_reverse):
        """Test concurrent reverse RPCs.

        This test verifies that multiple concurrent RPCs can be handled over a
        reverse tunnel. Previously this test was skipped due to a race condition
        that caused 'GRPC_CALL_ERROR_TOO_MANY_OPERATIONS' errors, but the issue
        has been fixed by serializing writes through a queue in the main loop.
        """
        server_addr, handler = tunnel_server_with_reverse

        async with grpc.aio.insecure_channel(server_addr) as transport_channel:
            stub = TunnelServiceStub(transport_channel)
            reverse_server = ReverseTunnelServer(stub)

            # Register echo service
            reverse_server.register_method(
                "test.EchoService/Echo",
                EchoServiceImpl().Echo,
                is_client_stream=False,
                is_server_stream=False,
            )

            async def run_reverse_tunnel():
                started, err = await reverse_server.serve()
                return started, err

            tunnel_task = asyncio.create_task(run_reverse_tunnel())
            await asyncio.sleep(0.3)

            reverse_channel = handler.as_channel()
            assert reverse_channel.ready()

            stub_method = reverse_channel.unary_unary(
                "test.EchoService/Echo",
                request_serializer=lambda msg: msg.SerializeToString(),
                response_deserializer=echo_pb2.EchoResponse.FromString,
            )

            # Make multiple concurrent RPCs (fewer to avoid timeouts)
            async def make_call(i):
                request = echo_pb2.EchoRequest(message=f"concurrent-{i}")
                response = await stub_method(request)
                return response.message

            tasks = [asyncio.create_task(make_call(i)) for i in range(5)]
            results = await asyncio.gather(*tasks)

            # Verify all calls succeeded
            assert len(results) == 5
            for i, result in enumerate(results):
                assert result == f"concurrent-{i}"

            # Small delay to allow cleanup before stopping
            await asyncio.sleep(0.1)
            await reverse_server.stop()
            try:
                started, err = await asyncio.wait_for(tunnel_task, timeout=1.0)
                assert started
            except asyncio.TimeoutError:
                pytest.fail("Reverse tunnel did not complete")
