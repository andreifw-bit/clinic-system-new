from services.schedule_service import (
    load_data,
    find_conflicts,
    doctor_schedule,
    room_schedule,
    add_walk_in,
    cancel_appointment,
    register_new_appointment,
    resolve_doctor,
    resolve_room,
)
from services.billing_service import calculate_fee
from utils.formatter import format_fee, priority_color, priority_color_again
from utils.colors import success, error, warn, info, bold
from utils.time_utils import end_time
from config import VALID_DOCTORS, VALID_ROOMS

# ─── helpers de exibição ──────────────────────────────────────────────────────

def print_all():
    data = load_data()
    print(bold("\n=== CONSULTAS ==="))
    total_fees = 0
    for appointment in data["appointments"]:
        fee = calculate_fee(appointment)
        color = priority_color(appointment["priority"])
        color2 = priority_color_again(appointment["priority"])
        total_fees += fee

        status_label = appointment["status"]
        end = end_time(appointment["time"])

        print(f"Paciente : {appointment['patient']}")
        print(f"Médico   : {appointment['doctor']}")
        print(f"Horário  : {appointment['time']}–{end}")
        print(f"Sala     : {appointment['room']}")
        print(f"Honorário: {format_fee(fee)}")
        print(f"Cor      : {color} / {color2}")
        print(f"Status   : {status_label}")
        print("─" * 32)
    print(f"TOTAL HONORÁRIOS : {format_fee(total_fees)}")
    print(f"CONFLITOS        : {find_conflicts(data)}")

def print_schedule(entries, title):
    """Exibe uma agenda (médico ou sala) de forma legível."""
    print(bold(f"\n=== {title} ==="))
    if not entries:
        print(warn("  Nenhuma consulta encontrada."))
        return
    for e in entries:
        status_color = success if e["status"] == "scheduled" else error
        print(f"  {e['time']}–{e['end_time']}  |  "
              f"Paciente: {e['patient']}  |  "
              f"Status: {status_color(e['status'])}  |  "
              f"Honorário: {format_fee(e['fee'])}")
    print()

# ─── fluxos interativos ───────────────────────────────────────────────────────

def walk_in_flow():
    print(bold("\n=== ADD WALK-IN ==="))
    print(info(f"Médicos disponíveis: {', '.join(VALID_DOCTORS)}"))
    print(info("Prioridades        : normal, urgent, emergency"))
    print()
    patient  = input("Nome do paciente : ").strip()
    doctor   = input("Médico           : ").strip()
    priority = input("Prioridade       : ").strip().lower()

    resolved = resolve_doctor(doctor)
    if resolved is None:
        print(error(f"✘ Médico '{doctor}' não reconhecido. Opções: {', '.join(VALID_DOCTORS)}"))
        return
    if resolved.lower() != doctor.lower():
        print(info(f"  → Interpretado como: {resolved}"))

    if priority not in ("normal", "urgent", "emergency"):
        print(error(f"✘ Prioridade '{priority}' inválida. Opções: normal, urgent, emergency"))
        return

    if not patient:
        print(error("✘ Nome do paciente não pode estar vazio."))
        return


    from utils.time_utils import end_time
    ok, result = add_walk_in(patient, resolved, priority)
    if ok:
        print(success(f"✔ Walk-in adicionado para {patient} com Dr. {resolved} às {result}–{end_time(result)} (prioridade: {priority})."))
    else:
        print(error(f"✘ {result}"))

def cancel_flow():
    print(bold("\n=== CANCELAR CONSULTA ==="))
    data = load_data()
    agendadas = [a for a in data["appointments"] if a["status"] != "cancelled"]
    if not agendadas:
        print(warn("  Nenhuma consulta ativa para cancelar."))
        return
    print(info("Consultas ativas:"))
    for a in agendadas:
        print(f"  ID {a['id']:>3} | {a['time']} | {a['patient']:<15} | Dr. {a['doctor']}")
    print()
    raw = input("ID da consulta a cancelar: ").strip()
    try:
        appointment_id = int(raw)
    except ValueError:
        print(error(f"✘ '{raw}' não é um ID válido."))
        return

    ids_ativos = {a["id"] for a in agendadas}
    if appointment_id not in ids_ativos:
        print(error(f"✘ Nenhuma consulta ativa com ID {appointment_id}."))
        return

    cancel_appointment(appointment_id)
    alvo = next(a for a in agendadas if a["id"] == appointment_id)
    print(success(f"✔ Consulta ID {appointment_id} ({alvo['patient']} – Dr. {alvo['doctor']} às {alvo['time']}) cancelada."))

def new_appointment_flow():
    print(bold("\n=== CADASTRAR NOVA CONSULTA ==="))
    print(info(f"Médicos    : {', '.join(VALID_DOCTORS)}"))
    print(info(f"Salas      : {', '.join(VALID_ROOMS)}"))
    print(info("Convênios  : A, B, C"))
    print(info("Prioridades: normal, urgent, emergency"))
    print()

    patient   = input("Nome do paciente : ").strip()
    doctor    = input("Médico           : ").strip()
    time      = input("Horário (HH:MM)  : ").strip()
    room      = input("Sala             : ").strip()
    insurance = input("Convênio (A/B/C) : ").strip().upper()
    priority  = input("Prioridade       : ").strip().lower()

    ok, msg = register_new_appointment(patient, doctor, time, room, insurance, priority)
    print()
    if ok:
        print(success("✔ " + msg))
    else:
        print(error("✘ " + msg))
    print()

def doctor_schedule_flow():
    print(bold("\n=== AGENDA POR MÉDICO ==="))
    print(info(f"Médicos disponíveis: {', '.join(VALID_DOCTORS)}"))
    raw = input("Digite o médico: ").strip()
    resolved = resolve_doctor(raw)
    if resolved is None:
        print(error(f"✘ Médico '{raw}' não reconhecido. Opções: {', '.join(VALID_DOCTORS)}"))
        return
    if resolved.lower() != raw.lower():
        print(info(f"  → Interpretado como: {resolved}"))
    entries = doctor_schedule(load_data(), resolved)
    print_schedule(entries, f"Agenda – Dr. {resolved}")

def room_schedule_flow():
    print(bold("\n=== AGENDA POR SALA ==="))
    print(info(f"Salas disponíveis: {', '.join(VALID_ROOMS)}"))
    raw = input("Digite a sala: ").strip()
    resolved = resolve_room(raw)
    if resolved is None:
        print(error(f"✘ Sala '{raw}' inválida. Opções: {', '.join(VALID_ROOMS)}"))
        return
    if resolved != raw:
        print(info(f"  → Interpretado como sala: {resolved}"))
    entries = room_schedule(load_data(), resolved)
    print_schedule(entries, f"Agenda – Sala {resolved}")

# ─── main ─────────────────────────────────────────────────────────────────────

def main():
    while True:
        print(bold("\n=== MENU ==="))
        print("1 - Listar consultas")
        print("2 - Cadastrar nova consulta")
        print("3 - Add walk-in")
        print("4 - Cancelar consulta")
        print("5 - Agenda por médico")
        print("6 - Agenda por sala")
        print("7 - Sair")
        op = input("Escolha: ").strip()

        if op == "1":
            print_all()
        elif op == "2":
            new_appointment_flow()
        elif op == "3":
            walk_in_flow()
        elif op == "4":
            cancel_flow()
        elif op == "5":
            doctor_schedule_flow()
        elif op == "6":
            room_schedule_flow()
        elif op == "7":
            break
        else:
            print(error("✘ Opção inválida."))

if __name__ == "__main__":
    main()
