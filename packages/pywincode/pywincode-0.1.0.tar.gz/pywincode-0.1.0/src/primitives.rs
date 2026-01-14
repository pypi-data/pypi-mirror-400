//! Primitive type serialization for pywincode.
//!
//! This module provides serialization/deserialization for primitive types
//! including integers, floats, and booleans.

use pyo3::prelude::*;

use crate::error::{Error, Result};

// Unsigned integer serialization

/// Serialize a u8 value.
#[pyfunction]
pub fn serialize_u8(value: u8) -> Vec<u8> {
    vec![value]
}

/// Deserialize a u8 value.
#[pyfunction]
pub fn deserialize_u8(data: &[u8]) -> PyResult<u8> {
    deserialize_u8_impl(data).map_err(Into::into)
}

/// Serialize a u16 value.
#[pyfunction]
pub fn serialize_u16(value: u16) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize a u16 value.
#[pyfunction]
pub fn deserialize_u16(data: &[u8]) -> PyResult<u16> {
    deserialize_u16_impl(data).map_err(Into::into)
}

/// Serialize a u32 value.
#[pyfunction]
pub fn serialize_u32(value: u32) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize a u32 value.
#[pyfunction]
pub fn deserialize_u32(data: &[u8]) -> PyResult<u32> {
    deserialize_u32_impl(data).map_err(Into::into)
}

/// Serialize a u64 value.
#[pyfunction]
pub fn serialize_u64(value: u64) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize a u64 value.
#[pyfunction]
pub fn deserialize_u64(data: &[u8]) -> PyResult<u64> {
    deserialize_u64_impl(data).map_err(Into::into)
}

// Signed integer serialization

/// Serialize an i8 value.
#[pyfunction]
pub fn serialize_i8(value: i8) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize an i8 value.
#[pyfunction]
pub fn deserialize_i8(data: &[u8]) -> PyResult<i8> {
    deserialize_i8_impl(data).map_err(Into::into)
}

/// Serialize an i16 value.
#[pyfunction]
pub fn serialize_i16(value: i16) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize an i16 value.
#[pyfunction]
pub fn deserialize_i16(data: &[u8]) -> PyResult<i16> {
    deserialize_i16_impl(data).map_err(Into::into)
}

/// Serialize an i32 value.
#[pyfunction]
pub fn serialize_i32(value: i32) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize an i32 value.
#[pyfunction]
pub fn deserialize_i32(data: &[u8]) -> PyResult<i32> {
    deserialize_i32_impl(data).map_err(Into::into)
}

/// Serialize an i64 value.
#[pyfunction]
pub fn serialize_i64(value: i64) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize an i64 value.
#[pyfunction]
pub fn deserialize_i64(data: &[u8]) -> PyResult<i64> {
    deserialize_i64_impl(data).map_err(Into::into)
}

// Float serialization

/// Serialize an f32 value.
#[pyfunction]
pub fn serialize_f32(value: f32) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize an f32 value.
#[pyfunction]
pub fn deserialize_f32(data: &[u8]) -> PyResult<f32> {
    deserialize_f32_impl(data).map_err(Into::into)
}

/// Serialize an f64 value.
#[pyfunction]
pub fn serialize_f64(value: f64) -> Vec<u8> {
    value.to_le_bytes().to_vec()
}

/// Deserialize an f64 value.
#[pyfunction]
pub fn deserialize_f64(data: &[u8]) -> PyResult<f64> {
    deserialize_f64_impl(data).map_err(Into::into)
}

// Boolean serialization

/// Serialize a bool value.
#[pyfunction]
pub fn serialize_bool(value: bool) -> Vec<u8> {
    vec![u8::from(value)]
}

/// Deserialize a bool value.
#[pyfunction]
pub fn deserialize_bool(data: &[u8]) -> PyResult<bool> {
    deserialize_bool_impl(data).map_err(Into::into)
}

// Internal implementation functions

fn deserialize_u8_impl(data: &[u8]) -> Result<u8> {
    if data.is_empty() {
        return Err(Error::InvalidLength {
            expected: 1,
            got: 0,
        });
    }
    Ok(data[0])
}

