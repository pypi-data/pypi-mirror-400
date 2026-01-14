from typing import Dict, Any, List, Optional, Tuple
import json

from jinja2 import Environment
from langgraph.types import interrupt

from .base import ActionStrategy
from ..agents.factory import AgentFactory, AgentAdapter
from ..agents.structured_output import create_structured_output_model, validate_field_definitions
from ..core.constants import (
    WorkflowKeys,
    DEFAULT_MAX_ATTEMPTS,
    MAX_ATTEMPTS_MESSAGE,
    TransitionPattern
)
from ..core.rollback_strategies import (
    RollbackStrategy,
    HistoryBasedRollback,
    DependencyBasedRollback
)
from ..core.state import initialize_state
from ..utils.logger import logger
from ..utils.tracing import trace_node_execution, trace_agent_invocation, add_node_result

VALIDATION_ERROR_MESSAGE = "validation failed for the provided input, please enter valid input"
INVALID_INPUT_MESSAGE = "Looks like the input is invalid. Please double-check and re-enter it."
COLLECTION_FAILURE_MESSAGE = "I couldn't understand your response. Please try again and provide the required information."

def _wrap_instructions_with_intent_detection(
        instructions: str,
        collector_nodes: Dict[str, str],
        with_structured_output: bool
) -> str:
    if not collector_nodes:
        return instructions

    collector_nodes_str = "\n".join(f"- {node_name}: {description}" for node_name, description in collector_nodes.items())
    return f"""
{instructions}

PREVIOUSLY COLLECTED INFORMATION:
{collector_nodes_str}

CORRECTION DETECTION:
If the user wants to CHANGE or CORRECT any previously collected information listed above,
respond with ONLY:
{"INTENT_CHANGE: <node_name>" if not with_structured_output else "set intent_change to <node_name>"}

Use the EXACT node_name from the list above.

Examples of when to trigger INTENT_CHANGE:
- "actually my order id is..." → INTENT_CHANGE: collect_order_id
- "my bad, the order number is..." → INTENT_CHANGE: collect_order_id
- "wait, I gave you the wrong..." → INTENT_CHANGE: [relevant node]
- "can I change my..." → INTENT_CHANGE: [relevant node]
- "no, my [field] is..." → INTENT_CHANGE: [relevant node]

Do NOT trigger INTENT_CHANGE if user is providing new information for your current question.

BOT RESPONSE RULES:
- If the user is asking a question or needs information, provide a helpful and concise response
- If the user input is unclear or does not provide enough information, ask for clarification or more details
- {"populate bot_response field to respond back to the user" if with_structured_output else ""}
- Do not respond or use bot_response if the user provides a valid input
"""


def _wrap_instructions_with_unknown_intent_detection(
    instructions: str,
    current_task_description: str,
    with_structured_output: bool
) -> str:
    """Add instructions for detecting when user wants something unrelated to current task."""
    return f"""{instructions}

IMPORTANT - INTENT RELEVANCE CHECK:
Your current task is: {current_task_description}

If the user's message is clearly NOT related to this task and they seem to want
something completely different, respond with ONLY:
{"INTENT_CHANGE: unknown" if not with_structured_output else "set intent_change to 'unknown'"}

Examples of when to trigger INTENT_CHANGE: unknown:
- User asks about a completely different topic
- User says "actually I want to..." (different service)
- User ignores your question and asks for something else

Do NOT trigger INTENT_CHANGE: unknown if:
- User is providing clarifying information about their request
- User is answering your question (even if indirectly)
- User is asking for help understanding your question
"""


def _create_rollback_strategy(strategy_name: str) -> RollbackStrategy:
    if strategy_name == "dependency_based":
        return DependencyBasedRollback()
    elif strategy_name == "history_based":
        return HistoryBasedRollback()
    else:
        logger.warning(f"Unknown rollback strategy '{strategy_name}', using history_based")
        return HistoryBasedRollback()

