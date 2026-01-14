"""
Runtime Checks for TCS Engine

Provides assertion and warning utilities for numerical safety.

License: MIT (Core Module)
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


def assert_finite(value: float, name: str = "value"):
    """
    Assert that a constraint value is finite.

    Args:
        value: The value to check
        name: Name for error message

    Raises:
        AssertionError: If value is NaN or infinite
    """
    assert np.isfinite(value), f"{name} must be finite, got {value}"


def warn_high_regret(regret: float, agent_id: int, threshold: float = 1000.0):
    """
    Log warning if regret exceeds threshold.

    Args:
        regret: Current regret value
        agent_id: Agent identifier
        threshold: Warning threshold (default 1000)
    """
    if regret > threshold:
        logger.warning(
            f"Agent {agent_id} regret exceeds {threshold}: {regret:.2f}"
        )


def validate_constraints(constraints: dict) -> bool:
    """
    Validate all constraint values are finite.

    Args:
        constraints: Dictionary of constraint values

    Returns:
        True if all valid, raises AssertionError otherwise
    """
    for name, value in constraints.items():
        if isinstance(value, (int, float)):
            assert_finite(value, name)
    return True
