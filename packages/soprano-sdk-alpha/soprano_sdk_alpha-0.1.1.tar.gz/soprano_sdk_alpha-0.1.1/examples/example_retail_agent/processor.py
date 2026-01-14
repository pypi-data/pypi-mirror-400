"""
Retail Agent Processor

Multi-workflow processor with LLM-based intent detection.
Supports: returns, order status, and profile inquiries.
Includes suspend/resume for workflow switching.
"""

import json
import os
import sys
import uuid
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
                "intent_queue": [],  # Queue for multi-intent processing
                "offer_queue_continue": False,  # Ask before processing next queued intent
            }
        return self._thread_states[thread_id]

    def _queue_intents(
        self, thread_id: str, intents: list
    ) -> None:
        """
        Queue multiple intents for sequential processing.

        Args:
            thread_id: Thread ID
            intents: List of (intent, context) tuples to queue
        """
        state = self._get_thread_state(thread_id)
        state["intent_queue"] = intents
        print(f"[Processor] Queued {len(intents)} intent(s): {[i[0] for i in intents]}")

    def _pop_next_intent(self, thread_id: str) -> tuple | None:
        """
        Pop and return the next intent from the queue.

        Returns:
            Tuple of (intent, context) or None if queue is empty
        """
        state = self._get_thread_state(thread_id)
        queue = state.get("intent_queue", [])
        if queue:
            next_intent = queue.pop(0)
            print(f"[Processor] Processing next queued intent: {next_intent[0]}")
            return next_intent
        return None

    def _has_queued_intents(self, thread_id: str) -> bool:
        """Check if there are queued intents waiting."""
        state = self._get_thread_state(thread_id)
        return bool(state.get("intent_queue"))

    def _process_next_queued_intent(self, thread_id: str) -> str:
        """Process the next intent from the queue."""
        next_intent = self._pop_next_intent(thread_id)
        if not next_intent:
            return "How else can I help you?"

        intent, context = next_intent
        state = self._get_thread_state(thread_id)
        state["offer_queue_continue"] = False

        self._thread_workflows[thread_id] = intent
        print(f"[Processor] Starting queued intent: {intent}")

        result = self.workflow_tools[intent].execute(
            thread_id=thread_id,
            initial_context=context
        )
        return self._parse_interrupt(result, thread_id)

    def _clear_intent_queue(self, thread_id: str) -> None:
        """Clear all queued intents."""
        state = self._get_thread_state(thread_id)
        state["intent_queue"] = []
        state["offer_queue_continue"] = False
        print("[Processor] Cleared intent queue")

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
        last_prompt = state.get("last_prompt", "")  # Get saved prompt

        if current_workflow:
            suspended = {
                "workflow_type": current_workflow,
                "thread_id": thread_id,
                "suspended_at": datetime.now().isoformat(),
                "last_prompt": last_prompt,  # Store the interrupted prompt
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
        last_prompt = suspended.get("last_prompt", "")

        # Generate a new thread_id for the resumed workflow (fresh start)
        new_thread_id = f"{thread_id}_resume_{uuid.uuid4().hex[:8]}"

        # Store mapping so we know which workflow thread to use
        state["resumed_workflow_thread"] = new_thread_id

        self._thread_workflows[thread_id] = workflow_type
        state["status"] = "interrupted"
        state["offer_resume"] = False
        state["last_prompt"] = last_prompt

        print(f"[Processor] Resuming suspended {workflow_type} workflow (new thread: {new_thread_id})")

        # Return the stored prompt - don't call execute()!
        # The next user message will start a fresh workflow with the new thread
        return last_prompt

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
                state["last_prompt"] = parts[3]  # Save prompt for suspend/resume
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

        # Completed - check for queued intents first, then suspended workflows
        state["status"] = "completed"
        if thread_id in self._thread_workflows:
            del self._thread_workflows[thread_id]

        # Clear resumed thread when workflow completes
        if "resumed_workflow_thread" in state:
            del state["resumed_workflow_thread"]

        # If there are queued intents from multi-intent detection, ask before continuing
        if self._has_queued_intents(thread_id):
            next_intent_info = state["intent_queue"][0]  # Peek, don't pop yet
            intent, _ = next_intent_info
            display_name = WORKFLOWS.get(intent, {}).get("display_name", intent)
            state["offer_queue_continue"] = True
            return f"{result}\n\nWould you like me to help with your {display_name} next?"

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

        # Check if we're offering to continue with queued intent
        if state.get("offer_queue_continue"):
            if self._is_resume_accepted(user_message):
                return self._process_next_queued_intent(thread_id)
            elif self._is_resume_declined(user_message):
                self._clear_intent_queue(thread_id)
                return "Okay, is there anything else I can help you with?"
            else:
                # User said something else - treat as new intent
                self._clear_intent_queue(thread_id)

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

            # Use resumed thread if available (for workflows resumed after suspension)
            # DON'T delete it - keep using it for ALL messages in the resumed workflow
            workflow_thread = state.get("resumed_workflow_thread", thread_id)

            print(f"[Processor] Continuing {workflow_type} workflow (thread: {workflow_thread})")
            result = self.workflow_tools[workflow_type].execute(
                thread_id=workflow_thread,
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

        # Detect intent(s) and extract context using multi-intent detection
        intents = self.router.route_multi(user_message, history)

        if not intents:
            return self._unknown_intent_response()

        # Get the first intent to process now
        first_intent, first_context = intents[0]

        # Queue remaining intents for later processing
        if len(intents) > 1:
            self._queue_intents(thread_id, intents[1:])

        # Start the first workflow
        self._thread_workflows[thread_id] = first_intent
        print(f"[Processor] Starting {first_intent} workflow")

        result = self.workflow_tools[first_intent].execute(
            thread_id=thread_id,
            initial_context=first_context
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

    # Single intent test messages
    single_intent_messages = [
        ("I want to return an item", []),
        ("Where is my order?", []),
        ("What's my account status?", []),
    ]

    # Multi-intent test messages
    multi_intent_messages = [
        ("I want to know my profile details and return my order", []),
        ("Check my order status and also update my email address", []),
        ("Return order #12345, check status of #67890, and show my profile", []),
    ]

    print("Testing SINGLE intent detection:")
    print("=" * 60)
    for msg, history in single_intent_messages:
        intents = processor.router.route_multi(msg, history)
        print(f"Message: {msg}")
        print(f"Intents: {[(i, c) for i, c in intents]}")
        print("-" * 60)

    print("\nTesting MULTI-intent detection:")
    print("=" * 60)
    for msg, history in multi_intent_messages:
        intents = processor.router.route_multi(msg, history)
        print(f"Message: {msg}")
        print(f"Detected {len(intents)} intent(s):")
        for i, (intent, context) in enumerate(intents, 1):
            print(f"  {i}. {intent}: {context}")
        print("-" * 60)
