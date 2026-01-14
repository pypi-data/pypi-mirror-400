"""Tests for pywincode zerocopy functionality.

This module tests the zerocopy operations that allow zero-copy
access to serialized data in memory.
"""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass


class TestZeroCopyBytes:
    """Tests for zero-copy byte operations."""

    def test_zerocopy_view(self) -> None:
        """Test creating a zero-copy view of bytes."""
        import pywincode

        data = b"hello world"
        view = pywincode.zerocopy_view(data)

        assert view is not None
        assert len(view) == len(data)

    def test_zerocopy_view_readonly(self) -> None:
        """Test that zero-copy view is read-only."""
        import pywincode

        data = b"hello world"
        view = pywincode.zerocopy_view(data)

        assert isinstance(view, memoryview)
        assert view.readonly

    def test_zerocopy_view_content(self) -> None:
        """Test zero-copy view has correct content."""
        import pywincode

        data = b"hello world"
        view = pywincode.zerocopy_view(data)

        assert bytes(view) == data

    def test_zerocopy_view_empty(self) -> None:
        """Test zero-copy view of empty bytes."""
        import pywincode

        data = b""
        view = pywincode.zerocopy_view(data)

        assert len(view) == 0


class TestZeroCopyU8Array:
    """Tests for zero-copy u8 array operations."""

    def test_zerocopy_u8_array(self) -> None:
        """Test creating a zero-copy u8 array view."""
        import pywincode

        data = bytes([1, 2, 3, 4, 5])
        view = pywincode.zerocopy_u8_array(data)

        assert len(view) == 5
        assert list(view) == [1, 2, 3, 4, 5]

    def test_zerocopy_u8_array_slicing(self) -> None:
        """Test slicing zero-copy u8 array."""
        import pywincode

        data = bytes(range(10))
        view = pywincode.zerocopy_u8_array(data)

        assert list(view[2:5]) == [2, 3, 4]


class TestZeroCopyU16Array:
    """Tests for zero-copy u16 array operations."""

    def test_zerocopy_u16_array(self) -> None:
        """Test creating a zero-copy u16 array view."""
        import pywincode

        data = struct.pack("<5H", 1, 2, 3, 4, 5)
        view = pywincode.zerocopy_u16_array(data)

        assert len(view) == 5
        assert list(view) == [1, 2, 3, 4, 5]

    def test_zerocopy_u16_array_alignment(self) -> None:
        """Test u16 array requires proper alignment."""
        import pywincode

        data = struct.pack("<3H", 256, 512, 1024)
        view = pywincode.zerocopy_u16_array(data)

        assert list(view) == [256, 512, 1024]


class TestZeroCopyU32Array:
    """Tests for zero-copy u32 array operations."""

    def test_zerocopy_u32_array(self) -> None:
        """Test creating a zero-copy u32 array view."""
        import pywincode

        data = struct.pack("<5I", 1, 2, 3, 4, 5)
        view = pywincode.zerocopy_u32_array(data)

        assert len(view) == 5
        assert list(view) == [1, 2, 3, 4, 5]

    def test_zerocopy_u32_array_large_values(self) -> None:
        """Test u32 array with large values."""
        import pywincode

        values = [0, 1, 65536, 4294967295]
        data = struct.pack(f"<{len(values)}I", *values)
        view = pywincode.zerocopy_u32_array(data)

        assert list(view) == values


class TestZeroCopyU64Array:
    """Tests for zero-copy u64 array operations."""

    def test_zerocopy_u64_array(self) -> None:
        """Test creating a zero-copy u64 array view."""
        import pywincode

        data = struct.pack("<5Q", 1, 2, 3, 4, 5)
        view = pywincode.zerocopy_u64_array(data)

        assert len(view) == 5
        assert list(view) == [1, 2, 3, 4, 5]

    def test_zerocopy_u64_array_large_values(self) -> None:
        """Test u64 array with large values."""
        import pywincode

        values = [0, 1, 4294967296, 18446744073709551615]
        data = struct.pack(f"<{len(values)}Q", *values)
        view = pywincode.zerocopy_u64_array(data)

        assert list(view) == values


class TestZeroCopyI8Array:
    """Tests for zero-copy i8 array operations."""

    def test_zerocopy_i8_array(self) -> None:
        """Test creating a zero-copy i8 array view."""
        import pywincode

        data = struct.pack("<5b", -2, -1, 0, 1, 2)
        view = pywincode.zerocopy_i8_array(data)

        assert len(view) == 5
        assert list(view) == [-2, -1, 0, 1, 2]


class TestZeroCopyI16Array:
    """Tests for zero-copy i16 array operations."""

    def test_zerocopy_i16_array(self) -> None:
        """Test creating a zero-copy i16 array view."""
        import pywincode

        data = struct.pack("<5h", -2, -1, 0, 1, 2)
        view = pywincode.zerocopy_i16_array(data)

        assert len(view) == 5
        assert list(view) == [-2, -1, 0, 1, 2]


class TestZeroCopyI32Array:
    """Tests for zero-copy i32 array operations."""

    def test_zerocopy_i32_array(self) -> None:
        """Test creating a zero-copy i32 array view."""
        import pywincode

        data = struct.pack("<5i", -2, -1, 0, 1, 2)
        view = pywincode.zerocopy_i32_array(data)

        assert len(view) == 5
        assert list(view) == [-2, -1, 0, 1, 2]


