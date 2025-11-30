from datetime import datetime
from typing import Dict, List, Optional
import math
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Geofence Event Service",
    version="1.0.0",
)

class LocationEvent(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float
    timestamp: datetime

class Zone(BaseModel):
    id: str
    name: str
    center_lat: float
    center_lon: float
    radius_m: float

class VehicleState(BaseModel):
    vehicle_id: str
    last_lat: float
    last_lon: float
    last_timestamp: datetime
    current_zone_id: Optional[str] = None

class ZoneEvent(BaseModel):
    event_type: str
    zone_id: str
    timestamp: datetime

class LocationResponse(BaseModel):
    vehicle_id: str
    current_zone_id: Optional[str]
    events: List[ZoneEvent]

class VehicleStatus(BaseModel):
    vehicle_id: str
    current_zone_id: Optional[str]
    last_lat: float
    last_lon: float
    last_timestamp: datetime

vehicle_states: Dict[str, VehicleState] = {}

zones: List[Zone] = [
    Zone(id="zone_airport", name="Airport", center_lat=12.955, center_lon=77.665, radius_m=1500),
    Zone(id="zone_city", name="City Center", center_lat=12.975, center_lon=77.605, radius_m=1200),
]

def validate_coordinates(lat: float, lon: float) -> None:
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def find_zone(lat: float, lon: float):
    candidates = []
    for z in zones:
        dist = haversine_m(lat, lon, z.center_lat, z.center_lon)
        if dist <= z.radius_m:
            candidates.append((dist, z.id))
    return sorted(candidates)[0][1] if candidates else None

@app.get("/health")
def check():
    return {"status": "ok"}

@app.post("/events/location", response_model=LocationResponse)
def update_location(event: LocationEvent):
    validate_coordinates(event.latitude, event.longitude)
    state = vehicle_states.get(event.vehicle_id) or VehicleState(
        vehicle_id=event.vehicle_id,
        last_lat=event.latitude,
        last_lon=event.longitude,
        last_timestamp=event.timestamp,
        current_zone_id=None,
    )

    old_zone = state.current_zone_id
    new_zone = find_zone(event.latitude, event.longitude)
    events: List[ZoneEvent] = []

    if new_zone != old_zone:
        if old_zone:
            events.append(ZoneEvent(event_type="exit", zone_id=old_zone, timestamp=event.timestamp))
        if new_zone:
            events.append(ZoneEvent(event_type="enter", zone_id=new_zone, timestamp=event.timestamp))

    state.last_lat, state.last_lon, state.last_timestamp, state.current_zone_id = (
        event.latitude,
        event.longitude,
        event.timestamp,
        new_zone,
    )
    vehicle_states[event.vehicle_id] = state

    return LocationResponse(vehicle_id=event.vehicle_id, current_zone_id=new_zone, events=events)

@app.get("/vehicles/{vehicle_id}/zone-status", response_model=VehicleStatus)
def vehicle_status(vehicle_id: str):
    state = vehicle_states.get(vehicle_id)
    if not state:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return state
