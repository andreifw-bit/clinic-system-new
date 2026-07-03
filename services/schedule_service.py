import json
from config import DATA_FILE, VALID_DOCTORS, VALID_ROOMS
from services.billing_service import calculate_fee_again
from utils.time_utils import same_slot, end_time, find_free_slot
from utils.fuzzy import fuzzy_match

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_conflicts(data):
    conflicts = []
    appointments = data["appointments"]
    for i in range(len(appointments)):
        for j in range(len(appointments)):
            if i != j:
                same_doctor   = appointments[i]["doctor"] == appointments[j]["doctor"]
                same_time_val = same_slot(appointments[i]["time"], appointments[j]["time"])
                same_room     = appointments[i]["room"] == appointments[j]["room"]
                if same_doctor and same_time_val:
                    conflicts.append((appointments[i]["id"], appointments[j]["id"], "doctor"))
                if same_room and same_time_val:
                    conflicts.append((appointments[i]["id"], appointments[j]["id"], "room"))
    return conflicts

def check_new_appointment_conflicts(data, new_appointment):
    """
    Verifica se uma nova consulta causa sobreposição com as existentes (duração 30 min).
    Ignora consultas canceladas.
    """
    conflicts = []
    for existing in data["appointments"]:
        if existing["status"] == "cancelled":
            continue
        if not same_slot(existing["time"], new_appointment["time"]):
            continue
        if existing["doctor"] == new_appointment["doctor"]:
            conflicts.append(
                f"Conflito de médico: Dr. {new_appointment['doctor']} já tem consulta às "
                f"{existing['time']}–{end_time(existing['time'])} "
                f"(Paciente: {existing['patient']}, ID: {existing['id']})"
            )
        if existing["room"] == new_appointment["room"]:
            conflicts.append(
                f"Conflito de sala: Sala {new_appointment['room']} já está ocupada às "
                f"{existing['time']}–{end_time(existing['time'])} "
                f"(Paciente: {existing['patient']}, ID: {existing['id']})"
            )
    return conflicts

def resolve_doctor(raw):
    """Resolve nome de médico com fuzzy matching. Retorna o nome canônico ou None."""
    return fuzzy_match(raw, VALID_DOCTORS)

def resolve_room(raw):
    """Resolve nome de sala com fuzzy matching. Retorna o nome canônico ou None."""
    return fuzzy_match(raw, VALID_ROOMS)

def validate_appointment_data(patient, doctor, time, room, insurance, priority):
    """
    Valida os dados de uma nova consulta.
    Retorna (erros, doctor_resolved, room_resolved).
    """
    errors = []

    if not patient or not patient.strip():
        errors.append("Nome do paciente não pode estar vazio.")

    doctor_resolved = resolve_doctor(doctor)
    if doctor_resolved is None:
        errors.append(f"Médico '{doctor}' não reconhecido. Opções: {', '.join(VALID_DOCTORS)}")

    room_resolved = resolve_room(room)
    if room_resolved is None:
        errors.append(f"Sala '{room}' inválida. Opções: {', '.join(VALID_ROOMS)}")

    try:
        parts = time.split(":")
        if len(parts) != 2:
            raise ValueError()
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError()
    except (ValueError, AttributeError):
        errors.append(f"Horário '{time}' inválido. Use o formato HH:MM (ex: 09:30).")

    if insurance not in ("A", "B", "C"):
        errors.append(f"Convênio '{insurance}' inválido. Opções: A, B, C")

    if priority not in ("normal", "urgent", "emergency"):
        errors.append(f"Prioridade '{priority}' inválida. Opções: normal, urgent, emergency")

    return errors, doctor_resolved, room_resolved

def register_new_appointment(patient, doctor, time, room, insurance, priority):
    """
    Registra uma nova consulta após validação e verificação de conflitos.
    Retorna (True, mensagem_sucesso) ou (False, mensagem_erro).
    """
    errors, doctor_resolved, room_resolved = validate_appointment_data(
        patient, doctor, time, room, insurance, priority
    )
    if errors:
        return False, "Dados inválidos:\n" + "\n".join(f"  - {e}" for e in errors)

    data = load_data()
    new_appointment = {
        "patient":  patient.strip(),
        "doctor":   doctor_resolved,
        "time":     time,
        "room":     room_resolved,
        "insurance": insurance,
        "priority": priority,
        "status":   "scheduled",
    }

    conflicts = check_new_appointment_conflicts(data, new_appointment)
    if conflicts:
        return False, (
            "Não foi possível cadastrar a consulta. Conflitos encontrados:\n"
            + "\n".join(f"  - {c}" for c in conflicts)
        )

    new_id = max((a["id"] for a in data["appointments"]), default=0) + 1
    new_appointment["id"] = new_id
    data["appointments"].append(new_appointment)
    save_data(data)

    return True, (
        f"Consulta cadastrada com sucesso! (ID: {new_id})\n"
        f"  Paciente   : {patient.strip()}\n"
        f"  Médico     : {doctor_resolved}\n"
        f"  Horário    : {time}–{end_time(time)}\n"
        f"  Sala       : {room_resolved}\n"
        f"  Convênio   : {insurance}\n"
        f"  Prioridade : {priority}"
    )

def doctor_schedule(data, doctor_name):
    result = []
    for appointment in data["appointments"]:
        if appointment["doctor"] == doctor_name:
            fee = calculate_fee_again(appointment)
            result.append({
                "patient":   appointment["patient"],
                "time":      appointment["time"],
                "end_time":  end_time(appointment["time"]),
                "priority":  appointment["priority"],
                "fee":       fee,
                "room":      appointment["room"],
                "status":    appointment["status"],
            })
    return result

def room_schedule(data, room_name):
    result = []
    for appointment in data["appointments"]:
        if appointment["room"] == room_name:
            fee = calculate_fee_again(appointment)
            result.append({
                "patient":  appointment["patient"],
                "doctor":   appointment["doctor"],
                "time":     appointment["time"],
                "end_time": end_time(appointment["time"]),
                "fee":      fee,
                "status":   appointment["status"],
            })
    return result

def add_walk_in(patient, doctor, priority):
    data = load_data()

    # Sala padrão por médico
    room = "104"
    if doctor == "Cardio":
        room = "101"
    elif doctor == "Ortho":
        room = "102"
    elif doctor == "Pediatrics":
        room = "103"

    # Coleta horários já ocupados pelo médico e pela sala (ignora cancelados)
    occupied = []
    for a in data["appointments"]:
        if a["status"] == "cancelled":
            continue
        if a["doctor"] == doctor or a["room"] == room:
            occupied.append(a["time"])

    new_time = find_free_slot(occupied, priority)
    if new_time is None:
        return False, "Sem slots disponíveis na agenda hoje para este médico/sala."

    new_id = max((a["id"] for a in data["appointments"]), default=0) + 1
    data["appointments"].append({
        "id":        new_id,
        "patient":   patient,
        "doctor":    doctor,
        "time":      new_time,
        "insurance": "C",
        "priority":  priority,
        "status":    "scheduled",
        "room":      room,
    })
    save_data(data)
    return True, new_time

def cancel_appointment(appointment_id):
    data = load_data()
    for appointment in data["appointments"]:
        if appointment["id"] == appointment_id:
            appointment["status"] = "cancelled"
    save_data(data)
