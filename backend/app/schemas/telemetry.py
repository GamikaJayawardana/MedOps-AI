from pydantic import BaseModel
from datetime import datetime


class WardState(BaseModel):
    ward: str
    patient_influx: int      # new patients this tick
    available_beds: int      # free beds right now
    staff_on_shift: int      # staff currently working
    occupancy_rate: float    # 0.0–1.0, how full the ward is


class Telemetry(BaseModel):
    timestamp: datetime
    hospital_pressure: float          # 0.0–1.0, overall time-of-day load
    wards: list[WardState]            # one entry per ward