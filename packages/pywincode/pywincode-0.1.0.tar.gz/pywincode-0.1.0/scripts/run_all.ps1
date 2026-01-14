# scripts/run_all.ps1
# Run all builds, tests, and smoke checks for pywincode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "[run_all] Verifying toolchains..."
cargo --version
py --version

Write-Host "[run_all] Setting up Python virtual environment..."
if (-not (Test-Path ".\.venv")) {
    py -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

Write-Host "[run_all] Installing maturin..."
python -m pip install maturin

Write-Host "[run_all] Building Rust library..."
cargo build --release
if ($LASTEXITCODE -ne 0) { throw "Cargo build failed" }

cargo test --release
if ($LASTEXITCODE -ne 0) { throw "Cargo test failed" }

Write-Host "[run_all] Building Python wheel with maturin..."
maturin develop --release
if ($LASTEXITCODE -ne 0) { throw "Maturin develop failed" }

Write-Host "[run_all] Installing test dependencies..."
python -m pip install pytest pytest-cov hypothesis

Write-Host "[run_all] Running Python tests..."
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) { throw "Python tests failed" }

Write-Host "[run_all] Running smoke test..."
$smokeTest = @"
import pywincode
data = b'hello world'
serialized = pywincode.serialize(data)
deserialized = pywincode.deserialize(serialized)
assert deserialized == data, 'Roundtrip failed'
print('Smoke test passed!')
"@
python -c $smokeTest
if ($LASTEXITCODE -ne 0) { throw "Smoke test failed" }

Write-Host "[run_all] Linting Rust code..."
cargo fmt --all -- --check
if ($LASTEXITCODE -ne 0) { throw "Cargo fmt check failed" }

cargo clippy --all-targets --all-features -- -D warnings
if ($LASTEXITCODE -ne 0) { throw "Clippy failed" }

Write-Host "[run_all] All checks passed!"
