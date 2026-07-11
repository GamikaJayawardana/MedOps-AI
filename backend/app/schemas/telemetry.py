from datetime import datetime
from pydantic import BaseModel


class Telemetry(BaseModel):
    timestamp: datetime
    patient_influx: int  # new patients arriving this tick
    available_beds: int  # available beds in the hospital
    staff_on_shifts: int  # nurses/doctors on shift
    ward: str # ward name or identifier (repiratory, cardiology, etc.)
    
