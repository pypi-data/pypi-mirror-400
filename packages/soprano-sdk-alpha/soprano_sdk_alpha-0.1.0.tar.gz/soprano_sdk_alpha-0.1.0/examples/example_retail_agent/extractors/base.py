"""
Base extractor class for intent-specific context extraction.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel


class BaseExtractor(ABC):
    """Base class for intent-specific context extractors."""

    intent: str  # e.g., "return", "order_status", "profile"
    context_model: type[BaseModel]  # Pydantic model for extraction

    @abstractmethod
    def get_extraction_prompt(self) -> str:
        """Return the prompt for extracting context from user message."""
        pass

    def extract(self, llm: Any, message: str) -> Dict[str, Any]:
        """
        Extract context from message using LLM structured output.

        Args:
            llm: LangChain ChatOpenAI instance
            message: User's message to extract context from

        Returns:
            Dict with extracted fields (only non-None values)
        """
        prompt = f"{self.get_extraction_prompt()}\n\nMessage: {message}"

        try:
            extractor = llm.with_structured_output(self.context_model)
            result = extractor.invoke(prompt)
            # Return only non-None values
            return {k: v for k, v in result.model_dump().items() if v is not None}
        except Exception as e:
            print(f"[{self.__class__.__name__}] Extraction error: {e}")
            return {}
