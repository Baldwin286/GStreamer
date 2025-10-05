import cv2
import time

# ========== CONFIG ==========
width = 320
height = 240
host_ip = "192.168.1.100"   
port = 5000

# ============================

def stream_and_detect_face():
    face_detect = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    if face_detect.empty():
        raise IOError("Unable to load the face cascade classifier xml file")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    frame_size = (width, height)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 30

    print(f"Camera: {width}x{height} @ {fps}fps")

    gst_str = (
        f"appsrc ! videoconvert ! "
        f"v4l2h264enc extra-controls=\"encode,profile=baseline\" ! "
        f"rtph264pay config-interval=1 pt=96 ! "
        f"udpsink host={host_ip} port={port}"
    )

    out = cv2.VideoWriter(gst_str, cv2.CAP_GSTREAMER, 0, fps, frame_size, True)

    if not cap.isOpened() or not out.isOpened():
        print("Camera/GStreamer pipeline Error!")
        print(gst_str)
        return

    prev_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        curr_time = time.time()
        fps_calc = 1 / (curr_time - prev_time)
        prev_time = curr_time
        print(f"FPS: {fps_calc:.2f}")

        resize_frame = cv2.resize(frame, frame_size, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(resize_frame, cv2.COLOR_BGR2GRAY)

        face_detection = face_detect.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in face_detection:
            cv2.rectangle(resize_frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
        
        out.write(resize_frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    stream_and_detect_face()
