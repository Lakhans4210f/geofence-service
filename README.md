\# Geofence Event Processing Service



This project is a backend service that processes real-time GPS location updates for vehicles.

It detects when a vehicle enters or exits predefined geographic zones and allows clients to

check the current zone of any vehicle. The service is built with Python and FastAPI and keeps

vehicle state in memory for simplicity.



\## Tech Stack



\- \*\*Language:\*\* Python 3

\- \*\*Framework:\*\* FastAPI (for building the HTTP API)

\- \*\*Server:\*\* Uvicorn (ASGI server for running FastAPI)

\- \*\*Data Handling:\*\* Pydantic models for request/response validation

\- \*\*Storage:\*\* In-memory dictionary for vehicle state (no external DB for simplicity)

\- \*\*Tools:\*\* Git for version control, Swagger UI for API testing



\## API Endpoints



\### POST /events/location

This endpoint receives real-time GPS updates from vehicles.



\*\*Request Body Example\*\*

```json

{

&nbsp; "vehicle\_id": "cab-1",

&nbsp; "latitude": 12.955,

&nbsp; "longitude": 77.665,

&nbsp; "timestamp": "2025-11-30T10:00:00Z"

}


## Event Processing Flow
### Location event handling (POST /events/location)

1. The service receives a JSON payload containing `vehicle_id`, `latitude`, `longitude`, and `timestamp`.
2. The coordinates are validated (latitude and longitude must be in valid ranges).
3. The current in-memory state for that `vehicle_id` is loaded (or created if this is the first update for that vehicle).
4. The new location is checked against all configured zones using a simple circular distance check.
5. Based on the result:
   - If the vehicle was previously outside all zones and now is inside a zone → an **enter** event is generated.
   - If the vehicle was previously inside a zone and now is outside all zones → an **exit** event is generated.
   - If it moves from one zone to another → an **exit** for the old zone and an **enter** for the new zone are generated.
6. The in-memory vehicle state is updated with the latest location, timestamp, and current zone.
7. The API returns the current zone id (or `null`) and a list of any enter/exit events created for this update.

### Zone status lookup (GET /vehicles/{vehicle_id}/zone-status)

1. The client calls the endpoint with a specific `vehicle_id`.
2. The service looks up the vehicle in the in-memory state map.
3. If the vehicle has never sent a location update, a 404 error is returned.
4. If the vehicle exists, the service returns:
   - the last known latitude and longitude,
   - the last timestamp,
   - and the current zone id (or `null` if the vehicle is not inside any zone).

## Assumptions

- Zones are defined as simple circles with a fixed center point and radius in meters.
- Zones are static while the service is running (no dynamic creation or updates).
- The number of zones is small, so checking all zones on each request is acceptable.
- Vehicle state can be kept in memory for this assignment (no need for a database).
- Location events arrive roughly in order for each vehicle, and the latest event is treated as the source of truth.
- Overlapping zones are not a focus in this version. If multiple zones contain a point, the closest zone center is chosen.

## Edge Cases Considered

- **First update for a vehicle**: if the service has never seen a vehicle_id before, a new in-memory entry is created on the first location event.
- **Vehicle outside all zones**: if a vehicle is not inside any geofence, `current_zone_id` is returned as `null` and no events are generated.
- **Leaving a zone**: when a vehicle moves from inside a zone to outside all zones, an `exit` event is generated.
- **Switching between zones**: if a vehicle moves directly from one zone to another, the service generates an `exit` event for the old zone and an `enter` event for the new zone in the same request.
- **Unknown vehicle status**: requesting `/vehicles/{vehicle_id}/zone-status` for a vehicle that never sent a location returns HTTP 404.
- **Invalid coordinates**: if latitude or longitude are out of valid ranges, the service returns HTTP 400 with a validation error.

## Future Improvements

If I had more time, I would improve the service in the following ways:

- **Persistent storage**: move vehicle state out of memory into a database or cache (e.g. PostgreSQL, Redis) so the state survives restarts.
- **Config-driven zones**: load zones from a configuration file or database instead of hard-coding them in code.
- **More complex geofences**: support polygon-based zones instead of just circles, and handle overlapping zones with explicit priorities.
- **Authentication and rate limiting**: secure the API so that only authorized clients can send location events or query vehicle status.
- **Metrics and monitoring**: expose basic metrics (event rate, errors, number of tracked vehicles) and integrate with a monitoring system.
- **Horizontal scaling**: run multiple instances of the service behind a load balancer and use a shared store for vehicle state to handle higher load.
## How to Run

### Prerequisites
- Python 3 installed
- Git installed

### Setup Instructions

```bash
# Clone the repository (or download the project folder)
git clone <your-github-repo-url>
cd geofence-service

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

git add README.md
git commit -m "Add repository link to README"
git push




