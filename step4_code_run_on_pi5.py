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
import subprocess
import time

from hailo_apps.hailo_app_python.core.common.buffer_utils import get_caps_from_pad, get_numpy_from_buffer
from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.hailo_app_python.apps.detection.detection_pipeline import GStreamerDetectionApp

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1447260795359596598/z0AycOqXHn3Douayq5BRKbZj_p3GdvrWncBbJ6hZAzFRzzwK9LpyVkmH9wNFvO0dP2RU"
TARGET_LABEL = "ear"
CONFIDENCE_THRESHOLD = 0.70

class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.last_notified_id = -1 

    def send_discord_thread(self, frame, obj_id, confidence):
        try:
            h, w = frame.shape[:2]
            scale = 1080 / w
            small_frame = cv2.resize(frame, (1080, int(h * scale)))
            small_frame_bgr = cv2.cvtColor(small_frame, cv2.COLOR_RGB2BGR)
            
            image_path = f"/tmp/ear_{obj_id}.jpg"
            cv2.imwrite(image_path, small_frame_bgr)
            
            with open(image_path, "rb") as f:
                payload = {"content": f" ^=^t^t **New Ear Detected**\nObject ID: {obj_id}\nConfidence: {confidence*100:.1f}%"}
                files = {"file": ("ear.jpg", f, "image/jpeg")}
                r = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files, timeout=8)
                if r.status_code in [200, 204]:
                    print(f"Discord ID {obj_id} Sent")
            
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
    
    for detection in detections:
        label = detection.get_label()
        confidence = detection.get_confidence()
        
        tracking_info = detection.get_objects_typed(hailo.HAILO_UNIQUE_ID)
        obj_id = tracking_info[0].get_id() if tracking_info else -1
        
        if TARGET_LABEL in label.lower() and confidence >= CONFIDENCE_THRESHOLD:
            if obj_id > user_data.last_notified_id:
                format, width, height = get_caps_from_pad(pad)
                frame = get_numpy_from_buffer(buffer, format, width, height) if format else None
                
                if frame is not None:
                    user_data.last_notified_id = obj_id 
                    user_data.send_discord_alert(frame, obj_id, confidence)
                    break 
            
    return Gst.PadProbeReturn.OK

def force_shutter_v4l2():
    time.sleep(8) 
    print(" ^=^z^` NUCLEAR STRIKE: Forcing Hardware Controls...")
    try:
        subprocess.run(['v4l2-ctl', '-d', '/dev/v4l-subdev0', '--set-ctrl', 'exposure=2000'], check=False)
        subprocess.run(['v4l2-ctl', '-d', '/dev/v4l-subdev0', '--set-ctrl', 'analogue_gain=150'], check=False)
        #   ^{     ^t Auto Exposure
        subprocess.run(['v4l2-ctl', '-d', '/dev/v4l-subdev0', '--set-ctrl', 'auto_exposure=1'], check=False) 
        print(" ^|^e STRIKE COMPLETE: Hardware values should be locked.")
    except Exception as e:
        print(f" ^}^l Error during strike: {e}")

if __name__ == "__main__":
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)   
    t = threading.Thread(target=force_shutter_v4l2)
    t.daemon = True
    t.start()
    
    app.run()
