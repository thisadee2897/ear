#!/usr/bin/env python3
"""
Step 4: Run YOLO Ear Detection on Raspberry Pi 5 + Hailo AI Kit
Uses Picamera2 for camera input and Hailo-8L for inference.
"""

import numpy as np
import cv2
from picamera2 import Picamera2
from hailo_platform import (HEF, VDevice, HailoStreamInterface, 
                            InferVStreams, ConfigureParams)
import time
from pathlib import Path

class HailoYOLODetector:
    """YOLO Detector using Hailo AI accelerator"""
    
    def __init__(self, hef_path, conf_threshold=0.25, iou_threshold=0.45):
        """
        Initialize Hailo YOLO Detector
        
        Args:
            hef_path: Path to .hef model file
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
        """
        self.hef_path = hef_path
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
        # Class names
        self.class_names = ['ear']  # Update based on your model
        
        # Load HEF model
        print(f"Loading HEF model: {hef_path}")
        self.hef = HEF(hef_path)
        
        # Get target device (Hailo-8L)
        self.target = VDevice()
        
        # Configure network group
        self.network_group = self.target.configure(self.hef)[0]
        self.network_group_params = self.network_group.create_params()
        
        # Get input/output shapes
        self.input_vstream_info = self.hef.get_input_vstream_infos()[0]
        self.output_vstream_info = self.hef.get_output_vstream_infos()[0]
        
        # Get input shape (height, width)
        self.input_shape = self.input_vstream_info.shape
        print(f"Input shape: {self.input_shape}")
        print(f"Model loaded successfully!")
    
    def preprocess(self, image):
        """
        Preprocess image for YOLO
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Preprocessed image ready for inference
        """
        # Get model input size
        height, width = self.input_shape[0], self.input_shape[1]
        
        # Resize image
        resized = cv2.resize(image, (width, height))
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1]
        normalized = rgb.astype(np.float32) / 255.0
        
        # Add batch dimension
        input_data = np.expand_dims(normalized, axis=0)
        
        return input_data
    
    def postprocess(self, outputs, orig_shape):
        """
        Postprocess YOLO outputs
        
        Args:
            outputs: Raw model outputs
            orig_shape: Original image shape (H, W)
            
        Returns:
            List of detections [x1, y1, x2, y2, confidence, class_id]
        """
        # This is a simplified version - adjust based on your YOLO output format
        detections = []
        
        # Parse outputs (format depends on YOLO version)
        # Typically: [batch, num_boxes, 5+num_classes] where 5 = x, y, w, h, conf
        
        for output in outputs:
            # Filter by confidence
            mask = output[..., 4] > self.conf_threshold
            filtered = output[mask]
            
            if len(filtered) == 0:
                continue
            
            # Extract boxes and scores
            boxes = filtered[..., :4]
            scores = filtered[..., 4:5] * filtered[..., 5:]
            
            # Get class with highest score
            class_ids = np.argmax(scores, axis=1)
            confidences = np.max(scores, axis=1)
            
            # Convert to corner format and scale to original image
            orig_h, orig_w = orig_shape
            input_h, input_w = self.input_shape[0], self.input_shape[1]
            
            for box, conf, cls_id in zip(boxes, confidences, class_ids):
                # YOLO format: [x_center, y_center, width, height]
                x_center, y_center, w, h = box
                
                # Convert to corner format
                x1 = (x_center - w/2) * orig_w / input_w
                y1 = (y_center - h/2) * orig_h / input_h
                x2 = (x_center + w/2) * orig_w / input_w
                y2 = (y_center + h/2) * orig_h / input_h
                
                detections.append([x1, y1, x2, y2, conf, cls_id])
        
        # Apply NMS
        if len(detections) > 0:
            detections = self.non_max_suppression(np.array(detections))
        
        return detections
    
    def non_max_suppression(self, detections):
        """Apply Non-Maximum Suppression"""
        if len(detections) == 0:
            return []
        
        boxes = detections[:, :4]
        scores = detections[:, 4]
        
        # Convert to format expected by cv2.dnn.NMSBoxes
        boxes_list = boxes.tolist()
        scores_list = scores.tolist()
        
        indices = cv2.dnn.NMSBoxes(
            boxes_list, scores_list, 
            self.conf_threshold, self.iou_threshold
        )
        
        if len(indices) > 0:
            return detections[indices.flatten()]
        return []
    
    def infer(self, image):
        """
        Run inference on image
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            List of detections
        """
        # Preprocess
        input_data = self.preprocess(image)
        
        # Run inference
        with InferVStreams(self.network_group, self.network_group_params) as infer_pipeline:
            input_dict = {self.input_vstream_info.name: input_data}
            
            with self.network_group.activate(self.network_group_params):
                output_dict = infer_pipeline.infer(input_dict)
        
        # Postprocess
        outputs = list(output_dict.values())
        detections = self.postprocess(outputs, image.shape[:2])
        
        return detections
    
    def draw_detections(self, image, detections):
        """
        Draw detection boxes on image
        
        Args:
            image: Input image
            detections: List of detections
            
        Returns:
            Image with drawn detections
        """
        for det in detections:
            x1, y1, x2, y2, conf, cls_id = det
            
            # Convert to integers
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cls_id = int(cls_id)
            
            # Get class name
            class_name = self.class_names[cls_id] if cls_id < len(self.class_names) else f"Class_{cls_id}"
            
            # Draw box
            color = (0, 255, 0)  # Green
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name}: {conf:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            
            # Background for text
            cv2.rectangle(
                image, 
                (x1, y1 - label_size[1] - 10), 
                (x1 + label_size[0], y1), 
                color, 
                -1
            )
            
            # Draw text
            cv2.putText(
                image, label, 
                (x1, y1 - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, (0, 0, 0), 2
            )
        
        return image

def main():
    print("="*60)
    print("STEP 4: YOLO Ear Detection on Raspberry Pi 5")
    print("Using Hailo AI Kit + Picamera2")
    print("="*60)
    
    # Configuration
    HEF_MODEL_PATH = 'models/hef/ear_detection.hef'  # Update this path
    CONF_THRESHOLD = 0.25
    IOU_THRESHOLD = 0.45
    DISPLAY_FPS = True
    SAVE_VIDEO = False
    OUTPUT_VIDEO = 'output_detection.mp4'
    
    # Check if HEF model exists
    if not Path(HEF_MODEL_PATH).exists():
        print(f"\n❌ Error: HEF model not found: {HEF_MODEL_PATH}")
        print("\nPlease ensure you have:")
        print("1. Converted your model to HEF format using step3_file_onnx_to_file_hef.py")
        print("2. Copied the HEF file to Raspberry Pi 5")
        print("3. Updated HEF_MODEL_PATH in this script")
        return
    
    print(f"\nConfiguration:")
    print(f"  HEF Model: {HEF_MODEL_PATH}")
    print(f"  Confidence Threshold: {CONF_THRESHOLD}")
    print(f"  IoU Threshold: {IOU_THRESHOLD}")
    
    # Initialize Hailo detector
    print(f"\n{'='*60}")
    print("Initializing Hailo AI detector...")
    print(f"{'='*60}")
    detector = HailoYOLODetector(HEF_MODEL_PATH, CONF_THRESHOLD, IOU_THRESHOLD)
    
    # Initialize Picamera2
    print(f"\n{'='*60}")
    print("Initializing Picamera2...")
    print(f"{'='*60}")
    
    picam2 = Picamera2()
    
    # Configure camera
    camera_config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam2.configure(camera_config)
    
    # Start camera
    picam2.start()
    print("✓ Camera started")
    
    # Video writer (if saving)
    video_writer = None
    if SAVE_VIDEO:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, 20.0, (640, 480))
        print(f"✓ Saving video to: {OUTPUT_VIDEO}")
    
    # FPS calculation
    fps_counter = 0
    fps_start_time = time.time()
    fps = 0
    
    print(f"\n{'='*60}")
    print("Starting detection... Press 'q' to quit")
    print(f"{'='*60}\n")
    
    try:
        while True:
            # Capture frame
            frame = picam2.capture_array()
            
            # Convert RGB to BGR for OpenCV
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Run detection
            detections = detector.infer(frame_bgr)
            
            # Draw detections
            output_frame = detector.draw_detections(frame_bgr.copy(), detections)
            
            # Calculate FPS
            fps_counter += 1
            if fps_counter >= 30:
                fps_end_time = time.time()
                fps = fps_counter / (fps_end_time - fps_start_time)
                fps_counter = 0
                fps_start_time = time.time()
            
            # Draw FPS
            if DISPLAY_FPS:
                cv2.putText(
                    output_frame, 
                    f"FPS: {fps:.1f}", 
                    (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0), 2
                )
            
            # Draw detection count
            cv2.putText(
                output_frame, 
                f"Detections: {len(detections)}", 
                (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (0, 255, 0), 2
            )
            
            # Save video frame
            if video_writer is not None:
                video_writer.write(output_frame)
            
            # Display frame
            cv2.imshow('Ear Detection - Raspberry Pi 5 + Hailo', output_frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Cleanup
        print("\n" + "="*60)
        print("Cleaning up...")
        print("="*60)
        
        picam2.stop()
        cv2.destroyAllWindows()
        
        if video_writer is not None:
            video_writer.release()
            print(f"✓ Video saved to: {OUTPUT_VIDEO}")
        
        print("✓ Done!")

if __name__ == '__main__':
    main()
