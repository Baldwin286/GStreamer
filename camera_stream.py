# import cv2
# import socket
# import struct
# import pickle

# # Tạo socket server
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('0.0.0.0', 8485))  # Mở cổng 8485 cho mọi IP
# server_socket.listen(1)

# print("Đang chờ kết nối từ client...")
# conn, addr = server_socket.accept()
# print("Kết nối từ:", addr)

# cam = cv2.VideoCapture(0)

# while True:
#     ret, frame = cam.read()
#     data = pickle.dumps(frame)
#     message = struct.pack("Q", len(data)) + data
#     try:
#         conn.sendall(message)
#     except:
#         break

# cam.release()
# conn.close()
import cv2
import face_recognition
import numpy as np

face_detect = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
if face_detect.empty():
    raise IOError("Unable to load the face cascade classifier xml file")

# Mở camera
cap = cv2.VideoCapture(0)  # hoặc 0 / 1 tùy camera

# Cấu hình pipeline GStreamer để gửi qua UDP
gst_str = (
    "appsrc ! videoconvert ! "
    "x264enc tune=zerolatency bitrate=800 speed-preset=superfast ! "
    "rtph264pay config-interval=1 pt=96 ! "
    "udpsink host=192.168.1.101 port=5000"
)

# Khởi tạo VideoWriter (streamer)
out = cv2.VideoWriter(
    gst_str,
    cv2.CAP_GSTREAMER,
    0,          
    30,        
    # (640, 480), 
    (320, 240), 
    True        
)

if not cap.isOpened() or not out.isOpened():
    print("Không mở được camera hoặc GStreamer pipeline")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    resize_frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2GRAY)
    face_detection = face_detect.detectMultiScale(gray,1.3,5)
    for (x,y,w,h) in face_detection:
        cv2.rectangle(resize_frame,(x,y),(x+w,y+h),(0,0,255),10)
        gray_roi = gray[y:y+h, x:x+w]
        color_roi = resize_frame[y:y+h, x:x+w]
    # Gửi frame qua network
    out.write(resize_frame)

    # (Tuỳ chọn) xem preview ngay trên Pi để debug
    cv2.imshow("Preview", frame)
    cv2.imshow("Realtime Detection", resize_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

