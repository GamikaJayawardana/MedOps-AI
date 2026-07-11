import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.simulator import HospitalSimulator

router = APIRouter()

# Define the list of wards for generating random telemetry data
WARDS = ["respiratory", "cardiology", "general", "pediatrics"]

@router.websocket("/ws/telemetry")
async def telemetry_stream(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()
    # Initialize the hospital simulator
    simulator = HospitalSimulator()
    try:
        while True:
            while True:
                 # Generate a new telemetry snapshot using the simulator
                 snapshot = simulator.tick()
                 # Send the telemetry snapshot to the connected WebSocket client as JSON
                 await websocket.send_text(snapshot.model_dump_json())
                 await asyncio.sleep(2)  # Send updates every 2 second
                
    except WebSocketDisconnect:
            # Handle the case when the client disconnects
            print("Client disconnected from telemetry stream")   