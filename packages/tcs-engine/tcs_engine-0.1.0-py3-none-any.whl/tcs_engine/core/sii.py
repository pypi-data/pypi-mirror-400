"""
Sigma Integration Index (SII) Module

Implements eigen-energy formulation:
SII = Σ log(var_i) - Σ log(lambda_i)

Where:
- var_i = marginal variances (diagonal of covariance)
- lambda_i = eigenvalues of full covariance matrix

NUMERICAL COMPUTATION ONLY - statistical coupling metric.
NOT derived from IIT. No claims about phenomenal consciousness.

License: MIT (Core Module)
"""

import numpy as np
from typing import List, Optional


class SigmaIntegrationIndex:
    """
    Sigma-Integration Index for measuring system coupling.

    Uses eigen-energy formulation for numerical stability.
    Purely statistical metric - not a consciousness indicator.
    """

    def __init__(self, num_subsystems: int = 4):
        self.num_subsystems = num_subsystems
        self.history: List[float] = []

    def _eigen_energy(self, matrix: np.ndarray) -> float:
        """
        Compute eigen-energy: Σ log(1 + λ_i)

        Numerically stable measure of matrix information content.
        """
        if matrix.ndim == 0:
            return np.log(1 + abs(float(matrix)))

        try:
            eigenvalues = np.linalg.eigvalsh(matrix)
            eigenvalues = np.maximum(eigenvalues, 0)
            energy = np.sum(np.log(1 + eigenvalues))
            return float(energy)
        except:
            return 0.0

    def compute(self, full_state: np.ndarray,
                subsystem_states: Optional[List[np.ndarray]] = None) -> float:
        """
        Compute SII using eigen-energy formulation.

        Formula: SII = Σ_i log(1 + λ_i) − Σ_k Σ_j log(1 + λ_{k,j})
        """
        if full_state.ndim == 1:
            full_state = full_state.reshape(-1, 1)

        try:
            full_cov = np.cov(full_state.T)
            if full_cov.ndim == 0:
                full_cov = np.array([[full_cov]])
            full_energy = self._eigen_energy(full_cov)
        except:
            full_energy = 0.0

        sub_energy_sum = 0.0
        if subsystem_states is not None:
            for sub_state in subsystem_states:
                if sub_state.ndim == 1:
                    sub_state = sub_state.reshape(-1, 1)
                try:
                    sub_cov = np.cov(sub_state.T)
                    if sub_cov.ndim == 0:
                        sub_cov = np.array([[sub_cov]])
                    sub_energy_sum += self._eigen_energy(sub_cov)
                except:
                    pass

        sii = max(0.0, full_energy - sub_energy_sum)
        self.history.append(sii)

        return float(sii)

    def compute_from_agents(self, agent_states: List[np.ndarray]) -> float:
        """
        Compute SII from list of agent state vectors.

        Measures cross-agent integration using correlation-based formulation:
        SII = sum_i log(var_i) - sum_i log(lambda_i)
        """
        if len(agent_states) == 0:
            return 0.0

        n_agents = len(agent_states)
        if n_agents < 2:
            return 0.0

        full_matrix = np.column_stack(agent_states)

        try:
            full_cov = np.cov(full_matrix)
            if full_cov.ndim == 0:
                self.history.append(0.0)
                return 0.0

            full_cov += np.eye(full_cov.shape[0]) * 1e-8

            variances = np.diag(full_cov)
            variances = np.maximum(variances, 1e-10)

            eigenvalues = np.linalg.eigvalsh(full_cov)
            eigenvalues = np.maximum(eigenvalues, 1e-10)

            marginal_entropy = np.sum(np.log(variances))
            joint_entropy = np.sum(np.log(eigenvalues))

            sii = max(0.0, marginal_entropy - joint_entropy)

        except:
            sii = 0.0

        self.history.append(sii)
        return float(sii)

    def get_mean(self) -> float:
        """Get mean SII over history."""
        if not self.history:
            return 0.0
        return float(np.mean(self.history))

    def get_current(self) -> float:
        """Get most recent SII value."""
        if not self.history:
            return 0.0
        return self.history[-1]
