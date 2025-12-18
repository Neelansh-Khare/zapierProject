"""
Core domain models for the MCP Universe Simulator.
"""

from typing import List, Dict, Any, Optional, Literal, Tuple
from pydantic import BaseModel, Field
from enum import Enum


class ErrorType(str, Enum):
    """Error types that can be simulated."""
    RATE_LIMIT = "rate_limit"
    AUTH_EXPIRED = "auth_expired"
    NETWORK_UNREACHABLE = "network_unreachable"
    SCHEMA_ERROR = "schema_error"
    PARTIAL_FAILURE = "partial_failure"
    DATA_INCONSISTENCY = "data_inconsistency"
    INVALID_INPUT = "invalid_input"
    SERVER_ERROR = "server_error"
    AUTH_ERROR = "auth_error"


class AppCategory(str, Enum):
    """App categories from PRD."""
    EMAIL = "email"
    STORAGE = "storage"
    PRODUCTIVITY = "productivity"
    CRM = "crm"
    FINANCE = "finance"
    DEVELOPER_TOOLS = "developer_tools"
    MESSAGING = "messaging"
    CALENDAR = "calendar"
    OPERATIONS = "operations"
    FILE_PROCESSING = "file_processing"


class SchemaComplexity(str, Enum):
    """Schema complexity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ErrorProfile(str, Enum):
    """Error profile levels."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LatencyProfile(str, Enum):
    """Latency profile levels."""
    FAST = "fast"
    NORMAL = "normal"
    SLOW = "slow"


class RateLimitProfile(BaseModel):
    """Rate limiting configuration."""
    requests_per_min: int = Field(ge=1, description="Requests allowed per minute")
    burst_limit: int = Field(ge=1, description="Burst limit for concurrent requests")


class ErrorDistribution(BaseModel):
    """Error distribution configuration for an action."""
    error_type: ErrorType
    probability: float = Field(ge=0.0, le=1.0, description="Probability of this error occurring")
    enabled: bool = True


class Action(BaseModel):
    """Represents a single action within an app."""
    name: str = Field(description="Action name (e.g., 'send_email', 'create_task')")
    inputs_schema: Dict[str, Any] = Field(description="JSON Schema for action inputs")
    outputs_schema: Dict[str, Any] = Field(description="JSON Schema for action outputs")
    side_effects: List[str] = Field(
        default_factory=list,
        description="List of state changes this action causes"
    )
    errors: List[ErrorType] = Field(
        default_factory=list,
        description="Possible error types this action can raise"
    )
    error_distributions: List[ErrorDistribution] = Field(
        default_factory=list,
        description="Error probability distributions"
    )
    latency_range_ms: Tuple[int, int] = Field(
        default=(50, 400),
        description="Latency range in milliseconds (min, max)"
    )


class AppMetadata(BaseModel):
    """App metadata."""
    name: str = Field(description="App name")
    category: AppCategory = Field(description="App category")
    description: str = Field(description="App description")


class StateDefinition(BaseModel):
    """State definition for an app."""
    initial_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Initial state structure"
    )
    state_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON Schema for app state"
    )


class App(BaseModel):
    """Complete app definition matching PRD structure."""
    metadata: AppMetadata
    actions: List[Action] = Field(default_factory=list)
    rate_limits: RateLimitProfile
    state_definition: Optional[StateDefinition] = None
    version: str = "1.0.0"

    def get_action(self, action_name: str) -> Optional[Action]:
        """Get an action by name."""
        for action in self.actions:
            if action.name == action_name:
                return action
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert app to dictionary for JSON serialization."""
        return self.model_dump(mode="json", exclude_none=True)

