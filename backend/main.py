from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
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

# --- Manifest Endpoints ---
@app.post("/manifest", response_model=schemas.ManifestResponse, tags=["Manifest"])
async def create_manifest(manifest: schemas.ManifestCreate, db: Session = Depends(get_db)):
    return crud.create_manifest(db=db, manifest=manifest)

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
