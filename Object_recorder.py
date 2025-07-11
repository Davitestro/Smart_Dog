from picamera2 import Picamera2
import cv2
import numpy as np
import tflite_runtime.interpreter as tftlite
import time
import os
from telegram import Bot
from free_space import get_disk_usage
from collections import deque


# === Connect to telegram bot ===

with open("api.env", 'r') as file:
    api = file.readlines()[0].strip()
    ses = file.readlines()[1].strip()


telegram_api = api
session = ses

bot = Bot(token=telegram_api)

# === Load TensorFlow Lite model ===
interpreter = tftlite.Interpreter(model_path="tftlite_model/detect.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

fps = 10  # Frames per second
pre_record_seconds = 3
pre_buffer = deque(maxlen=fps * pre_record_seconds)  # 30 frames for 3 seconds at 10 FPS

# === Initialize PiCamera2 ===
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (1024, 768)})
picam2.configure(config)
picam2.set_controls({"FrameDurationLimits": (33333, 33333)})
picam2.start()

# === Video Recording Setup ===
recording = False
video_writer = None
output_dir = "recordings"
os.makedirs(output_dir, exist_ok=True)
no_person_counter = 0
no_person_threshold = 100  # frames to wait before stopping recording

print("System initialized. Waiting for person...")

while True:
    frame = picam2.capture_array()
    pre_buffer.append(frame.copy())

    # Prepare image for detection
    img_resized = cv2.resize(frame, (300, 300))
    input_data = np.expand_dims(img_resized, axis=0).astype(np.uint8)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[0]['index'])[0]
    class_ids = interpreter.get_tensor(output_details[1]['index'])[0]
    scores = interpreter.get_tensor(output_details[2]['index'])[0]

    h, w, _ = frame.shape
    person_detected = False

    for i in range(len(scores)):
        if scores[i] > 0.5 and int(class_ids[i]) == 0:  # 0 = person class in COCO
            ymin, xmin, ymax, xmax = boxes[i]
            xmin = int(xmin * w)
            xmax = int(xmax * w)
            ymin = int(ymin * h)
            ymax = int(ymax * h)

            #cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            #cv2.putText(frame, 'Person', (xmin, ymin - 10),
                        #cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            person_detected = True

    if person_detected:
        no_person_counter = 0
        if not recording:
            day = time.strftime("%Y.%m.%d")
            moment = time.strftime("%H%M%S")
            try:
                os.mkdir(os.path.join(output_dir, day))
            except:
                print("Folder exits")

            filename = os.path.join(output_dir, day, f"person_{day+'-'+moment}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(filename, fourcc, 10, (w, h))
            print(f"🎥 Started recording: {filename}")
            for buffered_frame in pre_buffer:
                video_writer.write(buffered_frame)
            pre_buffer.clear()
            recording = True
    else:
        if recording:
            no_person_counter += 1
            if no_person_counter > no_person_threshold:
                print("Stopped recording")
                video_writer.release()
                recording = False
                video_writer = None
                print("Sending")
                try:
                    with open(filename, 'rb') as video_file:
                        bot.send_video(chat_id=session, video=video_file)
                    bot.send_message(chat_id=session, text=day+' '+time.strftime("%H:%M")+' ')
                    
                    if get_disk_usage() <= 10:
                        bot.send_message(chat_id=session, text=f"WARNING {int(get_disk_usage())}% disk has low free space")
                    
                    
                    print(f"Disk free space is {get_disk_usage()}%")
                    print("Video sent")
                except Exception as e:
                    print(f"Faile to send: {e}")

    if recording and video_writer:
        video_writer.write(frame)

    # Optional display (disabled for headless mode)
    # cv2.imshow("Object Detection", frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# Cleanup
if video_writer:
    video_writer.release()
    

cv2.destroyAllWindows()
