import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.simulator import HospitalSimulator
from app.services.analysis import run_analysis, resume_analysis

router = APIRouter()

# Pressure at/above this auto-triggers the agent graph.
AUTO_TRIGGER_PRESSURE = 0.85
# Don't auto-trigger more than once every N seconds (avoid spamming the LLM).
AUTO_TRIGGER_COOLDOWN = 30


@router.websocket("/ws/telemetry")
async def telemetry_stream(websocket: WebSocket):
    await websocket.accept()
    simulator = HospitalSimulator()
    latest_snapshot = {"value": simulator.tick()}
    last_trigger = {"time": 0.0}

    async def send_telemetry():
        """Continuously push telemetry every 2 seconds."""
        while True:
            snapshot = simulator.tick()
            latest_snapshot["value"] = snapshot
            await websocket.send_text(json.dumps({
                "type": "telemetry",
                "data": json.loads(snapshot.model_dump_json()),
            }))

            # Auto-trigger analysis if pressure is high and cooldown passed.
            now = asyncio.get_event_loop().time()
            if (snapshot.hospital_pressure >= AUTO_TRIGGER_PRESSURE
                    and now - last_trigger["time"] > AUTO_TRIGGER_COOLDOWN):
                last_trigger["time"] = now
                await run_and_send(snapshot, reason="auto")

            await asyncio.sleep(2)

    async def run_and_send(snapshot, reason: str):
        """Run the agent graph and send the result to the browser."""
        await websocket.send_text(json.dumps({
            "type": "analysis_started", "reason": reason,
        }))
        # Run the (blocking) graph in a thread so it doesn't freeze the socket.
        result = await asyncio.to_thread(run_analysis, snapshot)
        await websocket.send_text(json.dumps({
            "type": "analysis_result", "data": result,
        }))

    async def listen_for_commands():
        """Listen for messages from the browser (analyse / approve)."""
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            if msg.get("action") == "analyse":
                await run_and_send(latest_snapshot["value"], reason="manual")

            elif msg.get("action") == "approve":
                thread_id = msg.get("thread_id")
                result = await asyncio.to_thread(resume_analysis, thread_id)
                await websocket.send_text(json.dumps({
                    "type": "analysis_result", "data": result,
                }))

    try:
        # Run both loops at the same time.
        await asyncio.gather(send_telemetry(), listen_for_commands())
    except WebSocketDisconnect:
        print("Client disconnected from telemetry stream")