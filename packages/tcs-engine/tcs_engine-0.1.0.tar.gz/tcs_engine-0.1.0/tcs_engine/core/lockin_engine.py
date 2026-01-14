"""
Lock-In Engine Module

Implements population history lock-in.

L(t) = 1 if Stability(t) > tau for T steps, else 0
Stability(t) = 1 - ||MC(t) - MC(t-1)|| / max_change

NUMERICAL COMPUTATION ONLY - no phenomenal experience.

License: MIT (Core Module)
"""

import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class LockedState:
    """Locked macro-state record."""
    state_vector: np.ndarray
    timestamp: int
    strength: float


class LockInEngine:
    """
    Population history lock-in system.

    Stable states become irreversibly locked, creating path dependence.
    """

    def __init__(self, state_dim: int = 50, tau: float = 0.8, T: int = 10):
        self.state_dim = state_dim
        self.tau = tau
        self.T = T
        self.lambda_lockin = 0.35

        self.stability_history: List[float] = []
        self.consecutive_stable: int = 0
        self.locked_states: List[LockedState] = []
        self.previous_state: Optional[np.ndarray] = None
        self.total_lockins: int = 0
        self.inertia: float = 0.0

    def compute_stability(self, macro_state: np.ndarray) -> float:
        """
        Compute stability metric.

        Stability = 1 - ||MC(t) - MC(t-1)|| / max_change
        """
        if self.previous_state is None:
            self.previous_state = macro_state.copy()
            return 1.0

        change = np.linalg.norm(macro_state - self.previous_state)
        max_change = np.sqrt(self.state_dim) * 2
        stability = 1.0 - min(change / max_change, 1.0)

        self.previous_state = macro_state.copy()
        self.stability_history.append(stability)

        return float(stability)

    def update(self, macro_state: np.ndarray, timestep: int) -> Dict[str, Any]:
        """
        Update lock-in system.

        Triggers lock if Stability > tau for T consecutive steps.
        """
        stability = self.compute_stability(macro_state)

        if stability > self.tau:
            self.consecutive_stable += 1
        else:
            self.consecutive_stable = 0

        locked = False
        if self.consecutive_stable >= self.T:
            self._create_lock(macro_state, timestep)
            locked = True
            self.consecutive_stable = 0

        self.inertia = self._compute_inertia()

        return {
            "stability": stability,
            "locked": locked,
            "total_lockins": self.total_lockins,
            "inertia": self.inertia
        }

    def _create_lock(self, state: np.ndarray, timestep: int):
        """Create locked state record."""
        lock = LockedState(
            state_vector=state.copy(),
            timestamp=timestep,
            strength=min(1.0, self.consecutive_stable / self.T)
        )
        self.locked_states.append(lock)
        self.total_lockins += 1

    def _compute_inertia(self) -> float:
        """Compute collective inertia from locked states."""
        if not self.locked_states:
            return 0.0

        total = 0.0
        current_time = len(self.stability_history)
        for lock in self.locked_states:
            age = current_time - lock.timestamp
            weight = np.exp(-0.01 * age)
            total += lock.strength * weight

        return float(total)

    def compute_deviation_cost(self, proposed_state: np.ndarray) -> float:
        """Compute cost of deviating from locked states."""
        if not self.locked_states:
            return 0.0

        total = 0.0
        for lock in self.locked_states:
            dist = np.linalg.norm(proposed_state - lock.state_vector)
            total += lock.strength * dist

        return float(total)

    def compute_constraint(self, current_state: np.ndarray,
                          target_state: np.ndarray) -> float:
        """Compute lock-in constraint signal."""
        cost = self.compute_deviation_cost(target_state)
        return self.lambda_lockin * cost * (1 + self.inertia)

    def is_locked(self) -> bool:
        """Check if any state is currently locked."""
        return len(self.locked_states) > 0

    def get_mean_stability(self) -> float:
        """Get mean stability over history."""
        if not self.stability_history:
            return 0.0
        return float(np.mean(self.stability_history))
