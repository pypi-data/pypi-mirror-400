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

"""Tests for automatic service registration in grpctunnel."""

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


class FullEchoService(echo_pb2_grpc.EchoServiceServicer):
    """Echo service implementation with all method types.

    This class extends the generated EchoServiceServicer base class, which allows
    grpctunnel to automatically detect the service name and method signatures.
    """

    async def Echo(
        self, request: echo_pb2.EchoRequest, context: any
    ) -> echo_pb2.EchoResponse:
        """Unary-unary method."""
        return echo_pb2.EchoResponse(message=f"Echo: {request.message}")

    async def EchoError(
        self, request: echo_pb2.ErrorRequest, context: any
    ) -> echo_pb2.EchoResponse:
        """Unary-unary method that returns error."""
        raise Exception(f"Error: {request.message}")

    async def EchoServerStream(
        self, request: echo_pb2.EchoRequest, context: any
    ):
        """Unary-server streaming method."""
        for i in range(3):
            yield echo_pb2.EchoResponse(message=f"{request.message}-{i}")

    async def EchoClientStream(
        self, request_iterator, context: any
    ) -> echo_pb2.EchoResponse:
        """Client streaming-unary method."""
        messages = []
        async for request in request_iterator:
            messages.append(request.message)
        return echo_pb2.EchoResponse(message=",".join(messages))

    async def EchoBidiStream(self, request_iterator, context: any):
        """Bidirectional streaming method."""
        async for request in request_iterator:
            yield echo_pb2.EchoResponse(message=f"bidi:{request.message}")


@pytest.fixture
async def tunnel_server():
    """Create a gRPC server with tunnel support."""
    server = grpc.aio.server()
    handler = TunnelServiceHandler(TunnelServiceHandlerOptions())
    add_TunnelServiceServicer_to_server(handler.service(), server)

    port = server.add_insecure_port("[::]:0")
    await server.start()

    yield f"localhost:{port}", handler

    await server.stop(grace=1.0)


