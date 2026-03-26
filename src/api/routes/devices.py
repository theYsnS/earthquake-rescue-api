"""IoT device management API routes."""

from fastapi import APIRouter
from src.models.database import Database
from src.models.schemas import DeviceCreate, SensorData

router = APIRouter(prefix="/devices", tags=["devices"])
db = Database()


@router.post("/register")
async def register_device(device: DeviceCreate):
    return db.register_device(device.model_dump())


@router.post("/{device_id}/data")
async def submit_sensor_data(device_id: str, data: SensorData):
    db.add_sensor_data(device_id, data.model_dump())
    return {"device_id": device_id, "status": "received"}


@router.get("/{device_id}/status")
async def device_status(device_id: str):
    return {"device_id": device_id, "status": "active"}
