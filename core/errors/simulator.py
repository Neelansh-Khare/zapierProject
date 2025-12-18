"""Error simulation for rate limits, auth errors, network issues, etc."""
import random
import time
from typing import Dict, Optional, List, Any

from core.models import ErrorType


class ErrorSimulator:
    """Simulates various API errors with configurable noise levels."""
    
    def __init__(self, error_profile: Optional[Dict[str, float]] = None):
        """
        Initialize error simulator.
        
        Args:
            error_profile: Dict mapping error types to probability (0.0-1.0)
        """
        self.error_profile = error_profile or {
            ErrorType.RATE_LIMIT.value: 0.05,
            ErrorType.AUTH_EXPIRED.value: 0.02,
            ErrorType.NETWORK_UNREACHABLE.value: 0.03,
            ErrorType.SCHEMA_ERROR.value: 0.08,
            ErrorType.PARTIAL_FAILURE.value: 0.04,
            ErrorType.DATA_INCONSISTENCY.value: 0.02,
            ErrorType.INVALID_INPUT.value: 0.10,
            ErrorType.SERVER_ERROR.value: 0.02,
        }
        self.request_counts: Dict[str, List[float]] = {}  # app_name -> [timestamps]
        self.rate_limits: Dict[str, Dict[str, int]] = {}  # app_name -> {requests_per_min, burst_limit}
        self.auth_states: Dict[str, bool] = {}  # app_name -> is_authenticated
        self.network_states: Dict[str, bool] = {}  # app_name -> is_network_available
    
    def configure_rate_limit(self, app_name: str, requests_per_min: int, burst_limit: int) -> None:
        """Configure rate limits for an app."""
        self.rate_limits[app_name] = {
            "requests_per_min": requests_per_min,
            "burst_limit": burst_limit
        }
        if app_name not in self.request_counts:
            self.request_counts[app_name] = []
    
    def set_auth_state(self, app_name: str, is_authenticated: bool) -> None:
        """Set authentication state for an app."""
        self.auth_states[app_name] = is_authenticated
    
    def set_network_state(self, app_name: str, is_available: bool) -> None:
        """Set network availability for an app."""
        self.network_states[app_name] = is_available
    
    def check_rate_limit(self, app_name: str) -> bool:
        """Check if app has exceeded rate limit."""
        if app_name not in self.rate_limits:
            return False
        
        now = time.time()
        limits = self.rate_limits[app_name]
        
        # Clean old requests (older than 1 minute)
        self.request_counts[app_name] = [
            ts for ts in self.request_counts[app_name] 
            if now - ts < 60
        ]
        
        # Check if burst limit exceeded
        recent_requests = [ts for ts in self.request_counts[app_name] if now - ts < 10]
        if len(recent_requests) >= limits["burst_limit"]:
            return True
        
        # Check if requests per minute exceeded
        if len(self.request_counts[app_name]) >= limits["requests_per_min"]:
            return True
        
        return False
    
    def record_request(self, app_name: str) -> None:
        """Record a request for rate limiting."""
        if app_name not in self.request_counts:
            self.request_counts[app_name] = []
        self.request_counts[app_name].append(time.time())
    
    def simulate_error(self, app_name: str, action_name: str) -> Optional[Dict[str, Any]]:
        """
        Simulate an error based on configured profiles.
        
        Returns:
            Error dict with type, message, and details, or None if no error
        """
        # Check deterministic errors first
        if app_name in self.network_states and not self.network_states[app_name]:
            return {
                "type": ErrorType.NETWORK_UNREACHABLE.value,
                "message": "Network unreachable",
                "details": {"app": app_name, "action": action_name},
                "retry_after": None
            }
        
        if app_name in self.auth_states and not self.auth_states[app_name]:
            return {
                "type": ErrorType.AUTH_EXPIRED.value,
                "message": "Authentication expired",
                "details": {"app": app_name, "action": action_name},
                "retry_after": None
            }
        
        if self.check_rate_limit(app_name):
            retry_after = 60 - (time.time() - min(self.request_counts[app_name]))
            return {
                "type": ErrorType.RATE_LIMIT.value,
                "message": "Rate limit exceeded",
                "details": {
                    "app": app_name,
                    "action": action_name,
                    "limit": self.rate_limits[app_name]["requests_per_min"]
                },
                "retry_after": max(0, int(retry_after))
            }
        
        # Check probabilistic errors
        for error_type, probability in self.error_profile.items():
            if random.random() < probability:
                error_type_enum = ErrorType(error_type)
                return self._generate_error(error_type_enum, app_name, action_name)
        
        return None
    
    def _generate_error(self, error_type: ErrorType, app_name: str, action_name: str) -> Dict[str, Any]:
        """Generate a specific error."""
        errors = {
            ErrorType.SCHEMA_ERROR: {
                "type": error_type.value,
                "message": "Invalid input schema",
                "details": {
                    "app": app_name,
                    "action": action_name,
                    "field": "unknown",
                    "expected": "string"
                },
                "retry_after": None
            },
            ErrorType.PARTIAL_FAILURE: {
                "type": error_type.value,
                "message": "Partial failure in operation",
                "details": {
                    "app": app_name,
                    "action": action_name,
                    "succeeded_items": 3,
                    "failed_items": 2
                },
                "retry_after": None
            },
            ErrorType.DATA_INCONSISTENCY: {
                "type": error_type.value,
                "message": "Data inconsistency detected",
                "details": {
                    "app": app_name,
                    "action": action_name,
                    "conflict_id": "12345"
                },
                "retry_after": None
            },
            ErrorType.INVALID_INPUT: {
                "type": error_type.value,
                "message": "Invalid input provided",
                "details": {
                    "app": app_name,
                    "action": action_name,
                    "validation_errors": ["field 'email' is required"]
                },
                "retry_after": None
            },
            ErrorType.SERVER_ERROR: {
                "type": error_type.value,
                "message": "Internal server error",
                "details": {
                    "app": app_name,
                    "action": action_name,
                    "error_code": "500"
                },
                "retry_after": 5
            },
        }
        return errors.get(error_type, {
            "type": error_type.value,
            "message": "Unknown error",
            "details": {"app": app_name, "action": action_name},
            "retry_after": None
        })
    
    def update_error_profile(self, profile: Dict[str, float]) -> None:
        """Update the error probability profile."""
        self.error_profile.update(profile)
    
    def set_chaos_mode(self, chaos_level: float) -> None:
        """Set chaos mode - increases all error probabilities."""
        # Scale all probabilities by chaos level (0.0 to 2.0)
        base_profile = {
            ErrorType.RATE_LIMIT.value: 0.05,
            ErrorType.AUTH_EXPIRED.value: 0.02,
            ErrorType.NETWORK_UNREACHABLE.value: 0.03,
            ErrorType.SCHEMA_ERROR.value: 0.08,
            ErrorType.PARTIAL_FAILURE.value: 0.04,
            ErrorType.DATA_INCONSISTENCY.value: 0.02,
            ErrorType.INVALID_INPUT.value: 0.10,
            ErrorType.SERVER_ERROR.value: 0.02,
        }
        self.error_profile = {
            k: min(0.95, v * chaos_level) 
            for k, v in base_profile.items()
        }


# Global error simulator instance
_error_simulator = None

def get_error_simulator(error_profile: Optional[Dict[str, float]] = None) -> ErrorSimulator:
    """Get or create the global error simulator instance."""
    global _error_simulator
    if _error_simulator is None:
        _error_simulator = ErrorSimulator(error_profile)
    return _error_simulator
