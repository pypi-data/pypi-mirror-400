"""
Existential Load Module

Implements: ExistentialLoad_i = H(SelfModel_i) + H(Narrative_i)

NUMERICAL COMPUTATION ONLY - entropy-based complexity metric.
No phenomenal experience or existential angst.

License: MIT (Core Module)
"""

import numpy as np
from typing import Dict, List


class ExistentialLoad:
    """
    Computational complexity from self-referential structures.

    Measures entropy of self-model and narrative vectors.
    """

    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.lambda_exist = 0.3

        self.loads: Dict[int, float] = {i: 0.0 for i in range(num_agents)}
        self.history: Dict[int, List[float]] = {i: [] for i in range(num_agents)}

    def _entropy(self, vector: np.ndarray) -> float:
        """Compute Shannon entropy of vector as probability distribution."""
        vec = np.abs(vector) + 1e-10
        probs = vec / np.sum(vec)
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        return float(entropy)

    def compute(self, agent_id: int, self_model: np.ndarray,
                narrative: np.ndarray) -> float:
        """
        Compute existential load (entropy-based complexity metric).

        ExistentialLoad = H(SelfModel) + H(Narrative)
        """
        sm_entropy = self._entropy(self_model)
        narr_entropy = self._entropy(narrative)

        load = sm_entropy + narr_entropy
        self.loads[agent_id] = load
        self.history[agent_id].append(load)

        return load

    def compute_constraint(self, agent_id: int, self_model: np.ndarray,
                          narrative: np.ndarray) -> float:
        """Compute existential load constraint signal."""
        return self.lambda_exist * self.compute(agent_id, self_model, narrative)

    def get_mean_load(self) -> float:
        """Get mean existential load across population."""
        return float(np.mean(list(self.loads.values())))

    def get_max_load(self) -> float:
        """Get maximum existential load."""
        return float(max(self.loads.values())) if self.loads else 0.0
