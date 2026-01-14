"""Tests for pywincode serialization/deserialization functions.

This module tests the core serialization functionality provided by the
wincode Rust library through Python bindings.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass


class TestSerialize:
    """Tests for the serialize function."""

    def test_serialize_bytes(self) -> None:
        """Test serializing bytes returns valid bytes."""
        import pywincode

        data = b"hello world"
        result = pywincode.serialize(data)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_serialize_empty_bytes(self) -> None:
        """Test serializing empty bytes."""
        import pywincode

        data = b""
        result = pywincode.serialize(data)

        assert isinstance(result, bytes)

    def test_serialize_large_bytes(self) -> None:
        """Test serializing large byte sequences."""
        import pywincode

        data = b"x" * 10000
        result = pywincode.serialize(data)

        assert isinstance(result, bytes)
        assert len(result) >= len(data)

    def test_serialize_binary_data(self) -> None:
        """Test serializing binary data with null bytes."""
        import pywincode

        data = b"\x00\x01\x02\xff\xfe\xfd"
        result = pywincode.serialize(data)

        assert isinstance(result, bytes)


class TestDeserialize:
    """Tests for the deserialize function."""

    def test_deserialize_roundtrip(self) -> None:
        """Test that serialize/deserialize is a roundtrip."""
        import pywincode

        original = b"hello world"
        serialized = pywincode.serialize(original)
        deserialized = pywincode.deserialize(serialized)

        assert deserialized == original

    def test_deserialize_empty_roundtrip(self) -> None:
        """Test roundtrip with empty bytes."""
        import pywincode

        original = b""
        serialized = pywincode.serialize(original)
        deserialized = pywincode.deserialize(serialized)

        assert deserialized == original

    def test_deserialize_binary_roundtrip(self) -> None:
        """Test roundtrip with binary data."""
        import pywincode

        original = bytes(range(256))
        serialized = pywincode.serialize(original)
        deserialized = pywincode.deserialize(serialized)

        assert deserialized == original

    def test_deserialize_invalid_data(self) -> None:
        """Test deserializing invalid data raises error."""
        import pywincode

        with pytest.raises(pywincode.WincodeError):
            pywincode.deserialize(b"\xff\xff\xff\xff\xff\xff\xff\xff")


class TestSerializedSize:
    """Tests for the serialized_size function."""

    def test_serialized_size_matches_serialize(self) -> None:
        """Test that serialized_size matches actual serialize output."""
        import pywincode

        data = b"test data"
        size = pywincode.serialized_size(data)
        serialized = pywincode.serialize(data)

        assert size == len(serialized)

    def test_serialized_size_empty(self) -> None:
        """Test serialized_size with empty data."""
        import pywincode

        size = pywincode.serialized_size(b"")

        assert isinstance(size, int)
        assert size >= 0

    def test_serialized_size_various_lengths(self) -> None:
        """Test serialized_size with various data lengths."""
        import pywincode

        for length in [1, 10, 100, 1000]:
            data = b"x" * length
            size = pywincode.serialized_size(data)
            serialized = pywincode.serialize(data)
            assert size == len(serialized)


class TestSerializeInto:
    """Tests for the serialize_into function."""

    def test_serialize_into_buffer(self) -> None:
        """Test serializing into a pre-allocated buffer."""
        import pywincode

        data = b"hello"
        size = pywincode.serialized_size(data)
        buffer = bytearray(size)
        bytes_written = pywincode.serialize_into(data, buffer)

        assert bytes_written == size
        assert bytes(buffer) == pywincode.serialize(data)

    def test_serialize_into_larger_buffer(self) -> None:
        """Test serializing into a larger buffer."""
        import pywincode

        data = b"hello"
        size = pywincode.serialized_size(data)
        buffer = bytearray(size + 100)
        bytes_written = pywincode.serialize_into(data, buffer)

        assert bytes_written == size

    def test_serialize_into_small_buffer_raises(self) -> None:
        """Test that too-small buffer raises error."""
        import pywincode

        data = b"hello world this is a longer string"
        buffer = bytearray(1)

        with pytest.raises(pywincode.WincodeError):
            pywincode.serialize_into(data, buffer)


class TestIntegerSerialization:
    """Tests for integer serialization."""

    def test_serialize_u8(self) -> None:
        """Test serializing u8 values."""
        import pywincode

        for value in [0, 1, 127, 255]:
            result = pywincode.serialize_u8(value)
            assert isinstance(result, bytes)

    def test_serialize_u16(self) -> None:
        """Test serializing u16 values."""
        import pywincode

        for value in [0, 1, 256, 65535]:
            result = pywincode.serialize_u16(value)
            assert isinstance(result, bytes)

    def test_serialize_u32(self) -> None:
        """Test serializing u32 values."""
        import pywincode

        for value in [0, 1, 65536, 4294967295]:
            result = pywincode.serialize_u32(value)
            assert isinstance(result, bytes)

    def test_serialize_u64(self) -> None:
        """Test serializing u64 values."""
        import pywincode

        for value in [0, 1, 4294967296, 18446744073709551615]:
            result = pywincode.serialize_u64(value)
            assert isinstance(result, bytes)

    def test_deserialize_u8(self) -> None:
        """Test deserializing u8 values."""
        import pywincode

        for expected in [0, 1, 127, 255]:
            serialized = pywincode.serialize_u8(expected)
            result = pywincode.deserialize_u8(serialized)
            assert result == expected

    def test_deserialize_u16(self) -> None:
        """Test deserializing u16 values."""
        import pywincode

        for expected in [0, 1, 256, 65535]:
            serialized = pywincode.serialize_u16(expected)
            result = pywincode.deserialize_u16(serialized)
            assert result == expected

    def test_deserialize_u32(self) -> None:
        """Test deserializing u32 values."""
        import pywincode

        for expected in [0, 1, 65536, 4294967295]:
            serialized = pywincode.serialize_u32(expected)
            result = pywincode.deserialize_u32(serialized)
            assert result == expected

    def test_deserialize_u64(self) -> None:
        """Test deserializing u64 values."""
        import pywincode

        for expected in [0, 1, 4294967296, 18446744073709551615]:
            serialized = pywincode.serialize_u64(expected)
            result = pywincode.deserialize_u64(serialized)
            assert result == expected

    def test_serialize_i8(self) -> None:
        """Test serializing i8 values."""
        import pywincode

        for value in [-128, -1, 0, 1, 127]:
            result = pywincode.serialize_i8(value)
            assert isinstance(result, bytes)

    def test_serialize_i16(self) -> None:
        """Test serializing i16 values."""
        import pywincode

        for value in [-32768, -1, 0, 1, 32767]:
            result = pywincode.serialize_i16(value)
            assert isinstance(result, bytes)

    def test_serialize_i32(self) -> None:
        """Test serializing i32 values."""
        import pywincode

        for value in [-2147483648, -1, 0, 1, 2147483647]:
            result = pywincode.serialize_i32(value)
            assert isinstance(result, bytes)

    def test_serialize_i64(self) -> None:
        """Test serializing i64 values."""
        import pywincode

        for value in [-9223372036854775808, -1, 0, 1, 9223372036854775807]:
            result = pywincode.serialize_i64(value)
            assert isinstance(result, bytes)


class TestFloatSerialization:
    """Tests for float serialization."""

    def test_serialize_f32(self) -> None:
        """Test serializing f32 values."""
        import pywincode

        for value in [0.0, 1.0, -1.0, 3.14159]:
            result = pywincode.serialize_f32(value)
            assert isinstance(result, bytes)
            assert len(result) == 4

    def test_serialize_f64(self) -> None:
        """Test serializing f64 values."""
        import pywincode

        for value in [0.0, 1.0, -1.0, 3.141592653589793]:
            result = pywincode.serialize_f64(value)
            assert isinstance(result, bytes)
            assert len(result) == 8

    def test_deserialize_f32_roundtrip(self) -> None:
        """Test f32 roundtrip."""
        import pywincode

        for expected in [0.0, 1.0, -1.0, 3.14159]:
            serialized = pywincode.serialize_f32(expected)
            result = pywincode.deserialize_f32(serialized)
            assert abs(result - expected) < 1e-6

    def test_deserialize_f64_roundtrip(self) -> None:
        """Test f64 roundtrip."""
        import pywincode

        for expected in [0.0, 1.0, -1.0, 3.141592653589793]:
            serialized = pywincode.serialize_f64(expected)
            result = pywincode.deserialize_f64(serialized)
            assert abs(result - expected) < 1e-15


class TestBoolSerialization:
    """Tests for boolean serialization."""

    def test_serialize_bool(self) -> None:
        """Test serializing boolean values."""
        import pywincode

        for value in [True, False]:
            result = pywincode.serialize_bool(value)
            assert isinstance(result, bytes)

    def test_deserialize_bool_roundtrip(self) -> None:
        """Test boolean roundtrip."""
        import pywincode

        for expected in [True, False]:
            serialized = pywincode.serialize_bool(expected)
            result = pywincode.deserialize_bool(serialized)
            assert result == expected


class TestStringSerialization:
    """Tests for string serialization."""

    def test_serialize_string(self) -> None:
        """Test serializing string values."""
        import pywincode

        result = pywincode.serialize_string("hello world")
        assert isinstance(result, bytes)

    def test_serialize_empty_string(self) -> None:
        """Test serializing empty string."""
        import pywincode

        result = pywincode.serialize_string("")
        assert isinstance(result, bytes)

    def test_serialize_unicode_string(self) -> None:
        """Test serializing unicode string."""
        import pywincode

        result = pywincode.serialize_string("hello 世界 🌍")
        assert isinstance(result, bytes)

    def test_deserialize_string_roundtrip(self) -> None:
        """Test string roundtrip."""
        import pywincode

        for expected in ["", "hello", "hello world", "unicode: 日本語"]:
            serialized = pywincode.serialize_string(expected)
            result = pywincode.deserialize_string(serialized)
            assert result == expected


class TestListSerialization:
    """Tests for list serialization."""

    def test_serialize_bytes_list(self) -> None:
        """Test serializing list of bytes."""
        import pywincode

        data = [b"hello", b"world"]
        result = pywincode.serialize_bytes_list(data)
        assert isinstance(result, bytes)

    def test_serialize_empty_list(self) -> None:
        """Test serializing empty list."""
        import pywincode

        result = pywincode.serialize_bytes_list([])
        assert isinstance(result, bytes)

    def test_deserialize_bytes_list_roundtrip(self) -> None:
        """Test bytes list roundtrip."""
        import pywincode

        expected = [b"hello", b"world", b"test"]
        serialized = pywincode.serialize_bytes_list(expected)
        result = pywincode.deserialize_bytes_list(serialized)
        assert result == expected

    def test_serialize_u64_list(self) -> None:
        """Test serializing list of u64."""
        import pywincode

        data = [1, 2, 3, 4, 5]
        result = pywincode.serialize_u64_list(data)
        assert isinstance(result, bytes)

    def test_deserialize_u64_list_roundtrip(self) -> None:
        """Test u64 list roundtrip."""
        import pywincode

        expected = [1, 2, 3, 1000000, 18446744073709551615]
        serialized = pywincode.serialize_u64_list(expected)
        result = pywincode.deserialize_u64_list(serialized)
        assert result == expected
