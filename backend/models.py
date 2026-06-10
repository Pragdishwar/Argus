from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime, timezone

class Manifest(Base):
    __tablename__ = "manifests"

    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(String, unique=True, index=True)
    flight_number = Column(String, index=True)
    destination = Column(String)
    status = Column(String)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    type = Column(String, index=True)
    severity = Column(String)
    message = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    package_id = Column(String, index=True)
    action = Column(String)
    result = Column(String)
    severity = Column(String)

class VerificationRecord(Base):
    __tablename__ = "verification_records"

    id = Column(Integer, primary_key=True, index=True)
    package_id = Column(String, index=True)
    ocr_status = Column(String)
    fingerprint_status = Column(String)
    zone_status = Column(String)
    disagreement_score = Column(Float)
