from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ModelGateway(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, messages: List[Dict[str, str]], **kwargs) -> str:
        pass

class StubModelGateway(ModelGateway):
    def generate_response(self, system_prompt: str, messages: List[Dict[str, str]], **kwargs) -> str:
        last_message = messages[-1]["content"] if messages else ""
        return f"[STUB LLM RESPONSE] Processed: {last_message}"

gateway = StubModelGateway()
