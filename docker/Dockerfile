# Dockerfile for Hailo Dataflow Compiler
FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
    python3-dev \
    python3-distutils \
    build-essential \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN python3 -m pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /workspace

# Copy the Hailo dataflow compiler wheel file
COPY hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl /tmp/

# Install Hailo Dataflow Compiler with --force-reinstall and --no-deps flags
# Then install dependencies separately
RUN pip3 install --force-reinstall --no-deps /tmp/hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl || \
    echo "Warning: Hailo compiler installation may have issues. Installing dependencies..." && \
    pip3 install \
    numpy==1.23.5 \
    protobuf==3.20.3 \
    onnx==1.14.1 \
    onnxruntime==1.15.1 \
    tensorflow==2.12.0 \
    h5py==3.8.0 \
    pillow \
    pyyaml \
    tqdm \
    scipy \
    matplotlib

# Install additional Python packages for model conversion (if Hailo installed)
RUN pip3 install --no-cache-dir \
    opencv-python-headless || true

# Try to install Hailo SDK Client after all dependencies
RUN pip3 install --upgrade --force-reinstall --no-deps /tmp/hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl || \
    echo "Hailo Dataflow Compiler may need manual installation"

# Set Python3 as default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Create a script to check Hailo installation
RUN echo '#!/bin/bash\n\
echo "Checking Hailo installation..."\n\
python3 -c "import sys; print(f\"Python: {sys.version}\")" || true\n\
python3 -c "try:\n    import hailo_sdk_client\n    print(\"✓ Hailo SDK Client installed\")\nexcept:\n    print(\"⚠ Hailo SDK Client not found - manual installation may be required\")" || true\n\
' > /usr/local/bin/check-hailo.sh && chmod +x /usr/local/bin/check-hailo.sh

# Default command
CMD ["/bin/bash"]
