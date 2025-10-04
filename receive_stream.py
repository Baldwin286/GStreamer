# import cv2
# cap = cv2.VideoCapture(
#     "udpsrc port=5000 caps=application/x-rtp,encoding-name=H264,payload=96 ! "
#     "rtph264depay ! avdec_h264 ! videoconvert ! appsink",
#     cv2.CAP_GSTREAMER
# )
import cv2

gst_str = (
    "udpsrc port=5000 caps=application/x-rtp,encoding-name=H264,payload=96 ! "
    "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
)

cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Không nhận được frame")
        break

    # Hiển thị frame (đã có bounding box từ Pi)
    cv2.imshow("Stream từ Pi", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
