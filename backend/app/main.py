from fastapi import FastAPI

from app.routers import stream

app = FastAPI(title="MedOps-AI", description="MedOps-AI API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

# Include the stream router for WebSocket telemetry streaming
app.include_router(stream.router)