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
Forward Tunnel Client Example

This client demonstrates how to create a forward tunnel to a server and make
RPC calls through that tunnel. All RPCs go through the same tunnel connection,
providing session affinity.

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

from grpctunnel import PendingChannel
from grpctunnel.proto.v1 import TunnelServiceStub
from proto import echo_pb2, echo_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Run the forward tunnel client."""
    server_address = "localhost:50051"
    logger.info(f"Connecting to server at {server_address}...")

    # Create a regular gRPC channel to the server
    async with grpc.aio.insecure_channel(server_address) as channel:
        # Create the tunnel service stub
        tunnel_stub = TunnelServiceStub(channel)

        # Create a pending channel (forward tunnel)
        # This establishes the tunnel connection
        pending = PendingChannel(tunnel_stub)
        logger.info("Creating forward tunnel...")

        # Start the tunnel and get a channel
        tunnel_channel = await pending.start()
        logger.info("✓ Forward tunnel established")

        try:
            # Create a stub for the Echo service
            # All calls through this stub go through the tunnel
            echo_stub = echo_pb2_grpc.EchoServiceStub(tunnel_channel)

            # Make some RPC calls through the tunnel
            logger.info("\n--- Making RPC calls through tunnel ---")

            for i in range(3):
                message = f"Hello from client #{i+1}"
                logger.info(f"Sending: {message}")

                request = echo_pb2.EchoRequest(message=message)
                response = await echo_stub.Echo(request)

                logger.info(f"Received: {response.message}")

            # Make multiple concurrent calls
            logger.info("\n--- Making concurrent calls through tunnel ---")

            async def make_call(msg: str) -> str:
                request = echo_pb2.EchoRequest(message=msg)
                response = await echo_stub.Echo(request)
                return response.message

            tasks = [make_call(f"concurrent-{i}") for i in range(5)]
            results = await asyncio.gather(*tasks)

            logger.info(f"Sent 5 concurrent requests")
            for result in results:
                logger.info(f"  - {result}")

            logger.info("\n✓ All calls completed successfully!")

        finally:
            # Clean up: close the tunnel
            logger.info("Closing tunnel...")
            await tunnel_channel.close_async()
            logger.info("Tunnel closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
    except grpc.aio.AioRpcError as e:
        logger.error(f"RPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
