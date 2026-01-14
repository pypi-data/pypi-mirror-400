"""Property-based tests for pywincode.

This module uses hypothesis to test properties that should hold
for all inputs to the serialization functions.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

MAX_EXAMPLES = 100


class TestSerializationProperties:
    """Property-based tests for serialization."""

    @given(st.binary(max_size=10000))
    @settings(max_examples=MAX_EXAMPLES)
    def test_bytes_roundtrip(self, data: bytes) -> None:
        """Test that bytes serialize/deserialize is a roundtrip."""
        import pywincode

        serialized = pywincode.serialize(data)
        deserialized = pywincode.deserialize(serialized)

        assert deserialized == data

    @given(st.binary(max_size=10000))
    @settings(max_examples=MAX_EXAMPLES)
    def test_serialized_size_accurate(self, data: bytes) -> None:
        """Test that serialized_size returns accurate size."""
        import pywincode

        size = pywincode.serialized_size(data)
        serialized = pywincode.serialize(data)

        assert size == len(serialized)

    @given(st.binary(max_size=1000))
    @settings(max_examples=MAX_EXAMPLES)
    def test_serialize_into_matches_serialize(self, data: bytes) -> None:
        """Test that serialize_into produces same output as serialize."""
        import pywincode

        direct = pywincode.serialize(data)
        size = pywincode.serialized_size(data)
        buffer = bytearray(size)
        pywincode.serialize_into(data, buffer)

        assert bytes(buffer) == direct


class TestIntegerProperties:
    """Property-based tests for integer serialization."""

    @given(st.integers(min_value=0, max_value=255))
    @settings(max_examples=MAX_EXAMPLES)
    def test_u8_roundtrip(self, value: int) -> None:
        """Test u8 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_u8(value)
        deserialized = pywincode.deserialize_u8(serialized)

        assert deserialized == value

    @given(st.integers(min_value=0, max_value=65535))
    @settings(max_examples=MAX_EXAMPLES)
    def test_u16_roundtrip(self, value: int) -> None:
        """Test u16 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_u16(value)
        deserialized = pywincode.deserialize_u16(serialized)

        assert deserialized == value

    @given(st.integers(min_value=0, max_value=4294967295))
    @settings(max_examples=MAX_EXAMPLES)
    def test_u32_roundtrip(self, value: int) -> None:
        """Test u32 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_u32(value)
        deserialized = pywincode.deserialize_u32(serialized)

        assert deserialized == value

    @given(st.integers(min_value=0, max_value=18446744073709551615))
    @settings(max_examples=MAX_EXAMPLES)
    def test_u64_roundtrip(self, value: int) -> None:
        """Test u64 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_u64(value)
        deserialized = pywincode.deserialize_u64(serialized)

        assert deserialized == value

    @given(st.integers(min_value=-128, max_value=127))
    @settings(max_examples=MAX_EXAMPLES)
    def test_i8_roundtrip(self, value: int) -> None:
        """Test i8 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_i8(value)
        deserialized = pywincode.deserialize_i8(serialized)

        assert deserialized == value

    @given(st.integers(min_value=-32768, max_value=32767))
    @settings(max_examples=MAX_EXAMPLES)
    def test_i16_roundtrip(self, value: int) -> None:
        """Test i16 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_i16(value)
        deserialized = pywincode.deserialize_i16(serialized)

        assert deserialized == value

    @given(st.integers(min_value=-2147483648, max_value=2147483647))
    @settings(max_examples=MAX_EXAMPLES)
    def test_i32_roundtrip(self, value: int) -> None:
        """Test i32 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_i32(value)
        deserialized = pywincode.deserialize_i32(serialized)

        assert deserialized == value

    @given(st.integers(min_value=-9223372036854775808, max_value=9223372036854775807))
    @settings(max_examples=MAX_EXAMPLES)
    def test_i64_roundtrip(self, value: int) -> None:
        """Test i64 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_i64(value)
        deserialized = pywincode.deserialize_i64(serialized)

        assert deserialized == value


class TestFloatProperties:
    """Property-based tests for float serialization."""

    @given(st.floats(allow_nan=False, allow_infinity=False, width=32))
    @settings(max_examples=MAX_EXAMPLES)
    def test_f32_roundtrip(self, value: float) -> None:
        """Test f32 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_f32(value)
        deserialized = pywincode.deserialize_f32(serialized)

        if value == 0.0:
            assert deserialized == 0.0
        else:
            assert abs(deserialized - value) / abs(value) < 1e-6

    @given(st.floats(allow_nan=False, allow_infinity=False, width=64))
    @settings(max_examples=MAX_EXAMPLES)
    def test_f64_roundtrip(self, value: float) -> None:
        """Test f64 roundtrip."""
        import pywincode

        serialized = pywincode.serialize_f64(value)
        deserialized = pywincode.deserialize_f64(serialized)

        if value == 0.0:
            assert deserialized == 0.0
        else:
            assert abs(deserialized - value) / abs(value) < 1e-14


class TestStringProperties:
    """Property-based tests for string serialization."""

    @given(st.text(max_size=1000))
    @settings(max_examples=MAX_EXAMPLES)
    def test_string_roundtrip(self, value: str) -> None:
        """Test string roundtrip."""
        import pywincode

        serialized = pywincode.serialize_string(value)
        deserialized = pywincode.deserialize_string(serialized)

        assert deserialized == value


class TestListProperties:
    """Property-based tests for list serialization."""

    @given(st.lists(st.binary(max_size=100), max_size=50))
    @settings(max_examples=MAX_EXAMPLES)
    def test_bytes_list_roundtrip(self, values: list[bytes]) -> None:
        """Test bytes list roundtrip."""
        import pywincode

        serialized = pywincode.serialize_bytes_list(values)
        deserialized = pywincode.deserialize_bytes_list(serialized)

        assert deserialized == values

    @given(st.lists(st.integers(min_value=0, max_value=18446744073709551615), max_size=100))
    @settings(max_examples=MAX_EXAMPLES)
    def test_u64_list_roundtrip(self, values: list[int]) -> None:
        """Test u64 list roundtrip."""
        import pywincode

        serialized = pywincode.serialize_u64_list(values)
        deserialized = pywincode.deserialize_u64_list(serialized)

        assert deserialized == values


class TestZeroCopyProperties:
    """Property-based tests for zerocopy operations."""

    @given(st.binary(max_size=1000))
    @settings(max_examples=MAX_EXAMPLES)
    def test_zerocopy_view_preserves_content(self, data: bytes) -> None:
        """Test zerocopy view preserves content."""
        import pywincode

        view = pywincode.zerocopy_view(data)

        assert bytes(view) == data

    @given(st.lists(st.integers(min_value=0, max_value=255), min_size=1, max_size=100))
    @settings(max_examples=MAX_EXAMPLES)
    def test_zerocopy_u8_array_content(self, values: list[int]) -> None:
        """Test zerocopy u8 array content."""
        import pywincode

        data = bytes(values)
        view = pywincode.zerocopy_u8_array(data)

        assert list(view) == values
