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
Reverse Tunnel Client Example

This client demonstrates how to open a reverse tunnel to a server, allowing
the server to make RPC calls back to this client. This enables "server push"
patterns and allows servers to reach clients behind NAT/firewalls.

Run the server first, then run this:
    python client.py
"""

import asyncio
import logging
import sys
from pathlib import Path

import grpc

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from grpctunnel import ReverseTunnelServer
from grpctunnel.proto.v1 import TunnelServiceStub
from proto import echo_pb2, echo_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EchoService(echo_pb2_grpc.EchoServiceServicer):
    """Echo service implementation that runs on the client.

    This class extends the generated EchoServiceServicer base class, which allows
    grpctunnel to automatically detect the service name and method signatures.
    """

    async def Echo(
        self, request: echo_pb2.EchoRequest, context: any
    ) -> echo_pb2.EchoResponse:
        """Echo back the request message."""
        logger.info(f"Client received request: {request.message}")

        # Create and return response
        response = echo_pb2.EchoResponse(message=f"Echo: {request.message}")
        return response


async def main():
    """Run the reverse tunnel client."""
    server_address = "localhost:50051"
    logger.info(f"Connecting to server at {server_address}...")

    # Create a regular gRPC channel to the server
    async with grpc.aio.insecure_channel(server_address) as channel:
        # Create the tunnel service stub
        tunnel_stub = TunnelServiceStub(channel)

        # Create a reverse tunnel server (runs on the client side)
        reverse_server = ReverseTunnelServer(tunnel_stub)

        # Create and register our Echo service
        # The server will be able to call this service
        echo_service = EchoService()

        # Register the service - service name and method signatures are auto-detected
        # from the EchoServiceServicer base class
        reverse_server.register_service(echo_service)
        logger.info("Registered Echo service on client")

        # Open the reverse tunnel in a background task
        logger.info("Opening reverse tunnel to server...")

        async def run_tunnel():
            started, err = await reverse_server.serve()
            if err:
                logger.error(f"Tunnel error: {err}")
            return started

        tunnel_task = asyncio.create_task(run_tunnel())

        # Give the tunnel time to establish
        await asyncio.sleep(0.5)

        if tunnel_task.done() and not tunnel_task.result():
            logger.error("Failed to establish reverse tunnel")
            return

        logger.info("✓ Reverse tunnel established")
        logger.info("Server can now make RPC calls to this client")
        logger.info("Waiting for calls from server...")

        # Keep the client running to handle requests from server
        try:
            # Wait for the tunnel (it will run until we stop it)
            await asyncio.sleep(10.0)

            logger.info("\nClosing reverse tunnel...")
            await reverse_server.stop()

            # Wait for tunnel to complete
            try:
                await asyncio.wait_for(tunnel_task, timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("Tunnel did not close cleanly")

            logger.info("Client stopped")

        except KeyboardInterrupt:
            logger.info("\nInterrupted by user, closing tunnel...")
            await reverse_server.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nClient stopped by user")
    except grpc.aio.AioRpcError as e:
        logger.error(f"RPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
