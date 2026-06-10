import cv2
import time
from camera_feed import CameraFeed
from manifest_client import ManifestClient
from ocr_engine import OCREngine
from fingerprint_engine import FingerprintEngine
from zone_tracker import ZoneTracker
from voting_engine import VotingEngine

def main():
    print("Initializing ARGUS Engines...")
    
    # 1. Init clients and modules
    manifest_client = ManifestClient()
    manifest_client.fetch_manifest()
    
    ocr = OCREngine(manifest_client)
    fingerprint = FingerprintEngine()
    zone = ZoneTracker()
    voting = VotingEngine()
    
    camera = CameraFeed()
    camera.start()
    
    print("Starting Main Loop. Press 's' to simulate SCAN, 'v' to simulate VERIFY, 'q' to quit.")
    
    current_package_id = None
    
    try:
        while True:
            ret, frame = camera.get_frame()
            if not ret:
                continue
                
            # Render text on frame
            cv2.putText(frame, "ARGUS SYSTEM ACTIVE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("ARGUS Feed", frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
                
            elif key == ord('s'):
                print("\n--- SCAN POINT ---")
                # 1. OCR Extract
                ocr_res = ocr.process_frame(frame)
                dest = ocr_res.get("matched_destination")
                
                # Try to map destination to a mock package ID
                current_package_id = f"PKG-{int(time.time())}" # mock generation
                for item in manifest_client.manifest_data:
                    if item.get("destination", "").upper() == dest:
                        current_package_id = item["package_id"]
                        break
                        
                ocr_status = "MATCH" if dest else "MISMATCH"
                print(f"Scanned Destination: {dest} | OCR Status: {ocr_status} | Assigned ID: {current_package_id}")
                
                # 2. Capture Visual Fingerprint
                fingerprint.capture_reference(frame)
                print("Captured Visual Fingerprint Reference.")
                
            elif key == ord('v'):
                if not current_package_id:
                    print("Error: Scan a package first ('s').")
                    continue
                    
                print("\n--- VERIFICATION POINT (30 SECONDS LATER) ---")
                # 1. Check Fingerprint
                fp_match, fp_score = fingerprint.verify_target(frame)
                fp_status = "MATCH" if fp_match else "MISMATCH"
                print(f"Fingerprint Status: {fp_status} (Score: {fp_score:.2f})")
                
                # 2. Check Handler Zone
                z_status, _ = zone.process_frame(frame)
                print(f"Handler Zone Status: {z_status}")
                
                # 3. Voting Engine
                # We assume OCR passed at scan time if we had a match, but here we evaluate the overall disagreement.
                ocr_is_match = "MATCH" if dest else "MISMATCH" # (In a real system we'd persist the scan status)
                score = voting.process_verification(current_package_id, "MATCH", fp_status, z_status)
                print(f"Final Disagreement Score: {score}")
                print("--------------------------------------------------")
                
                # Reset for next package
                current_package_id = None
                
    except Exception as e:
        print(f"System Error: {e}")
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
