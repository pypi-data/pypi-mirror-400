"""
Commitment Ledger Module

Implements irreversible commitments (non-erasable decision records).

Formula: s(t) = s_min + (s(t-1) - s_min) * (1 - gamma)

NUMERICAL COMPUTATION ONLY - no phenomenal experience.

License: MIT (Core Module)
"""

import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class Commitment:
    """Non-erasable decision record."""
    decision: int
    timestamp: int
    strength: float
    decay_rate: float
    agent_id: int


class CommitmentLedger:
    """
    Irreversible commitment tracking system.

    Commitments decay but are NEVER deleted.
    """

    def __init__(self, num_agents: int, num_actions: int = 5, s_min: float = 0.01):
        self.num_agents = num_agents
        self.num_actions = num_actions
        self.s_min = s_min
        self.lambda_commit = 0.6
        self.timestep = 0

        self.ledger: Dict[int, List[Commitment]] = {
            i: [] for i in range(num_agents)
        }
        self.violation_counts: Dict[int, int] = {i: 0 for i in range(num_agents)}

    def add(self, agent_id: int, decision: int, strength: float = 1.0,
            decay_rate: float = 0.05):
        """Add commitment (non-erasable)."""
        commitment = Commitment(
            decision=decision,
            timestamp=self.timestep,
            strength=strength,
            decay_rate=decay_rate,
            agent_id=agent_id
        )
        self.ledger[agent_id].append(commitment)

    def decay(self):
        """
        Apply asymptotic decay to all commitments.

        Formula: s(t) = s_min + (s(t-1) - s_min) * (1 - gamma)
        """
        for agent_id in range(self.num_agents):
            for c in self.ledger[agent_id]:
                c.strength = self.s_min + (c.strength - self.s_min) * (1 - c.decay_rate)

    def compute_violation(self, agent_id: int, action: int) -> float:
        """Compute violation cost for action."""
        total = 0.0
        for c in self.ledger[agent_id]:
            if c.strength > 0.1 and action != c.decision:
                total += c.strength
                self.violation_counts[agent_id] += 1
        return total

    def compute_constraint(self, agent_id: int, action: int) -> float:
        """Compute commitment constraint signal."""
        return self.lambda_commit * self.compute_violation(agent_id, action)

    def step(self):
        """Advance timestep and decay."""
        self.timestep += 1
        self.decay()

    def get_count(self, agent_id: int) -> int:
        """Get number of commitments for agent."""
        return len(self.ledger[agent_id])

    def get_active_count(self, agent_id: int) -> int:
        """Get number of active commitments (strength > 0.1)."""
        return sum(1 for c in self.ledger[agent_id] if c.strength > 0.1)

    def get_total_commitments(self) -> int:
        """Get total commitments across all agents."""
        return sum(len(self.ledger[i]) for i in range(self.num_agents))
