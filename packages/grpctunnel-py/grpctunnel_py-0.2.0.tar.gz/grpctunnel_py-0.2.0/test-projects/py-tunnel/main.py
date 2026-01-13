#!/usr/bin/env python3
"""
Python Edge Worker

This edge worker demonstrates:
1. Connecting to a Go control plane
2. Calling control plane RPCs (reportEdgeAlive, reportEdgeGoingAway)
3. Opening a reverse tunnel to allow the control plane to call back
4. Implementing EdgeService that the control plane can call

Run the Go control plane first, then run this edge worker:
    python main.py
"""

import asyncio
import logging
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
import uuid

import grpc

# Add parent directory to path to import grpctunnel
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from grpctunnel import ReverseTunnelServer
from grpctunnel.proto.v1 import TunnelServiceStub

# Import generated protobuf code
from pb import control_plane_pb2, control_plane_pb2_grpc
from pb import edge_pb2, edge_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EdgeServiceImpl(edge_pb2_grpc.EdgeServiceServicer):
    """Implementation of EdgeService that runs on the edge worker.

    This class extends the generated EdgeServiceServicer base class, which allows
    grpctunnel to automatically detect the service name and method signatures.
    """

    def __init__(self, edge_id: str):
        self.edge_id = edge_id
        self.hostname = socket.gethostname()

    async def GetId(
        self, request: edge_pb2.GetIdRequest, context: Any
    ) -> edge_pb2.GetIdResponse:
        """Return the edge worker's unique ID."""
        logger.info("✓ EdgeService.GetId() called by control plane")

        # Create and return response
        response = edge_pb2.GetIdResponse(
            id=self.edge_id,
            hostname=self.hostname
        )
        logger.info(f"  Responding with: id={self.edge_id}, hostname={self.hostname}")
        return response

    async def GetWhatTimeItIs(
        self, request: edge_pb2.GetTimeRequest, context: Any
    ) -> edge_pb2.GetTimeResponse:
        """Return the current time on the edge worker."""
        logger.info("✓ EdgeService.GetWhatTimeItIs() called by control plane")

        # Get current time
        now = datetime.now()
        timestamp = int(now.timestamp())
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")
        timezone = time.tzname[time.daylight]

        # Create and return response
        response = edge_pb2.GetTimeResponse(
            timestamp=timestamp,
            formatted=formatted,
            timezone=timezone
        )
        logger.info(f"  Responding with: {formatted} ({timezone})")
        return response


async def main():
    """Run the edge worker."""
    # Generate a unique edge ID
    edge_id = f"edge-{uuid.uuid4().hex[:8]}"
    logger.info(f"🚀 Starting Edge Worker with ID: {edge_id}")

    control_plane_address = "localhost:50051"
    logger.info(f"Connecting to control plane at {control_plane_address}...")

    # Create a regular gRPC channel to the control plane
    async with grpc.aio.insecure_channel(control_plane_address) as channel:
        # Create stubs for control plane services
        control_plane_stub = control_plane_pb2_grpc.ControlPlaneServiceStub(channel)
        tunnel_stub = TunnelServiceStub(channel)

        # Step 1: Report edge alive to control plane
        logger.info("\n→ Reporting edge alive to control plane...")
        try:
            alive_request = control_plane_pb2.EdgeAliveRequest(
                edge_id=edge_id,
                timestamp=int(time.time()),
                metadata={
                    "hostname": socket.gethostname(),
                    "version": "1.0.0"
                }
            )
            alive_response = await control_plane_stub.ReportEdgeAlive(alive_request)

            if alive_response.acknowledged:
                logger.info(f"✓ Edge alive acknowledged: {alive_response.message}")
            else:
                logger.warning("⚠ Edge alive not acknowledged")

        except grpc.aio.AioRpcError as e:
            logger.error(f"❌ Failed to report edge alive: {e.code()} - {e.details()}")
            # Continue anyway to establish reverse tunnel
        except Exception as e:
            logger.error(f"❌ Error reporting edge alive: {e}")
            # Continue anyway to establish reverse tunnel

        # Step 2: Create a reverse tunnel server
        logger.info("\n→ Setting up reverse tunnel...")
        reverse_server = ReverseTunnelServer(tunnel_stub)

        # Step 3: Create and register our EdgeService
        edge_service = EdgeServiceImpl(edge_id)

        # Register the service - service name and method signatures are auto-detected
        # from the EdgeServiceServicer base class
        reverse_server.register_service(edge_service)
        logger.info("✓ Registered EdgeService on reverse tunnel")

        # Step 4: Open the reverse tunnel in a background task
        logger.info("\n→ Opening reverse tunnel to control plane...")

        async def run_tunnel():
            started, err = await reverse_server.serve()
            if err:
                logger.error(f"❌ Tunnel error: {err}")
            return started

        tunnel_task = asyncio.create_task(run_tunnel())

        # Give the tunnel time to establish
        await asyncio.sleep(1.0)

        if tunnel_task.done():
            result = tunnel_task.result()
            if not result:
                logger.error("❌ Failed to establish reverse tunnel")
                return
            logger.info("✓ Reverse tunnel established successfully")
        else:
            logger.info("✓ Reverse tunnel is establishing...")

        logger.info("\n" + "=" * 60)
        logger.info("Edge worker is ready!")
        logger.info("Control plane can now make RPC calls to this edge worker")
        logger.info("=" * 60)
        logger.info("\nWaiting for calls from control plane...")
        logger.info("Press Ctrl+C to stop\n")

        # Keep the edge worker running to handle requests from control plane
        try:
            # Wait for the tunnel (it will run until we stop it)
            await asyncio.sleep(60.0)

            # Graceful shutdown: report going away
            logger.info("\n→ Reporting edge going away to control plane...")
            try:
                going_away_request = control_plane_pb2.EdgeGoingAwayRequest(
                    edge_id=edge_id,
                    reason="Normal shutdown"
                )
                going_away_response = await control_plane_stub.ReportEdgeGoingAway(
                    going_away_request
                )

                if going_away_response.acknowledged:
                    logger.info(f"✓ Edge going away acknowledged: {going_away_response.message}")
                else:
                    logger.warning("⚠ Edge going away not acknowledged")

            except grpc.aio.AioRpcError as e:
                logger.error(f"❌ Failed to report edge going away: {e.code()} - {e.details()}")
            except Exception as e:
                logger.error(f"❌ Error reporting edge going away: {e}")

            logger.info("\n→ Closing reverse tunnel...")
            await reverse_server.stop()

            # Wait for tunnel to complete
            try:
                await asyncio.wait_for(tunnel_task, timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("⚠ Tunnel did not close cleanly")

            logger.info("✓ Edge worker stopped")

        except KeyboardInterrupt:
            logger.info("\n✓ Interrupted by user")

            # Report going away
            try:
                going_away_request = control_plane_pb2.EdgeGoingAwayRequest(
                    edge_id=edge_id,
                    reason="Interrupted by user"
                )
                going_away_response = await control_plane_stub.ReportEdgeGoingAway(
                    going_away_request
                )
                logger.info(f"✓ Edge going away acknowledged: {going_away_response.message}")
            except Exception:
                pass  # Best effort

            logger.info("→ Closing tunnel...")
            await reverse_server.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n✓ Edge worker stopped by user")
    except grpc.aio.AioRpcError as e:
        logger.error(f"❌ RPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
