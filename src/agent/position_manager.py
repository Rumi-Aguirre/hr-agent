from typing import Dict, Tuple
from src.knowledge import CompanyKnowledgeBase

class PositionManager:
    def __init__(self, knowledge_base: CompanyKnowledgeBase):
        """Initialize with a knowledge base."""
        self.knowledge_base = knowledge_base
        self.team_id = "unknown"
        self.role_id = "unknown"
        self.role_info = {}
        self.team_info = {}
        self._assign_initial_position()

    def _assign_initial_position(self) -> None:
        try:
            self.team_id, self.role_id, self.role_info = self.knowledge_base.assign_random_position()
            self.team_info = self.knowledge_base.get_team_info(self.team_id)
        except ValueError as e:
            print(f"Error assigning position: {e}")

    def format_position_info(self) -> str:
        if not self.role_info or not self.team_info:
            return "Información del puesto no disponible"
        
        return f"""
Equipo: {self.team_info.get('name', 'No disponible')}
Puesto: {self.role_info.get('title', 'No disponible')}
Descripción del puesto: {self.role_info.get('description', 'No disponible')}
Líder del equipo: {self.team_info.get('lead', 'No disponible')}
Proyectos actuales: {', '.join(self.team_info.get('current_projects', ['No disponible']))}
"""

    def get_position_details(self) -> Dict:
        return {
            "team": self.team_info.get('name'),
            "role": self.role_info.get('title'),
            "department": self.role_info.get('department')
        } 