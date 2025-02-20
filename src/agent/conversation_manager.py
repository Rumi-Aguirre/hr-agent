from typing import Dict, Tuple
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
from .prompts.conversation_prompt import CONVERSATION_TEMPLATE
import os

class ConversationManager:
    def __init__(self, model_name: str = "mistral"):
        self.llm = Ollama(model=model_name, base_url=os.getenv("OLLAMA_HOST") or "http://localhost:11434/")
        
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self._create_prompt(),
            verbose=True
        )

    def _create_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["chat_history", "input", "current_state", "context", "position_info"],
            template=CONVERSATION_TEMPLATE
        )

    def format_chat_history(self) -> str:
        chat_history = self.memory.load_memory_variables({})["chat_history"]
        formatted_history = ""
        for msg in chat_history:
            if msg.type == "human":
                formatted_history += f"Human: {msg.content}\\n"
            else:
                formatted_history += f"Assistant: {msg.content}\\n"
        return formatted_history

    def generate_response(self, message: str, current_state: str, context: str, position_info: str) -> str:
        response = self.conversation.run(
            input=message,
            current_state=current_state,
            chat_history=self.format_chat_history(),
            context=context,
            position_info=position_info
        )
        
        # Update conversation memory
        self.memory.save_context(
            {"input": message},
            {"output": response}
        )
        
        return response

    def get_conversation_history(self) -> list[Dict]:
        """Get the full conversation history."""
        return [
            {
                "type": msg.type,
                "content": msg.content
            }
            for msg in self.memory.chat_memory.messages
        ] 