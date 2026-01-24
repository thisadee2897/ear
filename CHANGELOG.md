# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-01-25

### Added
- ✅ Complete YOLO training pipeline for MacOS
- ✅ Step 1: Train YOLO model with Ultralytics (Apple Silicon support)
- ✅ Step 2: Convert PyTorch (.pt) to ONNX format
- ✅ Step 3: Convert ONNX to Hailo HEF format (Docker)
- ✅ Step 4: Real-time inference on Raspberry Pi 5 with Picamera2
- ✅ Docker environment for Hailo Dataflow Compiler
- ✅ Setup scripts for MacOS and Raspberry Pi 5
- ✅ Comprehensive documentation (English & Thai)
- ✅ Quick start guide
- ✅ Requirements files for all platforms
- ✅ .gitignore for clean repository

### Features
- YOLOv8 training with data augmentation
- Apple MPS (Metal Performance Shaders) GPU support
- Automatic device detection (MPS/CPU)
- Model export with ONNX simplification
- Hailo-8L compilation for Raspberry Pi AI Kit
- Real-time detection at 30-60 FPS
- Picamera2 camera integration
- Video recording capability
- FPS monitoring
- Detection visualization with bounding boxes

### Documentation
- README.md - Complete guide in English
- QUICK_START_TH.md - Quick reference in Thai
- PROJECT_SUMMARY.md - Project overview
- docker/README.md - Docker setup guide
- CHANGELOG.md - Version history

### Scripts
- setup_macos.sh - MacOS environment setup
- setup_pi5.sh - Raspberry Pi 5 setup
- run_all.sh - Automated pipeline runner

### Requirements
- Python 3.8+
- PyTorch 2.0+
- Ultralytics YOLOv8
- ONNX & ONNXRuntime
- Docker (for HEF conversion)
- Hailo Dataflow Compiler 3.27.0
- Raspberry Pi 5 with Hailo AI Kit
- Picamera2 (for camera input)

### Tested On
- MacOS (M1/M2/M3 - Apple Silicon)
- Docker on MacOS/Linux
- Raspberry Pi 5 + Hailo AI Kit (13 TOPS)

---

## Future Releases

### [1.1.0] - Planned
- [ ] Multi-class detection support
- [ ] Object tracking algorithms
- [ ] Web interface for monitoring
- [ ] REST API for inference
- [ ] Performance benchmarks

### [1.2.0] - Planned
- [ ] Model auto-update mechanism
- [ ] Cloud integration
- [ ] Database logging
- [ ] Alert notifications
- [ ] Mobile app

### [2.0.0] - Planned
- [ ] Multi-camera support
- [ ] Distributed inference
- [ ] Auto-labeling tools
- [ ] Custom training UI
- [ ] Model marketplace

---

## Notes

This project uses:
- **Hailo Dataflow Compiler** 3.27.0 for model optimization
- **YOLOv8** from Ultralytics for object detection
- **Picamera2** for Raspberry Pi camera interface
- **Docker** for reproducible build environment
