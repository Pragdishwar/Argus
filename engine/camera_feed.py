import cv2

class CameraFeed:
    def __init__(self, camera_index=0, target_fps=15):
        self.camera_index = camera_index
        self.target_fps = target_fps
        self.cap = None

    def start(self):
        """Initializes the webcam capture."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera index {self.camera_index}")
        
        # Try to set framerate (Note: some webcams ignore this)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        # Try to set resolution to 720p as per SRS
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        print(f"Camera started. Resolution: {self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

    def get_frame(self):
        """Reads a frame from the webcam. Returns (success, frame)."""
        if self.cap is None or not self.cap.isOpened():
            return False, None
        ret, frame = self.cap.read()
        return ret, frame

    def release(self):
        """Releases the webcam resource."""
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
