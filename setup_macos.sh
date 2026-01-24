#!/bin/bash
# Setup script for MacOS - Train YOLO model

echo "=========================================="
echo "Setting up YOLO Training Environment"
echo "=========================================="

# Check Python version
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing requirements..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Setup completed!"
echo "=========================================="
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To train the model:"
echo "  python step1_train_model_to_pt.py"
echo ""
