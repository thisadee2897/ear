# Docker Setup for Hailo Dataflow Compiler

This Docker environment is used for converting ONNX models to Hailo HEF format.

## Prerequisites
- Docker installed on your system
- Docker Compose installed
- Hailo Dataflow Compiler wheel file: `hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl`

## Important Notes

⚠️ **Known Issue**: The Hailo Dataflow Compiler wheel may not install automatically due to platform compatibility. This is normal and can be fixed inside the container.

## Build and Run

### 1. Build the Docker image:
```bash
cd /Users/mac/Documents/project/ear/docker
docker-compose build
```

**Note**: Build may show warnings about Hailo installation. This is expected.

### 2. Start the container:
```bash
docker-compose up -d
```

### 3. Enter the container:
```bash
docker-compose exec hailo-compiler bash
```

### 4. Inside the container - Setup Hailo (if needed):

Check if Hailo is installed:
```bash
python3 -c "import hailo_sdk_client; print('Hailo OK')"
```

If not installed, run the setup script:
```bash
chmod +x docker/setup_hailo.sh
./docker/setup_hailo.sh
```

### 5. Run the ONNX to HEF conversion:
```bash
python3 step3_file_onnx_to_file_hef.py
```

### 6. Exit and stop the container:
```bash
exit
docker-compose down
```

## Alternative: Manual Installation Inside Container

If automatic installation fails:

```bash
# Enter container
docker-compose exec hailo-compiler bash

# Install dependencies
pip3 install numpy==1.23.5 protobuf==3.20.3 onnx==1.14.1 onnxruntime==1.15.1

# Try installing Hailo
pip3 install --force-reinstall --no-deps /tmp/hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl

# Verify
python3 -c "import hailo_sdk_client"
```

## Troubleshooting

### Issue: "not a supported wheel on this platform"

**Cause**: Python version or platform mismatch

**Solutions**:
1. The wheel file may be for a different Python version
2. Try running `./docker/setup_hailo.sh` inside the container
3. Contact Hailo support for the correct wheel file for your platform

### Issue: Docker build fails with memory error

**Solution**: Increase Docker memory:
- Docker Desktop → Settings → Resources → Memory: 4GB+

### Issue: Cannot access files inside container

**Solution**: The parent directory is mounted at `/workspace`
```bash
# Inside container
ls /workspace
cd /workspace
```

### Issue: Hailo SDK not found after installation

**Solution**: Check Python path and reinstall dependencies:
```bash
python3 -m pip list | grep hailo
pip3 install --upgrade /tmp/hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl
```

## File Structure

```
docker/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── setup_hailo.sh         # Hailo installation script
└── README.md              # This file
```

## Useful Commands

```bash
# Rebuild image (after changing Dockerfile)
docker-compose build --no-cache

# View container logs
docker-compose logs -f

# Check container status
docker-compose ps

# Remove everything and start fresh
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Notes

- The workspace is mounted at `/workspace` inside the container
- All files from the parent directory are accessible
- Hailo cache is stored in a Docker volume for persistence
- Python 3.8 is used for compatibility with Hailo SDK

## Getting Help

If you continue to have issues:

1. Check the Hailo Developer Zone: https://hailo.ai/developer-zone/
2. Verify you have the correct wheel file for Ubuntu 20.04 + Python 3.8
3. Try the manual installation steps above
4. Contact Hailo support with your specific error messages

## Alternative: Use Hailo Model Zoo

If the Dataflow Compiler installation fails, consider using Hailo's pre-compiled models or the Hailo Model Zoo tools which may have better installation support.
