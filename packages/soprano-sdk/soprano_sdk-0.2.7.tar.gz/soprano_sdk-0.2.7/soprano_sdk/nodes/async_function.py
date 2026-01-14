"""
Async Function Strategy - Handles asynchronous function calls with interrupt/resume pattern.

This strategy allows workflows to pause while waiting for an external async operation
to complete. The async function initiates an operation and returns a "pending" status.
The workflow then interrupts, and resumes when the external system calls back with the result.

Example YAML:
    - id: verify_identity
      action: call_async_function
      function: "services.identity.start_verification"
      output: verification_result
      transitions:
        - condition: "verified"
          next: approved
        - condition: "failed"
          next: rejected

The async function should return:
    - {"status": "pending", ...metadata} to trigger interrupt and wait for callback
    - Any other dict for synchronous completion (no interrupt)

On resume, the async result is passed via Command(resume=async_result) and stored
in the output field, then transitions are evaluated.
"""
from typing import Dict, Any

from langgraph.types import interrupt

from .base import ActionStrategy
from ..core.state import set_state_value, get_state_value
from ..core.constants import WorkflowKeys
from ..utils.logger import logger
from ..utils.template import get_nested_value


class AsyncFunctionStrategy(ActionStrategy):
    """Strategy for executing async functions with interrupt/resume pattern."""

    # Key for storing pending metadata in state
    PENDING_KEY_PREFIX = '_async_pending_'

    def __init__(self, step_config: Dict[str, Any], engine_context: Any):
        super().__init__(step_config, engine_context)
        self.function_path = step_config.get('function')
        self.output_field = step_config.get('output')
        self.transitions = self._get_transitions()
        self.next_step = self._get_next_step()

        if not self.function_path:
            raise RuntimeError(f"Step '{self.step_id}' missing required 'function' property")

        if not self.output_field:
            raise RuntimeError(f"Step '{self.step_id}' missing required 'output' property")

    @property
    def _pending_key(self) -> str:
        """State key for storing pending operation metadata."""
        return f"{self.PENDING_KEY_PREFIX}{self.step_id}"

    def _is_async_pending(self, state: Dict[str, Any]) -> bool:
        """Check if this node is waiting for async operation to complete."""
        return state.get(WorkflowKeys.STATUS) == f'{self.step_id}_pending'

    def pre_execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Pre-execution hook."""
        pass

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        from ..utils.tracing import trace_node_execution

        with trace_node_execution(
            node_id=self.step_id,
            node_type="call_async_function",
            function=self.function_path,
            output_field=self.output_field
        ) as span:
            # Check if we're resuming from a pending async operation
            if self._is_async_pending(state):
                span.add_event("async.resuming")
                pending_metadata = state.get(self._pending_key, {})
            else:
                # First invocation - call the async function
                result = self._call_function(state, span)

                if self._is_pending_result(result):
                    # Async operation started - store metadata and prepare to interrupt
                    span.add_event("async.pending", {"metadata": str(result)})
                    self._set_status(state, "pending")
                    state[self._pending_key] = result
                    pending_metadata = result
                else:
                    # Synchronous completion - no interrupt needed
                    span.add_event("async.sync_complete", {"result": str(result)})
                    return self._handle_sync_completion(state, result, span)

            # Interrupt with pending metadata
            # On resume, interrupt() returns the async result from Command(resume=...)
            async_result = interrupt({
                "type": "async",
                "step_id": self.step_id,
                "pending": pending_metadata
            })

            # Clean up pending state
            if self._pending_key in state:
                del state[self._pending_key]

            span.add_event("async.resumed", {"result": str(async_result)})

            # Store result and handle routing
            return self._handle_async_completion(state, async_result, span)

    def _call_function(self, state: Dict[str, Any], span) -> Any:
        """Load and execute the async function."""
        try:
            logger.info(f"Loading async function: {self.function_path}")
            func = self.engine_context.function_repository.load(self.function_path)
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.type", "LoadError")
            span.set_attribute("error.message", str(e))
            raise RuntimeError(
                f"Failed to load function '{self.function_path}' in step '{self.step_id}': {e}"
            )

        try:
            logger.info(f"Calling async function: {self.function_path}")
            result = func(state)
            logger.info(f"Async function {self.function_path} returned: {result}")
            return result
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            raise RuntimeError(
                f"Function '{self.function_path}' failed in step '{self.step_id}': {e}"
            )

    def _is_pending_result(self, result: Any) -> bool:
        """Check if the function result indicates a pending async operation."""
        if not isinstance(result, dict):
            return False
        return result.get("status") == "pending"

    def _handle_sync_completion(
        self,
        state: Dict[str, Any],
        result: Any,
        span
    ) -> Dict[str, Any]:
        """Handle synchronous function completion (no async wait needed)."""
        set_state_value(state, self.output_field, result)
        self._track_computed_field(state)
        return self._handle_routing(state, result, span)

    def _handle_async_completion(
        self,
        state: Dict[str, Any],
        async_result: Any,
        span
    ) -> Dict[str, Any]:
        """Handle async operation completion after resume."""
        set_state_value(state, self.output_field, async_result)
        self._track_computed_field(state)
        return self._handle_routing(state, async_result, span)

    def _track_computed_field(self, state: Dict[str, Any]):
        """Track this field as computed for rollback purposes."""
        computed_fields = get_state_value(state, WorkflowKeys.COMPUTED_FIELDS, [])
        if self.output_field not in computed_fields:
            computed_fields.append(self.output_field)
        set_state_value(state, WorkflowKeys.COMPUTED_FIELDS, computed_fields)

    def _handle_routing(
        self,
        state: Dict[str, Any],
        result: Any,
        span
    ) -> Dict[str, Any]:
        """Determine next step based on transitions or default routing."""
        if self.transitions:
            return self._handle_transition_routing(state, result, span)
        return self._handle_simple_routing(state, span)

    def _handle_transition_routing(
        self,
        state: Dict[str, Any],
        result: Any,
        span
    ) -> Dict[str, Any]:
        """Route based on transition conditions matching the result."""
        for transition in self.transitions:
            check_value = result

            # Support nested field references
            if 'ref' in transition:
                check_value = get_nested_value(result, transition['ref'])

            condition = transition['condition']

            # Support list of conditions
            if isinstance(condition, list):
                if check_value not in condition:
                    continue
            elif check_value != condition:
                continue

            next_dest = transition['next']
            logger.info(f"Async function matched transition, routing to {next_dest}")
            span.add_event("transition.matched", {"next": next_dest})
            self._set_status(state, next_dest)

            if next_dest in self.engine_context.outcome_map:
                self._set_outcome(state, next_dest)

            return state

        logger.warning(
            f"No matching transition for async result '{result}' in step '{self.step_id}'"
        )
        span.add_event("transition.no_match", {"result": str(result)})
        self._set_status(state, 'failed')
        return state

    def _handle_simple_routing(self, state: Dict[str, Any], span) -> Dict[str, Any]:
        """Route to next step when no transitions are defined."""
        self._set_status(state, 'success')

        if self.next_step:
            self._set_status(state, self.next_step)
            span.add_event("routing.next_step", {"next": self.next_step})

            if self.next_step in self.engine_context.outcome_map:
                self._set_outcome(state, self.next_step)

        return state
