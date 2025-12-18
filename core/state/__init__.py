"""
State engine for app state simulation.
Handles persistent app state, synthetic data generation, CRUD operations,
multi-app shared objects, and event propagation.
"""

from .engine import get_state_engine

__all__ = ["get_state_engine"]
