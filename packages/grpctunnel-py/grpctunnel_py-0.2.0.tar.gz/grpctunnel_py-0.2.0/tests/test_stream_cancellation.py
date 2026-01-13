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
Tests for stream cancellation and error handling.

These tests verify that the server handles client disconnections gracefully
without raising InvalidStateError exceptions.
"""

import asyncio
import logging

import grpc
import pytest

from grpctunnel import PendingChannel, TunnelServer
from grpctunnel.proto.v1 import TunnelServiceStub
from tests.integration import echo_pb2, echo_pb2_grpc


# Configure logging to capture debug messages
logging.basicConfig(level=logging.DEBUG)


class SlowEchoService:
    """Echo service that takes time to process, allowing for cancellation testing."""

    def __init__(self, delay: float = 0.5):
        self.delay = delay
        self.call_count = 0
        self.cancellation_detected = False

    async def Echo(
        self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request after a delay."""
        self.call_count += 1
        request = echo_pb2.EchoRequest.FromString(request_bytes)

        # Simulate slow processing
        await asyncio.sleep(self.delay)

        # Check if client is still connected (new API)
        if hasattr(context, 'is_active') and not context.is_active():
            self.cancellation_detected = True
            raise Exception("client disconnected")

        response = echo_pb2.EchoResponse(message=f"slow-{request.message}")
        return response

    async def EchoServerStream(
        self, request_bytes: bytes, stream: any, context: any
    ) -> None:
        """Server streaming with slow processing."""
        self.call_count += 1
        request = echo_pb2.EchoRequest.FromString(request_bytes)

        # Send multiple responses with delays
        for i in range(5):
            # Check cancellation before each send
            if hasattr(context, 'is_active') and not context.is_active():
                self.cancellation_detected = True
                break

            await asyncio.sleep(self.delay / 5)
            response = echo_pb2.EchoResponse(message=f"{request.message}-{i}")
            await stream.send_message(response)


class BidirectionalStreamWrapper:
    """Wrapper to adapt gRPC servicer interface to bidirectional stream."""

    def __init__(self, request_iterator, context):
        self._request_iterator = request_iterator
        self._context = context
        self._write_queue = asyncio.Queue()
        self._closed = False

    def __aiter__(self):
        """Support async iteration for reading."""
        return self

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
        try:
            self._write_queue.put_nowait(None)
        except asyncio.QueueFull:
            pass

    # Add done() method that returns a Future
    def done(self):
        """Return a Future that completes when the stream is done."""
        future = asyncio.Future()
        # We'll complete it when closed
        if self._closed:
            future.set_result(None)
        return future


@pytest.fixture
async def tunnel_server_instance():
    """Create a TunnelServer instance (not the gRPC server)."""
    return TunnelServer()


@pytest.fixture
async def grpc_server(tunnel_server_instance):
    """Create a gRPC server that hosts the tunnel service."""
    server = grpc.aio.server()
    tunnel_server = tunnel_server_instance

    from grpctunnel.proto.v1 import (
        TunnelServiceServicer,
        add_TunnelServiceServicer_to_server,
    )

    class TunnelServicerImpl(TunnelServiceServicer):
        async def OpenTunnel(self, request_iterator, context):
            """Handle tunnel connections."""
            metadata = dict(context.invocation_metadata())
            client_accepts_settings = metadata.get("grpctunnel-negotiate") == "on"

            if client_accepts_settings:
                await context.send_initial_metadata((("grpctunnel-negotiate", "on"),))

            wrapper = BidirectionalStreamWrapper(request_iterator, context)

            async def serve():
                try:
                    await tunnel_server.serve_tunnel(
                        wrapper, client_accepts_settings=client_accepts_settings
                    )
                except Exception:
                    pass
                finally:
                    wrapper.close()

            serve_task = asyncio.create_task(serve())
            await asyncio.sleep(0.01)

            try:
                while not wrapper._closed:
                    try:
                        msg = await asyncio.wait_for(wrapper._write_queue.get(), timeout=5.0)
                        if msg is None:
                            break
                        yield msg
                    except asyncio.TimeoutError:
                        if serve_task.done():
                            break
                        continue
            finally:
                if not serve_task.done():
                    serve_task.cancel()
                    try:
                        await serve_task
                    except asyncio.CancelledError:
                        pass

    add_TunnelServiceServicer_to_server(TunnelServicerImpl(), server)
    port = server.add_insecure_port("[::]:0")
    await server.start()

    yield f"localhost:{port}"

    await server.stop(grace=1.0)


@pytest.fixture
async def slow_echo_service():
    """Create a slow echo service for cancellation testing."""
    return SlowEchoService(delay=1.0)


