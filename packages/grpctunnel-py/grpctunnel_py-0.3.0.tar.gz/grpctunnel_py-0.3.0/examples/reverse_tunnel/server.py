#!/usr/bin/env python3
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
Reverse Tunnel Server Example

This server demonstrates how to accept reverse tunnels from clients and then
make RPC calls back to those clients. This enables "server push" patterns and
allows servers to call clients behind NAT/firewalls.

Run this first, then run the client:
    python server.py
"""

import asyncio
import logging
import sys
from pathlib import Path

import grpc

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from grpctunnel import TunnelServiceHandler, TunnelServiceHandlerOptions
from grpctunnel.proto.v1 import add_TunnelServiceServicer_to_server
from proto import echo_pb2, echo_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Run the reverse tunnel server."""
    logger.info("Starting Reverse Tunnel Server...")

    # Create a gRPC server
    server = grpc.aio.server()

    # Create the tunnel service handler that supports reverse tunnels
    handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

    # Register the tunnel service with the gRPC server
    # This allows clients to open reverse tunnels
    add_TunnelServiceServicer_to_server(handler.service(), server)

    # Start server on port 50051
    port = 50051
    server.add_insecure_port(f"[::]:{port}")
    await server.start()

    logger.info(f"✓ Server listening on port {port}")
    logger.info("Waiting for client to connect with reverse tunnel...")
    logger.info("(Start the client now if you haven't already)")

    # Wait for a reverse tunnel to be established
    await asyncio.sleep(3.0)

    # Get the reverse channel
    reverse_channel = handler.as_channel()

    if reverse_channel is None or not reverse_channel.ready():
        logger.warning("No reverse tunnel established yet")
        logger.info("Make sure the client is running!")
        await server.stop(grace=1.0)
        return

    logger.info("✓ Reverse tunnel established")

    # Now we can make RPC calls TO the client!
    logger.info("\n--- Making RPC calls to client ---")

    # Create a stub for the Echo service running on the client
    echo_stub = echo_pb2_grpc.EchoServiceStub(reverse_channel)

    try:
        # Make some RPC calls to the client
        for i in range(3):
            message = f"Hello from server #{i+1}"
            logger.info(f"Sending to client: {message}")

            request = echo_pb2.EchoRequest(message=message)
            response = await echo_stub.Echo(request)

            logger.info(f"Client responded: {response.message}")
            await asyncio.sleep(0.5)

        # Make concurrent calls to the client
        logger.info("\n--- Making concurrent calls to client ---")

        async def call_client(msg: str) -> str:
            request = echo_pb2.EchoRequest(message=msg)
            response = await echo_stub.Echo(request)
            return response.message

        tasks = [call_client(f"concurrent-{i}") for i in range(5)]
        results = await asyncio.gather(*tasks)

        logger.info("Sent 5 concurrent requests to client")
        for result in results:
            logger.info(f"  - {result}")

        logger.info("\n✓ All calls to client completed successfully!")

    except grpc.aio.AioRpcError as e:
        logger.error(f"RPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        # Keep server running for a bit longer
        logger.info("\nKeeping server running... Press Ctrl+C to stop")
        try:
            await asyncio.sleep(5.0)
        except KeyboardInterrupt:
            pass

        logger.info("Shutting down...")
        await server.stop(grace=2.0)
        logger.info("Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
