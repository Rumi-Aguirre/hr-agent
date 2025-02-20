from typing import List, Dict, Optional
from src.knowledge import CompanyKnowledgeBase

class QuestionHandler:
    QUESTION_INDICATORS = [
        'que', 'qué', 'cual', 'cuál', 'cuales', 'cuáles', 'quien', 'quién',
        'donde', 'dónde', 'cuando', 'cuándo', 'como', 'cómo', 'por que',
        'por qué', 'cuanto', 'cuánto', 'me puedes', 'me podrias', 'me podrías',
        'puedes', 'podrias', 'podrías', 'hay', 'tienen', 'existe', 'cuentan',
        'dime', 'explica', 'explícame', 'cuéntame', 'cuentame'
    ]

    def __init__(self, knowledge_base: CompanyKnowledgeBase):
        self.knowledge_base = knowledge_base

    def is_question(self, message: str) -> bool:
        message = message.lower().strip()
        
        if '?' in message:
            return True
            
        words = message.split()
        if not words:
            return False
            
        first_word = words[0]
        if first_word in self.QUESTION_INDICATORS:
            return True
            
        for indicator in self.QUESTION_INDICATORS:
            if indicator in message:
                return True
                
        return False

    def get_answer(self, message: str) -> Optional[str]:
        try:
            if not self.is_question(message):
                return None

            search_results = self.knowledge_base.search(message)
            if not search_results:
                return None

            return "\n".join(
                result['content'] for result in search_results
            )
        except Exception as e:
            print(f"Error searching for answer: {e}")
            return None 