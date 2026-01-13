#!/bin/bash
# Build rust_ml wheels for all supported platforms

set -e  # Exit on error

echo "========================================="
echo "Building rust_ml for All Platforms"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine script directory and move there
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $(pwd)"

# Find maturin executable
if command -v maturin &> /dev/null; then
    MATURIN_CMD="maturin"
elif [ -f "../.venv/bin/maturin" ]; then
    MATURIN_CMD="../.venv/bin/maturin"
else
    echo "Error: maturin not found in PATH or ../.venv/bin/maturin"
    exit 1
fi

echo "Using maturin: $MATURIN_CMD"

# Create output directory for extracted binaries
# Now relative to the project root (parent of rust_ml)
mkdir -p ../binaries
OUTPUT_DIR="../binaries"

# Function to extract binary from wheel
extract_binary() {
    local wheel_file=$1
    local target_name=$2
    local output_dir_abs=$3

    echo -e "${BLUE}Extracting binary from $wheel_file...${NC}"

    # Convert to absolute path before changing directory
    wheel_file_abs="$(cd "$(dirname "$wheel_file")" && pwd)/$(basename "$wheel_file")"

    # Create temp directory
    temp_dir=$(mktemp -d)
    cd "$temp_dir"

    # Extract wheel
    unzip -q "$wheel_file_abs"

    # Find the .so or .pyd file (rust_ml module)
    binary=$(find . -name "rust_ml*.so" -o -name "rust_ml*.pyd" | head -n 1)

    if [ -z "$binary" ]; then
        echo "Error: No binary found in wheel"
        exit 1
    fi

    # Copy to output directory
    cp "$binary" "$output_dir_abs/rust_ml_$target_name"

    # Cleanup
    cd - > /dev/null
    rm -rf "$temp_dir"

    echo -e "${GREEN}✓ Copied to $output_dir_abs/rust_ml_$target_name${NC}"
}

# Get absolute path to output directory
OUTPUT_DIR_ABS="$(cd .. && pwd)/binaries"

# Build for current platform first
echo -e "\n${BLUE}Building for current platform...${NC}"
$MATURIN_CMD build --release --strip

# Detect current platform
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CURRENT_PLATFORM="linux_x86_64.so"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if [[ $(uname -m) == "arm64" ]]; then
        CURRENT_PLATFORM="macos_aarch64.so"
    else
        CURRENT_PLATFORM="macos_x86_64.so"
    fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    CURRENT_PLATFORM="windows_x86_64.pyd"
fi

# Extract current platform binary
wheel=$(ls -t target/wheels/*.whl | head -n 1)
extract_binary "$wheel" "$CURRENT_PLATFORM" "$OUTPUT_DIR_ABS"

# Try to build for other platforms using Docker/Podman (if available)
CONTAINER_CMD=""
if command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    echo -e "\n${BLUE}Docker detected. Building for Linux platforms...${NC}"
elif command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    echo -e "\n${BLUE}Podman detected. Building for Linux platforms...${NC}"
fi

if [ -n "$CONTAINER_CMD" ]; then
    # Linux x86_64
    echo -e "\n${BLUE}Building for Linux x86_64...${NC}"
    $CONTAINER_CMD run --rm -v "$(pwd)":/io:Z ghcr.io/pyo3/maturin build --release --strip || {
        echo "⚠ Container build failed for Linux x86_64, skipping..."
    }

    if [ -f target/wheels/*manylinux*_x86_64.whl ]; then
        wheel=$(ls -t target/wheels/*manylinux*_x86_64.whl | head -n 1)
        extract_binary "$wheel" "linux_x86_64.so" "$OUTPUT_DIR_ABS"
    fi

    # Linux aarch64
    echo -e "\n${BLUE}Building for Linux aarch64...${NC}"
    $CONTAINER_CMD run --rm -v "$(pwd)":/io:Z ghcr.io/pyo3/maturin build --release --strip --target aarch64-unknown-linux-gnu || {
        echo "⚠ Container build failed for Linux aarch64, skipping..."
    }

    if [ -f target/wheels/*manylinux*_aarch64.whl ]; then
        wheel=$(ls -t target/wheels/*manylinux*_aarch64.whl | head -n 1)
        extract_binary "$wheel" "linux_aarch64.so" "$OUTPUT_DIR_ABS"
    fi
else
    echo "⚠ Docker/Podman not available, skipping Linux cross-compilation"
fi

# Instructions for other platforms
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}Build Summary${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo "Wheels built in target/wheels/:"
ls -lh target/wheels/*.whl 2>/dev/null || echo "No wheels found"
echo ""
echo "Extracted binaries in $OUTPUT_DIR:"
ls -lh "$OUTPUT_DIR"/rust_ml_* 2>/dev/null || echo "No binaries extracted"
echo ""
echo "To build for additional platforms:"
echo ""
echo "macOS x86_64:"
echo "  maturin build --release --strip --target x86_64-apple-darwin"
echo ""
echo "macOS aarch64 (M1/M2/M3):"
echo "  maturin build --release --strip --target aarch64-apple-darwin"
echo ""
echo "Windows x86_64:"
echo "  maturin build --release --strip --target x86_64-pc-windows-msvc"
echo ""
echo -e "${GREEN}Done! Wheels are in target/wheels/${NC}"
