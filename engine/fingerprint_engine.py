import cv2
import numpy as np

class FingerprintEngine:
    def __init__(self, threshold=0.7):
        self.threshold = threshold
        self.reference_hist = None

    def capture_reference(self, frame):
        """Captures the initial image of the package at the scan point."""
        self.reference_hist = self._calculate_histogram(frame)
        return True

    def verify_target(self, frame):
        """Compares the current frame at the loading point against the reference."""
        if self.reference_hist is None:
            return False, 0.0

        target_hist = self._calculate_histogram(frame)
        
        # Compare histograms using intersection (values are naturally 0.0 to 1.0 when normalized)
        score = cv2.compareHist(self.reference_hist, target_hist, cv2.HISTCMP_INTERSECT)
        
        # Ensure score is between 0 and 1
        score = max(0.0, min(1.0, score))
        
        is_match = score >= self.threshold
        return is_match, score

    def _calculate_histogram(self, frame):
        """Calculates a normalized color histogram for a given frame."""
        # Convert to HSV for better color invariance to lighting
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Calculate histogram for Hue and Saturation channels
        hist = cv2.calcHist([hsv_frame], [0, 1], None, [50, 60], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return hist
