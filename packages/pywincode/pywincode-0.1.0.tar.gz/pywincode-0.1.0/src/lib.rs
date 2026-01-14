//! Python bindings for wincode serialization library with zerocopy support.
//!
//! This crate provides Python bindings using `PyO3` for the wincode serialization
//! library, along with zerocopy functionality for efficient memory access.

mod error;
mod primitives;
mod serialization;
mod zerocopy_ops;

use pyo3::prelude::*;

use error::WincodeError;
use primitives::{
    deserialize_bool, deserialize_f32, deserialize_f64, deserialize_i16, deserialize_i32,
    deserialize_i64, deserialize_i8, deserialize_u16, deserialize_u32, deserialize_u64,
    deserialize_u8, serialize_bool, serialize_f32, serialize_f64, serialize_i16, serialize_i32,
    serialize_i64, serialize_i8, serialize_u16, serialize_u32, serialize_u64, serialize_u8,
};
use serialization::{
    deserialize, deserialize_bytes_list, deserialize_string, deserialize_u64_list, serialize,
    serialize_bytes_list, serialize_into, serialize_string, serialize_u64_list, serialized_size,
};
use zerocopy_ops::{
    f32_from_bytes, f32_into_bytes, f64_from_bytes, f64_into_bytes, u32_from_bytes, u32_into_bytes,
    u64_from_bytes, u64_into_bytes, zerocopy_f32_array, zerocopy_f64_array, zerocopy_i16_array,
    zerocopy_i32_array, zerocopy_i64_array, zerocopy_i8_array, zerocopy_u16_array,
    zerocopy_u32_array, zerocopy_u64_array, zerocopy_u8_array, zerocopy_view,
};

/// Python module for pywincode.
///
/// Provides serialization/deserialization functions and zerocopy operations.
#[pymodule]
fn _pywincode(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Register error type
    m.add("WincodeError", m.py().get_type::<WincodeError>())?;

    // Core serialization functions
    m.add_function(wrap_pyfunction!(serialize, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize, m)?)?;
    m.add_function(wrap_pyfunction!(serialized_size, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_into, m)?)?;

    // Primitive serialization - unsigned integers
    m.add_function(wrap_pyfunction!(serialize_u8, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_u16, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_u32, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_u64, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_u8, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_u16, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_u32, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_u64, m)?)?;

    // Primitive serialization - signed integers
    m.add_function(wrap_pyfunction!(serialize_i8, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_i16, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_i32, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_i64, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_i8, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_i16, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_i32, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_i64, m)?)?;

    // Primitive serialization - floats
    m.add_function(wrap_pyfunction!(serialize_f32, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_f64, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_f32, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_f64, m)?)?;

    // Primitive serialization - bool
    m.add_function(wrap_pyfunction!(serialize_bool, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_bool, m)?)?;

    // String serialization
    m.add_function(wrap_pyfunction!(serialize_string, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_string, m)?)?;

    // List serialization
    m.add_function(wrap_pyfunction!(serialize_bytes_list, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_bytes_list, m)?)?;
    m.add_function(wrap_pyfunction!(serialize_u64_list, m)?)?;
    m.add_function(wrap_pyfunction!(deserialize_u64_list, m)?)?;

    // Zerocopy operations
    m.add_function(wrap_pyfunction!(zerocopy_view, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_u8_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_u16_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_u32_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_u64_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_i8_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_i16_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_i32_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_i64_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_f32_array, m)?)?;
    m.add_function(wrap_pyfunction!(zerocopy_f64_array, m)?)?;

    // From/Into bytes operations
    m.add_function(wrap_pyfunction!(u32_from_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(u64_from_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(f32_from_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(f64_from_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(u32_into_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(u64_into_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(f32_into_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(f64_into_bytes, m)?)?;

    Ok(())
}
