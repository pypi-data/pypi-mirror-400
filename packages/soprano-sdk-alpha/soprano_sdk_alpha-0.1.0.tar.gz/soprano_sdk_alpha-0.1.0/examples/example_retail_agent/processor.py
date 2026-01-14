"""
Retail Agent Processor

Multi-workflow processor with LLM-based intent detection.
Supports: returns, order status, and profile inquiries.
Includes suspend/resume for workflow switching.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from soprano_sdk import WorkflowTool
from soprano_sdk.core.constants import InterruptType

from extractors import IntentRouter


# =============================================================================
# Workflow Configuration
# =============================================================================

WORKFLOWS = {
    "return": {
        "yaml": "workflows/return_workflow.yaml",
        "name": "return_workflow",
        "display_name": "return request",
    },
    "order_status": {
        "yaml": "workflows/order_status_workflow.yaml",
        "name": "order_status_workflow",
        "display_name": "order status check",
    },
    "profile": {
        "yaml": "workflows/profile_inquiry_workflow.yaml",
        "name": "profile_workflow",
        "display_name": "profile inquiry",
    },
}


# =============================================================================
# Retail Agent Processor
# =============================================================================

class RetailAgentProcessor:
    """
    Multi-workflow processor for retail agent with intelligent intent detection.

    Features:
    - LLM-based intent detection from message + conversation history
    - Context extraction for each workflow type (via IntentRouter)
    - Suspend/resume for workflow switching
    - Manages workflow state across conversation turns
    - Handles interrupts and resumes workflow appropriately
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the processor.

        Args:
            model: OpenAI model to use for intent detection and context extraction
        """
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.checkpointer = InMemorySaver()

        # Model config for workflow agents
        model_config = {
            "model_name": model,
            "base_url": os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
            "api_key": os.getenv("OPENAI_API_KEY", ""),
        }

        # Initialize workflow tools
        self.workflow_tools: Dict[str, WorkflowTool] = {}
        for key, config in WORKFLOWS.items():
            self.workflow_tools[key] = WorkflowTool(
                yaml_path=os.path.join(self.base_dir, config["yaml"]),
                name=config["name"],
                description=f"Process {key} requests",
                checkpointer=self.checkpointer,
                config={"model_config": model_config}
            )

        # Intent router handles detection + extraction
        llm = ChatOpenAI(model=model, temperature=0)
        self.router = IntentRouter(llm)

        # Thread state tracking
        self._thread_states: Dict[str, dict] = {}
        self._thread_workflows: Dict[str, str] = {}

    def _get_thread_state(self, thread_id: str) -> dict:
        """Get or create thread state."""
        if thread_id not in self._thread_states:
            self._thread_states[thread_id] = {
                "status": None,
                "suspended_workflows": [],
                "offer_resume": False,
            }
        return self._thread_states[thread_id]

    def _is_continuing_workflow(self, thread_id: str) -> bool:
        """Check if thread has an active workflow to continue."""
        state = self._get_thread_state(thread_id)
        return (
            thread_id in self._thread_workflows and
            state.get("status") == "interrupted"
        )

    def _unknown_intent_response(self) -> str:
        """Return help message for unknown intent."""
        return (
            "I'm not sure what you're looking for. I can help you with:\n"
            "- Returns and refunds\n"
            "- Order status and tracking\n"
            "- Profile and account information\n\n"
            "How can I assist you today?"
        )

    def _suspend_current_workflow(self, thread_id: str) -> None:
        """Suspend the current workflow to the stack."""
        state = self._get_thread_state(thread_id)
        current_workflow = self._thread_workflows.get(thread_id)

        if current_workflow:
            suspended = {
                "workflow_type": current_workflow,
                "thread_id": thread_id,
                "suspended_at": datetime.now().isoformat(),
            }
            state["suspended_workflows"].append(suspended)
            print(f"[Processor] Suspended {current_workflow} workflow")

    def _resume_suspended_workflow(self, thread_id: str) -> Optional[str]:
        """Pop and resume the most recently suspended workflow."""
        state = self._get_thread_state(thread_id)

        if not state.get("suspended_workflows"):
            return None

        suspended = state["suspended_workflows"].pop()
        workflow_type = suspended["workflow_type"]

        self._thread_workflows[thread_id] = workflow_type
        state["status"] = "interrupted"
        state["offer_resume"] = False

        print(f"[Processor] Resuming suspended {workflow_type} workflow")

        # Get the next prompt from the suspended workflow
        result = self.workflow_tools[workflow_type].execute(
            thread_id=thread_id,
            user_message=""  # Empty to just get the current prompt
        )
        return self._parse_interrupt(result, thread_id)

    def _discard_suspended_workflows(self, thread_id: str) -> None:
        """Discard all suspended workflows."""
        state = self._get_thread_state(thread_id)
        state["suspended_workflows"] = []
        state["offer_resume"] = False
        print("[Processor] Discarded suspended workflows")

    def _is_resume_accepted(self, message: str) -> bool:
        """Check if user message accepts resuming suspended workflow."""
        positive = ["yes", "yeah", "yep", "sure", "ok", "okay", "continue", "resume", "y"]
        return message.lower().strip() in positive

    def _is_resume_declined(self, message: str) -> bool:
        """Check if user message declines resuming suspended workflow."""
        negative = ["no", "nope", "nah", "cancel", "skip", "n", "forget it", "nevermind"]
        return message.lower().strip() in negative

    def _handle_intent_change(
        self,
        thread_id: str,
        detected_intent: str,
        user_message: str,
        history: List[Dict[str, str]]
    ) -> str:
        """Handle external intent change - suspend current and start new workflow."""
        # Suspend current workflow
        self._suspend_current_workflow(thread_id)

        # Map detected intent to workflow key
        intent = detected_intent.lower().strip()

        # If agent returned "unknown", classify using router
        if intent == "unknown":
            print("[Processor] Agent detected unknown intent, classifying with router...")
            intent, context = self.router.route(user_message, history)
            if intent == "unknown":
                return self._unknown_intent_response()
        else:
            # Check if it's a known workflow
            if intent not in self.workflow_tools:
                # Try to match partial names
                for key in self.workflow_tools:
                    if key in intent or intent in key:
                        intent = key
                        break
                else:
                    # Still not found - use router to classify
                    intent, context = self.router.route(user_message, history)
                    if intent == "unknown":
                        return self._unknown_intent_response()

            # Extract context for the new workflow
            context = self.router.extract_context(intent, user_message)

        # Start the new workflow
        self._thread_workflows[thread_id] = intent
        print(f"[Processor] Switching to {intent} workflow")

        result = self.workflow_tools[intent].execute(
            thread_id=thread_id,
            initial_context=context
        )
        return self._parse_interrupt(result, thread_id)

    def _parse_interrupt(self, result: str, thread_id: str) -> str:
        """Parse interrupt result and update state."""
        state = self._get_thread_state(thread_id)

        # User input interrupt
        if result.startswith(InterruptType.USER_INPUT):
            parts = result.split("|", 3)
            if len(parts) >= 4:
                state["status"] = "interrupted"
                return parts[3]

        # Async interrupt
        if result.startswith(InterruptType.ASYNC):
            parts = result.split("|", 3)
            if len(parts) >= 4:
                metadata = json.loads(parts[3])
                state["status"] = "async_pending"
                state["metadata"] = metadata
                return f"Processing your request... (Job: {metadata.get('job_id', 'unknown')})"

        # Intent change interrupt - this is handled separately via _handle_intent_change
        # This path is for when the interrupt comes back from a resume
        if result.startswith(InterruptType.INTENT_CHANGE):
            parts = result.split("|", 3)
            if len(parts) >= 4:
                metadata = json.loads(parts[3])
                detected_intent = metadata.get("detected_intent", "unknown")
                # This will be handled in process_message
                state["status"] = "intent_change"
                state["pending_intent"] = detected_intent
                return f"__INTENT_CHANGE__:{detected_intent}"

        # Completed - check for suspended workflows
        state["status"] = "completed"
        if thread_id in self._thread_workflows:
            del self._thread_workflows[thread_id]

        # If there are suspended workflows, offer to resume
        if state.get("suspended_workflows"):
            suspended = state["suspended_workflows"][-1]
            workflow_type = suspended["workflow_type"]
            display_name = WORKFLOWS.get(workflow_type, {}).get("display_name", workflow_type)
            state["offer_resume"] = True
            return f"{result}\n\nWould you like to continue with your {display_name}?"

        return result

    def process_message(
        self,
        thread_id: str,
        user_message: str,
        history: List[Dict[str, str]] = None
    ) -> str:
        """
        Process a user message through the appropriate workflow.

        Args:
            thread_id: Unique conversation/session ID
            user_message: User's message
            history: Conversation history for intent detection

        Returns:
            Response string (either workflow prompt or final outcome)
        """
        history = history or []
        state = self._get_thread_state(thread_id)

        # Check if we're offering to resume a suspended workflow
        if state.get("offer_resume"):
            if self._is_resume_accepted(user_message):
                return self._resume_suspended_workflow(thread_id)
            elif self._is_resume_declined(user_message):
                self._discard_suspended_workflows(thread_id)
                return "Okay, I've cancelled the previous request. How else can I help you?"
            else:
                # User said something else - treat as new intent
                self._discard_suspended_workflows(thread_id)

        # Check for pending intent change (from resume)
        if state.get("status") == "intent_change":
            detected_intent = state.pop("pending_intent", "unknown")
            state["status"] = None
            return self._handle_intent_change(thread_id, detected_intent, user_message, history)

        # Continue existing workflow if interrupted
        if self._is_continuing_workflow(thread_id):
            workflow_type = self._thread_workflows[thread_id]
            print(f"[Processor] Continuing {workflow_type} workflow")
            result = self.workflow_tools[workflow_type].execute(
                thread_id=thread_id,
                user_message=user_message
            )

            # Check if result is an intent change
            if result.startswith(InterruptType.INTENT_CHANGE):
                parts = result.split("|", 3)
                if len(parts) >= 4:
                    metadata = json.loads(parts[3])
                    detected_intent = metadata.get("detected_intent", "unknown")
                    return self._handle_intent_change(thread_id, detected_intent, user_message, history)

            return self._parse_interrupt(result, thread_id)

        # Detect intent and extract context
        intent, context = self.router.route(user_message, history)

        if intent == "unknown":
            return self._unknown_intent_response()

        # Start new workflow
        self._thread_workflows[thread_id] = intent
        print(f"[Processor] Starting {intent} workflow")

        result = self.workflow_tools[intent].execute(
            thread_id=thread_id,
            initial_context=context
        )
        return self._parse_interrupt(result, thread_id)

    def is_async_pending(self, thread_id: str) -> bool:
        """Check if a workflow is waiting for async operation."""
        return self._get_thread_state(thread_id).get("status") == "async_pending"

    def get_async_metadata(self, thread_id: str) -> dict:
        """Get metadata for pending async operation."""
        return self._get_thread_state(thread_id).get("metadata", {})

    def complete_async(self, thread_id: str, async_result: Any) -> str:
        """
        Complete a pending async operation by resuming the workflow.

        Args:
            thread_id: Thread ID of the pending workflow
            async_result: Result from the async operation

        Returns:
            Response string (next prompt or final outcome)
        """
        if not self.is_async_pending(thread_id):
            return "No pending async operation for this conversation."

        workflow_type = self._thread_workflows.get(thread_id)
        if not workflow_type:
            return "No active workflow found."

        result = self.workflow_tools[workflow_type].resume(thread_id, async_result)
        return self._parse_interrupt(result, thread_id)

    def is_workflow_active(self, thread_id: str) -> bool:
        """Check if a workflow is active (interrupted, waiting for input)."""
        status = self._get_thread_state(thread_id).get("status")
        return status in ("interrupted", "async_pending")

    def has_suspended_workflows(self, thread_id: str) -> bool:
        """Check if there are suspended workflows."""
        return bool(self._get_thread_state(thread_id).get("suspended_workflows"))

    def reset_workflow(self, thread_id: str):
        """Reset workflow state for a thread."""
        self._thread_states.pop(thread_id, None)
        self._thread_workflows.pop(thread_id, None)


# For direct testing
if __name__ == "__main__":
    processor = RetailAgentProcessor()

    test_messages = [
        ("I want to return an item", []),
        ("Where is my order?", []),
        ("What's my account status?", []),
        ("Order #12345 is damaged, I need to return it", []),
        ("Can you check the status of order 12342?", []),
        ("What's my email on file?", []),
    ]

    print("Testing intent detection + extraction:")
    print("=" * 60)
    for msg, history in test_messages:
        intent, context = processor.router.route(msg, history)
        print(f"Message: {msg}")
        print(f"Intent: {intent}")
        print(f"Context: {context}")
        print("-" * 60)
