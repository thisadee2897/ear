# -*- coding: utf-8 -*-
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
import requests
import threading
from pathlib import Path
import time

from hailo_apps.hailo_app_python.core.common.buffer_utils import get_caps_from_pad, get_numpy_from_buffer
from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.hailo_app_python.apps.detection.detection_pipeline import GStreamerDetectionApp

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1447260795359596598/z0AycOqXHn3Douayq5BRKbZj_p3GdvrWncBbJ6hZAzFRzzwK9LpyVkmH9wNFvO0dP2RU"
TARGET_LABEL = "ear"
CONFIDENCE_THRESHOLD = 0.75  # Balanced threshold

class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.last_notified_id = -1 

    def is_skin_color(self, crop_frame):
        if crop_frame is None or crop_frame.size == 0:
            return False
        # Convert to HSV (Hue, Saturation, Value)
        hsv_frame = cv2.cvtColor(crop_frame, cv2.COLOR_RGB2HSV)
        
        # Human skin tone range in HSV
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([25, 255, 255], dtype=np.uint8)
        
        mask = cv2.inRange(hsv_frame, lower_skin, upper_skin)
        skin_percentage = (cv2.countNonZero(mask) / (crop_frame.shape[0] * crop_frame.shape[1])) * 100
        
        # Returns True if more than 25% of the object is skin-colored
        return skin_percentage > 25

    def send_discord_thread(self, frame, obj_id, confidence):
        try:
            h, w = frame.shape[:2]
            scale = 1080 / w
            small_frame = cv2.resize(frame, (1080, int(h * scale)))
            small_frame_bgr = cv2.cvtColor(small_frame, cv2.COLOR_RGB2BGR)
            
            image_path = f"/tmp/ear_{obj_id}.jpg"
            cv2.imwrite(image_path, small_frame_bgr)
            
            with open(image_path, "rb") as f:
                payload = {"content": f"🎯 **Human Ear Verified**\nID: {obj_id}\nConfidence: {confidence*100:.1f}%"}
                files = {"file": ("ear.jpg", f, "image/jpeg")}
                requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files, timeout=8)
            
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            print(f"Discord Error: {e}")

    def send_discord_alert(self, frame, obj_id, confidence):
        thread = threading.Thread(target=self.send_discord_thread, args=(frame.copy(), obj_id, confidence))
        thread.daemon = True
        thread.start()

def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None: return Gst.PadProbeReturn.OK
    user_data.increment()
    
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)
    
    format, width, height = get_caps_from_pad(pad)

    for detection in detections:
        label = detection.get_label()
        confidence = detection.get_confidence()
        
        if TARGET_LABEL in label.lower() and confidence >= CONFIDENCE_THRESHOLD:
            # Get Unique ID
            tracking_info = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
            obj_id = tracking_info[0].get_id() if tracking_info else -1
            
            if obj_id > user_data.last_notified_id:
                # Get Frame for color verification
                frame = get_numpy_from_buffer(buffer, format, width, height)
                if frame is not None:
                    # Crop detection area
                    bbox = detection.get_bbox()
                    y1, x1, y2, x2 = int(bbox.ymin() * height), int(bbox.xmin() * width), \
                                     int(bbox.ymax() * height), int(bbox.xmax() * width)
                    crop = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]
                    
                    # SKIN TONE CHECK (The Earmuff Killer)
                    if user_data.is_skin_color(crop):
                        user_data.last_notified_id = obj_id 
                        user_data.send_discord_alert(frame, obj_id, confidence)
                        break 
                    else:
                        print(f"🚫 Blocked: Object {obj_id} is not skin-colored (Likely earmuff).")
            
    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    
    def get_fullscreen_pipeline():
        pipeline = app.get_pipeline_string()
        # Force Fullscreen on AOC
        if 'video-sink="autovideosink"' in pipeline:
            pipeline = pipeline.replace('video-sink="autovideosink"', 'video-sink="autovideosink fullscreen=true"')
        return pipeline

    app.get_pipeline_string = get_fullscreen_pipeline
    app.run()