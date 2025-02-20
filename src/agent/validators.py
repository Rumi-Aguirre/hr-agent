from typing import Optional

class UserDataValidator:
    @staticmethod
    def validate_age(age: int) -> Optional[str]:
        if age <= 18 or age > 80:
            return "La edad debe estar entre 18 y 80 años."
        return None

    @staticmethod
    def validate_name(name: str) -> Optional[str]:
        if not name.replace(" ", "").isalpha():
            return "El nombre debe contener solo letras."
        if len(name) < 2:
            return "El nombre debe tener al menos 2 caracteres."
        return None

    @staticmethod
    def validate_schedule(schedule: str) -> Optional[str]:
        if schedule.lower() not in ["mañana", "tarde"]:
            return "El horario debe ser 'mañana' o 'tarde'."
        return None 