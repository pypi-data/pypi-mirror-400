"""
Temporal Constraint Agent

Main agent class integrating all temporal constraint modules.

NUMERICAL COMPUTATIONS ONLY - no consciousness or phenomenal experience.

License: MIT (Core Module)
"""

import numpy as np
from typing import Dict, List, Any, Optional
import logging

from .temporal_drift import TemporalDrift
from .commitment_ledger import CommitmentLedger
from .regret_accumulator import RegretAccumulator
from .self_prediction_loss import SelfPredictionLoss
from .existential_load import ExistentialLoad
from .lockin_engine import LockInEngine
from .sii import SigmaIntegrationIndex

logger = logging.getLogger(__name__)


def _assert_finite(value: float, name: str = "value"):
    """Assert constraint value is finite."""
    assert np.isfinite(value), f"{name} must be finite, got {value}"


class TemporalConstraintAgent:
    """
    Agent with temporal constraint mechanisms.

    Integrates all six TCS mechanisms plus SII measurement.
    All mechanisms are NUMERICAL COMPUTATIONS ONLY.
    """

    def __init__(self, agent_id: int, identity_dim: int = 10,
                 narrative_dim: int = 15, num_actions: int = 5):
        self.agent_id = agent_id
        self.identity_dim = identity_dim
        self.narrative_dim = narrative_dim
        self.num_actions = num_actions
        self.timestep = 0

        self.identity = np.random.randn(identity_dim) * 0.1
        self.narrative = np.random.randn(narrative_dim) * 0.1
        self.self_model = np.random.randn(identity_dim) * 0.1

        self.last_action: Optional[int] = None

    def step(self, modules: Dict[str, Any], observation: np.ndarray = None
             ) -> Dict[str, Any]:
        """Execute one agent step with all temporal constraints."""
        self.timestep += 1

        drift_noise = np.random.randn(self.identity_dim) * 0.05
        self.identity = 0.95 * self.identity + 0.05 * drift_noise

        self.narrative = 0.9 * self.narrative + 0.1 * np.random.randn(self.narrative_dim) * 0.1
        self.self_model = 0.9 * self.self_model + 0.1 * self.identity[:self.identity_dim]

        action = self._select_action(modules.get("commitment_ledger"))
        constraints = self._compute_constraints(modules, action)

        for name, value in constraints.items():
            if isinstance(value, (int, float)):
                _assert_finite(value, name)

        self.last_action = action

        return {
            "agent_id": self.agent_id,
            "action": action,
            "identity": self.identity.copy(),
            "constraints": constraints,
            "timestep": self.timestep
        }

    def _select_action(self, commitment_ledger: Optional[CommitmentLedger]) -> int:
        """Select action considering commitments."""
        if np.random.rand() < 0.1:
            return np.random.randint(0, self.num_actions)

        if commitment_ledger is not None:
            active = commitment_ledger.get_active_count(self.agent_id)
            if active > 0:
                for c in commitment_ledger.ledger[self.agent_id]:
                    if c.strength > 0.5:
                        return c.decision

        return np.random.randint(0, self.num_actions)

    def _compute_constraints(self, modules: Dict[str, Any], action: int) -> Dict[str, float]:
        """Compute all constraint signals."""
        constraints = {}

        if "temporal_drift" in modules:
            td = modules["temporal_drift"]
            td.update(self.agent_id, self.identity)
            constraints["temporal_drift"] = td.compute(self.agent_id)
            constraints["temporal_constraint"] = td.compute_constraint(self.agent_id)

        if "commitment_ledger" in modules:
            cl = modules["commitment_ledger"]
            constraints["commitment_violation"] = cl.compute_violation(self.agent_id, action)
            constraints["commitment_constraint"] = cl.compute_constraint(self.agent_id, action)

        if "regret_accumulator" in modules:
            ra = modules["regret_accumulator"]
            constraints["regret"] = ra.get(self.agent_id)
            constraints["regret_constraint"] = ra.compute_constraint(self.agent_id)

        if "self_prediction" in modules:
            sp = modules["self_prediction"]
            constraints["self_prediction_error"] = sp.compute(self.agent_id, self.identity)
            constraints["self_prediction_constraint"] = sp.compute_constraint(
                self.agent_id, self.identity)
            sp.predict(self.agent_id, self.identity)

        if "existential_load" in modules:
            el = modules["existential_load"]
            constraints["existential_load"] = el.compute(
                self.agent_id, self.self_model, self.narrative)
            constraints["existential_constraint"] = el.compute_constraint(
                self.agent_id, self.self_model, self.narrative)

        total = sum(v for k, v in constraints.items() if "constraint" in k)
        constraints["total_constraint"] = total

        return constraints

    def update_regret(self, modules: Dict[str, Any], actual_utility: float,
                      counterfactual_utilities: List[float]):
        """Update regret accumulator with outcome."""
        if "regret_accumulator" in modules:
            modules["regret_accumulator"].update(
                self.agent_id, actual_utility, counterfactual_utilities)

    def make_commitment(self, modules: Dict[str, Any], decision: int,
                        strength: float = 1.0):
        """Add commitment to ledger."""
        if "commitment_ledger" in modules:
            modules["commitment_ledger"].add(self.agent_id, decision, strength)

    def get_state(self) -> Dict[str, Any]:
        """Get agent state snapshot."""
        return {
            "agent_id": self.agent_id,
            "timestep": self.timestep,
            "identity": self.identity.copy(),
            "narrative": self.narrative.copy(),
            "self_model": self.self_model.copy(),
            "last_action": self.last_action
        }