class TestRegisterService:
    """Tests for register_service functionality."""

    @pytest.mark.asyncio
    async def test_register_service_reverse_tunnel(self, tunnel_server):
        """Test register_service with reverse tunnel."""
        server_address, handler = tunnel_server

        async with grpc.aio.insecure_channel(server_address) as channel:
            tunnel_stub = TunnelServiceStub(channel)
            reverse_server = ReverseTunnelServer(tunnel_stub)

            # Create service implementation
            service = FullEchoService()

            # Register service - auto-detects service name and method signatures
            reverse_server.register_service(service)

            # Start reverse tunnel
            tunnel_task = asyncio.create_task(reverse_server.serve())

            # Wait for tunnel to establish
            await asyncio.sleep(0.5)

            # Get reverse channel
            reverse_channel = handler.as_channel()
            assert reverse_channel is not None

            # Wait for channel to be ready
            await reverse_channel.wait_for_ready(timeout=2.0)

            # Create stub and test unary call
            echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

            # Test 1: Unary call
            request = echo_pb2.EchoRequest(message="test")
            response = await echo_stub.Echo(request)
            assert response.message == "Echo: test"

            # TODO: Add streaming tests once streaming support is implemented

            # Clean up
            await reverse_server.stop()
            try:
                await asyncio.wait_for(tunnel_task, timeout=2.0)
            except asyncio.TimeoutError:
                pass

    @pytest.mark.asyncio
    async def test_register_service_forward_tunnel(self):
        """Test register_service with forward tunnel."""
        # Create server with handler
        server = grpc.aio.server()
        handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

        # Create service implementation
        service = FullEchoService()

        # Register service - auto-detects service name and method signatures
        handler.register_service(service)

        add_TunnelServiceServicer_to_server(handler.service(), server)
        port = server.add_insecure_port("[::]:0")
        await server.start()

        try:
            # Connect through forward tunnel
            from grpctunnel import PendingChannel

            async with grpc.aio.insecure_channel(f"localhost:{port}") as channel:
                tunnel_stub = TunnelServiceStub(channel)
                pending = PendingChannel(tunnel_stub)
                tunnel_channel = await pending.start()

                try:
                    echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                    # Test unary call
                    request = echo_pb2.EchoRequest(message="forward")
                    response = await echo_stub.Echo(request)
                    assert response.message == "Echo: forward"

                    # TODO: Add streaming tests once streaming support is implemented

                finally:
                    await tunnel_channel.close_async()
        finally:
            await server.stop(grace=1.0)

    @pytest.mark.asyncio
    async def test_register_service_with_auto_inference(self, tunnel_server):
        """Test register_service with auto-inference from generated servicer."""
        server_address, handler = tunnel_server

        async with grpc.aio.insecure_channel(server_address) as channel:
            tunnel_stub = TunnelServiceStub(channel)
            reverse_server = ReverseTunnelServer(tunnel_stub)

            # Create a service that extends the generated servicer
            class EchoServiceImpl(echo_pb2_grpc.EchoServiceServicer):
                """Implementation that extends the generated servicer."""

                async def Echo(self, request: echo_pb2.EchoRequest, context: any):
                    return echo_pb2.EchoResponse(message=f"Auto: {request.message}")

                async def EchoError(self, request: echo_pb2.ErrorRequest, context: any):
                    return echo_pb2.EchoResponse(message=f"Error: {request.message}")

            service = EchoServiceImpl()

            # Register service - full auto-detection
            reverse_server.register_service(service)

            # Start reverse tunnel
            tunnel_task = asyncio.create_task(reverse_server.serve())
            await asyncio.sleep(0.5)

            # Get reverse channel
            reverse_channel = handler.as_channel()
            await reverse_channel.wait_for_ready(timeout=2.0)

            # Test with generated stub
            echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

            # Test unary call
            request = echo_pb2.EchoRequest(message="inferred")
            response = await echo_stub.Echo(request)
            assert response.message == "Auto: inferred"

            # Clean up
            await reverse_server.stop()
            try:
                await asyncio.wait_for(tunnel_task, timeout=2.0)
            except asyncio.TimeoutError:
                pass

    @pytest.mark.asyncio
    async def test_register_service_requires_servicer_base_class(self):
        """Test that register_service requires extending a *Servicer base class."""
        from grpctunnel.options import TunnelOptions

        # Create a service without extending a generated servicer
        class CustomService:
            async def Echo(self, request: echo_pb2.EchoRequest, context: any):
                return echo_pb2.EchoResponse(message="test")

        service = CustomService()

        # Create a reverse server (doesn't need real tunnel)
        from unittest.mock import MagicMock

        mock_stub = MagicMock()
        reverse_server = ReverseTunnelServer(mock_stub, TunnelOptions())

        # Try to register - should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            reverse_server.register_service(service)

        # Check error message is helpful
        assert "must extend a generated" in str(exc_info.value)
        assert "Servicer base class" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_service_same_name_as_base(self, tunnel_server):
        """Test register_service when user's class has same name as generated base class.

        This tests the fix for the bug where the library would look for the
        add_*Servicer_to_server function in the wrong module when the user's
        implementation class has the same name as the generated base class.
        """
        server_address, handler = tunnel_server

        async with grpc.aio.insecure_channel(server_address) as channel:
            tunnel_stub = TunnelServiceStub(channel)
            reverse_server = ReverseTunnelServer(tunnel_stub)

            # Create a servicer with the SAME NAME as the generated base class
            # This is the exact scenario that caused the bug
            class EchoServiceServicer(echo_pb2_grpc.EchoServiceServicer):
                """User's implementation with same name as generated base."""

                async def Echo(self, request: echo_pb2.EchoRequest, context: any):
                    return echo_pb2.EchoResponse(message=f"SameName: {request.message}")

            service = EchoServiceServicer()

            # This should work now - the library should find the generated base class
            # in the _pb2_grpc module, not the user's class
            reverse_server.register_service(service)

            # Start reverse tunnel
            tunnel_task = asyncio.create_task(reverse_server.serve())
            await asyncio.sleep(0.5)

            # Get reverse channel
            reverse_channel = handler.as_channel()
            await reverse_channel.wait_for_ready(timeout=2.0)

            # Test with generated stub
            echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

            # Test unary call
            request = echo_pb2.EchoRequest(message="test")
            response = await echo_stub.Echo(request)
            assert response.message == "SameName: test"

            # Clean up
            await reverse_server.stop()
            try:
                await asyncio.wait_for(tunnel_task, timeout=2.0)
            except asyncio.TimeoutError:
                pass

    @pytest.mark.asyncio
    async def test_register_service_with_sync_methods(self, tunnel_server):
        """Test register_service with synchronous (non-async) methods.

        This tests that synchronous methods work correctly, which is important
        because the generated base class methods are synchronous by default.
        Users who follow the base class signature will naturally write sync methods.
        """
        server_address, handler = tunnel_server

        async with grpc.aio.insecure_channel(server_address) as channel:
            tunnel_stub = TunnelServiceStub(channel)
            reverse_server = ReverseTunnelServer(tunnel_stub)

            # Create a servicer with SYNCHRONOUS methods (regular def, not async def)
            # This matches the generated base class signature
            class SyncEchoService(echo_pb2_grpc.EchoServiceServicer):
                """Implementation with sync methods."""

                def Echo(self, request: echo_pb2.EchoRequest, context: any):
                    """Synchronous echo method."""
                    return echo_pb2.EchoResponse(message=f"Sync: {request.message}")

            service = SyncEchoService()

            # Register the service - should handle sync methods correctly
            reverse_server.register_service(service)

            # Start reverse tunnel
            tunnel_task = asyncio.create_task(reverse_server.serve())
            await asyncio.sleep(0.5)

            # Get reverse channel
            reverse_channel = handler.as_channel()
            await reverse_channel.wait_for_ready(timeout=2.0)

            # Test with generated stub
            echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

            # Test unary call - sync method should work via thread pool
            request = echo_pb2.EchoRequest(message="test")
            response = await echo_stub.Echo(request)
            assert response.message == "Sync: test"

            # Clean up
            await reverse_server.stop()
            try:
                await asyncio.wait_for(tunnel_task, timeout=2.0)
            except asyncio.TimeoutError:
                pass

    @pytest.mark.asyncio
    async def test_register_service_mixed_sync_async(self, tunnel_server):
        """Test register_service with mix of sync and async methods.

        This verifies that a servicer can have both sync and async methods,
        and both work correctly.
        """
        server_address, handler = tunnel_server

        async with grpc.aio.insecure_channel(server_address) as channel:
            tunnel_stub = TunnelServiceStub(channel)
            reverse_server = ReverseTunnelServer(tunnel_stub)

            # Create a servicer with BOTH sync and async methods
            class MixedEchoService(echo_pb2_grpc.EchoServiceServicer):
                """Implementation with mixed sync/async methods."""

                def Echo(self, request: echo_pb2.EchoRequest, context: any):
                    """Synchronous method."""
                    return echo_pb2.EchoResponse(message=f"Sync: {request.message}")

                async def EchoError(self, request: echo_pb2.ErrorRequest, context: any):
                    """Asynchronous method."""
                    return echo_pb2.EchoResponse(message=f"Async: {request.message}")

            service = MixedEchoService()

            # Register the service
            reverse_server.register_service(service)

            # Start reverse tunnel
            tunnel_task = asyncio.create_task(reverse_server.serve())
            await asyncio.sleep(0.5)

            # Get reverse channel
            reverse_channel = handler.as_channel()
            await reverse_channel.wait_for_ready(timeout=2.0)

            # Test with generated stub
            echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

            # Test sync method
            request = echo_pb2.EchoRequest(message="sync-test")
            response = await echo_stub.Echo(request)
            assert response.message == "Sync: sync-test"

            # Test async method
            error_request = echo_pb2.ErrorRequest(message="async-test")
            response = await echo_stub.EchoError(error_request)
            assert response.message == "Async: async-test"

            # Clean up
            await reverse_server.stop()
            try:
                await asyncio.wait_for(tunnel_task, timeout=2.0)
            except asyncio.TimeoutError:
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])