class TestZeroCopyI64Array:
    """Tests for zero-copy i64 array operations."""

    def test_zerocopy_i64_array(self) -> None:
        """Test creating a zero-copy i64 array view."""
        import pywincode

        data = struct.pack("<5q", -2, -1, 0, 1, 2)
        view = pywincode.zerocopy_i64_array(data)

        assert len(view) == 5
        assert list(view) == [-2, -1, 0, 1, 2]


class TestZeroCopyF32Array:
    """Tests for zero-copy f32 array operations."""

    def test_zerocopy_f32_array(self) -> None:
        """Test creating a zero-copy f32 array view."""
        import pywincode

        values = [1.0, 2.5, 3.14, -1.0, 0.0]
        data = struct.pack(f"<{len(values)}f", *values)
        view = pywincode.zerocopy_f32_array(data)

        assert len(view) == 5
        for i, v in enumerate(values):
            assert abs(view[i] - v) < 1e-6


class TestZeroCopyF64Array:
    """Tests for zero-copy f64 array operations."""

    def test_zerocopy_f64_array(self) -> None:
        """Test creating a zero-copy f64 array view."""
        import pywincode

        values = [1.0, 2.5, 3.141592653589793, -1.0, 0.0]
        data = struct.pack(f"<{len(values)}d", *values)
        view = pywincode.zerocopy_f64_array(data)

        assert len(view) == 5
        for i, v in enumerate(values):
            assert abs(view[i] - v) < 1e-15


class TestFromBytes:
    """Tests for from_bytes conversion."""

    def test_u32_from_bytes(self) -> None:
        """Test converting bytes to u32."""
        import pywincode

        data = struct.pack("<I", 12345678)
        result = pywincode.u32_from_bytes(data)

        assert result == 12345678

    def test_u64_from_bytes(self) -> None:
        """Test converting bytes to u64."""
        import pywincode

        data = struct.pack("<Q", 123456789012345)
        result = pywincode.u64_from_bytes(data)

        assert result == 123456789012345

    def test_f32_from_bytes(self) -> None:
        """Test converting bytes to f32."""
        import pywincode

        expected = 3.14159
        data = struct.pack("<f", expected)
        result = pywincode.f32_from_bytes(data)

        assert abs(result - expected) < 1e-5

    def test_f64_from_bytes(self) -> None:
        """Test converting bytes to f64."""
        import pywincode

        expected = 3.141592653589793
        data = struct.pack("<d", expected)
        result = pywincode.f64_from_bytes(data)

        assert abs(result - expected) < 1e-15

    def test_from_bytes_invalid_length(self) -> None:
        """Test from_bytes with invalid length raises error."""
        import pywincode

        with pytest.raises(pywincode.WincodeError):
            pywincode.u32_from_bytes(b"\x00\x00")


class TestIntoBytes:
    """Tests for into_bytes conversion."""

    def test_u32_into_bytes(self) -> None:
        """Test converting u32 to bytes."""
        import pywincode

        result = pywincode.u32_into_bytes(12345678)
        expected = struct.pack("<I", 12345678)

        assert result == expected

    def test_u64_into_bytes(self) -> None:
        """Test converting u64 to bytes."""
        import pywincode

        result = pywincode.u64_into_bytes(123456789012345)
        expected = struct.pack("<Q", 123456789012345)

        assert result == expected

    def test_f32_into_bytes(self) -> None:
        """Test converting f32 to bytes."""
        import pywincode

        value = 3.14159
        result = pywincode.f32_into_bytes(value)
        expected = struct.pack("<f", value)

        assert result == expected

    def test_f64_into_bytes(self) -> None:
        """Test converting f64 to bytes."""
        import pywincode

        value = 3.141592653589793
        result = pywincode.f64_into_bytes(value)
        expected = struct.pack("<d", value)

        assert result == expected


class TestZeroCopySlice:
    """Tests for zero-copy slice operations."""

    def test_slice_u32_array(self) -> None:
        """Test slicing a zero-copy u32 array."""
        import pywincode

        values = list(range(10))
        data = struct.pack(f"<{len(values)}I", *values)
        view = pywincode.zerocopy_u32_array(data)

        sliced = view[2:7]
        assert list(sliced) == [2, 3, 4, 5, 6]

    def test_slice_with_step(self) -> None:
        """Test slicing with step."""
        import pywincode

        values = list(range(10))
        data = struct.pack(f"<{len(values)}I", *values)
        view = pywincode.zerocopy_u32_array(data)

        sliced = view[::2]
        assert list(sliced) == [0, 2, 4, 6, 8]


class TestZeroCopyBuffer:
    """Tests for zero-copy buffer protocol."""

    def test_zerocopy_view_buffer_protocol(self) -> None:
        """Test that zerocopy_view returns memoryview."""
        import pywincode

        data = b"hello world"
        view = pywincode.zerocopy_view(data)

        assert isinstance(view, memoryview)
        assert view.readonly

    def test_numpy_compatibility(self) -> None:
        """Test that zerocopy arrays work with numpy."""
        pytest.importorskip("numpy")
        import numpy as np

        import pywincode

        data = struct.pack("<5I", 1, 2, 3, 4, 5)
        # zerocopy_u32_array returns a list of ints
        arr = pywincode.zerocopy_u32_array(data)
        np_arr = np.array(arr, dtype=np.uint32)
        assert list(np_arr) == [1, 2, 3, 4, 5]
