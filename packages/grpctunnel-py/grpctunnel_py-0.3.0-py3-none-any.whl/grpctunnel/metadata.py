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

"""Metadata conversion utilities for the gRPC tunnel.

This module provides functions to convert between gRPC metadata
(grpc.aio.Metadata) and protobuf Metadata messages.
"""

from collections import defaultdict
from typing import Sequence

import grpc

from grpctunnel.proto.v1 import Metadata


def to_proto(md: grpc.aio.Metadata | None) -> Metadata:
    """Convert gRPC metadata to protobuf Metadata message.

    Args:
        md: gRPC metadata as a sequence of (key, value) tuples, or None

    Returns:
        Protobuf Metadata message with all key-value pairs
    """
    if md is None:
        return Metadata()

    # Group values by key since gRPC metadata can have multiple values per key
    values_by_key: dict[str, list[str]] = defaultdict(list)
    for key, value in md:
        # gRPC metadata values can be str or bytes
        if isinstance(value, bytes):
            # Binary metadata keys end with -bin
            # For now, we'll decode as latin-1 (preserves byte values)
            value_str = value.decode("latin-1")
        else:
            value_str = value
        values_by_key[key].append(value_str)

    # Convert to protobuf format
    proto_md = Metadata()
    for key, vals in values_by_key.items():
        proto_md.md[key].val.extend(vals)

    return proto_md


def from_proto(md: Metadata | None) -> grpc.aio.Metadata:
    """Convert protobuf Metadata message to gRPC metadata.

    Args:
        md: Protobuf Metadata message, or None

    Returns:
        gRPC metadata as a tuple of (key, value) tuples
    """
    if md is None or not md.md:
        return grpc.aio.Metadata()

    # Convert from protobuf format to list of tuples
    items: list[tuple[str, str | bytes]] = []
    for key, values in md.md.items():
        for val in values.val:
            # Check if this is binary metadata (keys ending with -bin)
            if key.endswith("-bin"):
                # Encode back to bytes using latin-1
                items.append((key, val.encode("latin-1")))
            else:
                items.append((key, val))

    return grpc.aio.Metadata(*items)
