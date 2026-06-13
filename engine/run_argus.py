import cv2
import time
import base64
import numpy as np
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from camera_feed import CameraFeed
from manifest_client import ManifestClient
from ocr_engine import OCREngine
from fingerprint_engine import FingerprintEngine
from zone_tracker import ZoneTracker
from voting_engine import VotingEngine

app = Flask(__name__)
CORS(app) # Allow Next.js frontend to call endpoints

print("Initializing ARGUS Engines...")
manifest_client = ManifestClient()
manifest_client.fetch_manifest()

ocr = OCREngine(manifest_client)
fingerprint = FingerprintEngine()
zone = ZoneTracker()
voting = VotingEngine()

camera = CameraFeed()
camera.start()

# Global state
current_package_id = None
current_dest = None

def generate_frames():
    """Generator for MJPEG stream"""
    while True:
        ret, frame = camera.get_frame()
        if not ret:
            time.sleep(0.01)
            continue
            
        # Draw some telemetry on the frame
        cv2.putText(frame, "ARGUS LIVE FEED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if current_package_id:
            cv2.putText(frame, f"TARGET: {current_package_id}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/scan', methods=['POST'])
def trigger_scan():
    global current_package_id, current_dest
    
    ret, frame = camera.get_frame()
    if not ret:
        return jsonify({"status": "error", "message": "Failed to grab frame"}), 500
        
    print("\n--- SCAN POINT ---")
    ocr_res = ocr.process_frame(frame)
    dest = ocr_res.get("matched_destination")
    
    # Map destination to package ID
    current_package_id = f"PKG-{int(time.time())}"
    found_manifest = False
    for item in manifest_client.manifest_data:
        if item.get("destination", "").upper() == dest:
            current_package_id = item["package_id"]
            found_manifest = True
            break
            
    if not found_manifest:
        import requests
        import random
        import os
        from dotenv import load_dotenv

        load_dotenv()
        SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

        try:
            dummy_cities = ["SYDNEY", "BERLIN", "ROME", "DUBAI", "MADRID"]
            requests.post(
                f"{SUPABASE_URL}/rest/v1/manifests", 
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json={
                    "package_id": current_package_id,
                    "flight_number": "MN" + str(int(time.time()) % 1000),
                    "destination": dest if dest else random.choice(dummy_cities),
                    "status": "Pending"
                }, 
                timeout=2
            )
            manifest_client.fetch_manifest()
        except:
            pass

    ocr_status = "MATCH" if dest else "MISMATCH"
    current_dest = dest
    
    # Capture Visual Fingerprint
    fingerprint.capture_reference(frame)
    
    return jsonify({
        "status": "success",
        "package_id": current_package_id,
        "ocr_status": ocr_status,
        "destination": dest
    })

def decode_base64_image(b64_str):
    if "," in b64_str:
        b64_str = b64_str.split(",")[1]
    img_bytes = base64.b64decode(b64_str)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

@app.route('/scan_remote', methods=['POST'])
def trigger_scan_remote():
    global current_package_id, current_dest
    data = request.json
    if not data or 'image' not in data:
        return jsonify({"status": "error", "message": "No image provided"}), 400
    
    frame = decode_base64_image(data['image'])
    
    print("\n--- REMOTE SCAN POINT ---")
    ocr_res = ocr.process_frame(frame)
    dest = ocr_res.get("matched_destination")
    
    # Map destination to package ID
    current_package_id = f"PKG-{int(time.time())}"
    found_manifest = False
    for item in manifest_client.manifest_data:
        if item.get("destination", "").upper() == dest:
            current_package_id = item["package_id"]
            found_manifest = True
            break
            
    if not found_manifest:
        import requests
        import random
        import os
        from dotenv import load_dotenv

        load_dotenv()
        SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

        try:
            dummy_cities = ["SYDNEY", "BERLIN", "ROME", "DUBAI", "MADRID"]
            requests.post(
                f"{SUPABASE_URL}/rest/v1/manifests", 
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                json={
                    "package_id": current_package_id,
                    "flight_number": "MN" + str(int(time.time()) % 1000),
                    "destination": dest if dest else random.choice(dummy_cities),
                    "status": "Pending"
                }, 
                timeout=2
            )
            manifest_client.fetch_manifest()
        except:
            pass

    ocr_status = "MATCH" if dest else "MISMATCH"
    current_dest = dest
    
    # Capture Visual Fingerprint
    fingerprint.capture_reference(frame)
    
    return jsonify({
        "status": "success",
        "package_id": current_package_id,
        "ocr_status": ocr_status,
        "destination": dest
    })

@app.route('/verify', methods=['POST'])
def trigger_verify():
    global current_package_id, current_dest
    
    if not current_package_id:
        return jsonify({"status": "error", "message": "Scan a package first."}), 400
        
    ret, frame = camera.get_frame()
    if not ret:
        return jsonify({"status": "error", "message": "Failed to grab frame"}), 500
        
    print("\n--- VERIFICATION POINT ---")
    # 1. Check Fingerprint
    fp_match, fp_score = fingerprint.verify_target(frame)
    fp_status = "MATCH" if fp_match else "MISMATCH"
    
    # 2. Check Handler Zone
    z_status, _ = zone.process_frame(frame)
    
    # 3. Voting Engine
    ocr_is_match = "MATCH" if current_dest else "MISMATCH"
    score = voting.process_verification(current_package_id, ocr_is_match, fp_status, z_status)
    
    resp = {
        "status": "success",
        "package_id": current_package_id,
        "fingerprint_status": fp_status,
        "zone_status": z_status,
        "disagreement_score": score
    }
    
    # Reset for next package
    current_package_id = None
    current_dest = None
    
    return jsonify(resp)

@app.route('/verify_remote', methods=['POST'])
def trigger_verify_remote():
    global current_package_id, current_dest
    
    if not current_package_id:
        return jsonify({"status": "error", "message": "Scan a package first."}), 400
        
    data = request.json
    if not data or 'image' not in data:
        return jsonify({"status": "error", "message": "No image provided"}), 400
        
    frame = decode_base64_image(data['image'])
        
    print("\n--- REMOTE VERIFICATION POINT ---")
    # 1. Check Fingerprint
    fp_match, fp_score = fingerprint.verify_target(frame)
    fp_status = "MATCH" if fp_match else "MISMATCH"
    
    # 2. Check Handler Zone
    z_status, _ = zone.process_frame(frame)
    
    # 3. Voting Engine
    ocr_is_match = "MATCH" if current_dest else "MISMATCH"
    score = voting.process_verification(current_package_id, ocr_is_match, fp_status, z_status)
    
    resp = {
        "status": "success",
        "package_id": current_package_id,
        "fingerprint_status": fp_status,
        "zone_status": z_status,
        "disagreement_score": score
    }
    
    # Reset for next package
    current_package_id = None
    current_dest = None
    
    return jsonify(resp)

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5002, threaded=True)
    finally:
        camera.release()
