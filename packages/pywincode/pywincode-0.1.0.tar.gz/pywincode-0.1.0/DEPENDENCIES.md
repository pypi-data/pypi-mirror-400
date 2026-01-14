# Dependencies

This document lists all dependencies required for pywincode.

## System Requirements

### Rust Toolchain

- **Rust**: >= 1.85 (edition 2024)
- **Cargo**: Latest stable

Install Rust via [rustup](https://rustup.rs/):

```bash
# Linux/macOS
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Windows
# Download and run rustup-init.exe from https://rustup.rs/
```

### Python

- **Python**: >= 3.10

## Rust Dependencies

| Crate | Version | Purpose |
|-------|---------|---------|
| `pyo3` | 0.23 | Python bindings for Rust |
| `wincode` | 0.2 | Fast bincode serialization with placement initialization |
| `zerocopy` | 0.8 | Zero-copy type conversions |
| `thiserror` | 2.0 | Ergonomic error handling |

### Dev Dependencies (Rust)

| Crate | Version | Purpose |
|-------|---------|---------|
| `proptest` | 1.5 | Property-based testing |

## Python Dependencies

### Build Dependencies

```bash
# Using pip (in virtual environment)
python -m pip install maturin>=1.7

# Using uv
uv pip install maturin>=1.7
```

### Runtime Dependencies

The package has no runtime Python dependencies - it's a pure Rust extension.

### Development Dependencies

```bash
# Using pip (in virtual environment)
python -m pip install pytest>=8.0 pytest-cov>=4.0 hypothesis>=6.0 mypy>=1.0 ruff>=0.8

# Using uv
uv pip install pytest>=8.0 pytest-cov>=4.0 hypothesis>=6.0 mypy>=1.0 ruff>=0.8

# Or install all dev dependencies at once
python -m pip install pywincode[dev]
```

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | >= 8.0 | Test framework |
| `pytest-cov` | >= 4.0 | Coverage reporting |
| `hypothesis` | >= 6.0 | Property-based testing |
| `mypy` | >= 1.0 | Static type checking |
| `ruff` | >= 0.8 | Linting and formatting |

### Optional Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | >= 1.20 | NumPy array compatibility |

## Installation Commands

### Development Setup (Windows PowerShell)

```powershell
# Create virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# Install maturin
python -m pip install maturin

# Build and install in development mode
maturin develop --release

# Install test dependencies
python -m pip install pytest pytest-cov hypothesis mypy ruff
```

### Development Setup (Linux/macOS)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip

# Install maturin
python -m pip install maturin

# Build and install in development mode
maturin develop --release

# Install test dependencies
python -m pip install pytest pytest-cov hypothesis mypy ruff
```

### Production Build

```bash
# Build wheel
maturin build --release

# The wheel will be in target/wheels/
```

## Lockfile Guidance

### Rust

Use `Cargo.lock` for reproducible builds:

```bash
# Generate/update lockfile
cargo update

# Build with locked dependencies
cargo build --locked
```

### Python

For development, you can use `pip freeze` to capture versions:

```bash
python -m pip freeze > requirements-dev.txt
```

Or use `uv` for lockfile management:

```bash
uv lock
uv sync
```

## Security Auditing

### Rust Dependencies

```bash
# Install cargo-audit
cargo install cargo-audit

# Run audit
cargo audit

# Install cargo-deny for comprehensive checks
cargo install cargo-deny

# Run deny
cargo deny check
```

### Python Dependencies

```bash
# Using pip-audit
python -m pip install pip-audit
pip-audit

# Using safety
python -m pip install safety
safety check
```
