//! Zerocopy operations for pywincode.
//!
//! This module provides zero-copy array views and type conversions
//! using the zerocopy crate for efficient memory access.

use pyo3::prelude::*;
use pyo3::types::PyMemoryView;
use zerocopy::{FromBytes, IntoBytes};

use crate::error::{Error, Result};

/// Create a zero-copy view of bytes.
///
/// Returns a read-only memoryview of the input bytes.
#[pyfunction]
#[allow(clippy::needless_pass_by_value)]
pub fn zerocopy_view<'py>(
    data: &Bound<'py, pyo3::types::PyBytes>,
) -> PyResult<Bound<'py, PyMemoryView>> {
    PyMemoryView::from(data)
}

/// Create a zero-copy u8 array view.
#[pyfunction]
#[allow(clippy::needless_pass_by_value)]
pub fn zerocopy_u8_array<'py>(
    data: &Bound<'py, pyo3::types::PyBytes>,
) -> PyResult<Bound<'py, PyMemoryView>> {
    PyMemoryView::from(data)
}

/// Create a zero-copy u16 array view.
///
/// Data length must be a multiple of 2 bytes.
#[pyfunction]
pub fn zerocopy_u16_array(data: &[u8]) -> PyResult<Vec<u16>> {
    zerocopy_array_impl::<u16>(data).map_err(Into::into)
}

/// Create a zero-copy u32 array view.
///
/// Data length must be a multiple of 4 bytes.
#[pyfunction]
pub fn zerocopy_u32_array(data: &[u8]) -> PyResult<Vec<u32>> {
    zerocopy_array_impl::<u32>(data).map_err(Into::into)
}

/// Create a zero-copy u64 array view.
///
/// Data length must be a multiple of 8 bytes.
#[pyfunction]
pub fn zerocopy_u64_array(data: &[u8]) -> PyResult<Vec<u64>> {
    zerocopy_array_impl::<u64>(data).map_err(Into::into)
}

/// Create a zero-copy i8 array view.
#[pyfunction]
pub fn zerocopy_i8_array(data: &[u8]) -> PyResult<Vec<i8>> {
    zerocopy_array_impl::<i8>(data).map_err(Into::into)
}

/// Create a zero-copy i16 array view.
///
/// Data length must be a multiple of 2 bytes.
#[pyfunction]
pub fn zerocopy_i16_array(data: &[u8]) -> PyResult<Vec<i16>> {
    zerocopy_array_impl::<i16>(data).map_err(Into::into)
}

/// Create a zero-copy i32 array view.
///
/// Data length must be a multiple of 4 bytes.
#[pyfunction]
pub fn zerocopy_i32_array(data: &[u8]) -> PyResult<Vec<i32>> {
    zerocopy_array_impl::<i32>(data).map_err(Into::into)
}

/// Create a zero-copy i64 array view.
///
/// Data length must be a multiple of 8 bytes.
#[pyfunction]
pub fn zerocopy_i64_array(data: &[u8]) -> PyResult<Vec<i64>> {
    zerocopy_array_impl::<i64>(data).map_err(Into::into)
}

/// Create a zero-copy f32 array view.
///
/// Data length must be a multiple of 4 bytes.
#[pyfunction]
pub fn zerocopy_f32_array(data: &[u8]) -> PyResult<Vec<f32>> {
    zerocopy_array_impl::<f32>(data).map_err(Into::into)
}

/// Create a zero-copy f64 array view.
///
/// Data length must be a multiple of 8 bytes.
#[pyfunction]
pub fn zerocopy_f64_array(data: &[u8]) -> PyResult<Vec<f64>> {
    zerocopy_array_impl::<f64>(data).map_err(Into::into)
}

/// Convert bytes to u32 using zerocopy.
///
/// Data must be exactly 4 bytes.
#[pyfunction]
pub fn u32_from_bytes(data: &[u8]) -> PyResult<u32> {
    from_bytes_impl::<u32>(data).map_err(Into::into)
}

/// Convert bytes to u64 using zerocopy.
///
/// Data must be exactly 8 bytes.
#[pyfunction]
pub fn u64_from_bytes(data: &[u8]) -> PyResult<u64> {
    from_bytes_impl::<u64>(data).map_err(Into::into)
}

/// Convert bytes to f32 using zerocopy.
///
/// Data must be exactly 4 bytes.
#[pyfunction]
pub fn f32_from_bytes(data: &[u8]) -> PyResult<f32> {
    from_bytes_impl::<f32>(data).map_err(Into::into)
}

