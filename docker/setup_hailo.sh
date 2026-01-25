#!/bin/bash
# Setup script to install Hailo Dataflow Compiler inside Docker container
# Run this inside the container if the automatic installation fails

echo "=========================================="
echo "Hailo Dataflow Compiler Setup"
echo "=========================================="

# Check Python version
echo ""
echo "Python version:"
python3 --version

# Check pip version
echo ""
echo "Pip version:"
pip3 --version

# Check if wheel file exists
WHEEL_FILE="/tmp/hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl"
if [ ! -f "$WHEEL_FILE" ]; then
    echo ""
    echo "❌ Wheel file not found: $WHEEL_FILE"
    echo "Please ensure the wheel file is copied to the container"
    exit 1
fi

echo ""
echo "✓ Wheel file found: $WHEEL_FILE"

# Install dependencies first
echo ""
echo "Installing dependencies..."
pip3 install --upgrade pip setuptools wheel

pip3 install \
    numpy==1.23.5 \
    protobuf==3.20.3 \
    onnx==1.14.1 \
    onnxruntime==1.15.1 \
    h5py==3.8.0 \
    pillow \
    pyyaml \
    tqdm \
    scipy \
    matplotlib

# Try different installation methods
echo ""
echo "=========================================="
echo "Attempting Hailo Compiler Installation"
echo "=========================================="

# Method 1: Direct install
echo ""
echo "Method 1: Direct installation..."
if pip3 install "$WHEEL_FILE"; then
    echo "✓ Installation successful!"
else
    echo "⚠ Method 1 failed, trying Method 2..."
    
    # Method 2: Force reinstall with no deps
    echo ""
    echo "Method 2: Force reinstall without dependencies..."
    if pip3 install --force-reinstall --no-deps "$WHEEL_FILE"; then
        echo "✓ Installation successful!"
    else
        echo "⚠ Method 2 failed, trying Method 3..."
        
        # Method 3: Unzip and install manually
        echo ""
        echo "Method 3: Manual extraction..."
        cd /tmp
        unzip -q "$WHEEL_FILE" -d hailo_extracted || true
        
        if [ -d "hailo_extracted" ]; then
            cd hailo_extracted
            if [ -f "setup.py" ]; then
                python3 setup.py install
            else
                echo "⚠ setup.py not found in extracted files"
            fi
        fi
    fi
fi

# Verify installation
echo ""
echo "=========================================="
echo "Verifying Installation"
echo "=========================================="

python3 << 'EOF'
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

try:
    import hailo_sdk_client
    print("✓ Hailo SDK Client is installed")
    print(f"  Version: {hailo_sdk_client.__version__ if hasattr(hailo_sdk_client, '__version__') else 'unknown'}")
except ImportError as e:
    print("❌ Hailo SDK Client not found")
    print(f"  Error: {e}")
    print()
    print("You may need to:")
    print("  1. Check the wheel file is for the correct Python version")
    print("  2. Download the correct wheel from Hailo Developer Zone")
    print("  3. Contact Hailo support for assistance")
EOF

echo ""
echo "=========================================="
echo "Setup Complete"
echo "=========================================="
echo ""
echo "If Hailo SDK Client is installed, you can now run:"
echo "  python3 step3_file_onnx_to_file_hef.py"
echo ""
