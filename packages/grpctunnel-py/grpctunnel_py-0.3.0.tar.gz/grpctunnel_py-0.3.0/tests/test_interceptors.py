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

"""Tests for interceptor support in grpctunnel."""

import asyncio
from typing import Any, List

import grpc
import pytest

from grpctunnel import (
    PendingChannel,
    TunnelServer,
    TunnelServiceHandler,
    TunnelServiceHandlerOptions,
    tunnel_channel_from_context,
)
from grpctunnel.interceptors import (
    InterceptedTunnelChannel,
    LoggingInterceptor,
    MetadataInterceptor,
    TunnelServerInterceptor,
    intercept_tunnel_channel,
)
from grpctunnel.proto.v1 import (
    TunnelServiceStub,
    add_TunnelServiceServicer_to_server,
)
from tests.integration import echo_pb2, echo_pb2_grpc


class RecordingInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Test interceptor that records calls."""

    def __init__(self):
        """Initialize the recording interceptor."""
        self.calls: List[tuple] = []
        self.responses: List[Any] = []

    async def intercept_unary_unary(
        self,
        continuation: Any,
        client_call_details: Any,
        request: Any,
    ) -> Any:
        """Record the call and pass it through."""
        self.calls.append((client_call_details.method, request))
        # Call the continuation to get the actual response
        response = await continuation(client_call_details, request)
        self.responses.append(response)
        return response


class ModifyingInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Test interceptor that modifies requests."""

    def __init__(self, prefix: str):
        """Initialize the modifying interceptor."""
        self.prefix = prefix

    async def intercept_unary_unary(
        self,
        continuation: Any,
        client_call_details: Any,
        request: Any,
    ) -> Any:
        """Modify the request before passing it through."""
        # Modify the request if it's an EchoRequest
        if hasattr(request, 'message'):
            modified = echo_pb2.EchoRequest(
                message=f"{self.prefix}{request.message}"
            )
            return await continuation(client_call_details, modified)
        return await continuation(client_call_details, request)


class BlockingInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
    """Test interceptor that blocks certain calls."""

    def __init__(self, block_methods: List[str]):
        """Initialize the blocking interceptor."""
        self.block_methods = block_methods

    async def intercept_unary_unary(
        self,
        continuation: Any,
        client_call_details: Any,
        request: Any,
    ) -> Any:
        """Block calls to specific methods."""
        if client_call_details.method in self.block_methods:
            raise grpc.aio.AioRpcError(
                code=grpc.StatusCode.PERMISSION_DENIED,
                initial_metadata=grpc.aio.Metadata(),
                trailing_metadata=grpc.aio.Metadata(),
                details=f"Method {client_call_details.method} is blocked",
            )
        return await continuation(client_call_details, request)


class RecordingStreamInterceptor(grpc.aio.UnaryStreamClientInterceptor):
    """Test interceptor that records unary-stream calls."""

    def __init__(self):
        """Initialize the recording stream interceptor."""
        self.calls: List[tuple] = []
        self.response_counts: List[int] = []

    async def intercept_unary_stream(
        self,
        continuation: Any,
        client_call_details: Any,
        request: Any,
    ):
        """Record the call and pass it through."""
        self.calls.append((client_call_details.method, request))

        # Call the continuation to get the stream
        response_stream = await continuation(client_call_details, request)

        # Wrap the stream to count responses
        async def counted_stream():
            count = 0
            async for response in response_stream:
                count += 1
                yield response
            self.response_counts.append(count)

        return counted_stream()


class CountingClientStreamInterceptor(grpc.aio.StreamUnaryClientInterceptor):
    """Test interceptor that counts client streaming requests."""

    def __init__(self):
        """Initialize the counting interceptor."""
        self.calls: List[str] = []
        self.request_counts: List[int] = []

    async def intercept_stream_unary(
        self,
        continuation: Any,
        client_call_details: Any,
        request_iterator: Any,
    ) -> Any:
        """Count requests and pass them through."""
        self.calls.append(client_call_details.method)

        # Count and forward requests
        async def counted_iterator():
            count = 0
            async for request in request_iterator:
                count += 1
                yield request
            self.request_counts.append(count)

        # Call continuation with counted iterator
        response = await continuation(client_call_details, counted_iterator())
        return response


