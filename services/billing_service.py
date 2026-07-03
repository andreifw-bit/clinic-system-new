from config import (
    BASE_FEE,
    CARDIO_FEE,
    ORTHO_FEE,
    PEDIATRICS_FEE,
    INSURANCE_A_DISCOUNT,
    INSURANCE_B_DISCOUNT,
    URGENT_EXTRA,
    EMERGENCY_EXTRA,
)

def calculate_fee(appointment):
    base = BASE_FEE

    if appointment["doctor"] == "Cardio":
        base = CARDIO_FEE
    elif appointment["doctor"] == "Ortho":
        base = ORTHO_FEE
    elif appointment["doctor"] == "Pediatrics":
        base = PEDIATRICS_FEE

    if appointment["insurance"] == "A":
        base = base - INSURANCE_A_DISCOUNT
    elif appointment["insurance"] == "B":
        base = base - INSURANCE_B_DISCOUNT
    elif appointment["insurance"] == "C":
        base = base

    if appointment["priority"] == "urgent":
        base = base + URGENT_EXTRA
    elif appointment["priority"] == "emergency":
        base = base + EMERGENCY_EXTRA

    if appointment["status"] == "cancelled":
        return 0

    return base

def calculate_fee_again(appointment):
    base = BASE_FEE

    if appointment["doctor"] == "Cardio":
        base = CARDIO_FEE
    elif appointment["doctor"] == "Ortho":
        base = ORTHO_FEE
    elif appointment["doctor"] == "Pediatrics":
        base = PEDIATRICS_FEE

    if appointment["insurance"] == "A":
        base = base - INSURANCE_A_DISCOUNT
    elif appointment["insurance"] == "B":
        base = base - INSURANCE_B_DISCOUNT
    elif appointment["insurance"] == "C":
        base = base

    if appointment["priority"] == "urgent":
        base = base + URGENT_EXTRA
    elif appointment["priority"] == "emergency":
        base = base + EMERGENCY_EXTRA

    if appointment["status"] == "cancelled":
        return 0

    return base
