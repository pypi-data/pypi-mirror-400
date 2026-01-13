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

"""Tests for metadata conversion utilities."""

import grpc

from grpctunnel.metadata import from_proto, to_proto
from grpctunnel.proto.v1 import Metadata


class TestMetadataConversion:
    """Tests for metadata conversion between gRPC and protobuf formats."""

    def test_to_proto_empty(self) -> None:
        """Test converting empty metadata to protobuf."""
        md = grpc.aio.Metadata()
        proto = to_proto(md)
        assert isinstance(proto, Metadata)
        assert len(proto.md) == 0

    def test_to_proto_none(self) -> None:
        """Test converting None metadata to protobuf."""
        proto = to_proto(None)
        assert isinstance(proto, Metadata)
        assert len(proto.md) == 0

    def test_to_proto_single_value(self) -> None:
        """Test converting metadata with single values."""
        md = grpc.aio.Metadata(
            ("key1", "value1"),
            ("key2", "value2"),
        )
        proto = to_proto(md)
        assert len(proto.md) == 2
        assert list(proto.md["key1"].val) == ["value1"]
        assert list(proto.md["key2"].val) == ["value2"]

    def test_to_proto_multiple_values(self) -> None:
        """Test converting metadata with multiple values for same key."""
        md = grpc.aio.Metadata(
            ("key1", "value1"),
            ("key1", "value2"),
            ("key1", "value3"),
        )
        proto = to_proto(md)
        assert len(proto.md) == 1
        values = list(proto.md["key1"].val)
        assert len(values) == 3
        assert "value1" in values
        assert "value2" in values
        assert "value3" in values

    def test_to_proto_binary_metadata(self) -> None:
        """Test converting binary metadata."""
        binary_data = b"\x00\x01\x02\xff"
        md = grpc.aio.Metadata(
            ("key-bin", binary_data),
        )
        proto = to_proto(md)
        assert len(proto.md) == 1
        # Binary data should be encoded as latin-1
        stored_value = proto.md["key-bin"].val[0]
        assert stored_value.encode("latin-1") == binary_data

    def test_from_proto_empty(self) -> None:
        """Test converting empty protobuf metadata to gRPC."""
        proto = Metadata()
        md = from_proto(proto)
        assert isinstance(md, grpc.aio.Metadata)
        assert len(md) == 0

    def test_from_proto_none(self) -> None:
        """Test converting None protobuf metadata to gRPC."""
        md = from_proto(None)
        assert isinstance(md, grpc.aio.Metadata)
        assert len(md) == 0

    def test_from_proto_single_value(self) -> None:
        """Test converting protobuf metadata with single values."""
        proto = Metadata()
        proto.md["key1"].val.append("value1")
        proto.md["key2"].val.append("value2")

        md = from_proto(proto)
        # Convert to dict manually
        md_dict = {k: v for k, v in md}
        assert md_dict["key1"] == "value1"
        assert md_dict["key2"] == "value2"

    def test_from_proto_multiple_values(self) -> None:
        """Test converting protobuf metadata with multiple values."""
        proto = Metadata()
        proto.md["key1"].val.extend(["value1", "value2", "value3"])

        md = from_proto(proto)
        # Should have 3 tuples with same key
        values = [v for k, v in md if k == "key1"]
        assert len(values) == 3
        assert "value1" in values
        assert "value2" in values
        assert "value3" in values

    def test_from_proto_binary_metadata(self) -> None:
        """Test converting protobuf with binary metadata."""
        binary_data = b"\x00\x01\x02\xff"
        proto = Metadata()
        # Store binary data as latin-1 encoded string
        proto.md["key-bin"].val.append(binary_data.decode("latin-1"))

        md = from_proto(proto)
        # Convert to dict manually
        md_dict = {k: v for k, v in md}
        assert "key-bin" in md_dict
        # Should be decoded back to bytes
        assert md_dict["key-bin"] == binary_data

    def test_round_trip_conversion(self) -> None:
        """Test round-trip conversion maintains data integrity."""
        original = grpc.aio.Metadata(
            ("key1", "value1"),
            ("key2", "value2a"),
            ("key2", "value2b"),
            ("key3", "value3"),
        )

        # Convert to proto and back
        proto = to_proto(original)
        result = from_proto(proto)

        # Convert both to sorted lists for comparison
        original_sorted = sorted(original)
        result_sorted = sorted(result)

        assert len(original_sorted) == len(result_sorted)
        for orig_item, result_item in zip(original_sorted, result_sorted):
            assert orig_item == result_item

    def test_round_trip_binary_metadata(self) -> None:
        """Test round-trip conversion with binary metadata."""
        binary_data = b"\x00\x01\x02\xff\xfe\xfd"
        original = grpc.aio.Metadata(
            ("normal-key", "normal-value"),
            ("binary-key-bin", binary_data),
        )

        # Convert to proto and back
        proto = to_proto(original)
        result = from_proto(proto)

        # Check both keys are present
        result_dict = {k: v for k, v in result}
        assert "normal-key" in result_dict
        assert "binary-key-bin" in result_dict

        # Check values are correct
        assert result_dict["normal-key"] == "normal-value"
        assert result_dict["binary-key-bin"] == binary_data
