# association
I am not associated with the wincode or bincode teams.
I am just a fan who needs to use it in python and wants to give others the ability to do the same.
If there are any adjustments that you feel need to be made then go to [wincode](https://github.com/anza-xyz/wincode)

# pywincode

Python bindings for the [wincode](https://crates.io/crates/wincode) Rust serialization library with [zerocopy](https://crates.io/crates/zerocopy) support.

## What is pywincode?

pywincode provides fast binary serialization and deserialization for Python, powered by Rust. It wraps the wincode library (a fast bincode implementation with placement initialization) and adds zerocopy functionality for efficient memory access without copying data.

### Key Features

- **Fast serialization**: Rust-powered binary serialization compatible with bincode format
- **Zero-copy arrays**: Access binary data as typed arrays without memory copies
- **Type-safe**: Explicit serialization functions for all primitive types
- **NumPy compatible**: Zero-copy arrays work seamlessly with NumPy

## Installation

```bash
pip install pywincode
```

### From Source

```bash
# Clone the repository
git clone https://github.com/LecherousCthulhu/pywincode.git
cd pywincode

# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
# or: source .venv/bin/activate  # Linux/macOS

# Install with maturin
pip install maturin
maturin develop --release
```

## Quick Start

### Basic Serialization

```python
import pywincode

# Serialize bytes
data = b"hello world"
serialized = pywincode.serialize(data)
deserialized = pywincode.deserialize(serialized)
assert deserialized == data
```

### Primitive Types

```python
import pywincode

# Integers
serialized = pywincode.serialize_u64(12345678)
value = pywincode.deserialize_u64(serialized)

# Floats
serialized = pywincode.serialize_f64(3.14159)
value = pywincode.deserialize_f64(serialized)

# Strings
serialized = pywincode.serialize_string("hello")
text = pywincode.deserialize_string(serialized)
```

### Zero-Copy Arrays

```python
import struct
import pywincode

# Create binary data (10 u32 values)
values = list(range(10))
data = struct.pack(f"<{len(values)}I", *values)

# Get zero-copy view as u32 array
arr = pywincode.zerocopy_u32_array(data)
print(list(arr))  # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Works with NumPy
import numpy as np
np_arr = np.asarray(arr)
print(np_arr.dtype)  # uint32
```

### Lists

```python
import pywincode

# Serialize list of bytes
items = [b"hello", b"world"]
serialized = pywincode.serialize_bytes_list(items)
result = pywincode.deserialize_bytes_list(serialized)

# Serialize list of u64
numbers = [1, 2, 3, 1000000]
serialized = pywincode.serialize_u64_list(numbers)
result = pywincode.deserialize_u64_list(serialized)
```

## API Reference

### Core Functions

| Function | Description |
|----------|-------------|
| `serialize(data: bytes) -> bytes` | Serialize bytes to wincode format |
| `deserialize(data: bytes) -> bytes` | Deserialize bytes from wincode format |
| `serialized_size(data: bytes) -> int` | Get serialized size without serializing |
| `serialize_into(data: bytes, buffer: bytearray) -> int` | Serialize into pre-allocated buffer |

### Primitive Serialization

**Unsigned integers**: `serialize_u8`, `serialize_u16`, `serialize_u32`, `serialize_u64`
**Signed integers**: `serialize_i8`, `serialize_i16`, `serialize_i32`, `serialize_i64`
**Floats**: `serialize_f32`, `serialize_f64`
**Boolean**: `serialize_bool`
**String**: `serialize_string`

Each has a corresponding `deserialize_*` function.

### Zero-Copy Operations

| Function | Description |
|----------|-------------|
| `zerocopy_view(data: bytes) -> memoryview` | Create read-only view of bytes |
| `zerocopy_u8_array(data: bytes) -> list[int]` | View bytes as u8 array |
| `zerocopy_u16_array(data: bytes) -> list[int]` | View bytes as u16 array |
| `zerocopy_u32_array(data: bytes) -> list[int]` | View bytes as u32 array |
| `zerocopy_u64_array(data: bytes) -> list[int]` | View bytes as u64 array |
| `zerocopy_i8_array(data: bytes) -> list[int]` | View bytes as i8 array |
| `zerocopy_i16_array(data: bytes) -> list[int]` | View bytes as i16 array |
| `zerocopy_i32_array(data: bytes) -> list[int]` | View bytes as i32 array |
| `zerocopy_i64_array(data: bytes) -> list[int]` | View bytes as i64 array |
| `zerocopy_f32_array(data: bytes) -> list[float]` | View bytes as f32 array |
| `zerocopy_f64_array(data: bytes) -> list[float]` | View bytes as f64 array |

### Type Conversions

| Function | Description |
|----------|-------------|
| `u32_from_bytes(data: bytes) -> int` | Convert 4 bytes to u32 |
| `u64_from_bytes(data: bytes) -> int` | Convert 8 bytes to u64 |
| `f32_from_bytes(data: bytes) -> float` | Convert 4 bytes to f32 |
| `f64_from_bytes(data: bytes) -> float` | Convert 8 bytes to f64 |
| `u32_into_bytes(value: int) -> bytes` | Convert u32 to 4 bytes |
| `u64_into_bytes(value: int) -> bytes` | Convert u64 to 8 bytes |
| `f32_into_bytes(value: float) -> bytes` | Convert f32 to 4 bytes |
| `f64_into_bytes(value: float) -> bytes` | Convert f64 to 8 bytes |

## Error Handling

All functions may raise `pywincode.WincodeError` on failure:

```python
import pywincode

try:
    pywincode.deserialize(b"\xff\xff\xff\xff")
except pywincode.WincodeError as e:
    print(f"Deserialization failed: {e}")
```

## Development

### Prerequisites

- Python 3.10+
- Rust 1.85+
- maturin

### Building

```bash
# Windows
.\scripts\run_all.ps1

# Linux/macOS
./scripts/run_all.sh
```

### Running Tests

```bash
# Rust tests
cargo test

# Python tests
python -m pytest tests/ -v
```

## License

MIT License - see [LICENSE](LICENSE) for details.
