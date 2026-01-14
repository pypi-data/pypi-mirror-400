from abc import ABC, abstractmethod
from typing import Dict, List


class LLMAdapter(ABC):
    @abstractmethod
    def chat_completion(self, messages: List[Dict], temperature: float = 0.3) -> str:
        pass

    @abstractmethod
    def parse_intent(self, query: str, skills: list) -> Dict:
        pass
