import cv2
import threading
import time

class CameraFeed:
    def __init__(self, camera_index=0, target_fps=30):
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.cap = None
        self.frame = None
        self.ret = False
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        """Initializes the webcam capture and starts background thread."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera index {self.camera_index}")
        
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print(f"Camera started. Resolution: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        
        self.running = True
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while self.running:
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                with self.lock:
                    self.ret = ret
                    self.frame = frame
            time.sleep(0.001)

    def get_frame(self):
        """Reads the latest frame from the background thread."""
        with self.lock:
            if self.ret and self.frame is not None:
                return self.ret, self.frame.copy()
            return False, None

    def release(self):
        """Releases the webcam resource."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("Camera released.")

if __name__ == "__main__":
    # Test camera feed
    feed = CameraFeed()
    try:
        feed.start()
        print("Press 'q' to quit test feed.")
        while True:
            ret, frame = feed.get_frame()
            if not ret:
                print("Failed to get frame")
                break
            
            cv2.imshow("Test Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Camera error: {e}")
    finally:
        feed.release()
        cv2.destroyAllWindows()
