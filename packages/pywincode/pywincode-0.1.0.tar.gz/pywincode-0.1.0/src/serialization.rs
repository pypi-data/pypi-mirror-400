//! Core serialization functions for pywincode.
//!
//! This module provides the main serialize/deserialize functions
//! for bytes, strings, and lists.

#![allow(unsafe_code)]
#![allow(clippy::cast_possible_truncation)]

use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes, PyList};

use crate::error::{Error, Result};

/// Serialize bytes using wincode format.
///
/// # Arguments
/// * `data` - Bytes to serialize
///
/// # Returns
/// Serialized bytes
#[pyfunction]
pub fn serialize(data: &[u8]) -> PyResult<Vec<u8>> {
    Ok(serialize_bytes_impl(data))
}

/// Deserialize bytes from wincode format.
///
/// # Arguments
/// * `data` - Serialized bytes
///
/// # Returns
/// Deserialized bytes
#[pyfunction]
pub fn deserialize(data: &[u8]) -> PyResult<Vec<u8>> {
    deserialize_bytes_impl(data).map_err(Into::into)
}

/// Get the serialized size of bytes.
///
/// # Arguments
/// * `data` - Bytes to measure
///
/// # Returns
/// Size in bytes when serialized
#[pyfunction]
pub fn serialized_size(data: &[u8]) -> usize {
    // Length prefix (8 bytes for u64) + data length
    8 + data.len()
}

/// Serialize bytes into a pre-allocated buffer.
///
/// # Arguments
/// * `data` - Bytes to serialize
/// * `buffer` - Buffer to write into
///
/// # Returns
/// Number of bytes written
#[pyfunction]
pub fn serialize_into(data: &[u8], buffer: &Bound<'_, PyByteArray>) -> PyResult<usize> {
    let needed = serialized_size(data);

    // SAFETY: We check buffer length before writing
    let buf_len = buffer.len();
    if buf_len < needed {
        return Err(Error::BufferTooSmall {
            needed,
            got: buf_len,
        }
        .into());
    }

    let serialized = serialize_bytes_impl(data);

    // Copy serialized data to buffer
    // SAFETY: PyByteArray allows mutation through data()
    unsafe {
        let buf_ptr = buffer.data();
        std::ptr::copy_nonoverlapping(serialized.as_ptr(), buf_ptr, serialized.len());
    }

    Ok(serialized.len())
}

/// Serialize a string using wincode format.
///
/// # Arguments
/// * `data` - String to serialize
///
/// # Returns
/// Serialized bytes
#[pyfunction]
pub fn serialize_string(data: &str) -> PyResult<Vec<u8>> {
    Ok(serialize_bytes_impl(data.as_bytes()))
}

/// Deserialize a string from wincode format.
///
/// # Arguments
/// * `data` - Serialized bytes
///
/// # Returns
/// Deserialized string
#[pyfunction]
pub fn deserialize_string(data: &[u8]) -> PyResult<String> {
    let bytes = deserialize_bytes_impl(data)?;
    String::from_utf8(bytes).map_err(|e| Error::InvalidUtf8(e.to_string()).into())
}

/// Serialize a list of bytes using wincode format.
///
/// # Arguments
/// * `data` - List of byte sequences to serialize
///
/// # Returns
/// Serialized bytes
#[pyfunction]
pub fn serialize_bytes_list(data: &Bound<'_, PyList>) -> PyResult<Vec<u8>> {
    let items: Vec<Vec<u8>> = data.extract()?;
    Ok(serialize_vec_bytes_impl(&items))
}

/// Deserialize a list of bytes from wincode format.
///
/// # Arguments
/// * `data` - Serialized bytes
///
/// # Returns
/// List of byte sequences
#[pyfunction]
pub fn deserialize_bytes_list(py: Python<'_>, data: &[u8]) -> PyResult<Py<PyList>> {
    let items = deserialize_vec_bytes_impl(data)?;
    let list = PyList::new(py, items.iter().map(|b| PyBytes::new(py, b)))?;
    Ok(list.into())
}

/// Serialize a list of u64 values.
///
/// # Arguments
/// * `data` - List of u64 values
///
/// # Returns
/// Serialized bytes
#[pyfunction]
pub fn serialize_u64_list(data: Vec<u64>) -> PyResult<Vec<u8>> {
    Ok(serialize_u64_vec_impl(&data))
}

/// Deserialize a list of u64 values.
///
/// # Arguments
/// * `data` - Serialized bytes
///
/// # Returns
/// List of u64 values
#[pyfunction]
pub fn deserialize_u64_list(data: &[u8]) -> PyResult<Vec<u64>> {
    deserialize_u64_vec_impl(data).map_err(Into::into)
}

// Internal implementation functions

fn serialize_bytes_impl(data: &[u8]) -> Vec<u8> {
    // wincode format: length prefix (little-endian u64) + data
    let len = data.len() as u64;
    let mut result = Vec::with_capacity(8 + data.len());
    result.extend_from_slice(&len.to_le_bytes());
    result.extend_from_slice(data);
    result
}