def _get_agent_response(agent: AgentAdapter, conversation: List[Dict[str, str]]) -> Any:
    agent_response = agent.invoke(conversation)
    
    conversation.append({"role": "assistant", "content": str(agent_response)})
    
    return agent_response

class CollectInputStrategy(ActionStrategy):
    def __init__(self, step_config: Dict[str, Any], engine_context: Any):
        super().__init__(step_config, engine_context)
        self.field = step_config.get('field')
        self.agent_config = step_config.get('agent', {})
        self.max_attempts = step_config.get('retry_limit') or engine_context.get_config_value("max_retry_limit", DEFAULT_MAX_ATTEMPTS)
        self.on_max_attempts_reached = step_config.get('on_max_attempts_reached')
        self.transitions = self._get_transitions()
        self.next_step = self.step_config.get("next", None)
        self.is_structured_output = self.agent_config.get("structured_output", {}).get("enabled", False)

        rollback_strategy_name = engine_context.get_config_value("rollback_strategy", "history_based")
        self.rollback_strategy = _create_rollback_strategy(rollback_strategy_name)
        logger.info(f"Using rollback strategy: {self.rollback_strategy.get_strategy_name()}")

        self.validator = None
        if validator_function_path := self.step_config.get("validator"):
            self.validator = self.engine_context.function_repository.load(validator_function_path)

        if not self.field:
            raise RuntimeError(f"Step '{self.step_id}' missing required 'field' property")

        if not self.agent_config:
            raise RuntimeError(f"Step '{self.step_id}' missing required 'agent' configuration")

    @property
    def _conversation_key(self) -> str:
        return f'{self.field}_conversation'

    def pre_execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state['_active_input_field'] = self.step_config.get('field')
        # Inject MFA config for MFA validator nodes
        if self.step_id in self.engine_context.mfa_validator_steps:
            state['_mfa_config'] = self.engine_context.mfa_config

    @property
    def _formatted_field_name(self) -> str:
        return self.field.replace('_', ' ').title()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        with trace_node_execution(
            node_id=self.step_id,
            node_type="collect_input_with_agent",
            output_field=self.field
        ) as span:
            state = initialize_state(state)

            self._apply_context_value(state, span)

            is_self_loop = self._is_self_loop(state)

            if not is_self_loop:
                if self.rollback_strategy.should_save_snapshot():
                    self._save_snapshot_before_execution(state)

            conversation = self._get_or_create_conversation(state)

            if self._is_field_pre_populated(state):
                span.add_event("field.pre_populated", {"value": str(state.get(self.field))})
                state = self._handle_pre_populated_field(state, conversation)
                add_node_result(span, self.field, state.get(self.field), state.get(WorkflowKeys.STATUS))
                return self._add_node_to_execution_order(state)

            if self._max_attempts_reached(state):
                span.add_event("max_attempts.reached")
                return self._handle_max_attempts(state)

            agent = self._create_agent(state)

            # Check if there's a pending user message from rollback (intent change correction)
            pending_message = state.get('_pending_user_message')
            if pending_message:
                # Clear it from state so subsequent nodes don't see it
                # (must explicitly set to None, not pop, for LangGraph to update graph state)
                state['_pending_user_message'] = None

            if pending_message:
                # User already provided input during rollback, process it directly
                span.add_event("pending_message.processing", {"message_length": len(pending_message)})
                logger.info(f"Processing pending user message from rollback: {pending_message[:50]}...")
                user_input = pending_message
            else:
                # Normal flow - prompt user for input
                prompt = self._generate_prompt(agent, conversation, state)
                user_input = interrupt(prompt)

            conversation.append({"role": "user", "content": user_input})
            span.add_event("user.input_received", {"input_length": len(user_input)})

            with trace_agent_invocation(
                agent_name=self.agent_config.get('name', self.field),
                model=self.agent_config.get('model', 'default')
            ):
                agent_response = _get_agent_response(agent, conversation)

            if self.is_structured_output:
                state = self._handle_structured_output_transition(state, conversation, agent_response)
                add_node_result(span, self.field, state.get(self.field), state.get(WorkflowKeys.STATUS))
                return self._add_node_to_execution_order(state)

            # Skip intent change detection if we're processing a pending message
            # (the message was already identified as relevant to this step via rollback)
            if agent_response.startswith(TransitionPattern.INTENT_CHANGE) and not pending_message:
                span.add_event("intent.change_detected")
                return self._handle_intent_change(agent_response, state)

            state = self._process_transitions(state, conversation, agent_response)

            self._update_conversation(state, conversation)
            
            add_node_result(span, self.field, state.get(self.field), state.get(WorkflowKeys.STATUS))

        return self._add_node_to_execution_order(state)

    def _render_template_string(self, template_str: str, state: Dict[str, Any]) -> str:
        if not template_str:
            return ""
        template_loader = self.engine_context.get_config_value('template_loader', Environment())
        return template_loader.from_string(template_str).render(state)

    def _apply_context_value(self, state: Dict[str, Any], span) -> None:
        context_value = self.engine_context.get_context_value(self.field)
        if context_value is None:
            return
        logger.info(f"Using context value for '{self.field}': {context_value}")
        state[self.field] = context_value
        span.add_event("context.value_used", {"field": self.field, "value": str(context_value)})

    def _add_node_to_execution_order(self, state):
        if 'collecting' in state.get('_status'):
            return state

        self._register_node_execution(state)
        self._register_collector_node(state)

        return state

    def _is_self_loop(self, state: Dict[str, Any]) -> bool:
        return state.get(WorkflowKeys.STATUS) == f'{self.step_id}_collecting'

    def _save_snapshot_before_execution(self, state: Dict[str, Any]):
        state_history = state.get(WorkflowKeys.STATE_HISTORY, [])
        execution_index = len(state_history)
        self.rollback_strategy.save_snapshot(state, self.step_id, execution_index)

    def _register_node_execution(self, state: Dict[str, Any]):
        execution_order = state.get(WorkflowKeys.NODE_EXECUTION_ORDER, [])
        if self.step_id not in execution_order:
            execution_order.append(self.step_id)
        state[WorkflowKeys.NODE_EXECUTION_ORDER] = execution_order

    def _register_collector_node(self, state: Dict[str, Any]):
        collector_nodes = state.get(WorkflowKeys.COLLECTOR_NODES, {})
        description = self.agent_config.get('description', f"Collecting {self.field}")
        collector_nodes[self.step_id] = description
        state[WorkflowKeys.COLLECTOR_NODES] = collector_nodes

        node_field_map = state.get(WorkflowKeys.NODE_FIELD_MAP, {})
        node_field_map[self.step_id] = self.field
        state[WorkflowKeys.NODE_FIELD_MAP] = node_field_map

    def _is_field_pre_populated(self, state: Dict[str, Any]) -> bool:
        return state.get(self.field) is not None

    def _validate_collected_input(self, state) -> Tuple[bool, Optional[str]]:
        if not self.validator:
            return True, None
        return self.validator(**state)

    def _handle_pre_populated_field(self, state: Dict[str, Any], conversation: List) -> Dict[str, Any]:
        logger.info(f"Field '{self.field}' is populated, skipping collection")

        is_valid_input, validator_error_message = self._validate_collected_input(state)
        if not is_valid_input:
            self._set_status(state, "collecting")
            conversation.append({"role": "user", "content": f"{state[self.field]}"})
            return self._handle_validation_failure(state, conversation, message=validator_error_message)

        if self.transitions:
            first_transition = self.transitions[0]
            next_step = first_transition['next']
            self._set_status(state, next_step)

            if next_step in self.engine_context.outcome_map:
                self._set_outcome(state, next_step)

        if self.next_step:
            self._set_status(state, self.next_step)

            if self.next_step in self.engine_context.outcome_map:
                self._set_outcome(state, self.next_step)

        return state

    def _max_attempts_reached(self, state: Dict[str, Any]) -> bool:
        conversation = state.get(WorkflowKeys.CONVERSATIONS, {}).get(self._conversation_key, [])
        attempt_count = len([m for m in conversation if m['role'] == 'user'])
        return attempt_count >= self.max_attempts

    def _handle_max_attempts(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.warning(f"Max attempts reached for field '{self.field}'")
        self._set_status(state, 'max_attempts')
        if self.on_max_attempts_reached:
            message = self.on_max_attempts_reached
        else:
            message = MAX_ATTEMPTS_MESSAGE.format(field=self.field)
        state[WorkflowKeys.MESSAGES] = [message]
        return state

    def _get_or_create_conversation(self, state: Dict[str, Any]) -> List[Dict[str, str]]:
        conversations = state.get(WorkflowKeys.CONVERSATIONS, {})

        if self._conversation_key not in conversations:
            conversations[self._conversation_key] = []
            state[WorkflowKeys.CONVERSATIONS] = conversations

        return conversations[self._conversation_key]
    def _get_model_config(self) -> Dict[str, Any]:
        model_config = self.engine_context.get_config_value('model_config')
        if not model_config:
            raise ValueError("Model config not found in engine context")
        
        if model_id := self.agent_config.get("model"):
            model_config = model_config.copy()
            model_config["model_name"] = model_id
        
        return model_config

    def _get_instructions(self, state: Dict[str, Any], collector_nodes: Dict[str, str]) -> str:
        instructions = self.agent_config.get("instructions")

        instructions = self._render_template_string(instructions, state)

        # Internal intent change detection (within same workflow)
        if collector_nodes:
            collector_nodes_for_intent_change = {
                node_id: node_desc for node_id, node_desc in collector_nodes.items()
                if node_id not in self.engine_context.mfa_validator_steps
            }
            instructions = _wrap_instructions_with_intent_detection(instructions, collector_nodes_for_intent_change, self.is_structured_output)

        # External intent change detection (to other workflows) - always add
        task_description = self.agent_config.get('description', f"Collecting {self.field}")
        instructions = _wrap_instructions_with_unknown_intent_detection(
            instructions, task_description, self.is_structured_output
        )

        return instructions

    def _load_agent_tools(self, state: Dict[str, Any]) -> List:
        return [
            self.engine_context.tool_repository.load(tool_name, state)
            for tool_name in self.agent_config.get('tools', [])
        ]

    def _create_structured_output_model(self, collector_nodes: Dict[str, str]) -> Any:
        structured_output_config = self.agent_config.get('structured_output')
        if not structured_output_config or not structured_output_config.get('enabled'):
            return None
        
        fields = structured_output_config.get('fields', [])
        if not fields:
            return None
        
        validate_field_definitions(fields)
        model_name = f"{self.field.title().replace('_', '')}StructuredOutput"
        
        return create_structured_output_model(
            fields=fields,
            model_name=model_name,
            needs_intent_change=len(collector_nodes) > 0
        )

    def _create_agent(self, state: Dict[str, Any]) -> AgentAdapter:
        try:
            model_config = self._get_model_config()
            agent_tools = self._load_agent_tools(state)
            collector_nodes = state.get(WorkflowKeys.COLLECTOR_NODES, {})

            instructions = self._get_instructions(state, collector_nodes)
            structured_output_model = self._create_structured_output_model(collector_nodes)
            framework = self.engine_context.get_config_value('agent_framework', 'langgraph')

            return AgentFactory.create_agent(
                framework=framework,
                name=self.agent_config.get('name', f'{self.field}Collector'),
                model_config=model_config,
                tools=agent_tools,
                system_prompt=instructions,
                structured_output_model=structured_output_model
            )

        except Exception as e:
            raise RuntimeError(f"Failed to create agent for step '{self.step_id}': {e}")

    def _generate_prompt(
        self,
        agent: AgentAdapter,
        conversation: List[Dict[str, str]],
        state: Dict[str, Any]
    ) -> str:
        last_assistant_message = next((msg['content'] for msg in reversed(conversation) if msg['role'] == 'assistant'), None)

        if last_assistant_message is not None:
            return last_assistant_message

        if not (prompt := self.agent_config.get('initial_message')):
            prompt = agent.invoke([{"role": "user", "content": ""}])

        prompt = self._render_template_string(prompt, state)
        conversation.append({"role": "assistant", "content": prompt})

        return prompt

    def _update_conversation(self, state: Dict[str, Any], conversation: List[Dict[str, str]]):
        state[WorkflowKeys.CONVERSATIONS][self._conversation_key] = conversation

    def _handle_intent_change(self, target_node_or_response, state: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(target_node_or_response, str) and TransitionPattern.INTENT_CHANGE in target_node_or_response:
            target_node = target_node_or_response.split(TransitionPattern.INTENT_CHANGE)[1].strip()
        else:
            target_node = target_node_or_response

        logger.info(f"Intent change detected: {self.step_id} -> {target_node}")

        # Check if target node exists in current workflow (internal intent change)
        workflow_step_ids = [step.get('id') for step in self.engine_context.steps]

        if target_node in workflow_step_ids:
            # Internal intent change - rollback to node within same workflow
            rollback_state = self._rollback_state_to_node(state, target_node)

            if rollback_state is None:
                logger.error(f"Failed to rollback to node '{target_node}'")
                raise RuntimeError(f"Unable to process intent change to '{target_node}'")

            # Store the user message that triggered the rollback so target step can process it
            current_conversation = state.get(WorkflowKeys.CONVERSATIONS, {}).get(self._conversation_key, [])
            if current_conversation:
                last_user_message = next(
                    (msg['content'] for msg in reversed(current_conversation) if msg['role'] == 'user'),
                    None
                )
                if last_user_message:
                    rollback_state['_pending_user_message'] = last_user_message
                    logger.info(f"Stored pending user message for rollback: {last_user_message[:50]}...")

            return rollback_state
        else:
            # External intent change - interrupt to let processor handle workflow switch
            logger.info(f"External intent change detected: switching to '{target_node}'")
            interrupt({
                "type": "intent_change",
                "detected_intent": target_node,
                "from_step": self.step_id,
                "from_workflow": self.engine_context.workflow_name if hasattr(self.engine_context, 'workflow_name') else None
            })

    def _rollback_state_to_node(
        self,
        state: Dict[str, Any],
        target_node: str
    ) -> Dict[str, Any]:
        node_execution_order = state.get(WorkflowKeys.NODE_EXECUTION_ORDER, [])
        node_field_map = state.get(WorkflowKeys.NODE_FIELD_MAP, {})
        workflow_steps = self.engine_context.steps

        restored_state = self.rollback_strategy.rollback_to_node(
            state=state,
            target_node=target_node,
            node_execution_order=node_execution_order,
            node_field_map=node_field_map,
            workflow_steps=workflow_steps
        )

        for key, value in restored_state.items():
            context_value = self.engine_context.get_context_value(key)
            if context_value is not None:
                restored_state[key] = context_value

        if not restored_state:
            logger.warning(f"Rollback strategy returned empty state for node '{target_node}'")
            return {}

        restored_state[WorkflowKeys.STATUS] = f"{self.step_id}_{target_node}"

        return restored_state

    def _process_transitions(
        self,
        state: Dict[str, Any],
        conversation: List,
        agent_response: str
    ) -> Dict[str, Any]:
        matched = False
        self._set_status(state, 'collecting')

        for transition in self.transitions:
            patterns = transition['pattern']
            if isinstance(patterns, str):
                patterns = [patterns]

            matched_pattern = None
            for pattern in patterns:
                if pattern in agent_response:
                    matched_pattern = pattern
                    break

            if not matched_pattern:
                continue

            matched = True
            next_step = transition['next']

            logger.info(f"Matched transition: {transition}")

            value = agent_response.split(matched_pattern)[1].strip()
            if value:
                self._store_field_value(state, value)
                is_valid_input, validation_error_message = self._validate_collected_input(state)
                if not is_valid_input:
                    return self._handle_validation_failure(state, conversation, message=validation_error_message)
                state[WorkflowKeys.MESSAGES] = [f"✓ {self._formatted_field_name} collected: {value}" ]
            else:
                state[WorkflowKeys.MESSAGES] = []

            self._set_status(state, next_step)

            if next_step in self.engine_context.outcome_map:
                self._set_outcome(state, next_step)

            break

        if not matched:
            logger.info(f"No transition matched for response in step '{self.step_id}', continuing collection")
            state[WorkflowKeys.MESSAGES] = []

        return state

    def _handle_structured_output_transition(self, state: Dict[str, Any], conversation: List, agent_response: Any) -> Dict[str, Any]:

        try:
            agent_response = json.loads(agent_response)
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

        if target_node := agent_response.get("intent_change"):
            return self._handle_intent_change(target_node, state)

        self._set_status(state, "collecting")

        if bot_response := agent_response.get("bot_response"):
            conversation.append({"role": "assistant", "content": bot_response})
            return state

        self._store_field_value(state, agent_response)

        is_valid_input, validation_error_message = self._validate_collected_input(state)
        if not is_valid_input:
            return self._handle_validation_failure(state, conversation, message=validation_error_message)

        if next_node := self._find_matching_transition(agent_response):
            return self._complete_collection(state, next_node, agent_response)

        if self.next_step:
            return self._complete_collection(state, self.next_step, agent_response)

        return self._handle_collection_failure(state, conversation)

    def _handle_validation_failure(self, state: Dict[str, Any], conversation: List, message: Optional[str]=VALIDATION_ERROR_MESSAGE, role="assistant") -> Dict[str, Any]:
        self._store_field_value(state, None)
        self.engine_context.update_context({self.field: None})
        conversation.append({"role": role, "content": message})
        return state

    def _find_matching_transition(self, agent_response: Any) -> Optional[str]:
        for transition in self.transitions:
            next_node = transition.get("next")
            match_value = transition.get("match")
            ref_field = transition.get("ref")

            if not next_node or not ref_field or match_value is None:
                raise RuntimeError(f"Transition in step '{self.step_id}' missing required properties for structured output routing")

            field_value = agent_response.get(ref_field)
            if isinstance(match_value, list):
                if field_value in match_value:
                    return next_node
            elif field_value == match_value:
                return next_node

        return None

    def _complete_collection(self, state: Dict[str, Any], next_node: str, agent_response: Any) -> Dict[str, Any]:
        self._set_status(state, next_node)
        
        if next_node in self.engine_context.outcome_map:
            self._set_outcome(state, next_node)
        
        state[WorkflowKeys.MESSAGES] = [
            f"✓ {self._formatted_field_name} collected: {str(agent_response)}"
        ]
        
        return state

    def _handle_collection_failure(self, state: Dict[str, Any], conversation: List) -> Dict[str, Any]:
        conversation.append({"role": "assistant", "content": COLLECTION_FAILURE_MESSAGE})
        self._store_field_value(state, None)
        return state


    def _store_field_value(self, state: Dict[str, Any], value: Any):
        field_def = next((f for f in self.engine_context.data_fields if f['name'] == self.field), None)
        if not field_def:
            return

        if field_def.get('type') == 'number':
            try:
                state[self.field] = int(value)
            except (ValueError, TypeError):
                state[self.field] = value
        else:
            state[self.field] = value