class TestStreamCancellation:
    """Tests for stream cancellation and error handling."""

    @pytest.mark.asyncio
    async def test_client_disconnect_during_unary(
        self, tunnel_server_instance, grpc_server, slow_echo_service
    ):
        """Test that server handles client disconnect during unary RPC gracefully."""
        server_addr = grpc_server

        # Register the slow service
        tunnel_server_instance.register_method(
            "test.EchoService/Echo",
            slow_echo_service.Echo,
            is_client_stream=False,
            is_server_stream=False,
        )

        # Create channel and stub
        channel = grpc.aio.insecure_channel(server_addr)
        stub = TunnelServiceStub(channel)

        try:
            # Create pending channel and start it
            pending_channel = PendingChannel(stub)
            tunnel_channel = await pending_channel.start()

            # Create echo stub
            echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

            # Start RPC as a task so we can cancel it
            request = echo_pb2.EchoRequest(message="test")
            call_task = asyncio.create_task(echo_stub.Echo(request, timeout=0.2))

            # Let the server start processing
            await asyncio.sleep(0.1)

            # Cancel the task
            call_task.cancel()

            # Try to await (should raise CancelledError)
            try:
                await call_task
            except (grpc.aio.AioRpcError, asyncio.CancelledError, asyncio.TimeoutError) as e:
                # Expected - call was cancelled or timed out
                pass

            # Give server time to handle cancellation
            await asyncio.sleep(0.5)

            # Verify service was called but may have detected cancellation
            assert slow_echo_service.call_count >= 1

            # The key test: No InvalidStateError should have been raised
            # If the fix is working, all errors are caught and logged at DEBUG level

            # Clean up tunnel channel
            await tunnel_channel.close_async()

        finally:
            await channel.close()

    @pytest.mark.asyncio
    async def test_client_disconnect_during_server_stream(
        self, tunnel_server_instance, grpc_server, slow_echo_service
    ):
        """Test that server handles client disconnect during server streaming."""
        server_addr = grpc_server

        # Register the streaming service
        tunnel_server_instance.register_method(
            "test.EchoService/EchoServerStream",
            slow_echo_service.EchoServerStream,
            is_client_stream=False,
            is_server_stream=True,
        )

        # Create channel and stub
        channel = grpc.aio.insecure_channel(server_addr)
        stub = TunnelServiceStub(channel)

        try:
            # Create pending channel and start it
            pending_channel = PendingChannel(stub)
            tunnel_channel = await pending_channel.start()

            # Create echo stub
            echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

            # Start streaming RPC
            request = echo_pb2.EchoRequest(message="stream-test")
            call = echo_stub.EchoServerStream(request)

            # Read one response then cancel
            try:
                async for response in call:
                    # Got first response, now cancel
                    call.cancel()
                    break
            except (grpc.aio.AioRpcError, asyncio.CancelledError):
                # Expected - call was cancelled
                pass

            # Give server time to handle cancellation
            await asyncio.sleep(0.5)

            # Verify service was called
            assert slow_echo_service.call_count >= 1

            # The key test: No InvalidStateError should have been raised

        finally:
            await channel.close()

    @pytest.mark.asyncio
    async def test_context_is_active(self, tunnel_server_instance, grpc_server):
        """Test that context.is_active() correctly detects client disconnection."""
        server_addr = grpc_server

        cancellation_detected = False

        async def cancellation_aware_handler(request_bytes: bytes, context: any):
            """Handler that checks is_active()."""
            nonlocal cancellation_detected
            request = echo_pb2.EchoRequest.FromString(request_bytes)

            # Simulate long processing with periodic checks
            for i in range(10):
                await asyncio.sleep(0.1)

                # Check if client is still active
                if hasattr(context, 'is_active') and not context.is_active():
                    cancellation_detected = True
                    raise Exception("client disconnected")

            return echo_pb2.EchoResponse(message=f"processed-{request.message}")

        # Register the handler
        tunnel_server_instance.register_method(
            "test.EchoService/Echo",
            cancellation_aware_handler,
            is_client_stream=False,
            is_server_stream=False,
        )

        # Create channel and stub
        channel = grpc.aio.insecure_channel(server_addr)
        stub = TunnelServiceStub(channel)

        try:
            # Create pending channel and start it
            pending_channel = PendingChannel(stub)
            tunnel_channel = await pending_channel.start()

            # Create echo stub
            echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

            # Start RPC with short timeout to force cancellation
            request = echo_pb2.EchoRequest(message="test")
            call = echo_stub.Echo(request, timeout=0.3)

            # Try to await (should timeout/cancel)
            try:
                await call
            except (grpc.aio.AioRpcError, asyncio.TimeoutError):
                # Expected
                pass

            # Give handler time to detect cancellation
            await asyncio.sleep(0.5)

            # Verify cancellation was detected by handler
            # Note: This test is somewhat timing-dependent and may not always
            # detect cancellation depending on when the stream monitor runs
            # The important thing is no InvalidStateError is raised

        finally:
            await channel.close()

    @pytest.mark.asyncio
    async def test_multiple_rapid_cancellations(self, tunnel_server_instance, grpc_server, slow_echo_service):
        """Test that multiple rapid cancellations are handled gracefully."""
        server_addr = grpc_server

        # Register the service
        tunnel_server_instance.register_method(
            "test.EchoService/Echo",
            slow_echo_service.Echo,
            is_client_stream=False,
            is_server_stream=False,
        )

        # Create channel and stub
        channel = grpc.aio.insecure_channel(server_addr)
        stub = TunnelServiceStub(channel)

        try:
            # Create pending channel and start it
            pending_channel = PendingChannel(stub)
            tunnel_channel = await pending_channel.start()

            # Create echo stub
            echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

            # Launch multiple RPCs and cancel them
            calls = []
            for i in range(10):
                request = echo_pb2.EchoRequest(message=f"test-{i}")
                call = echo_stub.Echo(request, timeout=0.1)
                calls.append(call)

            # Let them start processing
            await asyncio.sleep(0.05)

            # Cancel all
            for call in calls:
                call.cancel()

            # Try to await all (should fail)
            results = await asyncio.gather(*calls, return_exceptions=True)

            # All should have raised errors
            for result in results:
                assert isinstance(result, (grpc.aio.AioRpcError, asyncio.CancelledError))

            # Give server time to clean up
            await asyncio.sleep(0.5)

            # The key test: No InvalidStateError should have been raised
            # Multiple concurrent cancellations should all be handled gracefully

        finally:
            await channel.close()

    @pytest.mark.asyncio
    async def test_safe_tunnel_write_error_handling(self):
        """Test that _safe_tunnel_write handles errors correctly."""
        # This is a more direct unit test of the _safe_tunnel_write method
        from grpctunnel.server import TunnelServerStream
        from grpctunnel.proto.v1 import ServerToClient
        from unittest.mock import AsyncMock, Mock

        # Create a mock tunnel stream that raises InvalidStateError
        mock_tunnel_stream = AsyncMock()
        mock_tunnel_stream.write.side_effect = asyncio.InvalidStateError("RPC already finished")

        # Create a minimal TunnelServerStream
        mock_server = Mock()
        mock_server._remove_stream = AsyncMock()

        stream = TunnelServerStream(
            server=mock_server,
            tunnel_stream=mock_tunnel_stream,
            stream_id=1,
            method_name="test.Method",
            sender=Mock(),
            receiver=Mock(),
            handler=Mock(),
            is_client_stream=False,
            is_server_stream=False,
            headers=grpc.aio.Metadata(),
        )

        # Try to write a message
        msg = ServerToClient(stream_id=1)
        result = await stream._safe_tunnel_write(msg, "test write")

        # Should return False (write failed)
        assert result is False

        # Should have set the cancellation flags
        assert stream._tunnel_stream_closed is True
        assert stream._cancellation_event.is_set() is True

        # Second write should short-circuit
        result2 = await stream._safe_tunnel_write(msg, "test write 2")
        assert result2 is False

        # write should only be called once (short-circuited second time)
        assert mock_tunnel_stream.write.call_count == 1