fn deserialize_bytes_impl(data: &[u8]) -> Result<Vec<u8>> {
    const LEN_SIZE: usize = 8;

    if data.len() < LEN_SIZE {
        return Err(Error::Deserialize(
            "data too short for length prefix".to_string(),
        ));
    }

    let len_bytes: [u8; 8] = data[..LEN_SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read length".to_string()))?;

    let len_u64 = u64::from_le_bytes(len_bytes);

    // Check for overflow before casting to usize
    let len = usize::try_from(len_u64)
        .map_err(|_| Error::Deserialize(format!("length {len_u64} exceeds maximum usize")))?;

    // Use checked_add to prevent overflow
    let required_len = LEN_SIZE
        .checked_add(len)
        .ok_or_else(|| Error::Deserialize("length overflow".to_string()))?;

    if data.len() < required_len {
        return Err(Error::Deserialize(format!(
            "data too short: expected {} bytes, got {}",
            required_len,
            data.len()
        )));
    }

    Ok(data[LEN_SIZE..LEN_SIZE + len].to_vec())
}

fn serialize_vec_bytes_impl(items: &[Vec<u8>]) -> Vec<u8> {
    // Format: count (u64) + [length (u64) + data] for each item
    let total_size: usize = 8 + items.iter().map(|item| 8 + item.len()).sum::<usize>();
    let mut result = Vec::with_capacity(total_size);

    // Write count
    let count = items.len() as u64;
    result.extend_from_slice(&count.to_le_bytes());

    // Write each item
    for item in items {
        let len = item.len() as u64;
        result.extend_from_slice(&len.to_le_bytes());
        result.extend_from_slice(item);
    }

    result
}

fn deserialize_vec_bytes_impl(data: &[u8]) -> Result<Vec<Vec<u8>>> {
    const LEN_SIZE: usize = 8;

    if data.len() < LEN_SIZE {
        return Err(Error::Deserialize(
            "data too short for count prefix".to_string(),
        ));
    }

    let count_bytes: [u8; 8] = data[..LEN_SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read count".to_string()))?;

    let count = u64::from_le_bytes(count_bytes) as usize;
    let mut result = Vec::with_capacity(count);
    let mut offset = LEN_SIZE;

    for _ in 0..count {
        if offset + LEN_SIZE > data.len() {
            return Err(Error::Deserialize(
                "data too short for item length".to_string(),
            ));
        }

        let len_bytes: [u8; 8] = data[offset..offset + LEN_SIZE]
            .try_into()
            .map_err(|_| Error::Deserialize("failed to read item length".to_string()))?;

        let len = u64::from_le_bytes(len_bytes) as usize;
        offset += LEN_SIZE;

        if offset + len > data.len() {
            return Err(Error::Deserialize(
                "data too short for item data".to_string(),
            ));
        }

        result.push(data[offset..offset + len].to_vec());
        offset += len;
    }

    Ok(result)
}

fn serialize_u64_vec_impl(items: &[u64]) -> Vec<u8> {
    // Format: count (u64) + values (each u64)
    let total_size = 8 + items.len() * 8;
    let mut result = Vec::with_capacity(total_size);

    // Write count
    let count = items.len() as u64;
    result.extend_from_slice(&count.to_le_bytes());

    // Write each value
    for item in items {
        result.extend_from_slice(&item.to_le_bytes());
    }

    result
}

fn deserialize_u64_vec_impl(data: &[u8]) -> Result<Vec<u64>> {
    const LEN_SIZE: usize = 8;

    if data.len() < LEN_SIZE {
        return Err(Error::Deserialize(
            "data too short for count prefix".to_string(),
        ));
    }

    let count_bytes: [u8; 8] = data[..LEN_SIZE]
        .try_into()
        .map_err(|_| Error::Deserialize("failed to read count".to_string()))?;

    let count = u64::from_le_bytes(count_bytes) as usize;
    let expected_len = LEN_SIZE + count * 8;

    if data.len() < expected_len {
        return Err(Error::Deserialize(format!(
            "data too short: expected {} bytes, got {}",
            expected_len,
            data.len()
        )));
    }

    let mut result = Vec::with_capacity(count);
    let mut offset = LEN_SIZE;

    for _ in 0..count {
        let value_bytes: [u8; 8] = data[offset..offset + 8]
            .try_into()
            .map_err(|_| Error::Deserialize("failed to read u64 value".to_string()))?;

        result.push(u64::from_le_bytes(value_bytes));
        offset += 8;
    }

    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_serialize_bytes_roundtrip() {
        let data = b"hello world";
        let serialized = serialize_bytes_impl(data);
        let deserialized = deserialize_bytes_impl(&serialized).expect("deserialize failed");
        assert_eq!(data.as_slice(), deserialized.as_slice());
    }

    #[test]
    fn test_serialize_empty_bytes() {
        let data = b"";
        let serialized = serialize_bytes_impl(data);
        let deserialized = deserialize_bytes_impl(&serialized).expect("deserialize failed");
        assert!(deserialized.is_empty());
    }

    #[test]
    fn test_serialize_vec_bytes_roundtrip() {
        let items = vec![b"hello".to_vec(), b"world".to_vec()];
        let serialized = serialize_vec_bytes_impl(&items);
        let deserialized = deserialize_vec_bytes_impl(&serialized).expect("deserialize failed");
        assert_eq!(items, deserialized);
    }

    #[test]
    fn test_serialize_u64_vec_roundtrip() {
        let items = vec![1u64, 2, 3, 1000000, u64::MAX];
        let serialized = serialize_u64_vec_impl(&items);
        let deserialized = deserialize_u64_vec_impl(&serialized).expect("deserialize failed");
        assert_eq!(items, deserialized);
    }
}
