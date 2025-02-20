from typing import Tuple
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
import json
from .extraction_chain import InformationExtractionChain
from .prompts.conversation_prompt import CONVERSATION_TEMPLATE
from .prompts.summary_prompt import SUMMARY_TEMPLATE
from .models.user_data_model import UserData
from .state_manager import StateManager
from .conversation_manager import ConversationManager
from .question_handler import QuestionHandler
from .position_manager import PositionManager
from src.knowledge import CompanyKnowledgeBase
from .field_names import FIELD_NAMES
import os

class HRAgent:
    def __init__(self, model_name: str = "mistral"):
        knowledge_base = CompanyKnowledgeBase()
        
        # Initialize components
        self.position_manager = PositionManager(knowledge_base)
        self.question_handler = QuestionHandler(knowledge_base)
        self.state_manager = StateManager()
        self.conversation_manager = ConversationManager(model_name=model_name)
        self.extraction_chain = InformationExtractionChain(model_name=model_name)
        
        # Initialize LLM components
        self.llm = Ollama(model=model_name,base_url=os.getenv("OLLAMA_HOST") or "http://localhost:11434/")
       
        self.summary_chain = LLMChain(
            llm=self.llm,
            prompt=self._create_summary_prompt(),
            verbose=True
        )

    def _create_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["chat_history", "input", "current_state", "context", "position_info"],
            template=CONVERSATION_TEMPLATE
        )

    def _create_summary_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["user_data", "conversation_history", "position_info"],
            template=SUMMARY_TEMPLATE
        )

    def process_message(self, message: str) -> Tuple[str, bool]:
        # Extract and validate information
        extracted_info = self.extraction_chain.extract(message)
        validation_error = None
        if extracted_info:
            validation_error = self.state_manager.validate_and_store_info(extracted_info)

        # Check for questions and get answers
        additional_context = self.question_handler.get_answer(message) or ""
        
        # Get current state and prepare context
        current_state = self.state_manager.get_current_state()
        context = self.state_manager.prepare_context(validation_error)
        if additional_context:
            context += f"\n\nInformación adicional encontrada:\n{additional_context}"
        
        # Generate response
        response = self.conversation_manager.generate_response(
            message=message,
            current_state=current_state,
            context=context,
            position_info=self.position_manager.format_position_info()
        )
        
        return response, self.state_manager.is_complete()

    def generate_summary(self) -> str:
        """Generate a summary of the conversation and key points."""
        if not self.state_manager.is_complete():
            raise ValueError("Cannot generate summary: conversation is not complete")

        # Format user data
        user_data = self.state_manager.get_user_data()
        formatted_data = "\n".join(
            f"{FIELD_NAMES[k]}: {v}" 
            for k, v in user_data.items() 
            if v is not None
        )

        # Get conversation history
        conversation = self.conversation_manager.get_conversation_history()
        formatted_history = "\n".join(
            f"{'Usuario' if msg['type'] == 'human' else 'Asistente'}: {msg['content']}"
            for msg in conversation
        )

        # Generate summary
        return self.summary_chain.run(
            user_data=formatted_data,
            conversation_history=formatted_history,
            position_info=self.position_manager.format_position_info()
        )

    def save_conversation(self, file_path: str = "conversation.json"):
        data = {
            "is_complete": self.state_manager.is_complete(),
            "user_data": self.state_manager.get_user_data(),
            "assigned_position": self.position_manager.get_position_details(),
            "conversation": self.conversation_manager.get_conversation_history()
        }
        
        # Add summary if conversation is complete
        if self.state_manager.is_complete():
            data["summary"] = self.generate_summary()
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False) 