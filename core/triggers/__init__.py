"""
Trigger system for simulating Zapier-like triggers.
Supports polling, webhook, and scheduled trigger types with configurable frequency.
"""

from .system import get_trigger_system

__all__ = ["get_trigger_system"]
