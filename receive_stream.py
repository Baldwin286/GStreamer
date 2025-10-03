import cv2
cap = cv2.VideoCapture(
    "udpsrc port=5000 caps=application/x-rtp,encoding-name=H264,payload=96 ! "
    "rtph264depay ! avdec_h264 ! videoconvert ! appsink",
    cv2.CAP_GSTREAMER
)