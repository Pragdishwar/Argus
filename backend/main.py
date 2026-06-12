from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import engine, get_db
from ws_manager import manager

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ARGUS Backend API",
    description="Backend for Autonomous Real-time Gate & Cargo Unified Surveillance",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Manifest Endpoints ---
@app.post("/manifest", response_model=schemas.ManifestResponse, tags=["Manifest"])
async def create_manifest(manifest: schemas.ManifestCreate, db: Session = Depends(get_db)):
    db_manifest = crud.create_manifest(db=db, manifest=manifest)
    await manager.broadcast({"event": "manifest_updated", "data": {}})
    return db_manifest

@app.get("/manifest", response_model=List[schemas.ManifestResponse], tags=["Manifest"])
async def read_manifests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_manifests(db, skip=skip, limit=limit)

@app.get("/manifest/{manifest_id}", response_model=schemas.ManifestResponse, tags=["Manifest"])
async def read_manifest(manifest_id: int, db: Session = Depends(get_db)):
    db_manifest = crud.get_manifest(db, manifest_id=manifest_id)
    if db_manifest is None:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return db_manifest

@app.put("/manifest/{manifest_id}", response_model=schemas.ManifestResponse, tags=["Manifest"])
async def update_manifest(manifest_id: int, manifest: schemas.ManifestCreate, db: Session = Depends(get_db)):
    db_manifest = crud.update_manifest(db, manifest_id=manifest_id, manifest=manifest)
    if db_manifest is None:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return db_manifest

@app.delete("/manifest/{manifest_id}", tags=["Manifest"])
async def delete_manifest(manifest_id: int, db: Session = Depends(get_db)):
    success = crud.delete_manifest(db, manifest_id=manifest_id)
    if not success:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return {"detail": "Manifest deleted successfully"}

# --- Alerts Endpoints ---
@app.post("/alerts", response_model=schemas.AlertResponse, tags=["Alerts"])
async def create_alert(alert: schemas.AlertCreate, db: Session = Depends(get_db)):
    db_alert = crud.create_alert(db=db, alert=alert)
    # Broadcast alert via WebSockets
    await manager.broadcast({
        "event": "new_alert",
        "data": {
            "id": db_alert.id,
            "type": db_alert.type,
            "severity": db_alert.severity,
            "message": db_alert.message,
            "timestamp": db_alert.timestamp.isoformat()
        }
    })
    return db_alert

@app.get("/alerts", response_model=List[schemas.AlertResponse], tags=["Alerts"])
async def read_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_alerts(db, skip=skip, limit=limit)

@app.get("/alerts/{alert_id}", response_model=schemas.AlertResponse, tags=["Alerts"])
async def read_alert(alert_id: int, db: Session = Depends(get_db)):
    db_alert = crud.get_alert(db, alert_id=alert_id)
    if db_alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return db_alert

# --- Audit Logs Endpoints ---
@app.post("/audit", response_model=schemas.AuditLogResponse, tags=["Audit Logs"])
async def create_audit_log(audit_log: schemas.AuditLogCreate, db: Session = Depends(get_db)):
    return crud.create_audit_log(db=db, audit_log=audit_log)

@app.get("/audit", response_model=List[schemas.AuditLogResponse], tags=["Audit Logs"])
async def read_audit_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_audit_logs(db, skip=skip, limit=limit)

# --- Verifications Endpoints ---
@app.post("/verifications", response_model=schemas.VerificationRecordResponse, tags=["Verifications"])
async def create_verification_record(record: schemas.VerificationRecordCreate, db: Session = Depends(get_db)):
    db_record = crud.create_verification_record(db=db, record=record)
    
    if db_record.disagreement_score > 0:
        action = "System BLOCK" if db_record.disagreement_score >= 2 else "System HOLD"
        db_log = crud.create_audit_log(db=db, audit_log=schemas.AuditLogCreate(
            package_id=db_record.package_id,
            action=action,
            result=f"OCR: {db_record.ocr_status}, FP: {db_record.fingerprint_status}, Zone: {db_record.zone_status}",
            severity="HIGH" if action == "System BLOCK" else "MEDIUM"
        ))
        # Optional: broadcast new audit log
        await manager.broadcast({
            "event": "new_audit",
            "data": {
                "id": db_log.id,
                "timestamp": db_log.timestamp.isoformat(),
                "package_id": db_log.package_id,
                "action": db_log.action,
                "result": db_log.result,
                "severity": db_log.severity
            }
        })
    
    # Broadcast verification result
    await manager.broadcast({
        "event": "new_verification",
        "data": {
            "id": db_record.id,
            "package_id": db_record.package_id,
            "disagreement_score": db_record.disagreement_score,
            "ocr_status": db_record.ocr_status,
            "fingerprint_status": db_record.fingerprint_status,
            "zone_status": db_record.zone_status
        }
    })
    return db_record

