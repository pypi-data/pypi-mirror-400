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

"""Tests for Go-compatible TunnelChannel methods."""

import asyncio

import grpc
import pytest

from grpctunnel import PendingChannel, TunnelServer
from tests.integration import echo_pb2, echo_pb2_grpc


class EchoServiceImpl:
    """Simple echo service for testing."""

    async def Echo(
        self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message."""
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        return echo_pb2.EchoResponse(message=request.message)


class BidirectionalStreamWrapper:
    """Wrapper for bidirectional streaming."""

    def __init__(self, request_iterator, context):
        self._request_iterator = request_iterator
        self._context = context
        self._write_queue = asyncio.Queue()
        self._closed = False

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

    def close(self):
        """Mark the wrapper as closed."""
        self._closed = True
        try:
            self._write_queue.put_nowait(None)
        except asyncio.QueueFull:
            pass


@pytest.fixture
async def grpc_server():
    """Create a gRPC server with tunnel service for testing."""
    server = grpc.aio.server()

    # Create tunnel server
    tunnel_server = TunnelServer()

    # Register echo service
    echo_service = EchoServiceImpl()
    tunnel_server.register_method(
        "test.EchoService/Echo",
        echo_service.Echo,
        is_client_stream=False,
        is_server_stream=False,
    )

    # Register tunnel servicer
    from grpctunnel.proto.v1 import (
        TunnelServiceServicer,
        add_TunnelServiceServicer_to_server,
    )

    class TunnelServicerImpl(TunnelServiceServicer):
        async def OpenTunnel(self, request_iterator, context):
            """Handle tunnel connections."""
            # Check for negotiation
            metadata = dict(context.invocation_metadata())
            client_accepts_settings = metadata.get("grpctunnel-negotiate") == "on"

            if client_accepts_settings:
                await context.send_initial_metadata((("grpctunnel-negotiate", "on"),))

            # Create wrapper and serve tunnel
            wrapper = BidirectionalStreamWrapper(request_iterator, context)

            async def serve():
                try:
                    await tunnel_server.serve_tunnel(
                        wrapper, client_accepts_settings=client_accepts_settings
                    )
                finally:
                    wrapper.close()

            serve_task = asyncio.create_task(serve())
            await asyncio.sleep(0.01)  # Let serve task start

            try:
                while not wrapper._closed:
                    try:
                        msg = await asyncio.wait_for(
                            wrapper._write_queue.get(), timeout=5.0
                        )
                        if msg is None:
                            break
                        yield msg
                    except asyncio.TimeoutError:
                        if serve_task.done():
                            break
                        continue
            finally:
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

    # Start server
    port = server.add_insecure_port("[::]:0")
    await server.start()

    yield f"localhost:{port}"

    await server.stop(grace=1.0)


class TestTunnelChannelCompatibility:
    """Tests for Go-compatible TunnelChannel methods."""

    @pytest.mark.asyncio
    async def test_done_method(self, grpc_server):
        """Test the done() method returns an asyncio.Event."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Get the done event
                done_event = tunnel_channel.done()

                # Verify it's an asyncio.Event
                assert isinstance(done_event, asyncio.Event)

                # Should not be set initially
                assert not done_event.is_set()

                # Make a successful RPC
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)
                request = echo_pb2.EchoRequest(message="Test")
                response = await echo_stub.Echo(request)
                assert response.message == "Test"

                # Still not set after successful RPC
                assert not done_event.is_set()

                # Close the channel
                await tunnel_channel.close_async()

                # Now it should be set
                assert done_event.is_set()

            except:
                await tunnel_channel.close_async()
                raise

    @pytest.mark.asyncio
    async def test_err_method_normal_close(self, grpc_server):
        """Test the err() method returns None on normal close."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Initially no error
                assert tunnel_channel.err() is None

                # Close normally
                await tunnel_channel.close_async()

                # Should still be None after normal close
                assert tunnel_channel.err() is None

            except:
                await tunnel_channel.close_async()
                raise

    @pytest.mark.asyncio
    async def test_err_method_with_error(self, grpc_server):
        """Test the err() method returns the error that caused closure."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Initially no error
                assert tunnel_channel.err() is None

                # Simulate an error by forcefully closing the underlying stream
                # This is a bit hacky but demonstrates the error capture
                test_error = Exception("Test error")
                tunnel_channel._error = test_error
                tunnel_channel._closed = True
                tunnel_channel._done_event.set()

                # Now err() should return our error
                err = tunnel_channel.err()
                assert err is not None
                assert err == test_error

            finally:
                # Clean up
                if not tunnel_channel._closed:
                    await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_context_method(self, grpc_server):
        """Test the context() method returns channel context."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Get the context
                ctx = tunnel_channel.context()

                # Verify it's a dictionary
                assert isinstance(ctx, dict)

                # Should contain stream and tunnel_metadata keys
                assert "stream" in ctx
                assert "tunnel_metadata" in ctx

                # Stream should be the underlying stream
                assert ctx["stream"] is not None

                # tunnel_metadata should be a Metadata object or dict
                tunnel_metadata = ctx["tunnel_metadata"]
                # It could be grpc.aio.Metadata or dict depending on the context
                assert tunnel_metadata is not None

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_done_event_awaitable(self, grpc_server):
        """Test that done() event can be awaited."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                done_event = tunnel_channel.done()

                # Start a task to wait for done
                async def wait_for_done():
                    await done_event.wait()
                    return True

                wait_task = asyncio.create_task(wait_for_done())

                # Give it a moment
                await asyncio.sleep(0.1)

                # Should still be waiting
                assert not wait_task.done()

                # Close the channel
                await tunnel_channel.close_async()

                # Now the wait should complete
                result = await asyncio.wait_for(wait_task, timeout=1.0)
                assert result is True

            except:
                await tunnel_channel.close_async()
                raise

    @pytest.mark.asyncio
    async def test_multiple_done_calls_return_same_event(self, grpc_server):
        """Test that multiple calls to done() return the same Event."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Get done event multiple times
                event1 = tunnel_channel.done()
                event2 = tunnel_channel.done()
                event3 = tunnel_channel.done()

                # Should all be the same object
                assert event1 is event2
                assert event2 is event3

            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_compatibility_with_go_patterns(self, grpc_server):
        """Test that the methods work in Go-like usage patterns."""
        async with grpc.aio.insecure_channel(grpc_server) as transport_channel:
            from grpctunnel.proto.v1 import TunnelServiceStub

            stub = TunnelServiceStub(transport_channel)
            pending = PendingChannel(stub)
            tunnel_channel = await pending.start()

            try:
                # Simulate Go-style usage:
                # 1. Get done channel for monitoring
                done = tunnel_channel.done()

                # 2. Get context for passing around
                ctx = tunnel_channel.context()
                assert ctx is not None

                # 3. Do some work
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)
                request = echo_pb2.EchoRequest(message="Go-style")
                response = await echo_stub.Echo(request)
                assert response.message == "Go-style"

                # 4. Check for errors periodically
                assert tunnel_channel.err() is None

                # 5. Close and wait for done
                await tunnel_channel.close_async()
                await done.wait()

                # 6. Check final error state
                assert tunnel_channel.err() is None  # No error on clean close

            except Exception as e:
                # In case of error, close and capture
                await tunnel_channel.close_async()
                # In a real scenario, tunnel_channel.err() might return e
                raise