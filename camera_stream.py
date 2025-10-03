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
    0,          # fourcc (bỏ qua vì GStreamer lo)
    30,         # fps
    (640, 480), # kích thước khung hình
    True        # màu (True = BGR)
)

if not cap.isOpened() or not out.isOpened():
    print("Không mở được camera hoặc GStreamer pipeline")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Chuyển sang RGB để face_recognition xử lý
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Tìm tất cả khuôn mặt trong frame
    face_locations = face_recognition.face_locations(rgb_frame)

    # Vẽ khung cho từng khuôn mặt
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Gửi frame qua network
    out.write(frame)

    # (Tuỳ chọn) xem preview ngay trên Pi để debug
    cv2.imshow("Preview", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

