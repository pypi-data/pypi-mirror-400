"""
Regret Accumulator Module

Implements bounded monotonic regret accumulation.

Formula: AccumulatedRegret(t) = max((1-epsilon)*AR(t-1), rho*AR(t-1) + Regret(t))

NUMERICAL COMPUTATION ONLY - no phenomenal experience.

License: MIT (Core Module)
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class RegretAccumulator:
    """
    Numerical counterfactual regret accumulation.

    Regret is bounded monotonic - can never substantially decrease.
    """

    def __init__(self, num_agents: int, rho: float = 0.98, epsilon: float = 0.001):
        self.num_agents = num_agents
        self.rho = rho
        self.epsilon = epsilon
        self.lambda_regret = 0.4

        self.accumulated: Dict[int, float] = {i: 0.0 for i in range(num_agents)}
        self.history: Dict[int, List[float]] = {i: [] for i in range(num_agents)}

    def update(self, agent_id: int, actual_utility: float,
               counterfactual_utilities: List[float]):
        """
        Update regret with bounded monotonic formula.

        Regret(t) = max(0, U_cf_best - U_actual)
        AR(t) = max((1-epsilon)*AR(t-1), rho*AR(t-1) + Regret(t))
        """
        if not counterfactual_utilities:
            return

        best_cf = max(counterfactual_utilities)
        instant_regret = max(0.0, best_cf - actual_utility)

        ar_prev = self.accumulated[agent_id]

        # Bounded monotonic accumulation
        option_a = (1 - self.epsilon) * ar_prev
        option_b = self.rho * ar_prev + instant_regret

        self.accumulated[agent_id] = max(option_a, option_b)
        self.history[agent_id].append(instant_regret)

        # Runtime check: warn if regret exceeds 1000
        if self.accumulated[agent_id] > 1000:
            logger.warning(
                f"Agent {agent_id} regret exceeds 1000: {self.accumulated[agent_id]:.2f}"
            )

    def get(self, agent_id: int) -> float:
        """Get accumulated regret for agent."""
        return self.accumulated[agent_id]

    def compute_constraint(self, agent_id: int) -> float:
        """Compute regret constraint signal."""
        return self.lambda_regret * self.accumulated[agent_id] * 0.1

    def get_mean_regret(self) -> float:
        """Get mean accumulated regret across population."""
        return float(np.mean(list(self.accumulated.values())))

    def get_max_regret(self) -> float:
        """Get maximum regret across population."""
        return float(max(self.accumulated.values()))

    def reset(self, agent_id: int = None):
        """Reset regret (NOTE: violates irreversibility - use for testing only)."""
        if agent_id is not None:
            self.accumulated[agent_id] = 0.0
            self.history[agent_id] = []
        else:
            for i in range(self.num_agents):
                self.accumulated[i] = 0.0
                self.history[i] = []
