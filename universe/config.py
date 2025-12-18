"""Universe configuration management."""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from core.models import AppCategory, RateLimitProfile


class ErrorProfile(BaseModel):
    """Error simulation profile."""
    rate_limit: float = 0.05
    auth_expired: float = 0.02
    network_unreachable: float = 0.03
    schema_error: float = 0.08
    partial_failure: float = 0.04
    data_inconsistency: float = 0.02
    invalid_input: float = 0.10
    server_error: float = 0.02


class LatencyProfile(BaseModel):
    """Latency profile configuration."""
    min_ms: int = 50
    max_ms: int = 400
    mean_ms: int = 200


class UniverseConfig(BaseModel):
    """Universe configuration."""
    num_apps: int = Field(default=200, ge=1, le=2000)
    categories_enabled: List[AppCategory] = Field(default_factory=lambda: [
        AppCategory.EMAIL,
        AppCategory.STORAGE,
        AppCategory.PRODUCTIVITY,
        AppCategory.CRM,
        AppCategory.FINANCE,
        AppCategory.DEVELOPER_TOOLS,
        AppCategory.MESSAGING,
        AppCategory.CALENDAR,
        AppCategory.OPERATIONS,
        AppCategory.FILE_PROCESSING,
    ])
    rate_limit_profiles: Dict[str, RateLimitProfile] = Field(default_factory=dict)
    error_profile: ErrorProfile = Field(default_factory=ErrorProfile)
    latency_profile: LatencyProfile = Field(default_factory=LatencyProfile)
    data_density: float = Field(default=1.0, ge=0.1, le=10.0)  # Multiplier for data generation
    schema_complexity: str = Field(default="medium", pattern="^(low|medium|high)$")
    chaos_level: float = Field(default=1.0, ge=0.0, le=2.0)  # 0.0 = no chaos, 2.0 = max chaos
    
    def to_error_profile_dict(self) -> Dict[str, float]:
        """Convert error profile to dict format for ErrorSimulator."""
        return {
            "rate_limit": self.error_profile.rate_limit,
            "auth_expired": self.error_profile.auth_expired,
            "network_unreachable": self.error_profile.network_unreachable,
            "schema_error": self.error_profile.schema_error,
            "partial_failure": self.error_profile.partial_failure,
            "data_inconsistency": self.error_profile.data_inconsistency,
            "invalid_input": self.error_profile.invalid_input,
            "server_error": self.error_profile.server_error,
        }
    
    @classmethod
    def default(cls) -> "UniverseConfig":
        """Create default universe configuration."""
        return cls()


def load_config(config_dict: Optional[Dict[str, Any]] = None) -> UniverseConfig:
    """Load universe configuration from dict or return defaults."""
    if config_dict:
        return UniverseConfig(**config_dict)
    return UniverseConfig.default()

