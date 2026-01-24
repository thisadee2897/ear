# YOLO Ear Detection - Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     YOLO EAR DETECTION PIPELINE                         │
│                  Raspberry Pi 5 + Hailo AI Kit                          │
└─────────────────────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 1: TRAINING (MacOS with Apple Silicon)                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  📂 Dataset (YOLO Format)              🖥️  MacOS Environment
  ├── train/                            ├── Python 3.8+
  │   ├── images/ (1050 images)        ├── PyTorch 2.0+
  │   └── labels/                       ├── Ultralytics YOLO
  ├── valid/                            ├── Apple MPS GPU
  │   ├── images/ (100 images)         └── Virtual Environment (.venv)
  │   └── labels/
  └── test/
      ├── images/ (50 images)
      └── labels/
           │
           ▼
  ┌──────────────────────────────────┐
  │  step1_train_model_to_pt.py      │
  │  • Load YOLOv8 model             │
  │  • Train on dataset              │
  │  • Data augmentation             │
  │  • Validation & metrics          │
  │  • Early stopping                │
  └──────────────────────────────────┘
           │
           ▼
  📦 Output: best.pt (PyTorch Model)
  Location: runs/train/ear_detection/weights/best.pt
  
  Metrics:
  • mAP50: ~0.95
  • Precision: ~0.92
  • Recall: ~0.89
  • Training Time: 2-3 hours (100 epochs)


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 2: ONNX CONVERSION (MacOS)                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  📦 Input: best.pt
           │
           ▼
  ┌──────────────────────────────────┐
  │  step2_file_pt_to_file_onnx.py   │
  │  • Export to ONNX format         │
  │  • Verify model integrity        │
  │  • Simplify ONNX graph           │
  │  • Check input/output shapes     │
  └──────────────────────────────────┘
           │
           ▼
  📦 Output: best_simplified.onnx
  Location: models/onnx/best_simplified.onnx
  
  Format:
  • ONNX Opset 11 (Hailo compatible)
  • Static shapes (640x640)
  • FP32 precision
  • Simplified graph
  • Conversion Time: 1-2 minutes


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 3: HEF CONVERSION (Docker - Hailo Dataflow Compiler)           ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  🐳 Docker Container                   📦 Input: best_simplified.onnx
  ├── Ubuntu 20.04                            │
  ├── Python 3.8                              ▼
  ├── Hailo Dataflow Compiler 3.27.0   ┌──────────────────────────────────┐
  └── ONNX Runtime                     │  step3_file_onnx_to_file_hef.py  │
                                       │  • Parse ONNX model               │
  Commands:                            │  • Optimize for Hailo-8L          │
  $ cd docker                          │  • Create calibration dataset     │
  $ docker-compose build               │  • Quantize model (INT8)          │
  $ docker-compose up -d               │  • Compile to HEF                 │
  $ docker-compose exec \              └──────────────────────────────────┘
      hailo-compiler bash                         │
  (container)$ python3 \                          ▼
      step3_file_onnx_to_file_hef.py       📦 Output: ear_detection.hef
                                           Location: models/hef/ear_detection.hef
  
  Target Hardware:
  • Hailo-8L AI Processor
  • 13 TOPS performance
  • Raspberry Pi AI Kit
  • Compilation Time: 5-10 minutes


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  STEP 4: DEPLOYMENT (Raspberry Pi 5 + Hailo AI Kit)                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  🔧 Hardware Setup                     📦 Input: ear_detection.hef
  ├── Raspberry Pi 5 (4GB/8GB)                │
  ├── Hailo AI Kit (13 TOPS)                  │
  ├── Raspberry Pi Camera                      ▼
  ├── Power Supply (5V 5A)             ┌──────────────────────────────────┐
  └── MicroSD Card (32GB+)             │  step4_code_run_on_pi5.py        │
                                       │  • Initialize Hailo device        │
  Software:                            │  • Load HEF model                 │
  ├── Raspberry Pi OS                  │  • Setup Picamera2                │
  ├── Hailo Platform SDK               │  • Real-time inference            │
  ├── Picamera2                        │  • Draw bounding boxes            │
  └── OpenCV                           │  • Display FPS                    │
                                       │  • Optional: Save video           │
  Transfer model:                      └──────────────────────────────────┘
  $ scp models/hef/ear_detection.hef \             │
      pi@raspberrypi:~/                             ▼
                                            🎥 Real-time Detection
  Run inference:                            ├── 30-60 FPS
  $ python3 step4_code_run_on_pi5.py        ├── Live camera feed
                                            ├── Bounding boxes
                                            ├── Confidence scores
                                            └── Class labels


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  PERFORMANCE METRICS                                                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  Step          Device              Time          Notes
  ────────────────────────────────────────────────────────────────────
  Training      MacOS M1/M2        2-3 hours     100 epochs, GPU
  PT → ONNX     MacOS              1-2 min       Model export
  ONNX → HEF    Docker (x86)       5-10 min      Quantization
  Inference     Pi5 + Hailo        16-33 ms      30-60 FPS real-time
  

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  FILE STRUCTURE                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  📁 Project Root
  │
  ├── 🐍 Python Scripts
  │   ├── step1_train_model_to_pt.py       (Train YOLO)
  │   ├── step2_file_pt_to_file_onnx.py    (PT → ONNX)
  │   ├── step3_file_onnx_to_file_hef.py   (ONNX → HEF)
  │   ├── step4_code_run_on_pi5.py         (Inference)
  │   ├── test_setup.py                    (Verify setup)
  │   └── info.py                          (Project info)
  │
  ├── 🐳 Docker
  │   └── docker/
  │       ├── Dockerfile
  │       ├── docker-compose.yml
  │       └── README.md
  │
  ├── 🔧 Setup Scripts
  │   ├── setup_macos.sh                   (MacOS setup)
  │   ├── setup_pi5.sh                     (Pi5 setup)
  │   └── run_all.sh                       (Automated runner)
  │
  ├── 📋 Requirements
  │   ├── requirements.txt                 (MacOS packages)
  │   └── requirements_pi5.txt             (Pi5 packages)
  │
  ├── 📖 Documentation
  │   ├── README.md                        (Complete guide)
  │   ├── QUICK_START_TH.md               (Quick start Thai)
  │   ├── PROJECT_SUMMARY.md              (Project overview)
  │   ├── CHANGELOG.md                    (Version history)
  │   └── WORKFLOW.md                     (This file)
  │
  ├── 📊 Dataset
  │   ├── data.yaml                        (Dataset config)
  │   ├── train/                           (Training data)
  │   ├── valid/                           (Validation data)
  │   └── test/                            (Test data)
  │
  ├── 📦 Models (Generated)
  │   ├── models/onnx/                     (ONNX models)
  │   ├── models/hef/                      (HEF models)
  │   └── runs/train/                      (Training outputs)
  │
  └── 🔧 Other
      ├── .venv/                           (Virtual environment)
      ├── .gitignore                       (Git ignore rules)
      └── hailo_dataflow_compiler.whl      (Hailo compiler)


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  QUICK COMMANDS                                                       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  📋 Setup
  $ ./setup_macos.sh                    # Setup MacOS environment
  $ source .venv/bin/activate           # Activate environment
  $ python test_setup.py                # Verify setup

  🚀 Run Pipeline
  $ python step1_train_model_to_pt.py           # Train
  $ python step2_file_pt_to_file_onnx.py        # Convert to ONNX
  $ cd docker && docker-compose up -d           # Start Docker
  $ docker-compose exec hailo-compiler bash     # Enter container
  $ python3 step3_file_onnx_to_file_hef.py      # Convert to HEF
  $ exit && docker-compose down                 # Exit & stop

  📤 Deploy to Pi5
  $ scp models/hef/ear_detection.hef pi@raspberrypi:~/
  $ scp step4_code_run_on_pi5.py pi@raspberrypi:~/
  $ ssh pi@raspberrypi
  (pi5)$ python3 step4_code_run_on_pi5.py       # Run inference

  ℹ️  Info & Help
  $ python info.py                      # Show project info
  $ cat README.md                       # Read full guide
  $ cat QUICK_START_TH.md              # Quick start (Thai)


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  TROUBLESHOOTING                                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  ❓ MPS not available
  → Normal on Intel Mac, will use CPU (slower but works)

  ❓ Out of memory during training
  → Reduce BATCH size in step1_train_model_to_pt.py (try 8 or 4)

  ❓ Docker build fails
  → Increase Docker memory in Docker Desktop settings (4GB+)

  ❓ Camera not detected on Pi5
  → Check connection: libcamera-hello
  → Install Picamera2: sudo apt install python3-picamera2

  ❓ Hailo not found on Pi5
  → Install from: https://github.com/hailo-ai/hailo-rpi5-examples

  ❓ Slow inference
  → Check Hailo driver: hailo-info
  → Ensure power supply is 5V 5A
  → Add cooling (heatsink/fan)


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  RESOURCES & LINKS                                                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  📚 Documentation
  • Ultralytics YOLOv8:  https://docs.ultralytics.com/
  • Hailo Developer:     https://hailo.ai/developer-zone/
  • Raspberry Pi 5:      https://www.raspberrypi.com/products/raspberry-pi-5/
  • Picamera2 Manual:    https://datasheets.raspberrypi.com/camera/

  💻 GitHub Repositories
  • Ultralytics:         https://github.com/ultralytics/ultralytics
  • Hailo RPi5:          https://github.com/hailo-ai/hailo-rpi5-examples
  • Picamera2:           https://github.com/raspberrypi/picamera2

  🎓 Tutorials
  • YOLO Training:       https://docs.ultralytics.com/modes/train/
  • ONNX Export:         https://docs.ultralytics.com/modes/export/
  • Hailo Model Zoo:     https://github.com/hailo-ai/hailo_model_zoo


═══════════════════════════════════════════════════════════════════════

  🎉 Ready to start! Run: python info.py for quick reference
  
  Created: 2026-01-25
  Version: 1.0.0
  
═══════════════════════════════════════════════════════════════════════
```
