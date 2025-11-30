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



