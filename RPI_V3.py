import cv2
import time

width = 320
height = 240

def stream_and_detect():
    face_detect = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    if face_detect.empty():
        raise IOError("Unable to load the face cascade classifier xml file")

    # Pipeline GStreamer cho Raspberry Pi Camera Module 3
    gst_cam = (
        f"libcamerasrc ! video/x-raw,width={width},height={height},framerate=30/1 ! "
        "videoconvert ! appsink"
    )

    cap = cv2.VideoCapture(gst_cam, cv2.CAP_GSTREAMER)

    # Pipeline gửi stream qua UDP
    gst_str = (
        "appsrc ! videoconvert ! "
        "x264enc tune=zerolatency bitrate=1000 speed-preset=superfast ! "
        "rtph264pay config-interval=1 pt=96 ! "
        "udpsink host=192.168.1.100 port=5000"
    )

    frame_size = (width, height)
    fps = 30  # gán cứng vì nhiều khi libcamera không trả về FPS chính xác

    print(f"Camera: {width}x{height} @ {fps}fps")

    out = cv2.VideoWriter(
        gst_str,
        cv2.CAP_GSTREAMER,
        0,
        fps,
        frame_size,
        True
    )

    if not cap.isOpened() or not out.isOpened():
        print("Camera/GStreamer pipeline Error!")
        exit()

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
            cv2.rectangle(resize_frame, (x, y), (x + w, y + h), (0, 0, 255), 3)

        out.write(resize_frame)

    cap.release()
    out.release()

if __name__ == "__main__":
    stream_and_detect()
