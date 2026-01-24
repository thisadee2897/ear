#!/usr/bin/env python3
"""
Step 1: Train YOLO Model on MacOS
This script trains a YOLOv8 model for ear detection using the Ultralytics framework.
"""

from ultralytics import YOLO
import torch
import os
from pathlib import Path

def main():
    print("="*60)
    print("STEP 1: Training YOLO Model for Ear Detection")
    print("="*60)
    
    # Configuration
    DATA_YAML = 'data.yaml'
    MODEL_SIZE = 'yolov8n.pt'  # Options: yolov8n, yolov8s, yolov8m, yolov8l, yolov8x
    EPOCHS = 100
    IMGSZ = 640
    BATCH = 16
    PROJECT = 'runs/train'
    NAME = 'ear_detection'
    
    # Check if MPS (Apple Silicon GPU) is available
    if torch.backends.mps.is_available():
        device = 'mps'
        print(f"✓ Using Apple Silicon GPU (MPS)")
    else:
        device = 'cpu'
        print(f"✓ Using CPU")
    
    # Check if data.yaml exists
    if not os.path.exists(DATA_YAML):
        raise FileNotFoundError(f"Data configuration file '{DATA_YAML}' not found!")
    
    print(f"\nTraining Configuration:")
    print(f"  Model: {MODEL_SIZE}")
    print(f"  Device: {device}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Image Size: {IMGSZ}")
    print(f"  Batch Size: {BATCH}")
    print(f"  Data Config: {DATA_YAML}")
    
    # Load YOLO model
    print(f"\n{'='*60}")
    print("Loading YOLO model...")
    model = YOLO(MODEL_SIZE)
    
    # Train the model
    print(f"\n{'='*60}")
    print("Starting training...")
    print(f"{'='*60}\n")
    
    results = model.train(
        data=DATA_YAML,
        epochs=EPOCHS,
        imgsz=IMGSZ,
        batch=BATCH,
        device=device,
        project=PROJECT,
        name=NAME,
        patience=50,  # Early stopping patience
        save=True,
        save_period=10,  # Save checkpoint every 10 epochs
        cache=True,  # Cache images for faster training
        plots=True,  # Save training plots
        verbose=True,
        # Augmentation settings
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=0.0,
        translate=0.1,
        scale=0.5,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.0,
    )
    
    print(f"\n{'='*60}")
    print("Training completed!")
    print(f"{'='*60}")
    
    # Get the best model path
    best_model_path = Path(PROJECT) / NAME / 'weights' / 'best.pt'
    last_model_path = Path(PROJECT) / NAME / 'weights' / 'last.pt'
    
    if best_model_path.exists():
        print(f"\n✓ Best model saved to: {best_model_path}")
    if last_model_path.exists():
        print(f"✓ Last model saved to: {last_model_path}")
    
    # Validate the model
    print(f"\n{'='*60}")
    print("Validating model on test set...")
    print(f"{'='*60}\n")
    
    metrics = model.val()
    
    print(f"\n{'='*60}")
    print("Validation Results:")
    print(f"{'='*60}")
    print(f"  mAP50: {metrics.box.map50:.4f}")
    print(f"  mAP50-95: {metrics.box.map:.4f}")
    print(f"  Precision: {metrics.box.mp:.4f}")
    print(f"  Recall: {metrics.box.mr:.4f}")
    
    # Test prediction on sample images
    print(f"\n{'='*60}")
    print("Testing prediction on sample images...")
    print(f"{'='*60}\n")
    
    test_images_dir = Path('test/images')
    if test_images_dir.exists():
        test_images = list(test_images_dir.glob('*.jpg'))[:5]  # Test on first 5 images
        if test_images:
            results = model.predict(
                source=test_images,
                save=True,
                project=PROJECT,
                name=f"{NAME}_predictions",
                conf=0.25
            )
            print(f"✓ Predictions saved to: {PROJECT}/{NAME}_predictions")
    
    print(f"\n{'='*60}")
    print("Next Steps:")
    print(f"{'='*60}")
    print(f"1. Review training results in: {PROJECT}/{NAME}")
    print(f"2. Use the best model: {best_model_path}")
    print(f"3. Run Step 2 to convert .pt to .onnx:")
    print(f"   python step2_file_pt_to_file_onnx.py")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    main()
