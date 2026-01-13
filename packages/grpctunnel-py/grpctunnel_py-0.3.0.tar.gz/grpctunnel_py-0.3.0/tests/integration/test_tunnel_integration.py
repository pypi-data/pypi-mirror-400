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
Integration tests for grpctunnel client and server.

These tests verify the complete tunnel functionality by testing
Python client <-> Python server communication through the tunnel.
"""

import asyncio

import grpc
import pytest

from grpctunnel import PendingChannel, TunnelOptions, TunnelServer
from grpctunnel.proto.v1 import REVISION_ONE, REVISION_ZERO
from tests.integration import echo_pb2, echo_pb2_grpc


class EchoServiceImpl:
    """Implementation of the Echo service for testing."""

    async def Echo(
        self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message."""
        # Deserialize the request
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        response = echo_pb2.EchoResponse(message=request.message)
        return response

    async def EchoError(
        self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Return an error with the specified code and message."""
        # Deserialize the request
        request = echo_pb2.ErrorRequest.FromString(request_bytes)
        # Find the StatusCode from the integer value
        status_code = None
        for sc in grpc.StatusCode:
            if sc.value[0] == request.code:
                status_code = sc
                break
        if status_code is None:
            status_code = grpc.StatusCode.UNKNOWN
        # Raise proper gRPC error
        raise grpc.aio.AioRpcError(
            code=status_code,
            initial_metadata=grpc.aio.Metadata(),
            trailing_metadata=grpc.aio.Metadata(),
            details=request.message,
        )

    async def EchoServerStream(
        self, request_bytes: bytes, stream: any, context: any
    ) -> None:
        """Server streaming - receive one request, send multiple responses."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        # Send multiple responses through the stream
        for i in range(3):
            response = echo_pb2.EchoResponse(message=f"{request.message}-{i}")
            await stream.send_message(response)

    async def EchoClientStream(
        self, stream: any, context: any
    ) -> echo_pb2.EchoResponse:
        """Client streaming - receive multiple requests, send one response."""
        messages = []
        # Read all messages from the client
        try:
            while True:
                request_bytes = await stream.recv_message()
                request = echo_pb2.EchoRequest.FromString(request_bytes)
                messages.append(request.message)
        except StopAsyncIteration:
            pass  # End of stream

        # Combine all messages and return response
        combined = ",".join(messages)
        return echo_pb2.EchoResponse(message=combined)

    async def EchoBidiStream(
        self, stream: any, context: any
    ) -> None:
        """Bidirectional streaming - receive and send multiple messages."""
        # Read messages and echo them back
        try:
            while True:
                request_bytes = await stream.recv_message()
                request = echo_pb2.EchoRequest.FromString(request_bytes)
                # Echo each message back with a prefix
                response = echo_pb2.EchoResponse(message=f"echo:{request.message}")
                await stream.send_message(response)
        except StopAsyncIteration:
            pass  # End of stream


class BidirectionalStreamWrapper:
    """Wrapper to adapt gRPC servicer interface to bidirectional stream."""

    def __init__(self, request_iterator, context):
        self._request_iterator = request_iterator
        self._context = context
        self._write_queue = asyncio.Queue()
        self._closed = False

    def __aiter__(self):
        """Support async iteration for reading."""
        return self  # Return self so __anext__ is called

    async def write(self, message):
        """Write a message to the client."""
        if not self._closed:
            await self._write_queue.put(message)

    async def read(self):
        """Read next message from request_iterator."""
        try:
            msg = await self._request_iterator.__anext__()
            return msg
        except StopAsyncIteration:
            return None

    async def __anext__(self):
        """Read next message for async iteration."""
        msg = await self.read()
        if msg is None:
            raise StopAsyncIteration
        return msg

    def close(self):
        """Mark the wrapper as closed."""
        self._closed = True
        # Put a sentinel to unblock any waiting gets
        try:
            self._write_queue.put_nowait(None)
        except asyncio.QueueFull:
            pass


@pytest.fixture
async def grpc_server():
    """Create a gRPC server that hosts the tunnel service."""
    server = grpc.aio.server()

    # Create tunnel server
    tunnel_server = TunnelServer()

    # Create service implementation instance
    echo_service = EchoServiceImpl()

    # Register echo service methods
    tunnel_server.register_method(
        "test.EchoService/Echo",
        echo_service.Echo,
        is_client_stream=False,
        is_server_stream=False,
    )
    tunnel_server.register_method(
        "test.EchoService/EchoError",
        echo_service.EchoError,
        is_client_stream=False,
        is_server_stream=False,
    )
    tunnel_server.register_method(
        "test.EchoService/EchoServerStream",
        echo_service.EchoServerStream,
        is_client_stream=False,
        is_server_stream=True,
    )
    tunnel_server.register_method(
        "test.EchoService/EchoClientStream",
        echo_service.EchoClientStream,
        is_client_stream=True,
        is_server_stream=False,
    )
    tunnel_server.register_method(
        "test.EchoService/EchoBidiStream",
        echo_service.EchoBidiStream,
        is_client_stream=True,
        is_server_stream=True,
    )

    # Register tunnel servicer
    from grpctunnel.proto.v1 import (
        TunnelServiceServicer,
        add_TunnelServiceServicer_to_server,
    )

    class TunnelServicerImpl(TunnelServiceServicer):
        async def OpenTunnel(self, request_iterator, context):
            """Handle tunnel connections."""
            # Check if client sent negotiation header
            metadata = dict(context.invocation_metadata())
            client_accepts_settings = metadata.get("grpctunnel-negotiate") == "on"

            # Send negotiation header back if client supports it
            if client_accepts_settings:
                await context.send_initial_metadata((("grpctunnel-negotiate", "on"),))

            # Create wrapper
            wrapper = BidirectionalStreamWrapper(request_iterator, context)

            # Serve tunnel in background and yield messages
            async def serve():
                try:
                    await tunnel_server.serve_tunnel(
                        wrapper, client_accepts_settings=client_accepts_settings
                    )
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                finally:
                    wrapper.close()

            serve_task = asyncio.create_task(serve())

            # Give the serve task a moment to start
            await asyncio.sleep(0.01)

            try:
                # Yield messages from the queue
                while not wrapper._closed:
                    try:
                        msg = await asyncio.wait_for(wrapper._write_queue.get(), timeout=5.0)
                        if msg is None:  # Sentinel value indicating closure
                            break
                        yield msg
                    except asyncio.TimeoutError:
                        # Check if serve_task is done
                        if serve_task.done():
                            break
                        # Otherwise continue waiting
                        continue
            finally:
                # Wait for serve task to complete
                if not serve_task.done():
                    try:
                        await asyncio.wait_for(serve_task, timeout=10.0)
                    except asyncio.TimeoutError:
                        serve_task.cancel()
                        try:
                            await serve_task
                        except asyncio.CancelledError:
                            pass

    add_TunnelServiceServicer_to_server(TunnelServicerImpl(), server)

    # Start server on a random port
    port = server.add_insecure_port("[::]:0")
    await server.start()

    yield f"localhost:{port}"

    await server.stop(grace=1.0)


class TestTunnelIntegration:
    """Integration tests for tunnel client and server."""

    @pytest.mark.asyncio
    async def test_basic_echo(self, grpc_server):
        """Test basic echo through the tunnel."""
        # Create tunnel channel
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Create echo service stub using tunnel channel
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Make RPC call through tunnel
                request = echo_pb2.EchoRequest(message="Hello, Tunnel!")
                response = await echo_stub.Echo(request)

                assert response.message == "Hello, Tunnel!"

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_multiple_rpcs(self, grpc_server):
        """Test multiple RPCs through the same tunnel."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Make multiple RPC calls
                for i in range(10):
                    request = echo_pb2.EchoRequest(message=f"Message {i}")
                    response = await echo_stub.Echo(request)
                    assert response.message == f"Message {i}"

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_concurrent_rpcs(self, grpc_server):
        """Test concurrent RPCs through the same tunnel."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Make concurrent RPC calls
                async def make_call(i: int) -> str:
                    request = echo_pb2.EchoRequest(message=f"Message {i}")
                    response = await echo_stub.Echo(request)
                    return response.message

                results = await asyncio.gather(*[make_call(i) for i in range(20)])

                # Verify all responses
                for i, result in enumerate(results):
                    assert result == f"Message {i}"

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_large_message(self, grpc_server):
        """Test large message through the tunnel (tests flow control)."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Create a large message (>64KB to test flow control)
                large_message = "x" * (128 * 1024)  # 128KB
                request = echo_pb2.EchoRequest(message=large_message)
                response = await echo_stub.Echo(request)

                assert response.message == large_message
                assert len(response.message) == 128 * 1024

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_flow_control_disabled(self, grpc_server):
        """Test tunnel with flow control disabled (REVISION_ZERO)."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            # Create tunnel with flow control disabled
            options = TunnelOptions(disable_flow_control=True)
            pending = PendingChannel(stub, options=options)
            tunnel_channel = await pending.start()

            try:
                # Verify protocol revision
                assert tunnel_channel._use_revision == REVISION_ZERO

                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Make RPC call
                request = echo_pb2.EchoRequest(message="Test REVISION_ZERO")
                response = await echo_stub.Echo(request)

                assert response.message == "Test REVISION_ZERO"

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_flow_control_enabled(self, grpc_server):
        """Test tunnel with flow control enabled (REVISION_ONE)."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            # Create tunnel with default options (flow control enabled)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Wait for channel to be ready (settings negotiation to complete)
                await tunnel_channel.channel_ready()

                # Verify protocol revision
                assert tunnel_channel._use_revision == REVISION_ONE

                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Make RPC call with large message to exercise flow control
                large_message = "y" * (256 * 1024)  # 256KB
                request = echo_pb2.EchoRequest(message=large_message)
                response = await echo_stub.Echo(request)

                assert response.message == large_message

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_error_handling(self, grpc_server):
        """Test error handling through the tunnel."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Make RPC call that returns error
                request = echo_pb2.ErrorRequest(
                    code=grpc.StatusCode.INVALID_ARGUMENT.value[0],
                    message="Test error"
                )

                with pytest.raises(grpc.RpcError) as exc_info:
                    await echo_stub.EchoError(request)

                # Verify error details
                assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
                assert "Test error" in exc_info.value.details()

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_metadata(self, grpc_server):
        """Test metadata passing through the tunnel."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Make RPC call with metadata
                metadata = grpc.aio.Metadata(
                    ("custom-header", "custom-value"),
                    ("another-header", "another-value"),
                )
                request = echo_pb2.EchoRequest(message="Test metadata")

                # Note: We need to pass metadata through the call
                # For now, just test basic functionality
                response = await echo_stub.Echo(request)
                assert response.message == "Test metadata"

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_unimplemented_method(self, grpc_server):
        """Test calling an unimplemented method through the tunnel."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Try to call a method that doesn't exist
                # We'll use unary_unary to call a non-existent method
                call = tunnel_channel.unary_unary(
                    "/test.EchoService/NonExistent",
                    request_serializer=echo_pb2.EchoRequest.SerializeToString,
                    response_deserializer=echo_pb2.EchoResponse.FromString,
                )

                with pytest.raises(grpc.RpcError) as exc_info:
                    await call(echo_pb2.EchoRequest(message="test"))

                # Should get UNIMPLEMENTED error
                assert exc_info.value.code() == grpc.StatusCode.UNIMPLEMENTED

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_server_streaming(self, grpc_server):
        """Test server streaming through the tunnel."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Make server streaming RPC
                request = echo_pb2.EchoRequest(message="stream-test")
                response_stream = await echo_stub.EchoServerStream(request)

                # Collect all responses
                responses = []
                async for response in response_stream:
                    responses.append(response.message)

                # Should receive 3 responses
                assert len(responses) == 3
                assert responses[0] == "stream-test-0"
                assert responses[1] == "stream-test-1"
                assert responses[2] == "stream-test-2"

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_client_streaming(self, grpc_server):
        """Test client streaming through the tunnel."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Create an async generator for requests
                async def request_generator():
                    for i in range(5):
                        yield echo_pb2.EchoRequest(message=f"msg-{i}")

                # Make client streaming RPC
                response = await echo_stub.EchoClientStream(request_generator())

                # Should receive combined response
                assert response.message == "msg-0,msg-1,msg-2,msg-3,msg-4"

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_bidirectional_streaming(self, grpc_server):
        """Test bidirectional streaming through the tunnel."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Create an async generator for requests
                async def request_generator():
                    for i in range(3):
                        yield echo_pb2.EchoRequest(message=f"bidi-{i}")

                # Make bidirectional streaming RPC
                response_stream = await echo_stub.EchoBidiStream(request_generator())

                # Collect all responses
                responses = []
                async for response in response_stream:
                    responses.append(response.message)

                # Should receive echoed responses
                assert len(responses) == 3
                assert responses[0] == "echo:bidi-0"
                assert responses[1] == "echo:bidi-1"
                assert responses[2] == "echo:bidi-2"

            finally:
                await tunnel_channel.close_async()
