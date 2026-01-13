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

"""Stress tests for grpctunnel with concurrent operations."""

import asyncio
import random
import time
from typing import List

import grpc
import pytest

from grpctunnel import (
    PendingChannel,
    ReverseTunnelServer,
    TunnelServiceHandler,
    TunnelServiceHandlerOptions,
)
from grpctunnel.proto.v1 import (
    TunnelServiceStub,
    add_TunnelServiceServicer_to_server,
)
from tests.integration import echo_pb2, echo_pb2_grpc


class EchoService(echo_pb2_grpc.EchoServiceServicer):
    """Echo service implementation for stress testing.

    This class extends the generated EchoServiceServicer base class, which allows
    grpctunnel to automatically detect the service name and method signatures.
    """

    async def Echo(
        self, request: echo_pb2.EchoRequest, context: any
    ) -> echo_pb2.EchoResponse:
        """Simple echo that may add a small random delay."""
        # Add small random delay to simulate real work
        await asyncio.sleep(random.uniform(0.001, 0.01))
        return echo_pb2.EchoResponse(message=f"Echo: {request.message}")


@pytest.fixture
async def tunnel_server_stress():
    """Create a gRPC server with tunnel support for stress testing."""
    server = grpc.aio.server()
    handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

    # Register echo service - auto-detects service name and method signatures
    service = EchoService()
    handler.register_service(service)

    add_TunnelServiceServicer_to_server(handler.service(), server)
    port = server.add_insecure_port("[::]:0")
    await server.start()

    yield f"localhost:{port}", handler

    await server.stop(grace=2.0)


