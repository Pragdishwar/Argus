# ARGUS (Autonomous Real-time Gate & Cargo Unified Surveillance)

ARGUS is a pure-software, AI-powered cargo verification system designed to prevent wrong-flight cargo loading at airports. It operates in the 30-second window between a package's barcode scan and its physical boarding of an aircraft — the only gap that current commercial systems leave unmonitored.

Unlike existing solutions that verify packages only at the scan point, ARGUS continuously tracks both the physical cargo object and the handler carrying it through to the aircraft door using a "Triple-Redundancy" computer vision system.

## 🚀 Tech Stack

**Frontend:** Next.js 14, React, Tailwind CSS
**Backend:** Python, FastAPI, WebSockets, SQLite
**Computer Vision:** OpenCV, MediaPipe Pose Estimation, PyTesseract, RapidFuzz

## 🧠 Core Systems (Triple Redundancy)

1. **OCR Verification:** Reads the physical label on the box and cross-references it with the flight manifest.
2. **Visual Fingerprinting:** Takes a Hue/Saturation histogram snapshot at the scan point and compares it to the box being loaded at the aircraft door to prevent package swapping.
3. **Zone Tracking:** Uses Pose Estimation to track the cargo handler's center of mass, ensuring they walk to the correct assigned flight gate.

If the system detects 2 or more conflicts across these three checks, it automatically triggers a Critical Alert and sends a halt command to the conveyor belt API.

---

## 🛠️ How to Run Locally

Because ARGUS relies on a microservice architecture, you need to run its components simultaneously. Open **5 separate terminal windows** and run the following commands from the root `Argus` directory.

### 1. Start the FastAPI Backend & WebSockets
```powershell
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload
```
*(Runs on http://127.0.0.1:8000)*

### 2. Start the Mock Conveyor API
```powershell
cd engine
.\venv\Scripts\activate
python mock_conveyor_api.py
```
*(Runs on http://127.0.0.1:5001)*

### 3. Start the Mock Manifest API
```powershell
cd engine
.\venv\Scripts\activate
python mock_manifest_api.py
```
*(Runs on http://127.0.0.1:5000)*

### 4. Start the Next.js Dashboard
```powershell
cd frontend
npm run dev
```
*(Runs on http://localhost:3000)*

### 5. Launch the Computer Vision Engine
*Make sure the previous 4 services are running before launching this.*
```powershell
cd engine
.\venv\Scripts\activate
python run_argus.py
```

## 🎮 How to Test the Demo
Once the Computer Vision engine (Terminal 5) is running, your webcam will activate.
1. Press **`s`** on your keyboard to simulate a package arriving at the **Scan Point**.
2. Wait a moment, then press **`v`** to simulate that same package arriving at the **Verification Point** (the aircraft door).
3. Watch the Next.js Dashboard (http://localhost:3000) instantly populate with live verification data and alerts via WebSockets!

> **Note on MediaPipe & Tesseract:** For demonstration purposes on systems without Tesseract installed or running newer incompatible versions of Python (like 3.13), the engine will gracefully degrade to simulated mock tracking to ensure the full dashboard and backend pipeline remains testable.
