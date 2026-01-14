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


class DetectedIntent(BaseModel):
    """A single detected intent with its context."""

    intent: Literal["return", "order_status", "profile"] = Field(
        description="The detected intent type"
    )
    confidence: float = Field(
        description="Confidence score 0.0-1.0"
    )
    relevant_text: str = Field(
        description="The portion of the message related to this intent"
    )


class MultiIntentClassification(BaseModel):
    """Classify multiple user intents from a single message."""

    intents: List[DetectedIntent] = Field(
        description="List of detected intents in order of mention. Empty if no clear intents."
    )
    reasoning: str = Field(
        description="Brief explanation of the classification"
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
        self.multi_intent_classifier = llm.with_structured_output(MultiIntentClassification)

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

    def detect_multi_intent(
        self, message: str, history: List[Dict[str, str]]
    ) -> List[DetectedIntent]:
        """
        Detect multiple user intents from a single message.

        Args:
            message: Current user message
            history: Conversation history (list of {"role": ..., "content": ...})

        Returns:
            List of DetectedIntent objects in order of mention
        """
        # Format history for prompt (last 5 messages)
        history_text = ""
        if history:
            recent_history = history[-5:]
            history_text = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in recent_history
            ])

        prompt = f"""Analyze the user's message and identify ALL distinct intents they are expressing.

Available intents:
- return: Customer wants to return an item, get a refund, or process a return
- order_status: Customer wants to check order status, tracking, or delivery information
- profile: Customer wants to view or update their profile, account details, or loyalty info

IMPORTANT:
- A single message may contain MULTIPLE intents (e.g., "I want to return my order and check my profile")
- List intents in the ORDER they are mentioned in the message
- Extract the relevant portion of text for each intent
- Only include intents that are clearly expressed, not implied
- If no clear intents are found, return an empty list

Conversation history:
{history_text if history_text else "(No prior conversation)"}

Current message: {message}

Identify all intents the customer is expressing."""

        try:
            result = self.multi_intent_classifier.invoke(prompt)
            if result.intents:
                intent_names = [i.intent for i in result.intents]
                print(f"[IntentRouter] Detected {len(result.intents)} intent(s): {intent_names}")
                print(f"[IntentRouter] Reasoning: {result.reasoning}")
            else:
                print("[IntentRouter] No clear intents detected")
            return result.intents
        except Exception as e:
            print(f"[IntentRouter] Multi-intent detection error: {e}")
            return []

    def route_multi(
        self, message: str, history: List[Dict[str, str]]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Detect multiple intents and extract context for each.

        Args:
            message: Current user message
            history: Conversation history

        Returns:
            List of (intent, context_dict) tuples in order of mention
        """
        detected_intents = self.detect_multi_intent(message, history)

        if not detected_intents:
            # Fall back to single intent detection
            intent = self.detect_intent(message, history)
            if intent == "unknown":
                return []
            context = self.extract_context(intent, message)
            return [(intent, context)]

        results = []
        for detected in detected_intents:
            # Extract context using the relevant text portion
            context = self.extract_context(detected.intent, detected.relevant_text)
            results.append((detected.intent, context))

        return results
