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
Forward Tunnel Server Example

This server demonstrates how to set up a gRPC server that supports forward tunnels.
Clients can connect and create tunnels through which they make RPC calls to services
hosted on this server.

Run this before running the client:
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
from proto import echo_pb2

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EchoService:
    """Simple Echo service implementation."""

    async def Echo(
        self, request_bytes: bytes, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message."""
        # Deserialize the request
        request = echo_pb2.EchoRequest.FromString(request_bytes)
        logger.info(f"Received Echo request: {request.message}")

        # Create and return response
        response = echo_pb2.EchoResponse(message=f"Echo: {request.message}")
        return response


async def main():
    """Run the forward tunnel server."""
    logger.info("Starting Forward Tunnel Server...")

    # Create a gRPC server
    server = grpc.aio.server()

    # Create the tunnel service handler
    # This handles tunnel creation and forwards RPCs to registered services
    handler = TunnelServiceHandler(TunnelServiceHandlerOptions())

    # Create and register our Echo service
    echo_service = EchoService()
    handler.register_service(
        echo_service,
        "test.EchoService",
        {
            "Echo": {"is_client_stream": False, "is_server_stream": False},
        },
    )
    logger.info("Registered Echo service")

    # Register the tunnel service with the gRPC server
    # This allows clients to open tunnels
    add_TunnelServiceServicer_to_server(handler.service(), server)

    # Start server on port 50051
    port = 50051
    server.add_insecure_port(f"[::]:{port}")
    await server.start()

    logger.info(f"✓ Server listening on port {port}")
    logger.info("Waiting for clients to connect...")
    logger.info("Press Ctrl+C to stop")

    try:
        # Keep server running
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("\nShutting down...")
        await server.stop(grace=2.0)
        logger.info("Server stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
