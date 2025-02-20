from typing import Dict, List, Optional
from .models.user_data_model import UserData
from .validators import UserDataValidator
from .field_names import FIELD_NAMES
class StateManager:
    def __init__(self):
        self.user_data = UserData()
        self.validator = UserDataValidator()

    def validate_and_store_info(self, extracted_info: Dict) -> Optional[str]:
        """Validate and store extracted information."""
        for field, value in extracted_info.items():
            if field not in self.user_data.model_dump():
                continue
                
            # Validate based on field type
            error = None
            if field == 'age':
                error = self.validator.validate_age(value)
            elif field == 'first_name':
                error = self.validator.validate_name(value)
            elif field == 'preferred_schedule':
                error = self.validator.validate_schedule(value)
                
            if error:
                return error
                
            # Store valid value
            setattr(self.user_data, field, value)
        
        return None

    def get_current_state(self) -> str:
        """Get the current state of collected information and what's missing."""
        state_lines = ["Información recopilada:"]
        
        # Add collected information
        if self.user_data.first_name:
            state_lines.append(f"- Nombre: {self.user_data.first_name}")
        if self.user_data.age:
            state_lines.append(f"- Edad: {self.user_data.age}")
        if self.user_data.preferred_schedule:
            state_lines.append(f"- Horario preferido: {self.user_data.preferred_schedule}")
        
        # Add missing fields
        missing = self.user_data.get_missing_fields()
        if missing:
            state_lines.append("\nInformación pendiente:")
            for field in missing:
                state_lines.append(f"- {FIELD_NAMES[field]}")
        
        return "\n".join(state_lines)

    def prepare_context(self, validation_error: Optional[str] = None) -> str:
        """Prepare context for the conversation based on current state."""
        if validation_error:
            # Add validation error context
            context = f"ERROR DE VALIDACIÓN: {validation_error}\\n"
            context += "ACCIÓN REQUERIDA: Explica el error y pide el dato de nuevo de forma amable."
            
            # Add specific guidance based on the missing field
            missing_fields = self.user_data.get_missing_fields()
            if missing_fields:
                field = missing_fields[0]
                if field == 'first_name':
                    context += "\\nRecuerda: El nombre debe contener solo letras y tener al menos 2 caracteres."
                elif field == 'age':
                    context += "\\nRecuerda: La edad debe estar entre 18 y 80 años."
                elif field == 'preferred_schedule':
                    context += "\\nRecuerda: El horario debe ser 'mañana' o 'tarde'."
        else:
            # Add context about what information to ask next
            missing_fields = self.user_data.get_missing_fields()
            if missing_fields:
                field = missing_fields[0]
                context = f"SIGUIENTE DATO REQUERIDO: {FIELD_NAMES[field]}"
            else:
                context = "INFORMACIÓN COMPLETA: Despídete amablemente."
        
        return context

    def is_complete(self) -> bool:
        """Check if all required information is complete."""
        return self.user_data.is_complete()

    def get_user_data(self) -> Dict:
        """Get the current user data."""
        return self.user_data.model_dump() 