/// Convert bytes to f64 using zerocopy.
///
/// Data must be exactly 8 bytes.
#[pyfunction]
pub fn f64_from_bytes(data: &[u8]) -> PyResult<f64> {
    from_bytes_impl::<f64>(data).map_err(Into::into)
}

/// Convert u32 to bytes using zerocopy.
#[pyfunction]
pub fn u32_into_bytes(value: u32) -> Vec<u8> {
    value.as_bytes().to_vec()
}

/// Convert u64 to bytes using zerocopy.
#[pyfunction]
pub fn u64_into_bytes(value: u64) -> Vec<u8> {
    value.as_bytes().to_vec()
}

/// Convert f32 to bytes using zerocopy.
#[pyfunction]
pub fn f32_into_bytes(value: f32) -> Vec<u8> {
    value.as_bytes().to_vec()
}

/// Convert f64 to bytes using zerocopy.
#[pyfunction]
pub fn f64_into_bytes(value: f64) -> Vec<u8> {
    value.as_bytes().to_vec()
}

// Internal implementation functions

fn zerocopy_array_impl<T>(data: &[u8]) -> Result<Vec<T>>
where
    T: FromBytes + Copy,
{
    let type_size = std::mem::size_of::<T>();

    if type_size == 0 {
        return Ok(Vec::new());
    }

    if data.len() % type_size != 0 {
        return Err(Error::InvalidLength {
            expected: (data.len() / type_size + 1) * type_size,
            got: data.len(),
        });
    }

    let count = data.len() / type_size;
    let mut result = Vec::with_capacity(count);

    for i in 0..count {
        let start = i * type_size;
        let end = start + type_size;
        let bytes = &data[start..end];

        let value = T::read_from_bytes(bytes).map_err(|_| {
            Error::Deserialize(format!(
                "failed to read {} at offset {}",
                std::any::type_name::<T>(),
                start
            ))
        })?;

        result.push(value);
    }

    Ok(result)
}

fn from_bytes_impl<T>(data: &[u8]) -> Result<T>
where
    T: FromBytes,
{
    let type_size = std::mem::size_of::<T>();

    if data.len() != type_size {
        return Err(Error::InvalidLength {
            expected: type_size,
            got: data.len(),
        });
    }

    T::read_from_bytes(data).map_err(|_| {
        Error::Deserialize(format!(
            "failed to convert bytes to {}",
            std::any::type_name::<T>()
        ))
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_zerocopy_u32_array() {
        let data: Vec<u8> = vec![1, 0, 0, 0, 2, 0, 0, 0, 3, 0, 0, 0];
        let result = zerocopy_array_impl::<u32>(&data).expect("zerocopy failed");
        assert_eq!(result, vec![1u32, 2, 3]);
    }

    #[test]
    fn test_zerocopy_u64_array() {
        let data: Vec<u8> = vec![1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0];
        let result = zerocopy_array_impl::<u64>(&data).expect("zerocopy failed");
        assert_eq!(result, vec![1u64, 2]);
    }

    #[test]
    fn test_zerocopy_invalid_length() {
        let data: Vec<u8> = vec![1, 0, 0]; // Not a multiple of 4
        let result = zerocopy_array_impl::<u32>(&data);
        assert!(result.is_err());
    }

    #[test]
    fn test_u32_from_bytes() {
        let data = 12345u32.to_le_bytes();
        let result = from_bytes_impl::<u32>(&data).expect("from_bytes failed");
        assert_eq!(result, 12345);
    }

    #[test]
    fn test_u64_from_bytes() {
        let data = 123456789012345u64.to_le_bytes();
        let result = from_bytes_impl::<u64>(&data).expect("from_bytes failed");
        assert_eq!(result, 123456789012345);
    }

    #[test]
    fn test_f32_from_bytes() {
        let expected = 3.14159f32;
        let data = expected.to_le_bytes();
        let result = from_bytes_impl::<f32>(&data).expect("from_bytes failed");
        assert!((result - expected).abs() < 1e-6);
    }

    #[test]
    fn test_f64_from_bytes() {
        let expected = std::f64::consts::PI;
        let data = expected.to_le_bytes();
        let result = from_bytes_impl::<f64>(&data).expect("from_bytes failed");
        assert!((result - expected).abs() < 1e-14);
    }

    #[test]
    fn test_from_bytes_invalid_length() {
        let data = vec![0u8, 0]; // Too short for u32
        let result = from_bytes_impl::<u32>(&data);
        assert!(result.is_err());
    }
}