class ModifyingBidiInterceptor(grpc.aio.StreamStreamClientInterceptor):
    """Test interceptor that modifies bidirectional stream messages."""

    def __init__(self, request_prefix: str, response_prefix: str):
        """Initialize the modifying bidi interceptor."""
        self.request_prefix = request_prefix
        self.response_prefix = response_prefix

    async def intercept_stream_stream(
        self,
        continuation: Any,
        client_call_details: Any,
        request_iterator: Any,
    ):
        """Modify both request and response streams."""
        # Modify requests
        async def modified_requests():
            async for request in request_iterator:
                if hasattr(request, 'message'):
                    modified = echo_pb2.EchoRequest(
                        message=f"{self.request_prefix}{request.message}"
                    )
                    yield modified
                else:
                    yield request

        # Call continuation with modified requests
        response_stream = await continuation(client_call_details, modified_requests())

        # Modify responses
        async def modified_responses():
            async for response in response_stream:
                if hasattr(response, 'message'):
                    modified = echo_pb2.EchoResponse(
                        message=f"{self.response_prefix}{response.message}"
                    )
                    yield modified
                else:
                    yield response

        return modified_responses()


# Server-side interceptors for testing


class RecordingServerInterceptor(grpc.aio.ServerInterceptor):
    """Test server interceptor that records method calls."""

    def __init__(self):
        """Initialize the recording server interceptor."""
        self.calls: List[str] = []

    def intercept_service(
        self,
        continuation: Any,
        handler_call_details: Any,
    ) -> Any:
        """Record the method call and pass through."""
        self.calls.append(handler_call_details.method)
        handler = continuation(handler_call_details)
        return handler


class ModifyingServerInterceptor(grpc.aio.ServerInterceptor):
    """Test server interceptor that modifies handler behavior."""

    def __init__(self, response_prefix: str):
        """Initialize the modifying server interceptor."""
        self.response_prefix = response_prefix

    def intercept_service(
        self,
        continuation: Any,
        handler_call_details: Any,
    ) -> Any:
        """Wrap the handler to modify responses."""
        # Get the original handler
        original_handler = continuation(handler_call_details)

        if original_handler is None:
            return None

        # Wrap the handler to modify responses
        async def modified_handler(request, context):
            # Call original handler
            response = await original_handler(request, context)

            # Modify the response if it has a message field
            if hasattr(response, 'message'):
                return echo_pb2.EchoResponse(
                    message=f"{self.response_prefix}{response.message}"
                )
            return response

        return modified_handler


class ErrorServerInterceptor(grpc.aio.ServerInterceptor):
    """Test server interceptor that raises errors for specific methods."""

    def __init__(self, error_methods: List[str]):
        """Initialize the error server interceptor."""
        self.error_methods = error_methods

    def intercept_service(
        self,
        continuation: Any,
        handler_call_details: Any,
    ) -> Any:
        """Raise error for specific methods."""
        if handler_call_details.method in self.error_methods:
            # Return a handler that raises an error
            async def error_handler(request, context):
                raise grpc.aio.AioRpcError(
                    code=grpc.StatusCode.INTERNAL,
                    initial_metadata=grpc.aio.Metadata(),
                    trailing_metadata=grpc.aio.Metadata(),
                    details=f"Server interceptor error for {handler_call_details.method}",
                )
            return error_handler

        # Pass through for other methods
        return continuation(handler_call_details)


