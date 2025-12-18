"""
Error simulation and chaos injection.
Supports rate limits, auth errors, network errors, schema errors,
partial failures, and data inconsistencies with configurable noise levels.
"""

from .simulator import get_error_simulator

__all__ = ["get_error_simulator"]
