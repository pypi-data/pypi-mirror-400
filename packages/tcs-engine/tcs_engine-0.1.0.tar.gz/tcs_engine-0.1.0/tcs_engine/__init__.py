"""
TCS Engine - Temporal Computational Selfhood

The first irreversible temporal identity engine for multi-agent AI systems.

Core Features (MIT Licensed):
- Temporal Drift measurement
- Irreversible Commitment tracking
- Bounded monotonic Regret accumulation
- Self-Prediction Loss
- Existential Load (entropy-based complexity)
- History Lock-In
- Sigma-Integration Index (SII)

Pro Features (Commercial License):
- REST API Dashboard
- Real-time Visualization
- Experiment Manager
- Phase Transition Scanner
- Alignment Auditor

All mechanisms are NUMERICAL COMPUTATIONS ONLY.
No consciousness, sentience, or phenomenal experience is created or implied.
"""

__version__ = "0.1.0"
__author__ = "Nicolai Mahangi"
__license__ = "MIT (Core) / Proprietary (Pro)"

from tcs_engine.core.agent import TemporalConstraintAgent, TemporalConstraintPopulation
from tcs_engine.core.temporal_drift import TemporalDrift
from tcs_engine.core.commitment_ledger import CommitmentLedger
from tcs_engine.core.regret_accumulator import RegretAccumulator
from tcs_engine.core.self_prediction_loss import SelfPredictionLoss
from tcs_engine.core.existential_load import ExistentialLoad
from tcs_engine.core.lockin_engine import LockInEngine
from tcs_engine.core.sii import SigmaIntegrationIndex

__all__ = [
    "__version__",
    "TemporalConstraintAgent",
    "TemporalConstraintPopulation",
    "TemporalDrift",
    "CommitmentLedger",
    "RegretAccumulator",
    "SelfPredictionLoss",
    "ExistentialLoad",
    "LockInEngine",
    "SigmaIntegrationIndex",
]
