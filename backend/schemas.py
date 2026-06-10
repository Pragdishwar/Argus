from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

# Manifest Schemas
class ManifestBase(BaseModel):
    package_id: str
    flight_number: str
    destination: str
    status: str

class ManifestCreate(ManifestBase):
    pass

class ManifestResponse(ManifestBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# Alert Schemas
class AlertBase(BaseModel):
    type: str
    severity: str
    message: str

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

# AuditLog Schemas
class AuditLogBase(BaseModel):
    package_id: str
    action: str
    result: str
    severity: str

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    id: int
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

# VerificationRecord Schemas
class VerificationRecordBase(BaseModel):
    package_id: str
    ocr_status: str
    fingerprint_status: str
    zone_status: str
    disagreement_score: float

class VerificationRecordCreate(VerificationRecordBase):
    pass

class VerificationRecordResponse(VerificationRecordBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
