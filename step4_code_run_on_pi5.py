import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import os
import numpy as np
import cv2
import hailo
import requests
import time
from pathlib import Path

from hailo_apps.hailo_app_python.core.common.buffer_utils import get_caps_from_pad, get_numpy_from_buffer
from hailo_apps.hailo_app_python.core.gstreamer.gstreamer_app import app_callback_class
from hailo_apps.hailo_app_python.apps.detection.detection_pipeline import GStreamerDetectionApp

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1447260795359596598/z0AycOqXHn3Douayq5BRKbZj_p3GdvrWncBbJ6hZAzFRzzwK9LpyVkmH9wNFvO0dP2RU"
TARGET_LABEL = "ear"
CONFIDENCE_THRESHOLD = 0.70
REQUIRED_CONFIRMATIONS = 5


class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.last_sent_count = 0
        self.stable_count = 0
        self.confirmation_frames = 0

    def send_discord_alert(self, frame, current_count, confidence):
        if current_count > self.last_sent_count:
            print(f"[*] Dispatching Alert: New count {current_count} exceeds previous {self.last_sent_count}")
            
            image_path = "/tmp/alert.jpg"
            cv2.imwrite(image_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            
            with open(image_path, "rb") as f:
                payload = {
                    "content": f"**New Detection Event**\nCurrent Count: {current_count}\nConfidence: {confidence*100:.1f}%"
                }
                files = {"file": ("detection.jpg", f, "image/jpeg")}
                try:
                    res = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files, timeout=10)
                    if res.status_code in [200, 204]:
                        self.last_sent_count = current_count
                except Exception as e:
                    print(f"[!] HTTP Error: {e}")
        
        elif current_count < self.last_sent_count:
            self.last_sent_count = current_count

def app_callback(pad, info, user_data):
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    user_data.increment()
    format, width, height = get_caps_from_pad(pad)
    frame = get_numpy_from_buffer(buffer, format, width, height) if format else None

    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    current_frame_ear_count = 0
    max_confidence = 0

    for detection in detections:
        label = detection.get_label()
        bbox = detection.get_bbox()
        confidence = detection.get_confidence()

        if TARGET_LABEL in label.lower() and confidence > CONFIDENCE_THRESHOLD:
            box_w = bbox.xmax() - bbox.xmin()
            box_h = bbox.ymax() - bbox.ymin()
            aspect_ratio = box_h / box_w if box_w > 0 else 0
            
            if aspect_ratio > 0.9 and box_h < 0.6:
                current_frame_ear_count += 1
                if confidence > max_confidence:
                    max_confidence = confidence
                
                if frame is not None:
                    x_min, y_min = int(bbox.xmin() * width), int(bbox.ymin() * height)
                    x_max, y_max = int(bbox.xmax() * width), int(bbox.ymax() * height)
                    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

    if current_frame_ear_count != user_data.stable_count:
        user_data.confirmation_frames = 0
        user_data.stable_count = current_frame_ear_count
    else:
        user_data.confirmation_frames += 1

    if user_data.confirmation_frames >= REQUIRED_CONFIRMATIONS:
        if user_data.stable_count > 0 and frame is not None:
            user_data.send_discord_alert(frame, user_data.stable_count, max_confidence)
        elif user_data.stable_count == 0:
            user_data.last_sent_count = 0

    if frame is not None:
        cv2.putText(frame, f"Confirmed Count: {user_data.stable_count}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        user_data.set_frame(display_frame)

    return Gst.PadProbeReturn.OK

if __name__ == "__main__":
    import os
    import subprocess
    from pathlib import Path

    try:
        subprocess.run(['v4l2-ctl', '-d', '/dev/v4l-subdev0', '--set-ctrl=focus_automatic_continuous=1'], check=False)
        print(" ^=^t^m Forcing Camera Auto Focus via V4L2...")
    except Exception as e:
        print(f" ^z   ^o Could not force AF: {e}")

    project_root = Path(__file__).resolve().parent.parent
    os.environ["HAILO_ENV_FILE"] = str(project_root / ".env")
    
    user_data = user_app_callback_class()
    app = GStreamerDetectionApp(app_callback, user_data)
    
    app.batch_size = 2 

    print(" ^=^z^` System started! Moving lens to find focus...")
    app.run()

