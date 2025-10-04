import cv2
import face_recognition
import numpy as np

face_detect = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
if face_detect.empty():
    raise IOError("Unable to load the face cascade classifier xml file")

cap = cv2.VideoCapture(0)  
# gst_str = (
#     "appsrc ! videoconvert ! "
#     "x264enc tune=zerolatency bitrate=4000 speed-preset=superfast ! "
#     "rtph264pay config-interval=1 pt=96 ! "
#     "udpsink host=192.168.1.100 port=5000"
# )

#frame_size = (640, 480)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = int(cap.get(cv2.CAP_PROP_FPS))

frame_size = (width, height)
if fps == 0:
    fps = 30

print(f"Camera: {width}x{height} @ {fps}fps")

gst_str = (
    "appsrc ! videoconvert ! video/x-raw,format=NV12,width={w},height={h},framerate={fps}/1 ! "
    "v4l2h264enc extra-controls=\"encode,frame_level_rate_control_enable=1,video_bitrate=4000000\" ! "
    "h264parse ! rtph264pay config-interval=1 pt=96 ! "
    "udpsink host=192.168.1.100 port=5000"
).format(w=width, h=height, fps=fps)

out = cv2.VideoWriter(
    gst_str,
    cv2.CAP_GSTREAMER,
    0,          
    # 30,        
    # (640, 480), 
    # (320, 240),
    fps,
    frame_size, 
    True        
)

if not cap.isOpened() or not out.isOpened():
    print("Camera/GStreamer pipeline Error!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # resize_frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    resize_frame = cv2.resize(frame, frame_size)
    gray = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2GRAY)
    face_detection = face_detect.detectMultiScale(gray,1.3,5)
    for (x,y,w,h) in face_detection:
        cv2.rectangle(resize_frame,(x,y),(x+w,y+h),(0,0,255),3)
        gray_roi = gray[y:y+h, x:x+w]
        color_roi = resize_frame[y:y+h, x:x+w]
    
    out.write(resize_frame)

    # cv2.imshow("Preview", frame)
    # cv2.imshow("Realtime Detection", resize_frame)

    # key = cv2.waitKey(1) & 0xFF
    # if key == ord('q') or key == 27:
    #     break

cap.release()
out.release()
# cv2.destroyAllWindows()

