import cv2
import time

# MediaPipe is currently unstable on Python 3.13 Windows. 
# We wrap the import in a try-except to gracefully degrade to a mock tracker for the demo if it fails.
try:
    import mediapipe as mp
    if not hasattr(mp, 'solutions'):
        raise ImportError("MediaPipe loaded but 'solutions' module is missing (likely Python version incompatibility).")
    MP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MediaPipe unavailable ({e}). Falling back to Mock Zone Tracker.")
    MP_AVAILABLE = False


class ZoneTracker:
    def __init__(self):
        self.correct_zone = {"x_min": 0.5, "x_max": 1.0, "y_min": 0.0, "y_max": 1.0}
        
        if MP_AVAILABLE:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        else:
            self.pose = None

    def process_frame(self, frame):
        """Processes the frame. Uses MediaPipe if available, otherwise uses a mock."""
        if not MP_AVAILABLE:
            # Mock behavior: Toggle between Correct/Wrong gate based on time for demo purposes
            # Even seconds = Correct, Odd seconds = Wrong
            status = "Correct Gate" if int(time.time()) % 2 == 0 else "Wrong Gate"
            return status, True

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        if not results.pose_landmarks:
            return "No Handler Detected", False

        # Calculate center of mass of the handler using hips and shoulders
        landmarks = results.pose_landmarks.landmark
        
        l_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        r_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        l_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
        r_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]

        center_x = (l_shoulder.x + r_shoulder.x + l_hip.x + r_hip.x) / 4
        center_y = (l_shoulder.y + r_shoulder.y + l_hip.y + r_hip.y) / 4

        in_correct_zone = (
            self.correct_zone["x_min"] <= center_x <= self.correct_zone["x_max"] and
            self.correct_zone["y_min"] <= center_y <= self.correct_zone["y_max"]
        )

        status = "Correct Gate" if in_correct_zone else "Wrong Gate"
        return status, True
