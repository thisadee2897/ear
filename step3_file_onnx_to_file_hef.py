#!/usr/bin/env python3
"""
Step 3: Convert ONNX model to Hailo HEF format
This script should be run inside the Hailo Docker container.
"""

import os
import sys
from pathlib import Path

def check_hailo_installation():
    """Check if Hailo Dataflow Compiler is installed"""
    try:
        import hailo_sdk_client
        print("✓ Hailo SDK Client is installed")
        return True
    except ImportError:
        print("❌ Hailo SDK Client not found!")
        print("\nThis script should be run inside the Hailo Docker container.")
        print("Please follow these steps:")
        print("1. cd docker")
        print("2. docker-compose up -d")
        print("3. docker-compose exec hailo-compiler bash")
        print("4. python3 step3_file_onnx_to_file_hef.py")
        return False

def create_alls_script(model_name, onnx_path, output_dir):
    """Create Hailo Model Zoo style alls script"""
    script_content = f"""#!/usr/bin/env python3
# Hailo Dataflow Compiler Script for {model_name}

import os
from hailo_sdk_client import ClientRunner

def main():
    # Model paths
    onnx_path = '{onnx_path}'
    output_dir = '{output_dir}'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize Hailo runner
    runner = ClientRunner(hw_arch='hailo8l')  # For Raspberry Pi AI Kit (Hailo-8L)
    
    # Step 1: Parse ONNX model
    print("\\n" + "="*60)
    print("Step 1: Parsing ONNX model...")
    print("="*60)
    hn, npz = runner.translate_onnx_model(
        onnx_path,
        net_name='{model_name}',
        start_node_names=None,
        end_node_names=None,
        net_input_shapes={{'images': [1, 3, 640, 640]}}
    )
    
    # Step 2: Optimize model
    print("\\n" + "="*60)
    print("Step 2: Optimizing model...")
    print("="*60)
    runner.load_model_script(hn)
    
    # Step 3: Model Quantization
    print("\\n" + "="*60)
    print("Step 3: Quantizing model...")
    print("="*60)
    
    # Create calibration dataset from test images
    calib_dataset_path = os.path.join(output_dir, 'calib_set.npy')
    
    # Use test images for calibration
    test_images_dir = 'test/images'
    if os.path.exists(test_images_dir):
        import numpy as np
        import cv2
        from pathlib import Path
        
        images = []
        image_files = list(Path(test_images_dir).glob('*.jpg'))[:50]  # Use 50 images
        
        print(f"Preparing calibration dataset with {{len(image_files)}} images...")
        for img_path in image_files:
            img = cv2.imread(str(img_path))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 640))
            img = img.astype(np.float32) / 255.0
            img = np.transpose(img, (2, 0, 1))  # HWC to CHW
            images.append(img)
        
        calib_dataset = np.array(images)
        np.save(calib_dataset_path, calib_dataset)
        print(f"✓ Calibration dataset saved: {{calib_dataset.shape}}")
    else:
        print("⚠ Test images not found, using random calibration data")
        calib_dataset = np.random.rand(10, 3, 640, 640).astype(np.float32)
        np.save(calib_dataset_path, calib_dataset)
    
    # Quantize model
    runner.load_model_script(hn)
    quantized_model_har_path = os.path.join(output_dir, f'{{model_name}}_quantized.har')
    runner.optimize(calib_dataset_path)
    runner.save_har(quantized_model_har_path)
    print(f"✓ Quantized model saved: {{quantized_model_har_path}}")
    
    # Step 4: Compile to HEF
    print("\\n" + "="*60)
    print("Step 4: Compiling to HEF...")
    print("="*60)
    
    hef_path = os.path.join(output_dir, f'{{model_name}}.hef')
    runner.compile()
    
    # Export HEF
    hef_data = runner.get_tf_hef()
    with open(hef_path, 'wb') as f:
        f.write(hef_data)
    
    print(f"\\n✓ HEF model compiled successfully!")
    print(f"  Output: {{hef_path}}")
    print(f"  Size: {{os.path.getsize(hef_path) / (1024*1024):.2f}} MB")
    
    return hef_path

if __name__ == '__main__':
    import numpy as np
    main()
"""
    return script_content