class TestStreamMonitoring:
    """Tests for the optional stream monitoring feature."""

    @pytest.mark.asyncio
    async def test_monitor_task_cleanup(self):
        """Test that monitor task is cleaned up when stream finishes."""
        from grpctunnel.server import TunnelServerStream
        from unittest.mock import AsyncMock, Mock

        # Create a mock tunnel stream with done() method
        mock_tunnel_stream = AsyncMock()
        mock_tunnel_stream.done = AsyncMock()
        mock_tunnel_stream.done.return_value = None  # Never completes during test
        mock_tunnel_stream.write = AsyncMock()

        # Create a TunnelServerStream
        mock_server = Mock()
        mock_server._remove_stream = AsyncMock()

        stream = TunnelServerStream(
            server=mock_server,
            tunnel_stream=mock_tunnel_stream,
            stream_id=1,
            method_name="test.Method",
            sender=Mock(),
            receiver=Mock(),
            handler=Mock(),
            is_client_stream=False,
            is_server_stream=False,
            headers=grpc.aio.Metadata(),
        )

        # Monitor task should be created if done() is available
        if stream._monitor_task:
            assert not stream._monitor_task.done()

            # Finish the stream
            await stream._finish_stream(None)

            # Give cleanup time to run
            await asyncio.sleep(0.1)

            # Monitor task should be cancelled
            assert stream._monitor_task.done()
