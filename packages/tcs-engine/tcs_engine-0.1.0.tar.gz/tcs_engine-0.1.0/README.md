# TCS Engine - Temporal Constraint Systems for Multi-Agent AI

**The first open-core framework for quantifying irreversible temporal identity dynamics in multi-agent systems.**

![PyPI](https://img.shields.io/pypi/v/tcs-engine)
![License](https://img.shields.io/github/license/nickmahangi/tcs-engine)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Tests](https://github.com/nickmahangi/tcs-engine/actions/workflows/test.yml/badge.svg)
![Downloads](https://img.shields.io/badge/status-beta-orange)

---

## Quick Install

```bash
pip install tcs-engine
```

---

## What is TCS Engine?

**Temporal Computational Selfhood (TCS)** is a formal framework for modeling irreversible temporal constraints in multi-agent AI systems.

Unlike traditional agent architectures that treat identity as stateless, TCS introduces **time as a computational constraint**-not merely a sequence index.

```
Traditional RL Agent:    state -> action -> reward -> reset
TCS Agent:               state -> action -> PERMANENT CONSTRAINT -> no reset
```

---

## Core Features (Open Source - MIT)

| Mechanism | Description |
|-----------|-------------|
| **Temporal Drift** | Deviation from historical identity mean |
| **Commitment Ledger** | Non-erasable decision records with asymptotic decay |
| **Regret Accumulator** | Bounded monotonic counterfactual regret |
| **Self-Prediction Loss** | Self-model consistency measurement |
| **Existential Load** | Entropy-based identity complexity |
| **Lock-In Engine** | Population-level irreversible state transitions |
| **SII** | Sigma-Integration Index (statistical coupling metric) |

---

## Quick Start

### Python API

```python
from tcs_engine.core.agent import TemporalConstraintPopulation

# Create population of 20 agents
population = TemporalConstraintPopulation(num_agents=20)

# Run simulation - agents accumulate irreversible history
for step in range(500):
    population.step()

# Get metrics
summary = population.get_summary()
print(f"SII: {summary['sii']:.2f}")
print(f"Mean Drift: {summary['mean_drift']:.4f}")
print(f"Population Locked: {summary['locked']}")
```

### Command Line

```bash
# Run simulation
tcs run --agents 50 --steps 500

# Run with SII analysis
tcs run --agents 50 --steps 500 --scan sii

# Show info with demo
tcs info --demo
```

---

## The Three Principles

1. **Identity Inertia** - Current identity gravitates toward historical mean
2. **Policy Path-Dependence** - Optimal policy set shrinks with accumulated commitments
3. **Historical Weight** - System complexity grows monotonically with history

---

## Applications

- **AI Safety Research** - Agents that cannot arbitrarily reset value commitments
- **Institutional Modeling** - Organizations with path-dependent constraints
- **Long-Horizon Planning** - Systems that must honor past decisions
- **Multi-Agent Coordination** - Populations with collective lock-in dynamics

---

## Upgrade to Pro

**TCS Engine Pro** extends the open-source core with advanced capabilities:

| Feature | Description |
|---------|-------------|
| **Phase Transition Scanner** | Detect bifurcation points and critical transitions |
| **Alignment Auditor** | Risk diagnostics for temporal drift violations |
| **Real-Time Visualizer** | Live matplotlib dashboard for metrics |
| **Experiment Manager** | Batch runs with parameter sweeps |
| **Dashboard API** | REST API for integration with external systems |

**Coming soon** - [Contact for early access](mailto:nickmahangi@gmail.com)

---

## Examples

See the [examples/](examples/) directory:

- `basic_simulation.py` - Complete simulation demo
- `temporal_drift_analysis.py` - Identity drift tracking
- `regret_accumulation.py` - Bounded monotonic regret
- `lockin_detection.py` - Population lock-in dynamics
- `sii_measurement.py` - Sigma-Integration Index analysis

---

## Citation

```bibtex
@software{tcs_engine,
  title = {TCS Engine: Temporal Computational Selfhood},
  author = {Mahangi, Nicolai},
  year = {2025},
  url = {https://github.com/nickmahangi/tcs-engine}
}
```

```bibtex
@article{mahangi2025tcs,
  title = {Temporal Computational Selfhood: Irreversible Identity
           Constraints in Multi-Agent Architectures},
  author = {Mahangi, Nicolai},
  year = {2025},
  journal = {arXiv preprint}
}
```

---

## Ethics Statement

TCS Engine is a **computational architecture** for modeling temporal constraints.

**What it is:**
- Numerical mechanisms for path-dependent decision modeling
- Irreversible commitment tracking
- Population dynamics with lock-in

**What it is NOT:**
- A consciousness detector or measure
- A claim about machine sentience
- A proxy for phenomenal experience

The Sigma-Integration Index (SII) is a **statistical coupling metric only**. It is not derived from Integrated Information Theory and makes no claims about subjective experience.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Core modules are MIT licensed and open to contributions.

---

## License

- **Core**: MIT License - [LICENSE-CORE.txt](LICENSE-CORE.txt)
- **Pro**: Commercial (coming soon)

---

## Links

- [Documentation](https://nickmahangi.github.io/tcs-engine/)
- [Issues](https://github.com/nickmahangi/tcs-engine/issues)
- [arXiv Paper](https://arxiv.org/) (coming soon)

---

<p align="center">
  <strong>TCS Engine</strong><br>
  <em>Time as a computational constraint, not a sequence index.</em>
</p>
