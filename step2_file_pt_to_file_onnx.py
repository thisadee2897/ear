#!/usr/bin/env python3
"""
Step 2: Convert YOLO .pt model to .onnx format
This script exports a trained YOLOv8 model to ONNX format for deployment.
"""

from ultralytics import YOLO
import os
from pathlib import Path
import onnx
import onnxsim

def verify_onnx_model(onnx_path):
    """Verify and simplify ONNX model"""
    print(f"\n{'='*60}")
    print("Verifying ONNX model...")
    print(f"{'='*60}")
    
    # Load and check ONNX model
    model = onnx.load(onnx_path)
    onnx.checker.check_model(model)
    print("✓ ONNX model is valid")
    
    # Print model info
    print(f"\nModel Information:")
    print(f"  IR Version: {model.ir_version}")
    print(f"  Producer: {model.producer_name}")
    print(f"  Opset Version: {model.opset_import[0].version}")
    
    # Print input/output info
    print(f"\nInput Tensors:")
    for input_tensor in model.graph.input:
        shape = [dim.dim_value for dim in input_tensor.type.tensor_type.shape.dim]
        print(f"  Name: {input_tensor.name}, Shape: {shape}")
    
    print(f"\nOutput Tensors:")
    for output_tensor in model.graph.output:
        shape = [dim.dim_value for dim in output_tensor.type.tensor_type.shape.dim]
        print(f"  Name: {output_tensor.name}, Shape: {shape}")
    
    # Simplify ONNX model
    print(f"\n{'='*60}")
    print("Simplifying ONNX model...")
    print(f"{'='*60}")
    
    try:
        model_simp, check = onnxsim.simplify(model)
        if check:
            simplified_path = onnx_path.replace('.onnx', '_simplified.onnx')
            onnx.save(model_simp, simplified_path)
            print(f"✓ Simplified ONNX model saved to: {simplified_path}")
            
            # Get file sizes
            original_size = os.path.getsize(onnx_path) / (1024 * 1024)
            simplified_size = os.path.getsize(simplified_path) / (1024 * 1024)
            print(f"  Original size: {original_size:.2f} MB")
            print(f"  Simplified size: {simplified_size:.2f} MB")
            print(f"  Size reduction: {((original_size - simplified_size) / original_size * 100):.1f}%")
            
            return simplified_path
        else:
            print("⚠ Simplification check failed, using original model")
            return onnx_path
    except Exception as e:
        print(f"⚠ Error during simplification: {e}")
        print("  Using original ONNX model")
        return onnx_path

def main():
    print("="*60)
    print("STEP 2: Convert .pt to .onnx")
    print("="*60)
    
    # Configuration
    PT_MODEL_PATH = 'runs/train/ear_detection/weights/best.pt'  # Change this to your model path
    OUTPUT_DIR = 'models/onnx'
    IMGSZ = 640  # Must match training image size
    SIMPLIFY = True
    OPSET = 11  # ONNX opset version (11 is compatible with Hailo)
    
    # Check if model exists
    if not os.path.exists(PT_MODEL_PATH):
        print(f"\n❌ Error: Model file not found: {PT_MODEL_PATH}")
        print("\nPlease ensure you have:")
        print("1. Trained a model using step1_train_model_to_pt.py")
        print("2. Updated PT_MODEL_PATH in this script to point to your trained model")
        print("\nExample paths:")
        print("  - runs/train/ear_detection/weights/best.pt")
        print("  - runs/train/ear_detection/weights/last.pt")
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"\nConversion Configuration:")
    print(f"  Input Model: {PT_MODEL_PATH}")
    print(f"  Output Directory: {OUTPUT_DIR}")
    print(f"  Image Size: {IMGSZ}")
    print(f"  ONNX Opset: {OPSET}")
    print(f"  Simplify: {SIMPLIFY}")
    
    # Load YOLO model
    print(f"\n{'='*60}")
    print("Loading YOLO model...")
    model = YOLO(PT_MODEL_PATH)
    
    # Export to ONNX
    print(f"\n{'='*60}")
    print("Exporting to ONNX format...")
    print(f"{'='*60}\n")
    
    try:
        # Export with specific settings for Hailo compatibility
        export_path = model.export(
            format='onnx',
            imgsz=IMGSZ,
            opset=OPSET,
            simplify=False,  # We'll simplify manually for better control
            dynamic=False,  # Static batch size for Hailo
            half=False,  # Full precision (FP32)
        )
        
        print(f"\n✓ ONNX model exported successfully!")
        print(f"  Path: {export_path}")
        
        # Get file size
        file_size = os.path.getsize(export_path) / (1024 * 1024)
        print(f"  Size: {file_size:.2f} MB")
        
        # Move to output directory
        output_path = os.path.join(OUTPUT_DIR, Path(export_path).name)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(export_path, output_path)
        print(f"\n✓ Model copied to: {output_path}")
        
        # Verify and simplify ONNX model
        if SIMPLIFY:
            simplified_path = verify_onnx_model(output_path)
            final_model = simplified_path
        else:
            verify_onnx_model(output_path)
            final_model = output_path
        
        print(f"\n{'='*60}")
        print("Conversion completed successfully!")
        print(f"{'='*60}")
        print(f"\nFinal ONNX model: {final_model}")
        
        print(f"\n{'='*60}")
        print("Next Steps:")
        print(f"{'='*60}")
        print(f"1. Use Docker to convert ONNX to HEF:")
        print(f"   cd docker")
        print(f"   docker-compose up -d")
        print(f"   docker-compose exec hailo-compiler bash")
        print(f"   python3 step3_file_onnx_to_file_hef.py")
        print(f"\n2. Or update step3_file_onnx_to_file_hef.py with:")
        print(f"   ONNX_MODEL_PATH = '{final_model}'")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error during export: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure ultralytics is installed: pip install ultralytics")
        print("2. Ensure onnx is installed: pip install onnx onnxruntime")
        print("3. Check that the model file is valid")

if __name__ == '__main__':
    main()
