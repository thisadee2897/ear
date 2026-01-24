# Dockerfile for Hailo Dataflow Compiler
FROM ubuntu:20.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.8 \
    python3-pip \
    python3-dev \
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

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Set working directory
WORKDIR /workspace

# Copy the Hailo dataflow compiler wheel file
COPY hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl /tmp/

# Install Hailo Dataflow Compiler
RUN pip3 install /tmp/hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl

# Install additional Python packages for model conversion
RUN pip3 install \
    onnx==1.15.0 \
    onnxruntime==1.16.3 \
    numpy==1.24.3 \
    pillow \
    pyyaml \
    tqdm

# Set Python3 as default
RUN ln -s /usr/bin/python3 /usr/bin/python

# Default command
CMD ["/bin/bash"]
