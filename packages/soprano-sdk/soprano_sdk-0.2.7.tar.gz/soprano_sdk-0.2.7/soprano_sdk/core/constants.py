from enum import Enum
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkflowKeys:
    STEP_ID = '_step_id'
    STATUS = '_status'
    OUTCOME_ID = '_outcome_id'
    MESSAGES = '_messages'
    CONVERSATIONS = '_conversations'
    STATE_HISTORY = '_state_history'
    COLLECTOR_NODES = '_collector_nodes'
    ATTEMPT_COUNTS = '_attempt_counts'
    NODE_EXECUTION_ORDER = '_node_execution_order'
    NODE_FIELD_MAP = '_node_field_map'
    COMPUTED_FIELDS = '_computed_fields'
    ERROR = 'error'


class ActionType(Enum):
    COLLECT_INPUT_WITH_AGENT = 'collect_input_with_agent'
    CALL_FUNCTION = 'call_function'
    CALL_ASYNC_FUNCTION = 'call_async_function'


class InterruptType:
    """Interrupt type markers for workflow pauses"""
    USER_INPUT = '__WORKFLOW_INTERRUPT__'
    ASYNC = '__ASYNC_INTERRUPT__'


class DataType(Enum):
    TEXT = 'text'
    NUMBER = 'number'
    DOUBLE = 'double'
    BOOLEAN = 'boolean'
    LIST = 'list'
    DICT = 'dict'
    ANY = "any"


class OutcomeType(Enum):
    SUCCESS = 'success'
    FAILURE = 'failure'


class StatusPattern:
    COLLECTING = '{step_id}_collecting'
    MAX_ATTEMPTS = '{step_id}_max_attempts'
    NEXT_STEP = '{step_id}_{next_step}'
    SUCCESS = '{step_id}_success'
    FAILED = '{step_id}_failed'
    INTENT_CHANGE = '{step_id}_{target_node}'


class TransitionPattern:
    CAPTURED = '{field}_CAPTURED:'
    FAILED = '{field}_FAILED:'
    INTENT_CHANGE = 'INTENT_CHANGE:'


DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_MODEL = 'gpt-4o-mini'
DEFAULT_TIMEOUT = 300

MAX_ATTEMPTS_MESSAGE = "I'm having trouble understanding your {field}. Please contact customer service for assistance."
WORKFLOW_COMPLETE_MESSAGE = "Workflow completed."


class MFAConfig(BaseSettings):
    """
    Configuration for MFA REST API endpoints.

    Values can be provided during initialization or will be automatically
    loaded from environment variables with the same name (uppercase).

    Example:
        # Load from environment variables
        config = MFAConfig()

        # Or provide specific values
        config = MFAConfig(
            generate_token_base_url="https://api.example.com",
            generate_token_path="/v1/mfa/generate"
        )
    """
    generate_token_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for the generate token endpoint"
    )
    generate_token_path: Optional[str] = Field(
        default=None,
        description="Path for the generate token endpoint"
    )
    validate_token_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for the validate token endpoint"
    )
    validate_token_path: Optional[str] = Field(
        default=None,
        description="Path for the validate token endpoint"
    )
    authorize_token_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for the authorize token endpoint"
    )
    authorize_token_path: Optional[str] = Field(
        default=None,
        description="Path for the authorize token endpoint"
    )
    api_timeout: int = Field(
        default=30,
        description="API request timeout in seconds"
    )
    mfa_cancelled_message: str = Field(
        default="Authentication has been cancelled.",
        description="Message to display when user cancels MFA authentication"
    )

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra='ignore'
    )
