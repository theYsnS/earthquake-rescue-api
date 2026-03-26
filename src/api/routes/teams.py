"""Team management API routes."""

from fastapi import APIRouter, HTTPException
from src.models.database import Database
from src.models.schemas import TeamCreate, LocationUpdate

router = APIRouter(prefix="/teams", tags=["teams"])
db = Database()


@router.post("")
async def create_team(team: TeamCreate):
    return db.create_team(team.model_dump())


@router.get("")
async def list_teams(available_only: bool = False):
    return db.get_teams(available_only)


@router.put("/{team_id}/location")
async def update_location(team_id: int, loc: LocationUpdate):
    if not db.update_team_location(team_id, loc.latitude, loc.longitude):
        raise HTTPException(404, "Team not found")
    return {"id": team_id, "latitude": loc.latitude, "longitude": loc.longitude}


@router.post("/{team_id}/assign")
async def assign_team(team_id: int, report_id: int):
    db.assign_team(team_id, report_id)
    return {"team_id": team_id, "report_id": report_id, "status": "assigned"}
