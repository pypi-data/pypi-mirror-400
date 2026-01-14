from typing import List, Set, Optional, TYPE_CHECKING

import jsonschema

from .schema import WORKFLOW_SCHEMA

if TYPE_CHECKING:
    from soprano_sdk.core.constants import MFAConfig


class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def __bool__(self):
        return self.is_valid

    def __str__(self):
        if self.is_valid:
            return "Validation passed"
        return f"Validation failed with {len(self.errors)} error(s):\n" + "\n".join(f"  - {e}" for e in self.errors)


class WorkflowValidator:
    def __init__(self, config: dict, mfa_config: Optional['MFAConfig'] = None):
        self.config = config
        self.mfa_config = mfa_config
        self.errors: List[str] = []

    def validate(self) -> ValidationResult:
        self.errors = []
        self._validate_schema()
        if not self.errors:
            self._validate_step_ids()
            self._validate_outcome_ids()
            self._validate_transitions()
            self._validate_data_fields()
            self._validate_input_fields()
            self._validate_function_references()

        return ValidationResult(is_valid=len(self.errors) == 0, errors=self.errors)

    def _validate_schema(self):
        try:
            jsonschema.validate(instance=self.config, schema=WORKFLOW_SCHEMA)
        except jsonschema.ValidationError as e:
            path = " -> ".join(str(p) for p in e.path) if e.path else "root"
            self.errors.append(f"Schema validation error at '{path}': {e.message}")
        except jsonschema.SchemaError as e:
            self.errors.append(f"Invalid schema definition: {e.message}")

    def _validate_input_fields(self):
        """Validate that all input field names reference valid data fields."""
        input_fields = self.config.get('inputs', [])
        data_fields = set([field.get('name') for field in self.config.get('data', [])])

        for field_name in input_fields:
            if field_name not in data_fields:
                self.errors.append(f"Input field '{field_name}' is not defined in data fields")

    def _validate_step_ids(self):
        steps = self.config.get('steps', [])
        step_ids: Set[str] = set()

        for i, step in enumerate(steps):
            step_id = step.get('id')
            if not step_id:
                self.errors.append(f"Step at index {i} is missing 'id' field")
                continue
            self._validate_authorizer(step)
            if step_id in step_ids:
                self.errors.append(f"Duplicate step ID: '{step_id}'")
            step_ids.add(step_id)

    def _validate_outcome_ids(self):
        outcomes = self.config.get('outcomes', [])
        outcome_ids: Set[str] = set()

        for i, outcome in enumerate(outcomes):
            outcome_id = outcome.get('id')
            if not outcome_id:
                self.errors.append(f"Outcome at index {i} is missing 'id' field")
                continue

            if outcome_id in outcome_ids:
                self.errors.append(f"Duplicate outcome ID: '{outcome_id}'")
            outcome_ids.add(outcome_id)

    def _validate_transitions(self):
        steps = self.config.get('steps', [])
        outcomes = self.config.get('outcomes', [])

        step_ids = {step.get('id') for step in steps if step.get('id')}
        outcome_ids = {outcome.get('id') for outcome in outcomes if outcome.get('id')}
        valid_targets = step_ids | outcome_ids

        for step in steps:
            step_id = step.get('id', 'unknown')

            next_step = step.get('next')
            if next_step and next_step not in valid_targets:
                self.errors.append(
                    f"Step '{step_id}' references unknown target in 'next': '{next_step}'"
                )

            transitions = step.get('transitions', [])
            for i, transition in enumerate(transitions):
                next_target = transition.get('next')
                if next_target and next_target not in valid_targets:
                    self.errors.append(
                        f"Step '{step_id}' transition {i} references unknown target: '{next_target}'"
                    )

    def _validate_authorizer(self, step):
        mfa_authorizer = step.get("mfa", None)
        if mfa_authorizer is None:
            return

        if mfa_authorizer and step['action'] != 'call_function':
            self.errors.append(
                f"MFA is enabled in step({step['id']}). MFA is supported only for `call_function` nodes"
            )

        model = mfa_authorizer.get('model')
        if not model:
            self.errors.append(f"step({step['id']}) -> mfa -> model is missing")

        mfa_type = mfa_authorizer.get('type')
        if mfa_type and mfa_type != 'REST':
            self.errors.append(f"step({step['id']}) -> mfa -> type '{mfa_type}' is unsupported. Only 'REST' is supported.")

        # Validate mfa_config if provided
        if self.mfa_config is not None:
            missing_fields = []
            if not self.mfa_config.generate_token_base_url:
                missing_fields.append('generate_token_base_url')
            if not self.mfa_config.generate_token_path:
                missing_fields.append('generate_token_path')
            if not self.mfa_config.validate_token_base_url:
                missing_fields.append('validate_token_base_url')
            if not self.mfa_config.validate_token_path:
                missing_fields.append('validate_token_path')
            if not self.mfa_config.authorize_token_base_url:
                missing_fields.append('authorize_token_base_url')
            if not self.mfa_config.authorize_token_path:
                missing_fields.append('authorize_token_path')

            if missing_fields:
                self.errors.append(
                    f"MFA configuration is missing required fields: {', '.join(missing_fields)}. "
                    f"Either provide them via mfa_config parameter or set corresponding environment variables."
                )


    def _validate_data_fields(self):
        data_fields = {field.get('name') for field in self.config.get('data', [])}
        steps = self.config.get('steps', [])
        has_mfa = False

        for step in steps:
            step_id = step.get('id', 'unknown')
            action = step.get('action')

            if action == 'collect_input_with_agent':
                field = step.get('field')
                if not field:
                    self.errors.append(f"Step '{step_id}' is missing 'field' property")
                elif field not in data_fields:
                    self.errors.append(
                        f"Step '{step_id}' references unknown field: '{field}'"
                    )

                agent = step.get('agent')
                if not agent:
                    self.errors.append(f"Step '{step_id}' is missing 'agent' configuration")
                elif not agent.get('instructions'):
                    self.errors.append(f"Step '{step_id}' agent is missing 'instructions'")

            elif action == 'call_function':
                output = step.get('output')
                function = step.get('function')

                if step.get('mfa'):
                    has_mfa = True

                if not function:
                    self.errors.append(f"Step '{step_id}' is missing 'function' property")

                if not output:
                    self.errors.append(f"Step '{step_id}' is missing 'output' property")
                elif output not in data_fields:
                    self.errors.append(
                        f"Step '{step_id}' output field '{output}' not defined in data fields"
                    )

        if has_mfa and 'bearer_token' not in data_fields:
            self.errors.append(
                "`bearer_token` must be defined in `data` section: for MFA authorization"
            )

    def _validate_function_references(self):
        steps = self.config.get('steps', [])

        for step in steps:
            if step.get('action') == 'call_function':
                step_id = step.get('id', 'unknown')
                function_path = step.get('function', '')

                if not function_path:
                    continue  # Already caught by _validate_data_fields

                if '.' not in function_path:
                    self.errors.append(
                        f"Step '{step_id}' function path '{function_path}' is invalid. "
                        f"Expected format: 'module.function'"
                    )


def validate_workflow(config: dict, mfa_config: Optional['MFAConfig'] = None) -> ValidationResult:
    validator = WorkflowValidator(config, mfa_config=mfa_config)
    result = validator.validate()

    if not result.is_valid:
        raise RuntimeError(str(result))

    return result
