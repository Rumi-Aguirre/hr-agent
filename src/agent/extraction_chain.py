from typing import Dict, Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
from langchain.output_parsers import PydanticOutputParser
from .models.extracted_info_model import ExtractedInfo
from .prompts import EXTRACTION_TEMPLATE
import os

class InformationExtractionChain:
    def __init__(self, model_name: str = "mistral"):
        self.llm = Ollama(model=model_name, base_url=os.getenv("OLLAMA_HOST") or "http://localhost:11434/")
        self.parser = PydanticOutputParser(pydantic_object=ExtractedInfo)
        self.chain = self._create_chain()

    def _create_chain(self) -> LLMChain:
        return LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                template=EXTRACTION_TEMPLATE,
                input_variables=["input"],
                partial_variables={"format_instructions": self.parser.get_format_instructions()}
            )
        )

    def _validate_extracted_info(self, extracted: ExtractedInfo, text: str) -> Dict:
        validated = {}

        if extracted.first_name:
            validated['first_name'] = extracted.first_name
            
        if extracted.age is not None:
            validated['age'] = extracted.age
            
        if extracted.preferred_schedule:
            validated['preferred_schedule'] = extracted.preferred_schedule
            
        return validated

    def extract(self, text: str) -> Dict:
        if not text or len(text.strip()) < 2:
            return {}
            
        try:
            result = self.chain.run(input=text)
            extracted = self.parser.parse(result)
            return self._validate_extracted_info(extracted, text)
            
        except Exception as e:
            print(f"Error parsing extraction result: {e}")
            return {} 