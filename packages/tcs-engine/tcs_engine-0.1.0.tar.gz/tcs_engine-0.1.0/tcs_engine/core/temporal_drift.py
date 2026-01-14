"""
Temporal Drift Module

Implements: TemporalDrift_i(t) = || ID_i(t) - (1/W) * sum(ID_i(t-k)) ||

NUMERICAL COMPUTATION ONLY - no phenomenal experience.

License: MIT (Core Module)
"""

import numpy as np
from typing import Dict, List
from collections import deque


class TemporalDrift:
    """
    Temporal identity drift measurement.

    Agents incur numerical penalty for deviating from historical identity mean.
    """

    def __init__(self, num_agents: int, identity_dim: int = 10, window: int = 20):
        self.num_agents = num_agents
        self.identity_dim = identity_dim
        self.window = window
        self.lambda_temporal = 0.5

        self.trajectories: Dict[int, deque] = {
            i: deque(maxlen=window) for i in range(num_agents)
        }
        for i in range(num_agents):
            self.trajectories[i].append(np.zeros(identity_dim))

    def update(self, agent_id: int, identity: np.ndarray):
        """Record identity snapshot."""
        if len(identity) != self.identity_dim:
            identity = np.resize(identity, self.identity_dim)
        if np.any(np.isnan(identity)) or np.any(np.isinf(identity)):
            identity = np.zeros(self.identity_dim)
        self.trajectories[agent_id].append(identity.copy())

    def compute(self, agent_id: int) -> float:
        """
        Compute temporal drift.

        Formula: || ID(t) - (1/W) * sum_{k=1}^{W} ID(t-k) ||
        """
        traj = list(self.trajectories[agent_id])
        if len(traj) < 2:
            return 0.0

        current = traj[-1]
        historical_mean = np.mean(traj[:-1], axis=0)
        drift = float(np.linalg.norm(current - historical_mean))
        return drift

    def compute_constraint(self, agent_id: int) -> float:
        """Compute temporal constraint signal."""
        return self.lambda_temporal * self.compute(agent_id)

    def get_mean_drift(self) -> float:
        """Get mean drift across population."""
        drifts = [self.compute(i) for i in range(self.num_agents)]
        return float(np.mean(drifts))

    def reset(self):
        """Reset all trajectories."""
        for i in range(self.num_agents):
            self.trajectories[i].clear()
            self.trajectories[i].append(np.zeros(self.identity_dim))