class TemporalConstraintPopulation:
    """
    Population of temporal constraint agents with shared modules.
    """

    def __init__(self, num_agents: int = 10, identity_dim: int = 10,
                 narrative_dim: int = 15, num_actions: int = 5):
        self.num_agents = num_agents
        self.timestep = 0

        self.agents = [
            TemporalConstraintAgent(i, identity_dim, narrative_dim, num_actions)
            for i in range(num_agents)
        ]

        self.modules = {
            "temporal_drift": TemporalDrift(num_agents, identity_dim),
            "commitment_ledger": CommitmentLedger(num_agents, num_actions),
            "regret_accumulator": RegretAccumulator(num_agents),
            "self_prediction": SelfPredictionLoss(num_agents, identity_dim),
            "existential_load": ExistentialLoad(num_agents),
            "lockin_engine": LockInEngine(),
            "sii": SigmaIntegrationIndex()
        }

    def step(self) -> List[Dict[str, Any]]:
        """Execute one population step."""
        self.timestep += 1

        results = []
        for agent in self.agents:
            result = agent.step(self.modules)
            results.append(result)

        self.modules["commitment_ledger"].step()
        self.modules["self_prediction"].step()

        macro_state = self._compute_macro_state()
        self.modules["lockin_engine"].update(macro_state, self.timestep)

        agent_states = [a.identity for a in self.agents]
        self.modules["sii"].compute_from_agents(agent_states)

        return results

    def _compute_macro_state(self) -> np.ndarray:
        """Compute population macro-state."""
        identities = np.vstack([a.identity for a in self.agents])
        narratives = np.vstack([a.narrative for a in self.agents])

        macro = np.concatenate([
            np.mean(identities, axis=0),
            np.std(identities, axis=0),
            np.mean(narratives, axis=0)
        ])

        return macro

    def get_summary(self) -> Dict[str, Any]:
        """Get population summary statistics."""
        return {
            "timestep": self.timestep,
            "num_agents": self.num_agents,
            "mean_drift": self.modules["temporal_drift"].get_mean_drift(),
            "mean_regret": self.modules["regret_accumulator"].get_mean_regret(),
            "max_regret": self.modules["regret_accumulator"].get_max_regret(),
            "mean_load": self.modules["existential_load"].get_mean_load(),
            "total_commitments": self.modules["commitment_ledger"].get_total_commitments(),
            "total_lockins": self.modules["lockin_engine"].total_lockins,
            "locked": self.modules["lockin_engine"].is_locked(),
            "stability": self.modules["lockin_engine"].get_mean_stability(),
            "sii": self.modules["sii"].get_current(),
            "mean_sii": self.modules["sii"].get_mean()
        }

    def get_metrics(self) -> Dict[str, float]:
        """Get all numerical metrics for dashboard/API."""
        summary = self.get_summary()
        return {k: v for k, v in summary.items() if isinstance(v, (int, float))}
