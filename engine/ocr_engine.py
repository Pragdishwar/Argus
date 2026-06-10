import cv2
import pytesseract
from rapidfuzz import process, fuzz
from camera_feed import CameraFeed
from manifest_client import ManifestClient
import time

class OCREngine:
    def __init__(self, manifest_client: ManifestClient):
        self.manifest_client = manifest_client
        # Note: If Tesseract is not in your PATH, you need to point pytesseract to the executable here:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def extract_text(self, frame):
        """Preprocesses the frame and extracts text using Tesseract."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply thresholding to make text pop out
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Extract text
        custom_config = r'--oem 3 --psm 6'
        try:
            text = pytesseract.image_to_string(thresh, config=custom_config)
            return text.strip().upper()
        except pytesseract.TesseractNotFoundError:
            print("\n[MOCK OCR] Tesseract not installed. Simulating a scan for 'NEW YORK'.")
            import random
            # Simulate scanning one of the known destinations randomly to show the dashboard working
            dests = self.manifest_client.get_known_destinations()
            if dests:
                return random.choice(dests)
            return "NEW YORK"

    def correct_text_fuzzy(self, extracted_text):
        """Uses RapidFuzz to match the extracted text against known destinations."""
        known_destinations = self.manifest_client.get_known_destinations()
        if not known_destinations:
            return None, 0.0

        # Look for the best match in our known destinations list
        # RapidFuzz process.extractOne returns (match, score, index)
        match = process.extractOne(
            extracted_text, 
            known_destinations, 
            scorer=fuzz.partial_ratio,
            score_cutoff=70.0 # Only consider matches with >70% similarity
        )
        
        if match:
            best_match_str, score, _ = match
            return best_match_str, score
        return None, 0.0

    def process_frame(self, frame):
        """Main pipeline for a single frame: Extract -> Correct."""
        raw_text = self.extract_text(frame)
        
        if not raw_text:
            return None, "No text found"

        matched_dest, score = self.correct_text_fuzzy(raw_text)
        
        return {
            "raw_text": raw_text,
            "matched_destination": matched_dest,
            "confidence_score": score
        }

if __name__ == "__main__":
    # Setup clients
    manifest = ManifestClient()
    # Fetch once for testing instead of polling
    manifest.fetch_manifest()
    
    camera = CameraFeed()
    ocr = OCREngine(manifest)

    try:
        camera.start()
        print("Starting OCR test. Hold a destination label up to the camera. Press 'q' to quit.")
        
        last_process_time = time.time()
        
        while True:
            ret, frame = camera.get_frame()
            if not ret:
                break
                
            # Process OCR every 1 second to avoid spamming / lag
            current_time = time.time()
            if current_time - last_process_time > 1.0:
                result = ocr.process_frame(frame)
                if result and result.get("matched_destination"):
                    print(f"Matched: {result['matched_destination']} (Confidence: {result['confidence_score']:.1f}%) | Raw: {result['raw_text'][:20]}...")
                last_process_time = current_time

            # Show the live feed
            cv2.imshow("OCR Engine Live", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error in OCR loop: {e}")
    finally:
        camera.release()
        cv2.destroyAllWindows()
