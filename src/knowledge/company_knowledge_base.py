from typing import List, Dict, Optional, Tuple
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import random

class CompanyKnowledgeBase:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.documents: List[Dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.teams_data: Dict = {}
        self.roles_data: Dict = {}
        self._load_company_data()
        self._load_organization_data()

    def _load_company_data(self) -> None:
        company_data_dir = Path("company_data")
        
        # Process each data file
        for file_path in company_data_dir.rglob("*"):
            if file_path.is_file():
                content = self._read_file(file_path)
                if content:
                    # Split content into chunks for better retrieval
                    chunks = self._chunk_content(content)
                    for chunk in chunks:
                        self.documents.append({
                            "content": chunk,
                            "source": str(file_path),
                            "type": file_path.suffix[1:]  # Remove the dot
                        })

        # Generate embeddings for all documents
        if self.documents:
            texts = [doc["content"] for doc in self.documents]
            self.embeddings = self.model.encode(texts, convert_to_tensor=True)

    def _read_file(self, file_path: Path) -> Optional[str]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix == '.json':
                    # Convert JSON to string representation
                    return json.dumps(json.load(f), indent=2, ensure_ascii=False)
                else:
                    return f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def _chunk_content(self, content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        chunks = []
        start = 0
        content_len = len(content)

        while start < content_len:
            end = start + chunk_size
            
            # Adjust end to not split in the middle of a line
            if end < content_len:
                # Try to find a line break near the end position
                next_newline = content.find('\n', end - overlap)
                if next_newline != -1 and next_newline - end < overlap:
                    end = next_newline + 1

            chunks.append(content[start:end])
            start = end - overlap

        return chunks

    def _load_organization_data(self) -> None:
        try:
            with open('company_data/organization/teams.json', 'r') as f:
                self.teams_data = json.load(f)['teams']
            with open('company_data/organization/roles.json', 'r') as f:
                self.roles_data = json.load(f)['roles']
        except Exception as e:
            print(f"Error loading organization data: {e}")
            self.teams_data = {}
            self.roles_data = {}

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.documents or self.embeddings is None:
            return []

        # Encode the query
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        
        # Ensure embeddings are on the same device and in the right format
        if hasattr(query_embedding, 'cpu'):
            query_embedding = query_embedding.cpu()
        if hasattr(self.embeddings, 'cpu'):
            embeddings = self.embeddings.cpu()
        else:
            embeddings = self.embeddings
            
        # Calculate similarities
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1),
            embeddings
        )[0]

        # Get top k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append({
                'content': self.documents[idx]['content'],
                'source': self.documents[idx]['source'],
                'similarity': float(similarities[idx])
            })
        
        return results

    def assign_random_position(self) -> Tuple[str, str, Dict]:
        # Get teams with open positions
        available_teams = []
        for team_id, team_info in self.teams_data.items():
            for role in team_info.get('roles', []):
                if role.get('openings', 0) > 0:
                    available_teams.append(team_id)
                    break
        
        if not available_teams:
            raise ValueError("No hay posiciones abiertas disponibles")

        # Select random team
        team_id = random.choice(available_teams)
        team_info = self.teams_data[team_id]

        # Get available roles in the team
        available_roles = [role['title'] for role in team_info.get('roles', []) 
                         if role.get('openings', 0) > 0]
        
        if not available_roles:
            raise ValueError(f"No hay roles disponibles en el equipo {team_info['name']}")

        # Select random role
        role_title = random.choice(available_roles)
        
        # Find detailed role info
        role_info = None
        for _, roles in self.roles_data.items():
            for role_id, role_data in roles.items():
                if role_data['title'] == role_title:
                    role_info = role_data
                    return team_id, role_id, role_info
        
        raise ValueError(f"No se encontró información detallada para el rol {role_title}")

    def get_team_info(self, team_id: str) -> Dict:
        return self.teams_data.get(team_id, {})
