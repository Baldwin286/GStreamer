# import cv2

# pipeline = (
#     "udpsrc port=5000 "
#     "! application/x-rtp,encoding-name=H264,payload=96 "
#     "! rtph264depay "
#     "! avdec_h264 "
#     "! videoconvert "
#     "! appsink drop=1 sync=false"
# )

# cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

# if not cap.isOpened():
#     print("Không mở được stream, kiểm tra OpenCV có GStreamer support chưa.")
#     exit()

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("Không nhận được frame")
#         break

#     cv2.imshow("Drone Stream", frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import cv2
import numpy as np

Gst.init(None)

class GstReceiver:
    def __init__(self):
        self.pipeline_str = (
            "udpsrc port=5000 caps=\"application/x-rtp,encoding-name=H264,payload=96\" ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink"
        )
        self.pipeline = Gst.parse_launch(self.pipeline_str)
        self.appsink = self.pipeline.get_by_name("sink")
        self.appsink.set_property("emit-signals", True)
        self.appsink.connect("new-sample", self.on_new_sample)

        self.frame = None
        self.loop = GLib.MainLoop()

    def on_new_sample(self, sink):
        sample = sink.emit("pull-sample")
        buf = sample.get_buffer()
        caps = sample.get_caps()
        arr = buf.extract_dup(0, buf.get_size())
        # Chuyển dữ liệu thành numpy array
        frame = np.frombuffer(arr, np.uint8)
        # Lấy kích thước frame từ caps
        structure = caps.get_structure(0)
        width = structure.get_value('width')
        height = structure.get_value('height')
        frame = frame.reshape((height, width, 3))
        self.frame = frame
        return Gst.FlowReturn.OK

    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            self.loop.run()
        except:
            pass

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.loop.quit()

if __name__ == "__main__":
    receiver = GstReceiver()

    import threading
    threading.Thread(target=receiver.start, daemon=True).start()

    while True:
        if receiver.frame is not None:
            cv2.imshow("Stream", receiver.frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            receiver.stop()
            break
    cv2.destroyAllWindows()











