# 🚀 Getting Started - YOLO Ear Detection

Welcome! This guide will help you get started quickly.

## ✅ What You Have

Your project is now **fully set up** with everything needed for:

1. ✅ **Training YOLO models** on MacOS (with Apple Silicon support)
2. ✅ **Converting models** to ONNX format
3. ✅ **Compiling models** to Hailo HEF format (Docker)
4. ✅ **Running inference** on Raspberry Pi 5 + Hailo AI Kit

## 📊 Current Status

- **Dataset**: ✅ 1,050 train + 100 valid + 50 test images
- **Hailo Compiler**: ✅ hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl
- **Scripts**: ✅ All 4 steps ready
- **Docker**: ✅ Configured
- **Documentation**: ✅ Complete (English + Thai)

## 🎯 Quick Start (3 Options)

### Option 1: Interactive Info (Recommended)
```bash
python info.py
```
This shows project status and all available commands.

### Option 2: Verify Setup First
```bash
python test_setup.py
```
This checks if all dependencies are installed.

### Option 3: Start Training Immediately
```bash
# 1. Setup environment (if not done)
./setup_macos.sh
source .venv/bin/activate

# 2. Start training
python step1_train_model_to_pt.py
```

## 📚 Documentation Files

Choose based on your needs:

| File | Purpose | When to Use |
|------|---------|-------------|
| **GETTING_STARTED.md** | Quick intro (this file) | First time setup |
| **info.py** | Interactive commands | Quick reference |
| **QUICK_START_TH.md** | Quick guide (Thai) | Thai speakers |
| **README.md** | Complete guide | Deep dive |
| **WORKFLOW.md** | Visual workflow | Understanding pipeline |
| **PROJECT_SUMMARY.md** | Project overview | Feature list |

## 🔄 Complete Workflow (Step by Step)

### Step 1: Train Model (MacOS)
```bash
# Activate environment
source .venv/bin/activate

# Train YOLO model
python step1_train_model_to_pt.py

# Output: runs/train/ear_detection/weights/best.pt
# Time: 2-3 hours (100 epochs)
```

### Step 2: Convert to ONNX (MacOS)
```bash
# Convert PyTorch model to ONNX
python step2_file_pt_to_file_onnx.py

# Output: models/onnx/best_simplified.onnx
# Time: 1-2 minutes
```

### Step 3: Convert to HEF (Docker)
```bash
# Start Docker container
cd docker
docker-compose build
docker-compose up -d

# Enter container
docker-compose exec hailo-compiler bash

# Inside container: Convert ONNX to HEF
python3 step3_file_onnx_to_file_hef.py

# Exit and stop container
exit
docker-compose down
cd ..

# Output: models/hef/ear_detection.hef
# Time: 5-10 minutes
```

### Step 4: Deploy to Raspberry Pi 5
```bash
# Copy files to Pi5
scp models/hef/ear_detection.hef pi@raspberrypi:~/
scp step4_code_run_on_pi5.py pi@raspberrypi:~/
scp setup_pi5.sh pi@raspberrypi:~/

# SSH to Pi5
ssh pi@raspberrypi

# On Pi5: Setup and run
chmod +x setup_pi5.sh
./setup_pi5.sh
python3 step4_code_run_on_pi5.py
```

## 💡 Tips & Tricks

### For Faster Training
```python
# Edit step1_train_model_to_pt.py
MODEL_SIZE = 'yolov8n.pt'  # Smallest/fastest
EPOCHS = 50                # Fewer epochs
BATCH = 8                  # Smaller batch if memory issues
```

### For Better Accuracy
```python
# Edit step1_train_model_to_pt.py
MODEL_SIZE = 'yolov8m.pt'  # Medium size
EPOCHS = 150               # More epochs
BATCH = 16                 # Larger batch if RAM allows
```

### For Custom Detection Threshold
```python
# Edit step4_code_run_on_pi5.py
CONF_THRESHOLD = 0.5   # Higher = fewer but more confident detections
IOU_THRESHOLD = 0.45   # NMS threshold
```

## 🔍 Useful Commands

### Check Dataset
```bash
# Count images
find train/images -name "*.jpg" | wc -l
find valid/images -name "*.jpg" | wc -l
find test/images -name "*.jpg" | wc -l
```

### Check Models
```bash
# List trained models
ls -lh runs/train/*/weights/

# List ONNX models
ls -lh models/onnx/

# List HEF models
ls -lh models/hef/
```

### View Training Results
```bash
# Open training directory
open runs/train/ear_detection/

# View plots
open runs/train/ear_detection/*.png
```

## ❓ Common Issues

### Issue: MPS not available
**Solution**: Normal on Intel Mac, will use CPU (slower but works fine)

### Issue: Out of memory
**Solution**: Reduce BATCH size to 8 or 4 in step1_train_model_to_pt.py

### Issue: Docker build fails
**Solution**: Increase Docker memory in Settings → Resources → Memory: 4GB+

### Issue: Picamera2 not found (Pi5)
**Solution**: 
```bash
sudo apt-get update
sudo apt-get install python3-picamera2
```

## 📞 Need Help?

1. **Quick Reference**: `python info.py`
2. **Thai Guide**: `cat QUICK_START_TH.md`
3. **Full Guide**: `cat README.md`
4. **Workflow Diagram**: `cat WORKFLOW.md`
5. **Test Setup**: `python test_setup.py`

## 🎓 Learning Resources

- [YOLOv8 Docs](https://docs.ultralytics.com/)
- [Hailo AI](https://hailo.ai/developer-zone/)
- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/)
- [Hailo RPi5 Examples](https://github.com/hailo-ai/hailo-rpi5-examples)

## ⚡ Performance Expectations

| Stage | Time | Device |
|-------|------|--------|
| Training | 2-3 hours | MacBook M1/M2 |
| ONNX Conversion | 1-2 min | MacOS |
| HEF Compilation | 5-10 min | Docker |
| Inference | 30-60 FPS | Pi5 + Hailo |

## 🎉 Ready to Start!

Everything is configured and ready. Choose your path:

1. **New User?** → Run `python info.py`
2. **Want to Train?** → Run `python step1_train_model_to_pt.py`
3. **Need Setup?** → Run `./setup_macos.sh`
4. **Test Setup?** → Run `python test_setup.py`

**Good luck with your YOLO Ear Detection project! 🚀**

---

Created: 2026-01-25  
Version: 1.0.0  
Project: YOLO Ear Detection for Raspberry Pi 5 + Hailo AI Kit