fn deserialize_u16_impl(data: &[u8]) -> Result<u16> {
    const SIZE: usize = 2;
    if data.len() < SIZE {
        return Err(Error::InvalidLength {
            expected: SIZE,
            got: data.len(),
        });
    }
    let bytes: [u8; SIZE] = data[..SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read u16".to_string()))?;
    Ok(u16::from_le_bytes(bytes))
}

fn deserialize_u32_impl(data: &[u8]) -> Result<u32> {
    const SIZE: usize = 4;
    if data.len() < SIZE {
        return Err(Error::InvalidLength {
            expected: SIZE,
            got: data.len(),
        });
    }
    let bytes: [u8; SIZE] = data[..SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read u32".to_string()))?;
    Ok(u32::from_le_bytes(bytes))
}

fn deserialize_u64_impl(data: &[u8]) -> Result<u64> {
    const SIZE: usize = 8;
    if data.len() < SIZE {
        return Err(Error::InvalidLength {
            expected: SIZE,
            got: data.len(),
        });
    }
    let bytes: [u8; SIZE] = data[..SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read u64".to_string()))?;
    Ok(u64::from_le_bytes(bytes))
}

fn deserialize_i8_impl(data: &[u8]) -> Result<i8> {
    if data.is_empty() {
        return Err(Error::InvalidLength {
            expected: 1,
            got: 0,
        });
    }
    Ok(i8::from_le_bytes([data[0]]))
}

fn deserialize_i16_impl(data: &[u8]) -> Result<i16> {
    const SIZE: usize = 2;
    if data.len() < SIZE {
        return Err(Error::InvalidLength {
            expected: SIZE,
            got: data.len(),
        });
    }
    let bytes: [u8; SIZE] = data[..SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read i16".to_string()))?;
    Ok(i16::from_le_bytes(bytes))
}

fn deserialize_i32_impl(data: &[u8]) -> Result<i32> {
    const SIZE: usize = 4;
    if data.len() < SIZE {
        return Err(Error::InvalidLength {
            expected: SIZE,
            got: data.len(),
        });
    }
    let bytes: [u8; SIZE] = data[..SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read i32".to_string()))?;
    Ok(i32::from_le_bytes(bytes))
}

fn deserialize_i64_impl(data: &[u8]) -> Result<i64> {
    const SIZE: usize = 8;
    if data.len() < SIZE {
        return Err(Error::InvalidLength {
            expected: SIZE,
            got: data.len(),
        });
    }
    let bytes: [u8; SIZE] = data[..SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read i64".to_string()))?;
    Ok(i64::from_le_bytes(bytes))
}

fn deserialize_f32_impl(data: &[u8]) -> Result<f32> {
    const SIZE: usize = 4;
    if data.len() < SIZE {
        return Err(Error::InvalidLength {
            expected: SIZE,
            got: data.len(),
        });
    }
    let bytes: [u8; SIZE] = data[..SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read f32".to_string()))?;
    Ok(f32::from_le_bytes(bytes))
}

fn deserialize_f64_impl(data: &[u8]) -> Result<f64> {
    const SIZE: usize = 8;
    if data.len() < SIZE {
        return Err(Error::InvalidLength {
            expected: SIZE,
            got: data.len(),
        });
    }
    let bytes: [u8; SIZE] = data[..SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read f64".to_string()))?;
    Ok(f64::from_le_bytes(bytes))
}

fn deserialize_bool_impl(data: &[u8]) -> Result<bool> {
    if data.is_empty() {
        return Err(Error::InvalidLength {
            expected: 1,
            got: 0,
        });
    }
    Ok(data[0] != 0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_u8_roundtrip() {
        for value in [0u8, 1, 127, 255] {
            let serialized = serialize_u8(value);
            let deserialized = deserialize_u8_impl(&serialized).expect("deserialize failed");
            assert_eq!(value, deserialized);
        }
    }

    #[test]
    fn test_u16_roundtrip() {
        for value in [0u16, 1, 256, 65535] {
            let serialized = serialize_u16(value);
            let deserialized = deserialize_u16_impl(&serialized).expect("deserialize failed");
            assert_eq!(value, deserialized);
        }
    }

    #[test]
    fn test_u32_roundtrip() {
        for value in [0u32, 1, 65536, u32::MAX] {
            let serialized = serialize_u32(value);
            let deserialized = deserialize_u32_impl(&serialized).expect("deserialize failed");
            assert_eq!(value, deserialized);
        }
    }

    #[test]
    fn test_u64_roundtrip() {
        for value in [0u64, 1, 4294967296, u64::MAX] {
            let serialized = serialize_u64(value);
            let deserialized = deserialize_u64_impl(&serialized).expect("deserialize failed");
            assert_eq!(value, deserialized);
        }
    }

    #[test]
    fn test_i8_roundtrip() {
        for value in [i8::MIN, -1, 0, 1, i8::MAX] {
            let serialized = serialize_i8(value);
            let deserialized = deserialize_i8_impl(&serialized).expect("deserialize failed");
            assert_eq!(value, deserialized);
        }
    }

    #[test]
    fn test_f32_roundtrip() {
        for value in [0.0f32, 1.0, -1.0, 3.14159] {
            let serialized = serialize_f32(value);
            let deserialized = deserialize_f32_impl(&serialized).expect("deserialize failed");
            assert!((value - deserialized).abs() < 1e-6);
        }
    }

    #[test]
    fn test_f64_roundtrip() {
        for value in [0.0f64, 1.0, -1.0, std::f64::consts::PI] {
            let serialized = serialize_f64(value);
            let deserialized = deserialize_f64_impl(&serialized).expect("deserialize failed");
            assert!((value - deserialized).abs() < 1e-14);
        }
    }

    #[test]
    fn test_bool_roundtrip() {
        for value in [true, false] {
            let serialized = serialize_bool(value);
            let deserialized = deserialize_bool_impl(&serialized).expect("deserialize failed");
            assert_eq!(value, deserialized);
        }
    }
}
