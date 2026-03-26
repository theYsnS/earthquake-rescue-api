"""FastAPI application for earthquake rescue coordination."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.rescue import router as rescue_router
from src.api.routes.teams import router as teams_router
from src.api.routes.devices import router as devices_router

app = FastAPI(
    title="Earthquake Rescue Coordination API",
    description="Backend API for post-disaster rescue coordination with IoT integration",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rescue_router)
app.include_router(teams_router)
app.include_router(devices_router)


@app.get("/")
async def root():
    return {"service": "Earthquake Rescue Coordination API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
