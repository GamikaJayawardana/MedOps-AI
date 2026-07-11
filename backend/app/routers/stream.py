import asyncio
from datetime import datetime, timezone
import random

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.schemas.telemetry import Telemetry

router = APIRouter()

# Define the list of wards for generating random telemetry data
WARDS = ["respiratory", "cardiology", "general", "pediatrics"]

def generate_snapshot():
    #create one fake telemetry reading
    return Telemetry(
        timestamp=datetime.now(timezone.utc),
        patient_influx=random.randint(0, 12),
        available_beds=random.randint(0, 30),
        staff_on_shifts=random.randint(1, 25), 
        ward=random.choice(WARDS) 
    )

@router.websocket("/ws/telemetry")
async def telemetry_stream(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()
    try:
        while True:
            # Generate a new telemetry snapshot and send it to the client
            snapshot = generate_snapshot()
            # Send the snapshot to the client as JSON
            await websocket.send_text(snapshot.model_dump_json())
            # Wait for 2 seconds before sending the next snapshot
            await asyncio.sleep(2)
    except WebSocketDisconnect:
            # Handle the case when the client disconnects
            print("Client disconnected from telemetry stream")   