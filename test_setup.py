#!/usr/bin/env python3
"""
Test script to verify the setup is correct
Run this after setting up the environment
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python version OK")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_packages():
    """Check if required packages are installed"""
    print_header("Checking Python Packages")
    
    packages = {
        'torch': 'PyTorch',
        'ultralytics': 'Ultralytics YOLOv8',
        'cv2': 'OpenCV (cv2)',
        'numpy': 'NumPy',
        'PIL': 'Pillow',
        'yaml': 'PyYAML',
        'onnx': 'ONNX',
        'onnxruntime': 'ONNX Runtime',
    }
    
    results = {}
    for module, name in packages.items():
        try:
            if module == 'cv2':
                import cv2
            elif module == 'PIL':
                import PIL
            elif module == 'yaml':
                import yaml
            else:
                __import__(module)
            print(f"✓ {name}")
            results[module] = True
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
            results[module] = False
    
    return all(results.values())

def check_pytorch_device():
    """Check PyTorch device availability"""
    print_header("Checking PyTorch Device")
    
    try:
        import torch
        
        print(f"PyTorch version: {torch.__version__}")
        
        # Check MPS (Apple Silicon)
        if torch.backends.mps.is_available():
            print("✓ MPS (Apple Silicon GPU) available")
            device = torch.device("mps")
            print(f"  Using device: {device}")
        else:
            print("⚠ MPS not available, using CPU")
            device = torch.device("cpu")
        
        # Test tensor creation
        x = torch.randn(3, 3).to(device)
        print(f"✓ Created test tensor on {device}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_dataset():
    """Check if dataset is available"""
    print_header("Checking Dataset")
    
    # Check data.yaml
    if Path('data.yaml').exists():
        print("✓ data.yaml found")
    else:
        print("❌ data.yaml not found")
        return False
    
    # Check directories
    dirs = ['train/images', 'valid/images', 'test/images']
    all_exist = True
    
    for dir_path in dirs:
        path = Path(dir_path)
        if path.exists():
            count = len(list(path.glob('*.jpg')))
            print(f"✓ {dir_path}: {count} images")
        else:
            print(f"❌ {dir_path}: not found")
            all_exist = False
    
    return all_exist

def check_docker():
    """Check Docker installation"""
    print_header("Checking Docker")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ Docker: {result.stdout.strip()}")
            
            # Check docker-compose
            result = subprocess.run(
                ['docker-compose', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"✓ Docker Compose: {result.stdout.strip()}")
                return True
        else:
            print("⚠ Docker installed but not running")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠ Docker not found or not running")
        print("  (Not required for training, only for HEF conversion)")
        return False

def check_hailo_wheel():
    """Check if Hailo wheel file exists"""
    print_header("Checking Hailo Dataflow Compiler")
    
    wheel_path = Path('hailo_dataflow_compiler-3.27.0-py3-none-linux_x86_64.whl')
    if wheel_path.exists():
        size = wheel_path.stat().st_size / (1024 * 1024)
        print(f"✓ Hailo wheel found: {size:.2f} MB")
        return True
    else:
        print("❌ Hailo wheel not found")
        print("  This is required for converting ONNX to HEF")
        return False

def check_scripts():
    """Check if all scripts exist"""
    print_header("Checking Scripts")
    
    scripts = [
        'step1_train_model_to_pt.py',
        'step2_file_pt_to_file_onnx.py',
        'step3_file_onnx_to_file_hef.py',
        'step4_code_run_on_pi5.py',
        'setup_macos.sh',
        'setup_pi5.sh',
        'run_all.sh',
    ]
    
    all_exist = True
    for script in scripts:
        path = Path(script)
        if path.exists():
            print(f"✓ {script}")
        else:
            print(f"❌ {script}")
            all_exist = False
    
    return all_exist

def main():
    """Run all checks"""
    print("\n" + "🔍 " + "="*56 + " 🔍")
    print("     YOLO Ear Detection - Setup Verification Test")
    print("🔍 " + "="*56 + " 🔍")
    
    results = {}
    
    # Run checks
    results['python'] = check_python_version()
    results['packages'] = check_packages()
    results['pytorch'] = check_pytorch_device()
    results['dataset'] = check_dataset()
    results['scripts'] = check_scripts()
    results['hailo'] = check_hailo_wheel()
    results['docker'] = check_docker()  # Optional
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} checks")
    
    if results['python'] and results['packages'] and results['pytorch'] and results['dataset']:
        print("\n✅ Ready for training! Run:")
        print("   python step1_train_model_to_pt.py")
    else:
        print("\n⚠️  Some required components are missing")
        print("   Please run: ./setup_macos.sh")
    
    if results['hailo'] and results['docker']:
        print("\n✅ Ready for HEF conversion!")
    elif not results['docker']:
        print("\n⚠️  Docker not available (optional for HEF conversion)")
    
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    main()
