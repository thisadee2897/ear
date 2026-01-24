#!/usr/bin/env python3
"""
Helper script to display project information and quick commands
"""

import os
from pathlib import Path

def print_banner():
    """Print project banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🎯 YOLO Ear Detection Pipeline                        ║
║        Raspberry Pi 5 + Hailo AI Kit (13 TOPS)              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_menu():
    """Print main menu"""
    print("\n📚 Documentation Files:")
    print("   1. README.md           - Complete guide (English)")
    print("   2. QUICK_START_TH.md   - Quick start (Thai)")
    print("   3. PROJECT_SUMMARY.md  - Project overview")
    print("   4. CHANGELOG.md        - Version history")
    print("   5. docker/README.md    - Docker setup guide")
    
    print("\n🔧 Setup Commands:")
    print("   MacOS Setup:")
    print("   $ ./setup_macos.sh")
    print("   $ source .venv/bin/activate")
    print()
    print("   Verify Setup:")
    print("   $ python test_setup.py")
    
    print("\n🚀 Quick Start:")
    print("   Step 1 - Train Model:")
    print("   $ python step1_train_model_to_pt.py")
    print()
    print("   Step 2 - Convert to ONNX:")
    print("   $ python step2_file_pt_to_file_onnx.py")
    print()
    print("   Step 3 - Docker + HEF:")
    print("   $ cd docker")
    print("   $ docker-compose up -d")
    print("   $ docker-compose exec hailo-compiler bash")
    print("   (inside container) $ python3 step3_file_onnx_to_file_hef.py")
    print()
    print("   Step 4 - Run on Pi5:")
    print("   $ scp models/hef/ear_detection.hef pi@raspberrypi:~/")
    print("   (on Pi5) $ python3 step4_code_run_on_pi5.py")
    
    print("\n🐳 Docker Commands:")
    print("   Build:   docker-compose -f docker/docker-compose.yml build")
    print("   Start:   docker-compose -f docker/docker-compose.yml up -d")
    print("   Enter:   docker-compose -f docker/docker-compose.yml exec hailo-compiler bash")
    print("   Stop:    docker-compose -f docker/docker-compose.yml down")
    
    print("\n📊 Project Structure:")
    print("   step1_train_model_to_pt.py      → Train YOLO model")
    print("   step2_file_pt_to_file_onnx.py   → Convert .pt to .onnx")
    print("   step3_file_onnx_to_file_hef.py  → Convert .onnx to .hef")
    print("   step4_code_run_on_pi5.py        → Run on Raspberry Pi 5")
    print("   docker/                          → Docker environment")
    print("   models/                          → Output models")
    print("   runs/                            → Training results")
    
    print("\n💡 Useful Commands:")
    print("   Check dataset:")
    print("   $ ls -lh train/images/ | wc -l")
    print()
    print("   Check YOLO models:")
    print("   $ ls -lh runs/train/*/weights/")
    print()
    print("   Check converted models:")
    print("   $ ls -lh models/onnx/ models/hef/")
    
    print("\n🔗 Resources:")
    print("   • YOLOv8 Docs:  https://docs.ultralytics.com/")
    print("   • Hailo AI:     https://hailo.ai/")
    print("   • RPi5 Examples: https://github.com/hailo-ai/hailo-rpi5-examples")
    print("   • Picamera2:    https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf")
    
    print("\n" + "="*65)
    print("💬 For help, read: README.md or QUICK_START_TH.md")
    print("="*65 + "\n")

def check_status():
    """Check project status"""
    print("\n📊 Project Status:")
    
    # Check virtual environment
    if Path('.venv').exists():
        print("   ✅ Virtual environment (.venv) exists")
    else:
        print("   ❌ Virtual environment not found - run: ./setup_macos.sh")
    
    # Check dataset
    train_images = len(list(Path('train/images').glob('*.jpg'))) if Path('train/images').exists() else 0
    valid_images = len(list(Path('valid/images').glob('*.jpg'))) if Path('valid/images').exists() else 0
    test_images = len(list(Path('test/images').glob('*.jpg'))) if Path('test/images').exists() else 0
    
    print(f"   📁 Dataset: {train_images} train, {valid_images} valid, {test_images} test")
    
    # Check models
    if Path('runs/train').exists():
        models = list(Path('runs/train').glob('*/weights/best.pt'))
        print(f"   🎯 Trained models: {len(models)}")
    else:
        print("   ⚪ No trained models yet")
    
    # Check ONNX models
    if Path('models/onnx').exists():
        onnx_models = list(Path('models/onnx').glob('*.onnx'))
        print(f"   🔄 ONNX models: {len(onnx_models)}")
    else:
        print("   ⚪ No ONNX models yet")
    
    # Check HEF models
    if Path('models/hef').exists():
        hef_models = list(Path('models/hef').glob('*.hef'))
        print(f"   🐳 HEF models: {len(hef_models)}")
    else:
        print("   ⚪ No HEF models yet")
    
    # Check Hailo wheel
    if Path('hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl').exists():
        print("   ✅ Hailo compiler wheel available")
    else:
        print("   ❌ Hailo compiler wheel not found")

def main():
    """Main function"""
    os.system('clear' if os.name == 'posix' else 'cls')
    print_banner()
    check_status()
    print_menu()

if __name__ == '__main__':
    main()
