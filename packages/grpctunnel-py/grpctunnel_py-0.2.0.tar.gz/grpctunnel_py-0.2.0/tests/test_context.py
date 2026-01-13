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

"""Tests for context utility functions."""

import grpc
import pytest

from grpctunnel.context import (
    set_tunnel_channel_in_context,
    set_tunnel_metadata_in_context,
    tunnel_channel_from_context,
    tunnel_metadata_from_incoming_context,
    tunnel_metadata_from_outgoing_context,
    with_tunnel_channel,
)


class MockServicerContext:
    """Mock gRPC servicer context for testing."""

    def __init__(self):
        """Initialize mock context."""
        pass


class MockTunnelChannel:
    """Mock tunnel channel for testing."""

    def __init__(self, channel_id: str):
        """Initialize mock channel."""
        self.channel_id = channel_id

    def __str__(self):
        """String representation."""
        return f"MockTunnelChannel({self.channel_id})"


class TestContextUtilities:
    """Tests for context utility functions."""

    def test_tunnel_channel_from_context_none(self):
        """Test getting tunnel channel from context when none exists."""
        context = MockServicerContext()
        channel = tunnel_channel_from_context(context)
        assert channel is None

    def test_tunnel_channel_from_context_with_channel(self):
        """Test getting tunnel channel from context when it exists."""
        context = MockServicerContext()
        mock_channel = MockTunnelChannel("test-channel-1")

        # Set the channel in context
        set_tunnel_channel_in_context(context, mock_channel)

        # Retrieve it
        channel = tunnel_channel_from_context(context)
        assert channel is mock_channel
        assert channel.channel_id == "test-channel-1"

    def test_with_tunnel_channel(self):
        """Test creating context values with tunnel channel."""
        mock_channel = MockTunnelChannel("test-channel-2")
        context_values = with_tunnel_channel(mock_channel)

        assert isinstance(context_values, dict)
        assert "grpctunnel.tunnel_channel" in context_values
        assert context_values["grpctunnel.tunnel_channel"] is mock_channel

    def test_tunnel_metadata_from_incoming_context_none(self):
        """Test getting tunnel metadata from context when none exists."""
        context = MockServicerContext()
        metadata = tunnel_metadata_from_incoming_context(context)
        assert metadata is None

    def test_tunnel_metadata_from_incoming_context_with_metadata(self):
        """Test getting tunnel metadata from context when it exists."""
        context = MockServicerContext()
        test_metadata = grpc.aio.Metadata(
            ("key1", "value1"),
            ("key2", "value2"),
        )

        # Set the metadata in context
        set_tunnel_metadata_in_context(context, test_metadata)

        # Retrieve it
        metadata = tunnel_metadata_from_incoming_context(context)
        assert metadata is not None
        assert isinstance(metadata, grpc.aio.Metadata)

        # Convert to dict for comparison
        metadata_dict = {k: v for k, v in metadata}
        assert metadata_dict["key1"] == "value1"
        assert metadata_dict["key2"] == "value2"

    def test_tunnel_metadata_from_incoming_context_with_list(self):
        """Test getting tunnel metadata when stored as list."""
        context = MockServicerContext()
        # Simulate internal storage as list
        setattr(context, '_tunnel_metadata', [("key3", "value3"), ("key4", "value4")])

        metadata = tunnel_metadata_from_incoming_context(context)
        assert metadata is not None
        assert isinstance(metadata, grpc.aio.Metadata)

        # Convert to dict for comparison
        metadata_dict = {k: v for k, v in metadata}
        assert metadata_dict["key3"] == "value3"
        assert metadata_dict["key4"] == "value4"

    def test_tunnel_metadata_from_outgoing_context_none(self):
        """Test getting tunnel metadata from outgoing context when none."""
        metadata = tunnel_metadata_from_outgoing_context(None)
        assert metadata is None

    def test_tunnel_metadata_from_outgoing_context_no_tunnel_metadata(self):
        """Test getting tunnel metadata when no tunnel-specific keys."""
        metadata = grpc.aio.Metadata(
            ("key1", "value1"),
            ("key2", "value2"),
        )
        tunnel_metadata = tunnel_metadata_from_outgoing_context(metadata)
        assert tunnel_metadata is None

    def test_tunnel_metadata_from_outgoing_context_with_tunnel_metadata(self):
        """Test getting tunnel metadata with tunnel-specific keys."""
        metadata = grpc.aio.Metadata(
            ("key1", "value1"),
            ("grpctunnel-negotiate", "on"),
            ("key2", "value2"),
            ("grpctunnel-custom", "value"),
        )
        tunnel_metadata = tunnel_metadata_from_outgoing_context(metadata)
        assert tunnel_metadata is not None

        # Convert to list and dict for verification
        tunnel_list = list(tunnel_metadata)
        assert len(tunnel_list) == 2

        tunnel_dict = {k: v for k, v in tunnel_metadata}
        assert "grpctunnel-negotiate" in tunnel_dict
        assert tunnel_dict["grpctunnel-negotiate"] == "on"
        assert "grpctunnel-custom" in tunnel_dict
        assert tunnel_dict["grpctunnel-custom"] == "value"
        # Non-tunnel keys should not be included
        assert "key1" not in tunnel_dict
        assert "key2" not in tunnel_dict

    def test_set_tunnel_channel_in_context(self):
        """Test setting tunnel channel in context."""
        context = MockServicerContext()
        mock_channel = MockTunnelChannel("test-channel-3")

        # Initially should not have channel
        assert not hasattr(context, '_tunnel_channel')

        # Set the channel
        set_tunnel_channel_in_context(context, mock_channel)

        # Should now have the channel
        assert hasattr(context, '_tunnel_channel')
        assert context._tunnel_channel is mock_channel

    def test_set_tunnel_metadata_in_context(self):
        """Test setting tunnel metadata in context."""
        context = MockServicerContext()
        test_metadata = grpc.aio.Metadata(
            ("meta1", "value1"),
            ("meta2", "value2"),
        )

        # Initially should not have metadata
        assert not hasattr(context, '_tunnel_metadata')

        # Set the metadata
        set_tunnel_metadata_in_context(context, test_metadata)

        # Should now have the metadata as list
        assert hasattr(context, '_tunnel_metadata')
        assert context._tunnel_metadata == [("meta1", "value1"), ("meta2", "value2")]

    def test_set_tunnel_metadata_in_context_none(self):
        """Test setting None metadata in context."""
        context = MockServicerContext()

        # Set None metadata
        set_tunnel_metadata_in_context(context, None)

        # Should not create the attribute
        assert not hasattr(context, '_tunnel_metadata')

    def test_context_utilities_round_trip(self):
        """Test round-trip usage of context utilities."""
        # Create a context and channel
        context = MockServicerContext()
        mock_channel = MockTunnelChannel("round-trip-channel")
        test_metadata = grpc.aio.Metadata(
            ("grpctunnel-test", "true"),
            ("custom-header", "value"),
        )

        # Set both channel and metadata
        set_tunnel_channel_in_context(context, mock_channel)
        set_tunnel_metadata_in_context(context, test_metadata)

        # Retrieve and verify
        retrieved_channel = tunnel_channel_from_context(context)
        retrieved_metadata = tunnel_metadata_from_incoming_context(context)

        assert retrieved_channel is mock_channel
        assert retrieved_channel.channel_id == "round-trip-channel"

        assert retrieved_metadata is not None
        # Convert to dict for comparison
        metadata_dict = {k: v for k, v in retrieved_metadata}
        assert metadata_dict["grpctunnel-test"] == "true"
        assert metadata_dict["custom-header"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])