#!/bin/bash
# Setup script for Raspberry Pi 5

echo "=========================================="
echo "Setting up Raspberry Pi 5 for Hailo AI"
echo "=========================================="

# Update system
echo ""
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-opencv \
    python3-numpy \
    libopencv-dev \
    v4l-utils

# Install Hailo AI Software
echo ""
echo "Installing Hailo AI software..."
# Follow official Hailo installation guide
# https://github.com/hailo-ai/hailo-rpi5-examples

# Install Picamera2
echo ""
echo "Installing Picamera2..."
sudo apt-get install -y python3-picamera2

# Install Python requirements
echo ""
echo "Installing Python packages..."
pip3 install --upgrade pip
pip3 install opencv-python numpy

echo ""
echo "=========================================="
echo "Setup completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy HEF model to this device"
echo "2. Run: python3 step4_code_run_on_pi5.py"
echo ""
