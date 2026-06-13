import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

class VotingEngine:
    def __init__(self, backend_url=f"{SUPABASE_URL}/rest/v1"):
        self.backend_url = backend_url
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        self.conveyor_url = "http://127.0.0.1:5001/halt"

    def calculate_score(self, ocr_match, fingerprint_match, zone_correct):
        """
        Calculates disagreement score based on 3 sources.
        Score meaning:
        0: All agree (0 conflicts)
        1: 1 conflict
        2: 2 conflicts
        3: 3 conflicts
        """
        score = 0
        if not ocr_match: score += 1
        if not fingerprint_match: score += 1
        if not zone_correct: score += 1
        return float(score)

    def process_verification(self, package_id, ocr_status, fingerprint_status, zone_status):
        """Evaluates the data, computes score, sends to backend, and halts if necessary."""
        ocr_match = ocr_status == "MATCH"
        fingerprint_match = fingerprint_status == "MATCH"
        zone_correct = zone_status == "Correct Gate"
        
        score = self.calculate_score(ocr_match, fingerprint_match, zone_correct)
        
        # 1. Post Verification Record to Backend
        payload = {
            "package_id": package_id,
            "ocr_status": ocr_status,
            "fingerprint_status": fingerprint_status,
            "zone_status": zone_status,
            "disagreement_score": score
        }
        
        try:
            requests.post(f"{self.backend_url}/verification_records", headers=self.headers, json=payload, timeout=2)
        except requests.RequestException as e:
            print(f"Failed to post verification: {e}")

        # 2. Check thresholds for Alerts & Halting & Audit
        if score > 0:
            action = "System BLOCK" if score >= 2 else "System HOLD"
            self._post_audit_log(package_id, action, f"OCR: {ocr_status}, FP: {fingerprint_status}, Zone: {zone_status}")

        if score >= 1:
            severity = "medium" if score == 1 else ("high" if score == 2 else "critical")
            message = f"Mismatch detected for package {package_id}. Conflicts: {int(score)}."
            self._post_alert("MISMATCH", severity, message)
        
        if score >= 2:
            print(f"CRITICAL: Halting conveyor for package {package_id}")
            self._halt_conveyor(package_id)

        return score

    def _post_alert(self, alert_type, severity, message):
        payload = {
            "type": alert_type,
            "severity": severity,
            "message": message
        }
        try:
            requests.post(f"{self.backend_url}/alerts", headers=self.headers, json=payload, timeout=2)
        except requests.RequestException:
            pass

    def _post_audit_log(self, package_id, action, result):
        payload = {
            "package_id": package_id,
            "action": action,
            "result": result,
            "severity": "HIGH" if "BLOCK" in action else "MEDIUM"
        }
        try:
            requests.post(f"{self.backend_url}/audit_logs", headers=self.headers, json=payload, timeout=2)
        except requests.RequestException:
            pass

    def _halt_conveyor(self, package_id):
        try:
            requests.post(self.conveyor_url, json={"package_id": package_id}, timeout=2)
        except requests.RequestException:
            pass
