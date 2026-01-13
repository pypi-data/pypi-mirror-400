# Copyright 2024 Daniel Valdivia
# Ported from the original Go implementation by Joshua Humphries
# Original: https://github.com/jhump/grpctunnel
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

"""Generated protocol buffer code for grpctunnel v1."""

from .tunnel_pb2 import (
    ClientToServer,
    ServerToClient,
    NewStream,
    MessageData,
    CloseStream,
    Metadata,
    Settings,
    ProtocolRevision,
    REVISION_ZERO,
    REVISION_ONE,
)
from .tunnel_pb2_grpc import (
    TunnelServiceStub,
    TunnelServiceServicer,
    add_TunnelServiceServicer_to_server,
)

__all__ = [
    # Messages
    "ClientToServer",
    "ServerToClient",
    "NewStream",
    "MessageData",
    "CloseStream",
    "Metadata",
    "Settings",
    # Enums
    "ProtocolRevision",
    "REVISION_ZERO",
    "REVISION_ONE",
    # gRPC service
    "TunnelServiceStub",
    "TunnelServiceServicer",
    "add_TunnelServiceServicer_to_server",
]