class EchoServiceImpl:
    """Simple echo service implementation for testing."""

    async def Echo(
        self, request_bytes: bytes, context: Any = None
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)

        # For testing, always return with [tunnel] prefix since we're testing tunnel interceptors
        return echo_pb2.EchoResponse(message=f"[tunnel] {request.message}")

    async def EchoServerStream(
        self, request_bytes: bytes, stream: Any, context: Any = None
    ) -> None:
        """Server streaming - send multiple responses."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        for i in range(3):
            response = echo_pb2.EchoResponse(message=f"[tunnel] {request.message}-{i}")
            await stream.send_message(response)

    async def EchoClientStream(
        self, stream: Any, context: Any = None
    ) -> echo_pb2.EchoResponse:
        """Client streaming - receive multiple requests."""
        messages = []
        try:
            while True:
                request_bytes = await stream.recv_message()
                request = echo_pb2.EchoRequest.FromString(request_bytes)
                messages.append(request.message)
        except StopAsyncIteration:
            pass
        combined = ",".join(messages)
        return echo_pb2.EchoResponse(message=f"[tunnel] {combined}")

    async def EchoBidiStream(self, stream: Any, context: Any = None) -> None:
        """Bidirectional streaming."""
        try:
            while True:
                request_bytes = await stream.recv_message()
                request = echo_pb2.EchoRequest.FromString(request_bytes)
                response = echo_pb2.EchoResponse(message=f"[tunnel] echo:{request.message}")
                await stream.send_message(response)
        except StopAsyncIteration:
            pass


@pytest.fixture
async def tunnel_server_with_echo():
    """Create a gRPC server with tunnel and echo service."""
    server = grpc.aio.server()

    # Create tunnel handler
    handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

    # Register echo service with tunnel
    echo_service = EchoServiceImpl()
    handler.register_method(
        "test.EchoService/Echo",
        echo_service.Echo,
        is_client_stream=False,
        is_server_stream=False,
    )
    handler.register_method(
        "test.EchoService/EchoServerStream",
        echo_service.EchoServerStream,
        is_client_stream=False,
        is_server_stream=True,
    )
    handler.register_method(
        "test.EchoService/EchoClientStream",
        echo_service.EchoClientStream,
        is_client_stream=True,
        is_server_stream=False,
    )
    handler.register_method(
        "test.EchoService/EchoBidiStream",
        echo_service.EchoBidiStream,
        is_client_stream=True,
        is_server_stream=True,
    )

    # Register tunnel service with server
    add_TunnelServiceServicer_to_server(handler.service(), server)

    # Start server on random port
    port = server.add_insecure_port("[::]:0")
    await server.start()

    yield f"localhost:{port}"

    await server.stop(grace=1.0)


class TestClientInterceptors:
    """Tests for client-side interceptors with tunnels."""

    @pytest.mark.asyncio
    async def test_single_interceptor(self, tunnel_server_with_echo):
        """Test that a single interceptor works with tunnels."""
        # Create tunnel connection
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Create recording interceptor
            interceptor = RecordingInterceptor()

            # Wrap channel with interceptor
            intercepted = intercept_tunnel_channel(tunnel_channel, [interceptor])

            # Create echo stub and make call
            echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)
            request = echo_pb2.EchoRequest(message="test message")
            response = await echo_stub.Echo(request)

            # Verify interceptor was called
            assert len(interceptor.calls) == 1
            assert interceptor.calls[0][0] == "/test.EchoService/Echo"
            assert interceptor.calls[0][1].message == "test message"

            # Verify response was recorded (from actual service through tunnel)
            assert len(interceptor.responses) == 1
            assert response.message == "[tunnel] test message"

            await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_multiple_interceptors(self, tunnel_server_with_echo):
        """Test that multiple interceptors work in correct order."""
        # Create tunnel connection
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Create interceptors
            recording = RecordingInterceptor()
            modifying = ModifyingInterceptor(prefix="modified:")

            # Wrap channel with interceptors (modifying first, then recording)
            # Order matters: modifying will run first, then recording
            intercepted = intercept_tunnel_channel(
                tunnel_channel, [modifying, recording]
            )

            # Create echo stub and make call
            echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)
            request = echo_pb2.EchoRequest(message="test")
            response = await echo_stub.Echo(request)

            # Verify recording interceptor saw the modified request
            # The interceptors are applied in order: modifying -> recording -> service
            # Recording sees the modified request (after modifying interceptor)
            assert len(recording.calls) == 1
            assert recording.calls[0][1].message == "modified:test"

            # Verify response contains modified message (modified by the modifying interceptor)
            # The modifying interceptor modifies the request before it reaches the service
            assert response.message == "[tunnel] modified:test"

            await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_blocking_interceptor(self, tunnel_server_with_echo):
        """Test that interceptors can block calls."""
        # Create tunnel connection
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Create blocking interceptor
            blocking = BlockingInterceptor(["/test.EchoService/Echo"])

            # Wrap channel with interceptor
            intercepted = intercept_tunnel_channel(tunnel_channel, [blocking])

            # Create echo stub and try to make call
            echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)
            request = echo_pb2.EchoRequest(message="test")

            # Verify call is blocked
            with pytest.raises(grpc.RpcError) as exc_info:
                await echo_stub.Echo(request)

            assert exc_info.value.code() == grpc.StatusCode.PERMISSION_DENIED
            assert "blocked" in exc_info.value.details()

            await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_metadata_interceptor(self, tunnel_server_with_echo):
        """Test that metadata interceptor adds headers."""
        # Create tunnel connection
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Create metadata interceptor
            metadata_interceptor = MetadataInterceptor([
                ("custom-header", "custom-value"),
                ("another-header", "another-value"),
            ])

            # Wrap channel with interceptor
            intercepted = intercept_tunnel_channel(
                tunnel_channel, [metadata_interceptor]
            )

            # Make call
            echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)
            request = echo_pb2.EchoRequest(message="test")
            response = await echo_stub.Echo(request)

            # Verify response (metadata handling would need server-side support)
            assert response.message == "[tunnel] test"

            await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_interceptor_with_error(self, tunnel_server_with_echo):
        """Test that interceptors properly handle errors."""

        class ErrorInterceptor(grpc.aio.UnaryUnaryClientInterceptor):
            """Interceptor that raises an error."""

            async def intercept_unary_unary(
                self, continuation: Any, client_call_details: Any, request: Any
            ) -> Any:
                raise ValueError("Test error from interceptor")

        # Create tunnel connection
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Create error interceptor
            error_interceptor = ErrorInterceptor()

            # Wrap channel with interceptor
            intercepted = intercept_tunnel_channel(
                tunnel_channel, [error_interceptor]
            )

            # Make call and verify error is raised
            echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)
            request = echo_pb2.EchoRequest(message="test")

            with pytest.raises(ValueError) as exc_info:
                await echo_stub.Echo(request)

            assert "Test error from interceptor" in str(exc_info.value)

            await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_unary_stream_single_interceptor(self, tunnel_server_with_echo):
        """Test that server streaming works with a single interceptor."""
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Create recording stream interceptor
            interceptor = RecordingStreamInterceptor()

            # Wrap channel with interceptor
            intercepted = intercept_tunnel_channel(tunnel_channel, [interceptor])

            # Create echo stub and make server streaming call
            echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)
            request = echo_pb2.EchoRequest(message="stream-test")
            response_stream = await echo_stub.EchoServerStream(request)

            # Collect all responses
            responses = []
            async for response in response_stream:
                responses.append(response.message)

            # Verify interceptor was called
            assert len(interceptor.calls) == 1
            assert interceptor.calls[0][0] == "/test.EchoService/EchoServerStream"
            assert interceptor.calls[0][1].message == "stream-test"

            # Verify response count was recorded
            assert len(interceptor.response_counts) == 1
            assert interceptor.response_counts[0] == 3

            # Verify responses
            assert len(responses) == 3
            assert responses[0] == "[tunnel] stream-test-0"
            assert responses[1] == "[tunnel] stream-test-1"
            assert responses[2] == "[tunnel] stream-test-2"

            await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_stream_unary_single_interceptor(self, tunnel_server_with_echo):
        """Test that client streaming works with a single interceptor."""
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Create counting client stream interceptor
            interceptor = CountingClientStreamInterceptor()

            # Wrap channel with interceptor
            intercepted = intercept_tunnel_channel(tunnel_channel, [interceptor])

            # Create echo stub and make client streaming call
            echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)

            # Create request generator
            async def request_generator():
                for i in range(5):
                    yield echo_pb2.EchoRequest(message=f"msg-{i}")

            # Make call
            response = await echo_stub.EchoClientStream(request_generator())

            # Verify interceptor was called
            assert len(interceptor.calls) == 1
            assert interceptor.calls[0] == "/test.EchoService/EchoClientStream"

            # Verify request count was recorded
            assert len(interceptor.request_counts) == 1
            assert interceptor.request_counts[0] == 5

            # Verify response
            assert response.message == "[tunnel] msg-0,msg-1,msg-2,msg-3,msg-4"

            await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_stream_stream_single_interceptor(self, tunnel_server_with_echo):
        """Test that bidirectional streaming works with a single interceptor."""
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Create modifying bidi interceptor
            interceptor = ModifyingBidiInterceptor(
                request_prefix="req:", response_prefix="resp:"
            )

            # Wrap channel with interceptor
            intercepted = intercept_tunnel_channel(tunnel_channel, [interceptor])

            # Create echo stub and make bidi streaming call
            echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)

            # Create request generator
            async def request_generator():
                for i in range(3):
                    yield echo_pb2.EchoRequest(message=f"bidi-{i}")

            # Make call
            response_stream = await echo_stub.EchoBidiStream(request_generator())

            # Collect all responses
            responses = []
            async for response in response_stream:
                responses.append(response.message)

            # Verify responses were modified
            # Requests are modified with "req:" prefix, then server echoes them
            # Then responses are modified with "resp:" prefix
            assert len(responses) == 3
            assert responses[0] == "resp:[tunnel] echo:req:bidi-0"
            assert responses[1] == "resp:[tunnel] echo:req:bidi-1"
            assert responses[2] == "resp:[tunnel] echo:req:bidi-2"

            await tunnel_channel.close_async()


class TestInterceptedChannelMethods:
    """Tests for InterceptedTunnelChannel methods."""

    @pytest.mark.asyncio
    async def test_channel_state_methods(self, tunnel_server_with_echo):
        """Test that state methods work on intercepted channel."""
        # Create tunnel connection
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Wrap with empty interceptors
            intercepted = InterceptedTunnelChannel(tunnel_channel, [])

            # Wait for channel to be ready
            await intercepted.channel_ready()

            # Test state methods
            state = intercepted.get_state()
            assert state == grpc.ChannelConnectivity.READY

            # Test close
            await intercepted.close_async()

            # Verify closed state
            state = intercepted.get_state()
            assert state == grpc.ChannelConnectivity.SHUTDOWN

    @pytest.mark.asyncio
    async def test_context_manager(self, tunnel_server_with_echo):
        """Test that intercepted channel works as context manager."""
        async with grpc.aio.insecure_channel(tunnel_server_with_echo) as channel:
            stub = TunnelServiceStub(channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            # Use intercepted channel as context manager
            async with InterceptedTunnelChannel(tunnel_channel, []) as intercepted:
                # Wait for channel to be ready
                await intercepted.channel_ready()

                echo_stub = echo_pb2_grpc.EchoServiceStub(intercepted)
                request = echo_pb2.EchoRequest(message="test")
                response = await echo_stub.Echo(request)
                assert response.message == "[tunnel] test"

            # Channel should be closed after context exit
            state = intercepted.get_state()
            assert state == grpc.ChannelConnectivity.SHUTDOWN


class TestServerInterceptors:
    """Tests for server-side interceptors with tunnels."""

    @pytest.mark.asyncio
    async def test_server_single_interceptor(self):
        """Test that a single server interceptor works with tunnels."""
        # Create recording server interceptor
        server_interceptor = RecordingServerInterceptor()

        # Create server
        server = grpc.aio.server()

        # Create tunnel handler with server interceptor
        options = TunnelServiceHandlerOptions(
            server_interceptors=[server_interceptor]
        )
        handler = TunnelServiceHandler(options)

        # Register echo service
        echo_service = EchoServiceImpl()
        handler.register_method(
            "test.EchoService/Echo",
            echo_service.Echo,
            is_client_stream=False,
            is_server_stream=False,
        )

        # Register tunnel service with server
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # Start server
        port = server.add_insecure_port("[::]:0")
        await server.start()

        try:
            # Create client connection
            async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
                stub = TunnelServiceStub(channel)
                pending = PendingChannel(stub)
                tunnel_channel = await pending.start()

                # Make call
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)
                request = echo_pb2.EchoRequest(message="test")
                response = await echo_stub.Echo(request)

                # Verify interceptor recorded the call
                assert len(server_interceptor.calls) == 1
                assert server_interceptor.calls[0] == "test.EchoService/Echo"

                # Verify response
                assert response.message == "[tunnel] test"

                await tunnel_channel.close_async()
        finally:
            await server.stop(grace=1.0)

    @pytest.mark.asyncio
    async def test_server_multiple_interceptors(self):
        """Test that multiple server interceptors work in correct order."""
        # Create interceptors
        recording = RecordingServerInterceptor()
        modifying = ModifyingServerInterceptor(response_prefix="[modified] ")

        # Create server
        server = grpc.aio.server()

        # Create tunnel handler with multiple interceptors
        # Order matters: they are applied in order
        options = TunnelServiceHandlerOptions(
            server_interceptors=[recording, modifying]
        )
        handler = TunnelServiceHandler(options)

        # Register echo service
        echo_service = EchoServiceImpl()
        handler.register_method(
            "test.EchoService/Echo",
            echo_service.Echo,
            is_client_stream=False,
            is_server_stream=False,
        )

        # Register tunnel service
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # Start server
        port = server.add_insecure_port("[::]:0")
        await server.start()

        try:
            # Create client connection
            async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
                stub = TunnelServiceStub(channel)
                pending = PendingChannel(stub)
                tunnel_channel = await pending.start()

                # Make call
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)
                request = echo_pb2.EchoRequest(message="test")
                response = await echo_stub.Echo(request)

                # Verify recording interceptor recorded the call
                assert len(recording.calls) == 1
                assert recording.calls[0] == "test.EchoService/Echo"

                # Verify response was modified by the modifying interceptor
                assert response.message == "[modified] [tunnel] test"

                await tunnel_channel.close_async()
        finally:
            await server.stop(grace=1.0)

    @pytest.mark.asyncio
    async def test_server_interceptor_all_methods(self):
        """Test that server interceptors work with all method types."""
        # Create recording interceptor
        recording = RecordingServerInterceptor()

        # Create server
        server = grpc.aio.server()

        # Create tunnel handler with interceptor
        options = TunnelServiceHandlerOptions(
            server_interceptors=[recording]
        )
        handler = TunnelServiceHandler(options)

        # Register all method types
        echo_service = EchoServiceImpl()
        handler.register_method(
            "test.EchoService/Echo",
            echo_service.Echo,
            is_client_stream=False,
            is_server_stream=False,
        )
        handler.register_method(
            "test.EchoService/EchoServerStream",
            echo_service.EchoServerStream,
            is_client_stream=False,
            is_server_stream=True,
        )
        handler.register_method(
            "test.EchoService/EchoClientStream",
            echo_service.EchoClientStream,
            is_client_stream=True,
            is_server_stream=False,
        )
        handler.register_method(
            "test.EchoService/EchoBidiStream",
            echo_service.EchoBidiStream,
            is_client_stream=True,
            is_server_stream=True,
        )

        # Register tunnel service
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # Start server
        port = server.add_insecure_port("[::]:0")
        await server.start()

        try:
            # Create client connection
            async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
                stub = TunnelServiceStub(channel)
                pending = PendingChannel(stub)
                tunnel_channel = await pending.start()

                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                # Test unary-unary
                request = echo_pb2.EchoRequest(message="test")
                response = await echo_stub.Echo(request)
                assert response.message == "[tunnel] test"

                # Test unary-stream
                request = echo_pb2.EchoRequest(message="stream")
                response_stream = await echo_stub.EchoServerStream(request)
                responses = []
                async for r in response_stream:
                    responses.append(r.message)
                assert len(responses) == 3

                # Test stream-unary
                async def request_gen():
                    for i in range(3):
                        yield echo_pb2.EchoRequest(message=f"msg{i}")

                response = await echo_stub.EchoClientStream(request_gen())
                assert "msg0" in response.message

                # Test stream-stream
                async def bidi_gen():
                    for i in range(2):
                        yield echo_pb2.EchoRequest(message=f"bidi{i}")

                stream = await echo_stub.EchoBidiStream(bidi_gen())
                bidi_responses = []
                async for r in stream:
                    bidi_responses.append(r.message)
                assert len(bidi_responses) == 2

                # Verify all methods were intercepted
                assert len(recording.calls) == 4
                assert "test.EchoService/Echo" in recording.calls
                assert "test.EchoService/EchoServerStream" in recording.calls
                assert "test.EchoService/EchoClientStream" in recording.calls
                assert "test.EchoService/EchoBidiStream" in recording.calls

                await tunnel_channel.close_async()
        finally:
            await server.stop(grace=1.0)

    @pytest.mark.asyncio
    async def test_server_interceptor_error_handling(self):
        """Test that server interceptors can raise errors."""
        # Create error interceptor
        error_interceptor = ErrorServerInterceptor(
            error_methods=["test.EchoService/Echo"]
        )

        # Create server
        server = grpc.aio.server()

        # Create tunnel handler with error interceptor
        options = TunnelServiceHandlerOptions(
            server_interceptors=[error_interceptor]
        )
        handler = TunnelServiceHandler(options)

        # Register echo service
        echo_service = EchoServiceImpl()
        handler.register_method(
            "test.EchoService/Echo",
            echo_service.Echo,
            is_client_stream=False,
            is_server_stream=False,
        )

        # Register tunnel service
        add_TunnelServiceServicer_to_server(handler.service(), server)

        # Start server
        port = server.add_insecure_port("[::]:0")
        await server.start()

        try:
            # Create client connection
            async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
                stub = TunnelServiceStub(channel)
                pending = PendingChannel(stub)
                tunnel_channel = await pending.start()

                # Make call and expect error
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)
                request = echo_pb2.EchoRequest(message="test")

                with pytest.raises(grpc.RpcError) as exc_info:
                    await echo_stub.Echo(request)

                # Verify error details
                assert exc_info.value.code() == grpc.StatusCode.INTERNAL
                assert "Server interceptor error" in exc_info.value.details()

                await tunnel_channel.close_async()
        finally:
            await server.stop(grace=1.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])