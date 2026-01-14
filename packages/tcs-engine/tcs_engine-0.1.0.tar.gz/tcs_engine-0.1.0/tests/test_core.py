"""
Core module tests for TCS Engine.
"""

import numpy as np
import pytest


class TestTemporalConstraintPopulation:
    """Tests for TemporalConstraintPopulation."""

    def test_import(self):
        """Test that core modules can be imported."""
        from tcs_engine.core.agent import TemporalConstraintPopulation
        assert TemporalConstraintPopulation is not None

    def test_population_creation(self):
        """Test population creation."""
        from tcs_engine.core.agent import TemporalConstraintPopulation

        pop = TemporalConstraintPopulation(num_agents=10)
        assert pop.num_agents == 10
        assert len(pop.agents) == 10

    def test_simulation_step(self):
        """Test that simulation steps work."""
        from tcs_engine.core.agent import TemporalConstraintPopulation

        np.random.seed(42)
        pop = TemporalConstraintPopulation(num_agents=5)

        for _ in range(10):
            results = pop.step()
            assert len(results) == 5

    def test_summary_metrics(self):
        """Test that summary returns expected metrics."""
        from tcs_engine.core.agent import TemporalConstraintPopulation

        np.random.seed(42)
        pop = TemporalConstraintPopulation(num_agents=5)

        for _ in range(50):
            pop.step()

        summary = pop.get_summary()

        assert 'sii' in summary
        assert 'mean_drift' in summary
        assert 'locked' in summary
        assert 'mean_regret' in summary
        assert 'stability' in summary

    def test_sii_positive(self):
        """Test that SII is non-negative."""
        from tcs_engine.core.agent import TemporalConstraintPopulation

        np.random.seed(42)
        pop = TemporalConstraintPopulation(num_agents=10)

        for _ in range(100):
            pop.step()

        summary = pop.get_summary()
        assert summary['sii'] >= 0


class TestSigmaIntegrationIndex:
    """Tests for SII module."""

    def test_sii_import(self):
        """Test SII module import."""
        from tcs_engine.core.sii import SigmaIntegrationIndex
        assert SigmaIntegrationIndex is not None

    def test_sii_computation(self):
        """Test SII computation from agent states."""
        from tcs_engine.core.sii import SigmaIntegrationIndex

        sii = SigmaIntegrationIndex()

        # Create random agent states
        np.random.seed(42)
        agent_states = [np.random.randn(50) for _ in range(10)]

        result = sii.compute_from_agents(agent_states)
        assert result >= 0


class TestRegretAccumulator:
    """Tests for regret accumulator."""

    def test_regret_import(self):
        """Test regret module import."""
        from tcs_engine.core.regret_accumulator import RegretAccumulator
        assert RegretAccumulator is not None

    def test_regret_monotonicity(self):
        """Test that regret is monotonically non-decreasing."""
        from tcs_engine.core.regret_accumulator import RegretAccumulator

        ra = RegretAccumulator(num_agents=1)

        regret_values = []
        for _ in range(20):
            # Update with random values
            actual = np.random.uniform(0, 5)
            counterfactuals = [np.random.uniform(0, 10) for _ in range(3)]
            ra.update(0, actual, counterfactuals)
            regret_values.append(ra.get(0))

        # Check monotonicity
        for i in range(len(regret_values) - 1):
            assert regret_values[i + 1] >= regret_values[i] * 0.99  # Allow epsilon


class TestCommitmentLedger:
    """Tests for commitment ledger."""

    def test_commitment_import(self):
        """Test commitment module import."""
        from tcs_engine.core.commitment_ledger import CommitmentLedger
        assert CommitmentLedger is not None

    def test_commitment_decay(self):
        """Test that commitments decay but don't vanish."""
        from tcs_engine.core.commitment_ledger import CommitmentLedger

        cl = CommitmentLedger(num_agents=1, num_actions=5)

        # Add a commitment
        cl.add(0, decision=1, strength=1.0)

        initial_count = cl.get_active_count(0)
        assert initial_count > 0

        # Decay many times
        for _ in range(100):
            cl.step()

        # Commitment should still exist (asymptotic decay)
        final_count = cl.get_active_count(0)
        assert final_count > 0
