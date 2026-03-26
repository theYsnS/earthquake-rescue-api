"""Rescue report API routes."""

from typing import Optional
from fastapi import APIRouter, HTTPException
from src.models.database import Database
from src.models.schemas import RescueReportCreate, StatusUpdate

router = APIRouter(prefix="/rescue", tags=["rescue"])
db = Database()


@router.post("/report")
async def create_report(report: RescueReportCreate):
    return db.create_report(report.model_dump())


@router.get("/reports")
async def list_reports(status: Optional[str] = None):
    return db.get_reports(status)


@router.put("/reports/{report_id}/status")
async def update_status(report_id: int, update: StatusUpdate):
    if not db.update_report_status(report_id, update.status.value):
        raise HTTPException(404, "Report not found")
    return {"id": report_id, "status": update.status}


@router.get("/reports/nearby")
async def nearby_reports(lat: float, lon: float, radius_km: float = 10):
    return db.get_nearby_reports(lat, lon, radius_km)


@router.get("/stats")
async def get_stats():
    return db.get_stats()
