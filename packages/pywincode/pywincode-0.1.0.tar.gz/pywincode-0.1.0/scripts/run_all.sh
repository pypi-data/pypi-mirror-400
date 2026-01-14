#!/usr/bin/env bash
# Run all builds, tests, and smoke checks for pywincode
set -euo pipefail

echo "[run_all] Verifying toolchains..."
cargo --version
python --version || python3 --version

echo "[run_all] Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python -m venv .venv || python3 -m venv .venv
fi
. .venv/bin/activate
python -m pip install --upgrade pip

echo "[run_all] Installing maturin..."
python -m pip install maturin[patchelf]

echo "[run_all] Building Rust library..."
cargo build --release
cargo test --release

echo "[run_all] Building Python wheel with maturin..."
maturin develop --release

echo "[run_all] Installing test dependencies..."
python -m pip install pytest pytest-cov hypothesis

echo "[run_all] Running Python tests..."
python -m pytest tests/ -v

echo "[run_all] Running smoke test..."
python -c "
import pywincode
data = b'hello world'
serialized = pywincode.serialize(data)
deserialized = pywincode.deserialize(serialized)
assert deserialized == data, 'Roundtrip failed'
print('Smoke test passed!')
"

echo "[run_all] Linting Rust code..."
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings

echo "[run_all] All checks passed!"
