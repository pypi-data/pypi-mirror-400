//! Error types for pywincode.
//!
//! This module defines the error types used throughout the library,
//! with proper conversion to Python exceptions.

use pyo3::create_exception;
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use thiserror::Error;

// Create a custom Python exception for wincode errors
create_exception!(pywincode, WincodeError, PyException);

/// Internal error type for wincode operations.
#[derive(Error, Debug)]
pub enum Error {
    /// Serialization failed.
    #[error("serialization error: {0}")]
    Serialize(String),

    /// Deserialization failed.
    #[error("deserialization error: {0}")]
    Deserialize(String),

    /// Buffer too small for serialization.
    #[error("buffer too small: need {needed} bytes, got {got}")]
    BufferTooSmall { needed: usize, got: usize },

    /// Invalid data length for zerocopy operation.
    #[error("invalid data length: expected {expected} bytes, got {got}")]
    InvalidLength { expected: usize, got: usize },

    /// Alignment issue for zerocopy operation.
    #[error("alignment error: data not aligned to {alignment} bytes")]
    Alignment { alignment: usize },

    /// Invalid UTF-8 string.
    #[error("invalid UTF-8: {0}")]
    InvalidUtf8(String),
}

impl From<Error> for PyErr {
    fn from(err: Error) -> Self {
        WincodeError::new_err(err.to_string())
    }
}

/// Result type alias for wincode operations.
pub type Result<T> = std::result::Result<T, Error>;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let err = Error::Serialize("test error".to_string());
        assert!(err.to_string().contains("serialization error"));
        assert!(err.to_string().contains("test error"));
    }

    #[test]
    fn test_buffer_too_small_display() {
        let err = Error::BufferTooSmall {
            needed: 100,
            got: 50,
        };
        assert!(err.to_string().contains("100"));
        assert!(err.to_string().contains("50"));
    }

    #[test]
    fn test_invalid_length_display() {
        let err = Error::InvalidLength {
            expected: 8,
            got: 4,
        };
        assert!(err.to_string().contains("8"));
        assert!(err.to_string().contains("4"));
    }
}
