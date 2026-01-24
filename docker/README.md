# Docker Setup for Hailo Dataflow Compiler

This Docker environment is used for converting ONNX models to Hailo HEF format.

## Prerequisites
- Docker installed on your system
- Docker Compose installed

## Build and Run

### Build the Docker image:
```bash
cd /Users/mac/Documents/project/ear/docker
docker-compose build
```

### Start the container:
```bash
docker-compose up -d
```

### Enter the container:
```bash
docker-compose exec hailo-compiler bash
```

### Run the ONNX to HEF conversion inside container:
```bash
python3 step3_file_onnx_to_file_hef.py
```

### Stop the container:
```bash
docker-compose down
```

## File Structure
- `Dockerfile`: Defines the Docker image with Hailo Dataflow Compiler
- `docker-compose.yml`: Docker Compose configuration
- `../hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl`: Hailo compiler wheel file

## Notes
- The workspace is mounted at `/workspace` inside the container
- All files from the parent directory are accessible
- Hailo cache is stored in a Docker volume for persistence
