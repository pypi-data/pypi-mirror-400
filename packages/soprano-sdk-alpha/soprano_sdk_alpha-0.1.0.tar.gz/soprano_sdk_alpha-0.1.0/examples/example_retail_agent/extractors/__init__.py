"""
Extractors module - handles intent detection and context extraction.
"""

from typing import Any, Dict, List, Literal, Tuple

from pydantic import BaseModel, Field

from .base import BaseExtractor
from .return_extractor import ReturnExtractor, ReturnRequestContext
from .order_extractor import OrderStatusExtractor, OrderStatusContext
from .profile_extractor import ProfileExtractor, ProfileContext

__all__ = [
    "IntentRouter",
    "BaseExtractor",
    "ReturnExtractor",
    "ReturnRequestContext",
    "OrderStatusExtractor",
    "OrderStatusContext",
    "ProfileExtractor",
    "ProfileContext",
]


class IntentClassification(BaseModel):
    """Classify user intent from message + conversation history."""

    intent: Literal["return", "order_status", "profile", "unknown"] = Field(
        description="Detected user intent"
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0"
    )
    reasoning: str = Field(
        description="Brief explanation of classification"
    )


class IntentRouter:
    """
    Routes messages to appropriate extractors based on detected intent.

    Handles:
    1. Intent detection from message + conversation history
    2. Context extraction using intent-specific extractors
    """

    EXTRACTORS: Dict[str, BaseExtractor] = {
        "return": ReturnExtractor(),
        "order_status": OrderStatusExtractor(),
        "profile": ProfileExtractor(),
    }

    def __init__(self, llm: Any):
        """
        Initialize the router.

        Args:
            llm: LangChain ChatOpenAI instance
        """
        self.llm = llm
        self.intent_classifier = llm.with_structured_output(IntentClassification)

    def detect_intent(self, message: str, history: List[Dict[str, str]]) -> str:
        """
        Detect user intent from current message + conversation history.

        Args:
            message: Current user message
            history: Conversation history (list of {"role": ..., "content": ...})

        Returns:
            Intent string: "return", "order_status", "profile", or "unknown"
        """
        # Format history for prompt (last 5 messages)
        history_text = ""
        if history:
            recent_history = history[-5:]
            history_text = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in recent_history
            ])

        prompt = f"""Classify the user's intent based on this message and conversation history.

Available intents:
- return: Customer wants to return an item, get a refund, or process a return
- order_status: Customer wants to check order status, tracking, or delivery information
- profile: Customer wants to view or update their profile, account details, or loyalty info
- unknown: Intent is unclear or doesn't match any of the above

Conversation history:
{history_text if history_text else "(No prior conversation)"}

Current message: {message}

Classify the intent based on what the customer is trying to accomplish."""

        try:
            result = self.intent_classifier.invoke(prompt)
            print(f"[IntentRouter] Detected: {result.intent} (confidence: {result.confidence:.2f})")
            print(f"[IntentRouter] Reasoning: {result.reasoning}")
            return result.intent
        except Exception as e:
            print(f"[IntentRouter] Detection error: {e}")
            return "unknown"

    def extract_context(self, intent: str, message: str) -> Dict[str, Any]:
        """
        Extract context from message using the appropriate extractor.

        Args:
            intent: Detected intent type
            message: User's message

        Returns:
            Dict with extracted fields (only non-None values)
        """
        extractor = self.EXTRACTORS.get(intent)
        if extractor:
            context = extractor.extract(self.llm, message)
            if context:
                print(f"[IntentRouter] Extracted context: {context}")
            return context
        return {}

    def route(self, message: str, history: List[Dict[str, str]]) -> Tuple[str, Dict[str, Any]]:
        """
        Detect intent and extract context in one call.

        Args:
            message: Current user message
            history: Conversation history

        Returns:
            Tuple of (intent, context_dict)
        """
        intent = self.detect_intent(message, history)
        context = self.extract_context(intent, message) if intent != "unknown" else {}
        return intent, context
