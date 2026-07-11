from datetime import datetime, timezone
import math
import random

from app.schemas.telemetry import Telemetry, WardState


WARDS = ["respiratory", "cardiology", "general", "pediatric"]

WARD_CAPACITY = {
    "respiratory": 25,
    "cardiology": 20,
    "general": 40,
    "pediatric": 15,
}

class HospitalSimulator:
    def __init__(self) -> None:
        # Initialize the hospital simulator with default values: half capacity for each ward
        self.beds_used = {w: WARD_CAPACITY[w] // 2 for w in WARDS}  
        self.staff = {w:10 for w in WARDS}  # Default staff count for each ward

    def _time_presure(self, now: datetime) -> float:
        # Calculate hospital pressure based on the time of day
        hour = now.hour + now.minute / 60.0
        # A sine wave peaking at 19:00 (7pm), lowest around 5am.
        # Shift so the peak lands in the evening.
        pressure = 0.5 + 0.5 * math.sin((hour - 5) / 24 * 2 * math.pi)
        return round(pressure, 2)
    
    def tick(self) -> Telemetry:
        now = datetime.now(timezone.utc)
        pressure = self._time_presure(now)

        ward_states = []
        for ward in WARDS:
            capacity = WARD_CAPACITY[ward]

            # More patients arrive when pressure is high. Poisson-like feel.
            influx = max(0, int(random.gauss(pressure * 6,2)))

            # Beds used drifts: new patients take beds, some patients leave.
            discharges = random.randint(0, 4)
            self.beds_used[ward] = min(
                capacity,
                max(0, self.beds_used[ward] + influx - discharges),
            )
            available = capacity - self.beds_used[ward]

            # Staff drifts slowly around a level tied to pressure.
            target_staff = int(8 + pressure * 10)
            if self.staff[ward] < target_staff:
                self.staff[ward] += random.randint(0, 2)
            elif self.staff[ward] > target_staff:
                self.staff[ward] -= random.randint(0, 1)

            ward_states.append(
                WardState(
                    ward=ward,
                    patient_influx=influx,
                    available_beds=available,
                    staff_on_shift=self.staff[ward],
                    occupancy_rate=round(self.beds_used[ward] / capacity, 2),
                )
            )

        return Telemetry(
            timestamp=now,
            hospital_pressure=pressure,
            wards=ward_states,
        )