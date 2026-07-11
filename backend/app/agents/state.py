from typing import TypedDict

# TypedDict is used to define the structure of a dictionary with 
# specific keys and value types. In this case, 
# HospitalState is a TypedDict that represents the state of a hospital 
# with three keys: pressure, classification, and action.
class HospitalState(TypedDict):
    pressure: float           # input: current hospital pressure 0.0–1.0
    classification: str       # filled in by the classify node
    action: str               # filled in by whichever action node runs