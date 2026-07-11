from langchain_core.tools import tool

# A fake inventory "database". In a real system this would be a DB query.
MOCK_INVENTORY = {
    "ventilator": {"total": 20, "in_use": 18},
    "cardiac_monitor": {"total": 30, "in_use": 25},
    "infusion_pump": {"total": 50, "in_use": 40},
    "defibrillator": {"total": 12, "in_use": 6},
}


@tool
def check_equipment_inventory(equipment: str) -> str:
    """Check how many units of a piece of medical equipment are available.

    Args:
        equipment: the equipment name, e.g. 'ventilator', 'cardiac_monitor',
                   'infusion_pump', or 'defibrillator'.
    """
    item = MOCK_INVENTORY.get(equipment.lower())
    if item is None:
        return f"Unknown equipment '{equipment}'. No inventory record."
    available = item["total"] - item["in_use"]
    return (
        f"{equipment}: {available} available "
        f"({item['in_use']} in use of {item['total']} total)."
    )


@tool
def find_transfer_ward(full_ward: str) -> str:
    """Find a ward that could accept overflow patients from a full ward.

    Args:
        full_ward: the name of the ward that is at capacity.
    """
    # Simplified logic: 'general' is the overflow ward unless it's the one asking.
    if full_ward.lower() == "general":
        return "No obvious overflow ward; general is the usual overflow and it is full."
    return "The 'general' ward is the designated overflow and may have capacity."