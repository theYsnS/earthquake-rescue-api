from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class Severity(str, Enum):
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class Status(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    RESCUED = 'rescued'
    DECEASED = 'deceased'

class RescueReportCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    severity: Severity = Severity.HIGH
    description: str = ''
    num_trapped: int = Field(1, ge=1)
    contact_phone: str = ''

class StatusUpdate(BaseModel):
    status: Status

class TeamCreate(BaseModel):
    name: str
    members: int = Field(..., ge=1)
    specialization: str = ''
    latitude: float = 0.0
    longitude: float = 0.0

class LocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

class DeviceCreate(BaseModel):
    device_id: str
    device_type: str
    latitude: float = 0.0
    longitude: float = 0.0

class SensorData(BaseModel):
    vibration: Optional[float] = None
    gas_level: Optional[float] = None
    sound_level: Optional[float] = None
    temperature: Optional[float] = None
    timestamp: Optional[str] = None
