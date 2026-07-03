import os
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "appointments.json")

BASE_FEE = 100
CARDIO_FEE = 200
ORTHO_FEE = 180
PEDIATRICS_FEE = 150

INSURANCE_A_DISCOUNT = 20
INSURANCE_B_DISCOUNT = 10

URGENT_EXTRA = 30
EMERGENCY_EXTRA = 80

# Listas de valores válidos para validação
VALID_DOCTORS = ["Cardio", "Ortho", "Pediatrics", "General"]
VALID_ROOMS = ["101", "102", "103", "104"]
