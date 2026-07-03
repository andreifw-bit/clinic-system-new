APPOINTMENT_DURATION_MINUTES = 30

def time_to_minutes(time_str):
    hour, minute = time_str.split(":")
    return int(hour) * 60 + int(minute)

def minutes_to_time(total_minutes):
    hour = (total_minutes // 60) % 24
    minute = total_minutes % 60
    return f"{hour:02d}:{minute:02d}"

def compare_time(a, b):
    return time_to_minutes(a) - time_to_minutes(b)

def same_slot(a, b):
    """Verifica sobreposição considerando duração de 30 minutos."""
    start_a = time_to_minutes(a)
    end_a   = start_a + APPOINTMENT_DURATION_MINUTES
    start_b = time_to_minutes(b)
    end_b   = start_b + APPOINTMENT_DURATION_MINUTES
    # Sobreposição: um começa antes do outro terminar
    return start_a < end_b and start_b < end_a

def end_time(time_str):
    """Retorna o horário de término de uma consulta."""
    return minutes_to_time(time_to_minutes(time_str) + APPOINTMENT_DURATION_MINUTES)

def find_free_slot(occupied_times, priority):
    """
    Dado os horários já ocupados (lista de strings HH:MM) e a prioridade,
    retorna o primeiro slot livre dentro do horário de funcionamento.

    - emergency : busca do início do dia (08:00) para frente
    - urgent    : busca a partir do horário atual (agora) para frente
    - normal    : busca do fim do dia (18:00) para trás, retorna o último slot livre
    """
    import datetime

    CLINIC_START = 8 * 60    # 08:00
    CLINIC_END   = 18 * 60   # 18:00 (último início às 17:30)

    # Converte ocupados para minutos
    occupied = set()
    for t in occupied_times:
        start = time_to_minutes(t)
        # marca todos os minutos cobertos pelo slot (a cada 30min)
        occupied.add(start)

    def slot_is_free(start_min):
        if start_min < CLINIC_START or start_min + APPOINTMENT_DURATION_MINUTES > CLINIC_END:
            return False
        for occ in occupied:
            occ_end = occ + APPOINTMENT_DURATION_MINUTES
            # sobreposição
            if start_min < occ_end and occ < start_min + APPOINTMENT_DURATION_MINUTES:
                return False
        return True

    slots = list(range(CLINIC_START, CLINIC_END, APPOINTMENT_DURATION_MINUTES))

    if priority == "emergency":
        # Primeiro slot livre do dia
        for s in slots:
            if slot_is_free(s):
                return minutes_to_time(s)

    elif priority == "urgent":
        # Primeiro slot livre a partir de agora
        now = datetime.datetime.now()
        now_min = now.hour * 60 + now.minute
        for s in slots:
            if s >= now_min and slot_is_free(s):
                return minutes_to_time(s)
        # Se não achou após agora, pega o primeiro livre do dia
        for s in slots:
            if slot_is_free(s):
                return minutes_to_time(s)

    else:  # normal
        # Último slot livre do dia
        for s in reversed(slots):
            if slot_is_free(s):
                return minutes_to_time(s)

    return None  # Sem slots disponíveis