def convert_onnx_to_hef_simple():
    """Simple conversion using hailo_model_zoo tools"""
    print("="*60)
    print("STEP 3: Convert ONNX to HEF (Hailo Format)")
    print("="*60)
    
    # Configuration
    ONNX_MODEL_PATH = 'models/onnx/best_simplified.onnx'  # Update this path
    OUTPUT_DIR = 'models/hef'
    MODEL_NAME = 'ear_detection'
    
    # Alternative paths to check
    alternative_paths = [
        'models/onnx/best.onnx',
        'models/onnx/best_simplified.onnx',
        'runs/train/ear_detection/weights/best.onnx',
    ]
    
    # Check if ONNX model exists
    if not os.path.exists(ONNX_MODEL_PATH):
        print(f"\n⚠ Model not found: {ONNX_MODEL_PATH}")
        print("\nSearching for ONNX models...")
        
        found = False
        for alt_path in alternative_paths:
            if os.path.exists(alt_path):
                ONNX_MODEL_PATH = alt_path
                print(f"✓ Found model: {alt_path}")
                found = True
                break
        
        if not found:
            print("\n❌ No ONNX model found!")
            print("\nPlease run step2_file_pt_to_file_onnx.py first to create an ONNX model.")
            print("\nOr update ONNX_MODEL_PATH in this script to point to your ONNX model.")
            return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\nConversion Configuration:")
    print(f"  Input ONNX: {ONNX_MODEL_PATH}")
    print(f"  Output Directory: {OUTPUT_DIR}")
    print(f"  Model Name: {MODEL_NAME}")
    print(f"  Target: Hailo-8L (Raspberry Pi AI Kit)")
    
    # Check Hailo installation
    if not check_hailo_installation():
        print("\n" + "="*60)
        print("Creating Hailo compilation script...")
        print("="*60)
        
        # Create the alls script
        script_path = os.path.join(OUTPUT_DIR, f'{MODEL_NAME}_compile.py')
        script_content = create_alls_script(MODEL_NAME, ONNX_MODEL_PATH, OUTPUT_DIR)
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"\n✓ Compilation script created: {script_path}")
        print(f"\nTo compile the model:")
        print(f"1. Start Docker container:")
        print(f"   cd docker")
        print(f"   docker-compose up -d")
        print(f"   docker-compose exec hailo-compiler bash")
        print(f"\n2. Inside container, run:")
        print(f"   python3 {script_path}")
        print(f"\n3. The HEF file will be saved to: {OUTPUT_DIR}/{MODEL_NAME}.hef")
        return
    
    # If Hailo is installed, run the conversion
    print(f"\n{'='*60}")
    print("Starting conversion process...")
    print(f"{'='*60}\n")
    
    try:
        from hailo_sdk_client import ClientRunner
        import numpy as np
        
        # Initialize runner for Hailo-8L (Raspberry Pi AI Kit)
        runner = ClientRunner(hw_arch='hailo8l')
        
        # Parse ONNX
        print("Step 1/4: Parsing ONNX model...")
        hn, npz = runner.translate_onnx_model(
            ONNX_MODEL_PATH,
            net_name=MODEL_NAME,
            start_node_names=None,
            end_node_names=None,
            net_input_shapes={'images': [1, 3, 640, 640]}
        )
        runner.load_model_script(hn)
        print("✓ Model parsed successfully")
        
        # Prepare calibration dataset
        print("\nStep 2/4: Preparing calibration dataset...")
        test_images_dir = 'test/images'
        
        if os.path.exists(test_images_dir):
            import cv2
            from pathlib import Path
            
            images = []
            image_files = list(Path(test_images_dir).glob('*.jpg'))[:50]
            
            for img_path in image_files:
                img = cv2.imread(str(img_path))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (640, 640))
                img = img.astype(np.float32) / 255.0
                img = np.transpose(img, (2, 0, 1))
                images.append(img)
            
            calib_dataset = np.array(images)
            print(f"✓ Prepared {len(images)} calibration images")
        else:
            print("⚠ Using synthetic calibration data")
            calib_dataset = np.random.rand(10, 3, 640, 640).astype(np.float32)
        
        # Save calibration dataset
        calib_path = os.path.join(OUTPUT_DIR, 'calib_set.npy')
        np.save(calib_path, calib_dataset)
        
        # Quantize
        print("\nStep 3/4: Quantizing model...")
        runner.optimize(calib_path)
        quantized_har = os.path.join(OUTPUT_DIR, f'{MODEL_NAME}_quantized.har')
        runner.save_har(quantized_har)
        print(f"✓ Model quantized: {quantized_har}")
        
        # Compile to HEF
        print("\nStep 4/4: Compiling to HEF...")
        runner.compile()
        hef_path = os.path.join(OUTPUT_DIR, f'{MODEL_NAME}.hef')
        
        hef_data = runner.get_hef()
        with open(hef_path, 'wb') as f:
            f.write(hef_data)
        
        file_size = os.path.getsize(hef_path) / (1024 * 1024)
        
        print(f"\n{'='*60}")
        print("Conversion completed successfully!")
        print(f"{'='*60}")
        print(f"\n✓ HEF model: {hef_path}")
        print(f"✓ Size: {file_size:.2f} MB")
        
        print(f"\n{'='*60}")
        print("Next Steps:")
        print(f"{'='*60}")
        print(f"1. Copy HEF file to Raspberry Pi 5:")
        print(f"   scp {hef_path} pi@raspberrypi:~/")
        print(f"\n2. Run inference on Raspberry Pi 5:")
        print(f"   python3 step4_code_run_on_pi5.py")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()

def main():
    convert_onnx_to_hef_simple()

if __name__ == '__main__':
    main()
