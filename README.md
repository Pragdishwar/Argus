# ARGUS (Autonomous Real-time Gate & Cargo Unified Surveillance)

ARGUS is a pure-software, AI-powered cargo verification system designed to prevent wrong-flight cargo loading at airports. It operates in the 30-second window between a package's barcode scan and its physical boarding of an aircraft — the only gap that current commercial systems leave unmonitored.

Unlike existing solutions that verify packages only at the scan point, ARGUS continuously tracks both the physical cargo object and the handler carrying it through to the aircraft door using a "Triple-Redundancy" computer vision system.

## 🚀 Deployed Application
The Argus dashboard is live! You can access the fully operational frontend here:
**[https://argus-red.vercel.app/](https://argus-red.vercel.app/)**

## 🛠️ Tech Stack

**Frontend:** Next.js 14, React, Tailwind CSS (Deployed on Vercel)
**Backend & Database:** Supabase (PostgreSQL, REST API)
**Computer Vision (Edge):** Python, OpenCV, YOLOv8 Nano, PyTesseract, RapidFuzz

## 🧠 Core Systems (Triple Redundancy)

1. **OCR Verification:** Reads the physical label on the box and cross-references it with the Supabase flight manifest. Uses fuzzy string matching to dynamically detect routing cities.
2. **Visual Fingerprinting:** Takes a Hue/Saturation histogram snapshot at the scan point and compares it to the box being loaded at the aircraft door to prevent package swapping.
3. **Zone Tracking:** Uses Pose Estimation and Object Detection to track the cargo handler's center of mass, ensuring they walk to the correct assigned flight gate.

If the system detects 2 or more conflicts across these three checks, it automatically triggers a Critical Alert in the dashboard.

---

## 💻 How to Run the Edge AI Engine Locally

The frontend dashboard runs in the cloud, but the heavy Computer Vision processing happens on the "edge" (your local machine's camera). To feed live camera data into the dashboard:

### 1. Install Requirements
```powershell
cd engine
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
Ensure your `.env` file in the `engine` directory contains your Supabase connection strings:
```env
SUPABASE_URL="your-supabase-url"
SUPABASE_KEY="your-supabase-key"
```

### 3. Launch the Computer Vision Engine
```powershell
cd engine
.\venv\Scripts\activate
python run_argus.py
```

## 🎮 How to Test

1. Open the [Live Dashboard](https://argus-red.vercel.app/).
2. Run `python run_argus.py` on your machine.
3. On the dashboard, click **START STREAM** and select **Local Cam** or **Edge Cam** depending on your setup.
4. Hold a piece of paper up to the camera with a recognized city written on it (e.g. `MADRID`, `BERLIN`, `SYDNEY`, `DUBAI`, or `ROME`).
5. Click **Scan** on the dashboard. The system will extract the text, look it up in the live Supabase manifest, and calculate the gate and weight.
6. Click **Verify** to simulate the package arriving at the aircraft door. The fingerprint and zone analyzer will cross-check the data!

> **Note on Webcams:** The Python engine automatically mirrors your video feed behind the scenes. This means you can write normally on your piece of paper and hold it up to a standard front-facing webcam, and the OCR engine will perfectly read it forward!
