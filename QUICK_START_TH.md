# คู่มือการใช้งาน (Quick Reference Guide)
# YOLO Ear Detection - Raspberry Pi 5 + Hailo AI Kit

## 🚀 เริ่มต้นอย่างรวดเร็ว (Quick Start)

### บน MacOS (สำหรับเทรนโมเดล)

```bash
# 1. ติดตั้ง environment
./setup_macos.sh
source .venv/bin/activate

# 2. เทรนโมเดล
python step1_train_model_to_pt.py

# 3. แปลงเป็น ONNX
python step2_file_pt_to_file_onnx.py

# 4. ตั้งค่า Docker
cd docker
docker-compose build
docker-compose up -d

# 5. เข้าไปใน Docker container
docker-compose exec hailo-compiler bash

# 6. แปลง ONNX เป็น HEF (ในcontainer)
python3 step3_file_onnx_to_file_hef.py
exit

# 7. ปิด Docker
docker-compose down
cd ..

# 8. ส่งโมเดลไป Raspberry Pi
scp models/hef/ear_detection.hef pi@raspberrypi:~/
scp step4_code_run_on_pi5.py pi@raspberrypi:~/
```

### บน Raspberry Pi 5

```bash
# 1. ติดตั้ง environment
chmod +x setup_pi5.sh
./setup_pi5.sh

# 2. รันโปรแกรมตรวจจับ
python3 step4_code_run_on_pi5.py

# กด 'q' เพื่อออก
```

## 📁 โครงสร้างไฟล์

```
📦 ear/
├── 🐍 step1_train_model_to_pt.py      # เทรนโมเดล YOLO
├── 🔄 step2_file_pt_to_file_onnx.py   # แปลง .pt → .onnx
├── 🐳 step3_file_onnx_to_file_hef.py  # แปลง .onnx → .hef (Docker)
├── 🎥 step4_code_run_on_pi5.py        # รันบน Raspberry Pi 5
├── 🐳 docker/                          # Docker สำหรับ Hailo compiler
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── README.md
├── 📊 data.yaml                        # ข้อมูล dataset
├── 📋 requirements.txt                 # สำหรับ MacOS
├── 📋 requirements_pi5.txt             # สำหรับ Raspberry Pi
├── 🔧 setup_macos.sh                   # ติดตั้งบน MacOS
├── 🔧 setup_pi5.sh                     # ติดตั้งบน Pi5
├── 🚀 run_all.sh                       # รันทุกอย่างอัตโนมัติ
└── 📖 README.md                        # คู่มือฉบับเต็ม
```

## 🔧 คำสั่งที่ใช้บ่อย

### MacOS - การเทรน

```bash
# เปิด virtual environment
source .venv/bin/activate

# เทรนโมเดล (ปรับค่าได้ในไฟล์)
python step1_train_model_to_pt.py

# ดูผลลัพธ์การเทรน
open runs/train/ear_detection/

# แปลงโมเดล
python step2_file_pt_to_file_onnx.py
```

### Docker - แปลงโมเดล

```bash
# เข้า docker directory
cd docker

# สร้าง image
docker-compose build

# เริ่ม container
docker-compose up -d

# เข้าไปใน container
docker-compose exec hailo-compiler bash

# แปลงโมเดล (ใน container)
python3 step3_file_onnx_to_file_hef.py

# ออกจาก container
exit

# หยุด container
docker-compose down
```

### Raspberry Pi 5 - การใช้งาน

```bash
# รันโปรแกรม
python3 step4_code_run_on_pi5.py

# รันและบันทึกวิดีโอ (แก้ในไฟล์: SAVE_VIDEO = True)
python3 step4_code_run_on_pi5.py

# ดูข้อมูล Hailo
hailo-info

# ตรวจสอบกล้อง
libcamera-hello
```

## ⚙️ การปรับแต่ง

### การเทรน (step1_train_model_to_pt.py)

```python
MODEL_SIZE = 'yolov8n.pt'  # n=เล็กสุด, s, m, l, x=ใหญ่สุด
EPOCHS = 100               # จำนวนรอบการเทรน
BATCH = 16                 # ขนาด batch (ลดถ้า RAM ไม่พอ)
IMGSZ = 640               # ขนาดภาพ
```

