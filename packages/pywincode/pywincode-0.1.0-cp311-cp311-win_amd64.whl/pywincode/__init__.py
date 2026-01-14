"""pywincode - Python bindings for wincode serialization with zerocopy support.

This package provides fast binary serialization/deserialization using the
wincode Rust library, along with zero-copy array operations.

Example:
    >>> import pywincode
    >>> data = b"hello world"
    >>> serialized = pywincode.serialize(data)
    >>> deserialized = pywincode.deserialize(serialized)
    >>> assert deserialized == data
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pywincode._pywincode import (
    WincodeError,
    deserialize,
    deserialize_bool,
    deserialize_bytes_list,
    deserialize_f32,
    deserialize_f64,
    deserialize_i8,
    deserialize_i16,
    deserialize_i32,
    deserialize_i64,
    deserialize_string,
    deserialize_u8,
    deserialize_u16,
    deserialize_u32,
    deserialize_u64,
    deserialize_u64_list,
    f32_from_bytes,
    f32_into_bytes,
    f64_from_bytes,
    f64_into_bytes,
    serialize,
    serialize_bool,
    serialize_bytes_list,
    serialize_f32,
    serialize_f64,
    serialize_i8,
    serialize_i16,
    serialize_i32,
    serialize_i64,
    serialize_into,
    serialize_string,
    serialize_u8,
    serialize_u16,
    serialize_u32,
    serialize_u64,
    serialize_u64_list,
    serialized_size,
    u32_from_bytes,
    u32_into_bytes,
    u64_from_bytes,
    u64_into_bytes,
    zerocopy_f32_array,
    zerocopy_f64_array,
    zerocopy_i8_array,
    zerocopy_i16_array,
    zerocopy_i32_array,
    zerocopy_i64_array,
    zerocopy_u8_array,
    zerocopy_u16_array,
    zerocopy_u32_array,
    zerocopy_u64_array,
    zerocopy_view,
)

__version__ = "0.1.0"
__all__ = [
    # Error type
    "WincodeError",
    # Core serialization
    "serialize",
    "deserialize",
    "serialized_size",
    "serialize_into",
    # Unsigned integers
    "serialize_u8",
    "serialize_u16",
    "serialize_u32",
    "serialize_u64",
    "deserialize_u8",
    "deserialize_u16",
    "deserialize_u32",
    "deserialize_u64",
    # Signed integers
    "serialize_i8",
    "serialize_i16",
    "serialize_i32",
    "serialize_i64",
    "deserialize_i8",
    "deserialize_i16",
    "deserialize_i32",
    "deserialize_i64",
    # Floats
    "serialize_f32",
    "serialize_f64",
    "deserialize_f32",
    "deserialize_f64",
    # Boolean
    "serialize_bool",
    "deserialize_bool",
    # Strings
    "serialize_string",
    "deserialize_string",
    # Lists
    "serialize_bytes_list",
    "deserialize_bytes_list",
    "serialize_u64_list",
    "deserialize_u64_list",
    # Zerocopy operations
    "zerocopy_view",
    "zerocopy_u8_array",
    "zerocopy_u16_array",
    "zerocopy_u32_array",
    "zerocopy_u64_array",
    "zerocopy_i8_array",
    "zerocopy_i16_array",
    "zerocopy_i32_array",
    "zerocopy_i64_array",
    "zerocopy_f32_array",
    "zerocopy_f64_array",
    # From/Into bytes
    "u32_from_bytes",
    "u64_from_bytes",
    "f32_from_bytes",
    "f64_from_bytes",
    "u32_into_bytes",
    "u64_into_bytes",
    "f32_into_bytes",
    "f64_into_bytes",
]
