from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
from fastapi import HTTPException

# Manifest CRUD
def get_manifest(db: Session, manifest_id: int):
    return db.query(models.Manifest).filter(models.Manifest.id == manifest_id).first()

def get_manifest_by_package(db: Session, package_id: str):
    return db.query(models.Manifest).filter(models.Manifest.package_id == package_id).first()

def get_manifests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Manifest).offset(skip).limit(limit).all()

def create_manifest(db: Session, manifest: schemas.ManifestCreate):
    db_manifest = models.Manifest(**manifest.model_dump())
    db.add(db_manifest)
    try:
        db.commit()
        db.refresh(db_manifest)
        return db_manifest
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Manifest with this package_id already exists")

def update_manifest(db: Session, manifest_id: int, manifest: schemas.ManifestCreate):
    db_manifest = db.query(models.Manifest).filter(models.Manifest.id == manifest_id).first()
    if not db_manifest:
        return None
    for key, value in manifest.model_dump().items():
        setattr(db_manifest, key, value)
    try:
        db.commit()
        db.refresh(db_manifest)
        return db_manifest
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error during update")

def delete_manifest(db: Session, manifest_id: int):
    db_manifest = db.query(models.Manifest).filter(models.Manifest.id == manifest_id).first()
    if db_manifest:
        db.delete(db_manifest)
        db.commit()
        return True
    return False

# Alert CRUD
def get_alert(db: Session, alert_id: int):
    return db.query(models.Alert).filter(models.Alert.id == alert_id).first()

def get_alerts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Alert).order_by(models.Alert.timestamp.desc()).offset(skip).limit(limit).all()

def create_alert(db: Session, alert: schemas.AlertCreate):
    db_alert = models.Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

# AuditLog CRUD
def get_audit_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

def create_audit_log(db: Session, audit_log: schemas.AuditLogCreate):
    db_log = models.AuditLog(**audit_log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# VerificationRecord CRUD
def get_verification_record(db: Session, record_id: int):
    return db.query(models.VerificationRecord).filter(models.VerificationRecord.id == record_id).first()

def get_verification_records(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.VerificationRecord).offset(skip).limit(limit).all()

def create_verification_record(db: Session, record: schemas.VerificationRecordCreate):
    db_record = models.VerificationRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record