### การตรวจจับ (step4_code_run_on_pi5.py)

```python
CONF_THRESHOLD = 0.25  # ความมั่นใจขั้นต่ำ (0-1)
IOU_THRESHOLD = 0.45   # IoU threshold สำหรับ NMS
SAVE_VIDEO = False     # True = บันทึกวิดีโอ
DISPLAY_FPS = True     # แสดง FPS
```

## 🎯 เป้าหมายประสิทธิภาพ

| ขั้นตอน | อุปกรณ์ | เวลา | หมายเหตุ |
|---------|---------|------|----------|
| เทรน | MacOS M1/M2 | 2-3 ชม. | 100 epochs |
| แปลง .pt→.onnx | MacOS | 1-2 นาที | - |
| แปลง .onnx→.hef | Docker | 5-10 นาที | ขึ้นกับขนาดโมเดล |
| ตรวจจับ | Pi5+Hailo | 30-60 FPS | Real-time |

## 🐛 แก้ปัญหา

### บน MacOS

**ปัญหา**: MPS not available
```bash
# ใช้ CPU แทน (ช้ากว่า)
# โมเดลจะเปลี่ยนอัตโนมัติ
```

**ปัญหา**: Out of memory
```bash
# ลด BATCH ในไฟล์ step1
BATCH = 8  # หรือ 4
```

**ปัญหา**: Docker build fail
```bash
# ให้ RAM มากขึ้นใน Docker Desktop
# Settings → Resources → Memory: 4GB+
```

### บน Raspberry Pi 5

**ปัญหา**: กล้องไม่ทำงาน
```bash
# ตรวจสอบกล้อง
libcamera-hello

# ติดตั้ง Picamera2
sudo apt-get install python3-picamera2
```

**ปัญหา**: Hailo not found
```bash
# ติดตั้ง Hailo software
# ดูที่: https://github.com/hailo-ai/hailo-rpi5-examples
```

**ปัญหา**: ช้า/lag
```bash
# ตรวจสอบว่า Hailo driver ทำงาน
hailo-info

# ลองรีบูต
sudo reboot
```

## 📊 ตัวอย่างผลลัพธ์

### การเทรน
```
Epoch 100/100: 100%|█████| 100/100
  mAP50: 0.95
  mAP50-95: 0.78
  Precision: 0.92
  Recall: 0.89
✓ Model saved: runs/train/ear_detection/weights/best.pt
```

### การตรวจจับ
```
FPS: 45.2
Detections: 2
✓ ear: 0.89
✓ ear: 0.92
```

## 🔗 ลิงก์ที่เป็นประโยชน์

- [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com/)
- [Hailo AI RPi5 Examples](https://github.com/hailo-ai/hailo-rpi5-examples)
- [Picamera2 Manual](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Raspberry Pi 5 Docs](https://www.raspberrypi.com/documentation/computers/raspberry-pi-5.html)

## 💡 เคล็ดลับ

1. **เทรนโมเดล**: ใช้ YOLOv8n (nano) สำหรับความเร็ว, YOLOv8m (medium) สำหรับความแม่นยำ
2. **Dataset**: ข้อมูลมากกว่า 1000 ภาพจะได้ผลดีกว่า
3. **Augmentation**: เปิดใช้ในไฟล์ step1 เพื่อเพิ่มความหลากหลาย
4. **Raspberry Pi**: ใช้ power supply 5V 5A สำหรับเสถียรภาพ
5. **Cooling**: ใส่พัดลม/heatsink บน Pi5 เพื่อประสิทธิภาพดีกว่า

## 📞 การสนับสนุน

หากมีปัญหา:
1. ตรวจสอบ README.md (คู่มือฉบับเต็ม)
2. ดู Troubleshooting section
3. ตรวจสอบ official documentation
4. เปิด issue บน GitHub

---

**สร้างโดย**: YOLO Ear Detection Pipeline
**ฮาร์ดแวร์**: Raspberry Pi 5 + Hailo AI Kit (13 TOPS)
**ซอฟต์แวร์**: YOLOv8 + Ultralytics + Hailo Dataflow Compiler
