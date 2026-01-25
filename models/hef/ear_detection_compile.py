#!/usr/bin/env python3
# Hailo Dataflow Compiler Script for ear_detection

import os
from hailo_sdk_client import ClientRunner

def main():
    # Model paths
    onnx_path = 'models/onnx/best_simplified.onnx'
    output_dir = 'models/hef'
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize Hailo runner
    runner = ClientRunner(hw_arch='hailo8l')  # For Raspberry Pi AI Kit (Hailo-8L)
    
    # Step 1: Parse ONNX model
    print("\n" + "="*60)
    print("Step 1: Parsing ONNX model...")
    print("="*60)
    hn, npz = runner.translate_onnx_model(
        onnx_path,
        net_name='ear_detection',
        start_node_names=None,
        end_node_names=None,
        net_input_shapes={'images': [1, 3, 640, 640]}
    )
    
    # Step 2: Optimize model
    print("\n" + "="*60)
    print("Step 2: Optimizing model...")
    print("="*60)
    runner.load_model_script(hn)
    
    # Step 3: Model Quantization
    print("\n" + "="*60)
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
        
        print(f"Preparing calibration dataset with {len(image_files)} images...")
        for img_path in image_files:
            img = cv2.imread(str(img_path))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 640))
            img = img.astype(np.float32) / 255.0
            img = np.transpose(img, (2, 0, 1))  # HWC to CHW
            images.append(img)
        
        calib_dataset = np.array(images)
        np.save(calib_dataset_path, calib_dataset)
        print(f"✓ Calibration dataset saved: {calib_dataset.shape}")
    else:
        print("⚠ Test images not found, using random calibration data")
        calib_dataset = np.random.rand(10, 3, 640, 640).astype(np.float32)
        np.save(calib_dataset_path, calib_dataset)
    
    # Quantize model
    runner.load_model_script(hn)
    quantized_model_har_path = os.path.join(output_dir, f'{model_name}_quantized.har')
    runner.optimize(calib_dataset_path)
    runner.save_har(quantized_model_har_path)
    print(f"✓ Quantized model saved: {quantized_model_har_path}")
    
    # Step 4: Compile to HEF
    print("\n" + "="*60)
    print("Step 4: Compiling to HEF...")
    print("="*60)
    
    hef_path = os.path.join(output_dir, f'{model_name}.hef')
    runner.compile()
    
    # Export HEF
    hef_data = runner.get_tf_hef()
    with open(hef_path, 'wb') as f:
        f.write(hef_data)
    
    print(f"\n✓ HEF model compiled successfully!")
    print(f"  Output: {hef_path}")
    print(f"  Size: {os.path.getsize(hef_path) / (1024*1024):.2f} MB")
    
    return hef_path

if __name__ == '__main__':
    import numpy as np
    main()
