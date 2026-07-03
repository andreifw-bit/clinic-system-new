class Appointment:
    def __init__(self, appointment_id, patient, doctor, time, insurance, priority, status, room):
        self.id = appointment_id
        self.patient = patient
        self.doctor = doctor
        self.time = time
        self.insurance = insurance
        self.priority = priority
        self.status = status
        self.room = room

    def describe(self):
        return f"{self.id} - {self.patient} / {self.doctor} / {self.time}"
