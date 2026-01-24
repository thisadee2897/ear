# YOLO Ear Detection Pipeline
Complete workflow for training YOLO model and deploying on Raspberry Pi 5 + Hailo AI Kit

## Overview
This project provides a complete pipeline for:
1. Training a YOLO model for ear detection on MacOS
2. Converting the model to ONNX format
3. Compiling the model to Hailo HEF format using Docker
4. Running real-time inference on Raspberry Pi 5 with Hailo AI Kit

## Project Structure
```
.
├── step1_train_model_to_pt.py      # Train YOLO model (MacOS)
├── step2_file_pt_to_file_onnx.py   # Convert .pt to .onnx
├── step3_file_onnx_to_file_hef.py  # Convert .onnx to .hef (Docker)
├── step4_code_run_on_pi5.py        # Run inference on Pi5
├── docker/                          # Docker setup for Hailo compiler
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── data.yaml                        # Dataset configuration
├── requirements.txt                 # Python dependencies
├── setup_macos.sh                   # MacOS setup script
└── setup_pi5.sh                     # Raspberry Pi setup script
```

## Step-by-Step Guide

### Step 1: Setup MacOS Environment (Training)

```bash
# Make setup script executable
chmod +x setup_macos.sh

# Run setup
./setup_macos.sh

# Activate virtual environment
source .venv/bin/activate
```

### Step 2: Train YOLO Model

```bash
# Train model
python step1_train_model_to_pt.py

# Model will be saved to: runs/train/ear_detection/weights/best.pt
```

**Training Configuration:**
- Model: YOLOv8n (nano) - can be changed to s, m, l, x
- Epochs: 100
- Image Size: 640x640
- Device: Apple Silicon GPU (MPS) or CPU

### Step 3: Convert to ONNX

```bash
# Convert .pt to .onnx
python step2_file_pt_to_file_onnx.py

# Model will be saved to: models/onnx/best_simplified.onnx
```

### Step 4: Setup Docker for Hailo Compiler

```bash
# Navigate to docker directory
cd docker

# Build Docker image
docker-compose build

# Start container
docker-compose up -d

# Enter container
docker-compose exec hailo-compiler bash
```

### Step 5: Convert ONNX to HEF (Inside Docker)

```bash
# Inside Docker container
python3 step3_file_onnx_to_file_hef.py

# Model will be saved to: models/hef/ear_detection.hef

# Exit container
exit

# Stop container
docker-compose down
```

### Step 6: Deploy to Raspberry Pi 5

**On MacOS:**
```bash
# Copy HEF model to Raspberry Pi
scp models/hef/ear_detection.hef pi@raspberrypi:~/

# Copy inference script
scp step4_code_run_on_pi5.py pi@raspberrypi:~/

# Copy setup script
scp setup_pi5.sh pi@raspberrypi:~/
```

**On Raspberry Pi 5:**
```bash
# Make setup script executable
chmod +x setup_pi5.sh

# Run setup
./setup_pi5.sh

# Run inference
python3 step4_code_run_on_pi5.py
```

## Hardware Requirements

### MacOS (Training)
- Mac with Apple Silicon (M1/M2/M3) or Intel CPU
- 8GB+ RAM recommended
- 10GB+ free disk space

### Raspberry Pi 5 (Inference)
- Raspberry Pi 5 (4GB or 8GB)
- Hailo AI Kit (13 TOPS) - HAT AI module
- Picamera2 compatible camera
- MicroSD card (32GB+ recommended)
- Power supply (5V, 5A recommended)

## Performance

### Training (MacOS M1/M2)
- ~2-3 hours for 100 epochs (depending on dataset size)
- Apple Silicon GPU acceleration supported

### Inference (Raspberry Pi 5 + Hailo)
- ~30-60 FPS at 640x640 resolution
- Real-time performance with camera input

## Dataset Format

The project uses YOLO format:
```
train/
  images/
    image1.jpg
  labels/
    image1.txt
valid/
  images/
  labels/
test/
  images/
  labels/
```

Label format (YOLO):
```
class_id x_center y_center width height
```

All coordinates are normalized (0-1).

## Troubleshooting

### MacOS Training Issues
1. **MPS not available**: Falls back to CPU automatically
2. **Out of memory**: Reduce batch size in `step1_train_model_to_pt.py`
3. **Slow training**: Use smaller model (yolov8n) or reduce image size

### Docker Issues
1. **Build fails**: Ensure Docker has enough resources (4GB+ RAM)
2. **Container won't start**: Check if ports are available
3. **Permission issues**: Run with `sudo` if needed

### Raspberry Pi Issues
1. **Camera not detected**: Check Picamera2 installation and camera connection
2. **Hailo not found**: Install Hailo software from official repository
3. **Slow inference**: Check if Hailo driver is loaded properly

## Configuration

### Modify Training Parameters
Edit `step1_train_model_to_pt.py`:
```python
MODEL_SIZE = 'yolov8n.pt'  # Change to yolov8s, yolov8m, etc.
EPOCHS = 100               # Adjust number of epochs
BATCH = 16                 # Adjust batch size
IMGSZ = 640               # Adjust image size
```

### Modify Detection Parameters
Edit `step4_code_run_on_pi5.py`:
```python
CONF_THRESHOLD = 0.25  # Confidence threshold
IOU_THRESHOLD = 0.45   # IoU threshold for NMS
```

## References

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [Hailo AI](https://hailo.ai/)
- [Hailo RPi5 Examples](https://github.com/hailo-ai/hailo-rpi5-examples)
- [Picamera2](https://github.com/raspberrypi/picamera2)

## License

This project follows the licenses of its dependencies:
- Ultralytics YOLOv8: AGPL-3.0
- Hailo Dataflow Compiler: Check Hailo license
- Dataset: CC BY 4.0 (as specified in data.yaml)

## Support

For issues and questions:
1. Check troubleshooting section
2. Review official documentation
3. Open an issue on GitHub

---

**Note**: This pipeline is designed for Raspberry Pi 5 with Hailo AI Kit (13 TOPS). For other hardware, modifications may be needed.