class TestStressConcurrency:
    """Stress tests for concurrent tunnel operations."""

    @pytest.mark.asyncio
    async def test_sequential_reverse_tunnels(self, tunnel_server_stress):
        """Test sequential reverse tunnels (concurrent reverse tunnels not supported)."""
        server_address, handler = tunnel_server_stress

        num_tunnels = 5

        for tunnel_id in range(num_tunnels):
            async with grpc.aio.insecure_channel(server_address) as channel:
                tunnel_stub = TunnelServiceStub(channel)
                reverse_server = ReverseTunnelServer(tunnel_stub)

                # Register service - auto-detects service name and method signatures
                service = EchoService()
                reverse_server.register_service(service)

                # Start reverse tunnel
                tunnel_task = asyncio.create_task(reverse_server.serve())
                await asyncio.sleep(0.3)

                try:
                    # Get reverse channel
                    reverse_channel = handler.as_channel()
                    await reverse_channel.wait_for_ready(timeout=2.0)

                    # Make a request
                    echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)
                    request = echo_pb2.EchoRequest(message=f"tunnel-{tunnel_id}")
                    response = await echo_stub.Echo(request)
                    assert response.message == f"Echo: tunnel-{tunnel_id}"
                finally:
                    await reverse_server.stop()
                    try:
                        await asyncio.wait_for(tunnel_task, timeout=2.0)
                    except asyncio.TimeoutError:
                        pass

        print(f"✓ {num_tunnels} sequential reverse tunnels completed")

    @pytest.mark.skip(
        reason="Concurrent forward tunnels expose stream ID reuse issues - needs investigation"
    )
    @pytest.mark.asyncio
    async def test_concurrent_forward_tunnels(self, tunnel_server_stress):
        """Test multiple concurrent forward tunnels.

        Note: This test is currently skipped as it exposes stream ID management
        issues when multiple tunnels are created rapidly. The issue is that
        when a tunnel closes and a new one starts, the stream IDs are not
        properly cleaned up or reset, causing "stream ID already exists" errors.
        """
        server_address, _ = tunnel_server_stress
        num_tunnels = 5
        num_requests_per_tunnel = 10

        async def run_forward_tunnel(tunnel_id: int) -> int:
            """Run forward tunnel and make multiple requests."""
            async with grpc.aio.insecure_channel(server_address) as channel:
                tunnel_stub = TunnelServiceStub(channel)
                pending = PendingChannel(tunnel_stub)
                tunnel_channel = await pending.start()

                try:
                    echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                    # Make multiple concurrent requests through this tunnel
                    async def make_request(req_id: int) -> str:
                        request = echo_pb2.EchoRequest(
                            message=f"tunnel{tunnel_id}-req{req_id}"
                        )
                        response = await echo_stub.Echo(request)
                        return response.message

                    # Fire off concurrent requests
                    request_tasks = [
                        make_request(i) for i in range(num_requests_per_tunnel)
                    ]
                    responses = await asyncio.gather(*request_tasks)

                    # Verify all responses
                    for i, resp in enumerate(responses):
                        expected = f"Echo: tunnel{tunnel_id}-req{i}"
                        assert resp == expected

                    return len(responses)
                finally:
                    await tunnel_channel.close_async()

        # Run multiple forward tunnels concurrently
        start_time = time.time()
        tasks = [run_forward_tunnel(i) for i in range(num_tunnels)]
        results = await asyncio.gather(*tasks)
        elapsed = time.time() - start_time

        total_requests = sum(results)
        print(
            f"✓ {num_tunnels} concurrent forward tunnels with "
            f"{total_requests} total requests completed in {elapsed:.2f}s"
        )
        print(f"  Average: {total_requests/elapsed:.1f} req/s")

    @pytest.mark.asyncio
    async def test_concurrent_requests_single_tunnel(self, tunnel_server_stress):
        """Test many concurrent requests through a single forward tunnel."""
        server_address, _ = tunnel_server_stress
        num_requests = 100

        async with grpc.aio.insecure_channel(server_address) as channel:
            tunnel_stub = TunnelServiceStub(channel)
            pending = PendingChannel(tunnel_stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                async def make_request(req_id: int) -> str:
                    request = echo_pb2.EchoRequest(message=f"concurrent-{req_id}")
                    response = await echo_stub.Echo(request)
                    return response.message

                # Fire off all requests concurrently
                start_time = time.time()
                tasks = [make_request(i) for i in range(num_requests)]
                responses = await asyncio.gather(*tasks)
                elapsed = time.time() - start_time

                # Verify all responses
                for i, resp in enumerate(responses):
                    expected = f"Echo: concurrent-{i}"
                    assert resp == expected

                print(
                    f"✓ {num_requests} concurrent requests through single tunnel "
                    f"completed in {elapsed:.2f}s"
                )
                print(f"  Average: {num_requests/elapsed:.1f} req/s")
            finally:
                await tunnel_channel.close_async()

    @pytest.mark.asyncio
    async def test_concurrent_streaming(self, tunnel_server_stress):
        """Test concurrent streaming operations through forward tunnel."""
        server_address, _ = tunnel_server_stress
        num_streams = 20

        async with grpc.aio.insecure_channel(server_address) as channel:
            tunnel_stub = TunnelServiceStub(channel)
            pending = PendingChannel(tunnel_stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                async def run_stream(stream_id: int) -> List[str]:
                    """Run a server streaming call."""
                    request = echo_pb2.EchoRequest(message=f"stream{stream_id}")
                    stream = await echo_stub.EchoServerStream(request)
                    responses = []
                    async for response in stream:
                        responses.append(response.message)
                    return responses

                # Run multiple streams concurrently
                start_time = time.time()
                tasks = [run_stream(i) for i in range(num_streams)]
                results = await asyncio.gather(*tasks)
                elapsed = time.time() - start_time

                # Verify all streams completed correctly
                for i, responses in enumerate(results):
                    assert len(responses) == 5
                    for j, resp in enumerate(responses):
                        expected = f"stream{i}-{j}"
                        assert resp == expected

                print(
                    f"✓ {num_streams} concurrent streams completed in {elapsed:.2f}s"
                )
            finally:
                await tunnel_channel.close_async()

    @pytest.mark.skip(
        reason="Sequential reconnections expose stream ID reuse issues - needs investigation"
    )
    @pytest.mark.asyncio
    async def test_tunnel_reconnection(self, tunnel_server_stress):
        """Test sequential tunnel creation and teardown.

        Note: This test is currently skipped as it exposes stream ID management
        issues when tunnels are closed and reopened sequentially. Stream IDs
        are not being properly reset between tunnel instances.
        """
        server_address, _ = tunnel_server_stress
        num_iterations = 10

        for i in range(num_iterations):
            async with grpc.aio.insecure_channel(server_address) as channel:
                tunnel_stub = TunnelServiceStub(channel)
                pending = PendingChannel(tunnel_stub)
                tunnel_channel = await pending.start()

                try:
                    echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)
                    request = echo_pb2.EchoRequest(message=f"iteration-{i}")
                    response = await echo_stub.Echo(request)
                    assert response.message == f"Echo: iteration-{i}"
                finally:
                    await tunnel_channel.close_async()

            # Small delay between iterations
            await asyncio.sleep(0.2)

        print(f"✓ {num_iterations} sequential tunnel reconnections completed")

    @pytest.mark.asyncio
    async def test_mixed_operations(self, tunnel_server_stress):
        """Test mix of unary and streaming operations concurrently."""
        server_address, _ = tunnel_server_stress
        num_unary = 30
        num_streaming = 10

        async with grpc.aio.insecure_channel(server_address) as channel:
            tunnel_stub = TunnelServiceStub(channel)
            pending = PendingChannel(tunnel_stub)
            tunnel_channel = await pending.start()

            try:
                echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

                async def unary_call(call_id: int) -> str:
                    request = echo_pb2.EchoRequest(message=f"unary-{call_id}")
                    response = await echo_stub.Echo(request)
                    return response.message

                async def streaming_call(call_id: int) -> int:
                    request = echo_pb2.EchoRequest(message=f"stream-{call_id}")
                    stream = await echo_stub.EchoServerStream(request)
                    count = 0
                    async for _ in stream:
                        count += 1
                    return count

                # Mix unary and streaming calls
                start_time = time.time()
                tasks = []
                tasks.extend([unary_call(i) for i in range(num_unary)])
                tasks.extend([streaming_call(i) for i in range(num_streaming)])

                # Shuffle to mix operation types
                random.shuffle(tasks)

                results = await asyncio.gather(*tasks)
                elapsed = time.time() - start_time

                # Verify results (first num_unary should be strings, rest should be counts)
                # Note: after shuffle, we just check totals
                string_results = [r for r in results if isinstance(r, str)]
                int_results = [r for r in results if isinstance(r, int)]

                assert len(string_results) == num_unary
                assert len(int_results) == num_streaming
                assert all(count == 5 for count in int_results)

                print(
                    f"✓ {num_unary} unary + {num_streaming} streaming operations "
                    f"completed in {elapsed:.2f}s"
                )
            finally:
                await tunnel_channel.close_async()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
