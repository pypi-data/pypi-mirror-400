"""
Experiment Manager - Batch Experiment Runner

PRO MODULE - Commercial License Required

Provides systematic experiment execution with parameter sweeps.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np

from .license import require_license


@dataclass
class ExperimentConfig:
    """Configuration for a single experiment."""
    name: str
    num_agents: int = 10
    num_steps: int = 500
    identity_dim: int = 10
    num_actions: int = 5
    random_seed: Optional[int] = None

    # Lambda coefficients
    lambda_temporal: float = 0.5
    lambda_commit: float = 0.6
    lambda_regret: float = 0.4
    lambda_self: float = 0.5
    lambda_exist: float = 0.3
    lambda_lockin: float = 0.35


@dataclass
class ExperimentResult:
    """Results from a single experiment run."""
    config: ExperimentConfig
    final_metrics: Dict[str, float]
    metric_history: Dict[str, List[float]]
    runtime_seconds: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "config": asdict(self.config),
            "final_metrics": self.final_metrics,
            "metric_history": self.metric_history,
            "runtime_seconds": self.runtime_seconds,
            "timestamp": self.timestamp
        }


@require_license("pro_individual")
class ExperimentManager:
    """
    Batch experiment runner for TCS Engine.

    Features:
    - Parameter sweeps
    - Multi-seed averaging
    - Result persistence
    - Progress tracking

    PRO LICENSE REQUIRED
    """

    def __init__(self, output_dir: str = "./experiments"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[ExperimentResult] = []

    def run_experiment(self, config: ExperimentConfig,
                      progress_callback: Optional[Callable] = None) -> ExperimentResult:
        """Run a single experiment."""
        from tcs_engine.core.agent import TemporalConstraintPopulation

        if config.random_seed is not None:
            np.random.seed(config.random_seed)

        start_time = time.time()

        # Create population
        population = TemporalConstraintPopulation(
            num_agents=config.num_agents,
            identity_dim=config.identity_dim,
            num_actions=config.num_actions
        )

        # Apply lambda coefficients
        population.modules["temporal_drift"].lambda_temporal = config.lambda_temporal
        population.modules["commitment_ledger"].lambda_commit = config.lambda_commit
        population.modules["regret_accumulator"].lambda_regret = config.lambda_regret
        population.modules["self_prediction"].lambda_self = config.lambda_self
        population.modules["existential_load"].lambda_exist = config.lambda_exist
        population.modules["lockin_engine"].lambda_lockin = config.lambda_lockin

        # Metric history
        history = {
            "drift": [],
            "regret": [],
            "sii": [],
            "load": [],
            "lockins": []
        }

        # Run simulation
        for step in range(config.num_steps):
            population.step()

            # Update regret
            for agent in population.agents:
                actual = np.random.uniform(0, 5)
                counterfactuals = [np.random.uniform(0, 7) for _ in range(3)]
                agent.update_regret(population.modules, actual, counterfactuals)

            # Random commitments
            if np.random.rand() < 0.05:
                agent_id = np.random.randint(0, config.num_agents)
                decision = np.random.randint(0, config.num_actions)
                population.agents[agent_id].make_commitment(population.modules, decision)

            # Record metrics
            summary = population.get_summary()
            history["drift"].append(summary["mean_drift"])
            history["regret"].append(summary["mean_regret"])
            history["sii"].append(summary["sii"])
            history["load"].append(summary["mean_load"])
            history["lockins"].append(summary["total_lockins"])

            if progress_callback:
                progress_callback(step + 1, config.num_steps)

        runtime = time.time() - start_time

        result = ExperimentResult(
            config=config,
            final_metrics=population.get_metrics(),
            metric_history=history,
            runtime_seconds=runtime,
            timestamp=datetime.now().isoformat()
        )

        self.results.append(result)
        return result

    def run_sweep(self, base_config: ExperimentConfig,
                  sweep_param: str, values: List[Any],
                  num_seeds: int = 3) -> List[ExperimentResult]:
        """
        Run parameter sweep experiment.

        Args:
            base_config: Base configuration
            sweep_param: Parameter name to sweep
            values: List of values to try
            num_seeds: Number of random seeds per value
        """
        results = []
        total = len(values) * num_seeds
        current = 0

        for value in values:
            for seed in range(num_seeds):
                config = ExperimentConfig(**asdict(base_config))
                setattr(config, sweep_param, value)
                config.random_seed = seed * 42
                config.name = f"{base_config.name}_{sweep_param}={value}_seed={seed}"

                current += 1
                print(f"Running experiment {current}/{total}: {config.name}")

                result = self.run_experiment(config)
                results.append(result)

        return results

    def save_results(self, filename: str = None):
        """Save all results to JSON file."""
        if filename is None:
            filename = f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.output_dir / filename

        data = {
            "experiment_count": len(self.results),
            "results": [r.to_dict() for r in self.results]
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Results saved to {filepath}")
        return filepath

    def load_results(self, filename: str):
        """Load results from JSON file."""
        filepath = self.output_dir / filename

        with open(filepath) as f:
            data = json.load(f)

        self.results = []
        for r in data["results"]:
            config = ExperimentConfig(**r["config"])
            result = ExperimentResult(
                config=config,
                final_metrics=r["final_metrics"],
                metric_history=r["metric_history"],
                runtime_seconds=r["runtime_seconds"],
                timestamp=r["timestamp"]
            )
            self.results.append(result)

        return self.results

    def summarize(self) -> Dict[str, Any]:
        """Generate summary statistics across all experiments."""
        if not self.results:
            return {}

        summary = {
            "total_experiments": len(self.results),
            "total_runtime": sum(r.runtime_seconds for r in self.results),
            "metrics": {}
        }

        # Aggregate final metrics
        for metric in ["mean_drift", "mean_regret", "sii", "mean_load", "total_lockins"]:
            values = [r.final_metrics.get(metric, 0) for r in self.results]
            summary["metrics"][metric] = {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values)
            }

        return summary