@app.get("/verifications", response_model=List[schemas.VerificationRecordResponse], tags=["Verifications"])
async def read_verifications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_verification_records(db, skip=skip, limit=limit)

@app.get("/verifications/{record_id}", response_model=schemas.VerificationRecordResponse, tags=["Verifications"])
async def read_verification(record_id: int, db: Session = Depends(get_db)):
    db_record = crud.get_verification_record(db, record_id=record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Verification record not found")
    return db_record

# --- System Health ---
@app.get("/system-health", tags=["System Health"])
async def check_health():
    return {"status": "ok", "service": "ARGUS Backend"}

# --- Simulator Endpoints ---
@app.post("/api/simulator/seed", tags=["Simulator"])
async def seed_simulator(db: Session = Depends(get_db)):
    import random
    import datetime
    import time
    
    # 1. Seed Manifests
    run_id = str(int(time.time()))[-4:]
    mock_manifests = [
        {"package_id": f"PKG-{run_id}-1", "flight_number": "AA100", "destination": "NEW YORK", "status": "Pending"},
        {"package_id": f"PKG-{run_id}-2", "flight_number": "BA200", "destination": "LONDON", "status": "Pending"},
        {"package_id": f"PKG-{run_id}-3", "flight_number": "JL300", "destination": "TOKYO", "status": "Pending"},
        {"package_id": f"PKG-{run_id}-4", "flight_number": "AF400", "destination": "PARIS", "status": "Pending"},
        {"package_id": f"PKG-{run_id}-5", "flight_number": "LH500", "destination": "FRANKFURT", "status": "Pending"},
    ]
    for m in mock_manifests:
        try:
            crud.create_manifest(db, schemas.ManifestCreate(**m))
        except Exception:
            pass # Ignore duplicates if already seeded

    # 2. Add some dummy verifications
    verifs = []
    for i in range(5):
        pkg = mock_manifests[i]["package_id"]
        v = crud.create_verification_record(db, schemas.VerificationRecordCreate(
            package_id=pkg,
            ocr_status="MATCH" if i != 3 else "MISMATCH",
            fingerprint_status="MATCH" if i != 4 else "MISMATCH",
            zone_status="Correct Gate" if i < 3 else "Wrong Gate",
            disagreement_score=0 if i < 3 else (2 if i == 3 else 1)
        ))
        verifs.append(v)
        
        if v.disagreement_score > 0:
            action = "System BLOCK" if v.disagreement_score >= 2 else "System HOLD"
            crud.create_audit_log(db, schemas.AuditLogCreate(
                package_id=pkg,
                action=action,
                result=f"OCR: {v.ocr_status}, FP: {v.fingerprint_status}, Zone: {v.zone_status}",
                severity="HIGH" if action == "System BLOCK" else "MEDIUM"
            ))
        
    # Broadcast to frontend that seeding is complete
    await manager.broadcast({"event": "simulator_seeded", "data": {}})
    
    return {"status": "seeded", "verifications_added": len(verifs)}

@app.post("/api/simulator/reset", tags=["Simulator"])
async def reset_simulator(db: Session = Depends(get_db)):
    crud.delete_all_verifications(db)
    crud.delete_all_alerts(db)
    crud.delete_all_audit_logs(db)
    crud.delete_all_manifests(db)
    
    # Broadcast reset to frontend
    await manager.broadcast({"event": "simulator_reset", "data": {}})
    return {"status": "reset"}

@app.post("/api/simulator/stream/start", tags=["Simulator"])
async def start_stream():
    # In reality, this would trigger the CV script or IP camera stream
    return {"status": "stream_started"}

# --- WebSockets ---
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We don't expect much data from client in this uni-directional dashboard setup, 
            # but we need to receive to keep connection alive and detect disconnects
            data = await websocket.receive_text()
            # Echo or process if necessary, for now we just keep connection open
    except WebSocketDisconnect:
        manager.disconnect(websocket)
