"""
Self-Prediction Loss Module

Implements: L_self = || ID_actual(t+Delta) - ID_predicted(t+Delta) ||

NUMERICAL COMPUTATION ONLY - no phenomenal experience.

License: MIT (Core Module)
"""

import numpy as np
from typing import Dict, List, Optional


class SelfPredictionLoss:
    """
    Self-predictive consistency measurement.

    Agents predict future identity and incur numerical cost on mismatch.
    """

    def __init__(self, num_agents: int, identity_dim: int = 10, horizon: int = 5):
        self.num_agents = num_agents
        self.identity_dim = identity_dim
        self.horizon = horizon
        self.lambda_self = 0.5
        self.timestep = 0

        self.predictions: Dict[int, np.ndarray] = {
            i: np.zeros(identity_dim) for i in range(num_agents)
        }
        self.prediction_times: Dict[int, int] = {i: 0 for i in range(num_agents)}
        self.errors: Dict[int, List[float]] = {i: [] for i in range(num_agents)}

    def predict(self, agent_id: int, current_identity: np.ndarray,
                velocity: Optional[np.ndarray] = None):
        """
        Make prediction about future identity.

        ID_predicted = ID_current + Delta * velocity
        """
        if len(current_identity) != self.identity_dim:
            current_identity = np.resize(current_identity, self.identity_dim)

        if velocity is None:
            velocity = np.zeros(self.identity_dim)
        elif len(velocity) != self.identity_dim:
            velocity = np.resize(velocity, self.identity_dim)

        prediction = current_identity + self.horizon * velocity

        if np.any(np.isnan(prediction)) or np.any(np.isinf(prediction)):
            prediction = current_identity.copy()

        self.predictions[agent_id] = prediction
        self.prediction_times[agent_id] = self.timestep

    def compute(self, agent_id: int, actual_identity: np.ndarray) -> float:
        """
        Compute self-prediction error.

        L_self = || ID_actual - ID_predicted ||
        """
        elapsed = self.timestep - self.prediction_times[agent_id]
        if elapsed < self.horizon:
            return 0.0

        if len(actual_identity) != self.identity_dim:
            actual_identity = np.resize(actual_identity, self.identity_dim)

        error = float(np.linalg.norm(actual_identity - self.predictions[agent_id]))
        self.errors[agent_id].append(error)
        return error

    def compute_constraint(self, agent_id: int, actual_identity: np.ndarray) -> float:
        """Compute self-prediction constraint signal."""
        return self.lambda_self * self.compute(agent_id, actual_identity)

    def step(self):
        """Advance timestep."""
        self.timestep += 1

    def get_mean_error(self) -> float:
        """Get mean prediction error across population."""
        errors = [self.errors[i][-1] if self.errors[i] else 0.0
                  for i in range(self.num_agents)]
        return float(np.mean(errors))
