#!/bin/bash
# Quick start script - Run all steps in sequence

echo "=========================================="
echo "YOLO Ear Detection - Complete Pipeline"
echo "=========================================="

# Check if we're on MacOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "This script is for MacOS only"
    echo "For Raspberry Pi, use setup_pi5.sh"
    exit 1
fi

# Step 0: Setup environment
echo ""
echo "Step 0: Setting up environment..."
if [ ! -d ".venv" ]; then
    chmod +x setup_macos.sh
    ./setup_macos.sh
fi

# Activate virtual environment
source .venv/bin/activate

# Step 1: Train model
echo ""
echo "=========================================="
echo "Step 1: Training YOLO model..."
echo "=========================================="
read -p "Start training? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python step1_train_model_to_pt.py
else
    echo "Skipping training..."
fi

# Step 2: Convert to ONNX
echo ""
echo "=========================================="
echo "Step 2: Converting .pt to .onnx..."
echo "=========================================="
read -p "Convert to ONNX? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python step2_file_pt_to_file_onnx.py
else
    echo "Skipping ONNX conversion..."
fi

# Step 3: Docker setup for HEF conversion
echo ""
echo "=========================================="
echo "Step 3: Docker setup for HEF conversion"
echo "=========================================="
echo ""
echo "To convert ONNX to HEF, run these commands:"
echo ""
echo "  cd docker"
echo "  docker-compose build"
echo "  docker-compose up -d"
echo "  docker-compose exec hailo-compiler bash"
echo "  python3 step3_file_onnx_to_file_hef.py"
echo "  exit"
echo "  docker-compose down"
echo ""

read -p "Setup Docker now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd docker
    echo "Building Docker image..."
    docker-compose build
    echo ""
    echo "Docker image built successfully!"
    echo ""
    echo "To convert ONNX to HEF:"
    echo "  docker-compose up -d"
    echo "  docker-compose exec hailo-compiler bash"
    echo "  python3 step3_file_onnx_to_file_hef.py"
    cd ..
else
    echo "Skipping Docker setup..."
fi

echo ""
echo "=========================================="
echo "Pipeline setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Convert ONNX to HEF using Docker"
echo "2. Copy HEF model to Raspberry Pi 5:"
echo "   scp models/hef/ear_detection.hef pi@raspberrypi:~/"
echo "3. Run inference on Pi5:"
echo "   python3 step4_code_run_on_pi5.py"
echo ""
