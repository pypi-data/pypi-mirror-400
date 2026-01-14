"""
Phase Transition Scanner - Lambda Sweep & Bifurcation Detection

PRO MODULE - Commercial License Required

Detects phase transitions and bifurcation points in TCS dynamics.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from .license import require_license


@dataclass
class PhaseTransition:
    """Detected phase transition."""
    parameter: str
    critical_value: float
    order_parameter_before: float
    order_parameter_after: float
    transition_type: str  # "first_order", "second_order", "crossover"
    confidence: float


@require_license("pro_lab")
class PhaseTransitionScanner:
    """
    Detect phase transitions in TCS dynamics.

    Scans parameter space to find:
    - Critical points where SII undergoes transitions
    - Bifurcation points in regret dynamics
    - Lock-in onset thresholds

    PRO LICENSE REQUIRED (Lab tier)
    """

    def __init__(self, num_agents: int = 20, num_steps: int = 200):
        self.num_agents = num_agents
        self.num_steps = num_steps
        self.scan_results: Dict[str, Any] = {}
        self.transitions: List[PhaseTransition] = []

    def scan_parameter(self, param_name: str,
                       min_val: float, max_val: float,
                       num_points: int = 20,
                       order_parameter: str = "sii") -> Dict[str, Any]:
        """
        Scan a single parameter for phase transitions.

        Args:
            param_name: Parameter to scan (e.g., "lambda_temporal")
            min_val: Minimum value
            max_val: Maximum value
            num_points: Number of scan points
            order_parameter: Which metric to use as order parameter
        """
        from tcs_engine.core.agent import TemporalConstraintPopulation

        values = np.linspace(min_val, max_val, num_points)
        order_params = []
        susceptibilities = []

        for val in values:
            # Run multiple seeds
            op_samples = []

            for seed in range(3):
                np.random.seed(seed * 42)

                population = TemporalConstraintPopulation(
                    num_agents=self.num_agents
                )

                # Set parameter
                self._set_parameter(population, param_name, val)

                # Run simulation
                op_history = []
                for _ in range(self.num_steps):
                    population.step()

                    for agent in population.agents:
                        actual = np.random.uniform(0, 5)
                        counterfactuals = [np.random.uniform(0, 7) for _ in range(3)]
                        agent.update_regret(population.modules, actual, counterfactuals)

                    summary = population.get_summary()
                    op_history.append(summary.get(order_parameter, 0))

                # Use last 20% as equilibrium
                equilibrium = np.mean(op_history[-int(len(op_history)*0.2):])
                op_samples.append(equilibrium)

            order_params.append(np.mean(op_samples))
            susceptibilities.append(np.std(op_samples))

        # Detect transitions
        transitions = self._detect_transitions(
            param_name, values, order_params, susceptibilities
        )

        result = {
            "parameter": param_name,
            "values": values.tolist(),
            "order_parameter": order_params,
            "susceptibility": susceptibilities,
            "transitions": transitions
        }

        self.scan_results[param_name] = result
        self.transitions.extend(transitions)

        return result

    def _set_parameter(self, population, param_name: str, value: float):
        """Set a parameter on the population modules."""
        param_map = {
            "lambda_temporal": ("temporal_drift", "lambda_temporal"),
            "lambda_commit": ("commitment_ledger", "lambda_commit"),
            "lambda_regret": ("regret_accumulator", "lambda_regret"),
            "lambda_self": ("self_prediction", "lambda_self"),
            "lambda_exist": ("existential_load", "lambda_exist"),
            "lambda_lockin": ("lockin_engine", "lambda_lockin"),
            "tau": ("lockin_engine", "tau"),
            "rho": ("regret_accumulator", "rho"),
        }

        if param_name in param_map:
            module_name, attr_name = param_map[param_name]
            setattr(population.modules[module_name], attr_name, value)

    def _detect_transitions(self, param_name: str,
                           values: np.ndarray,
                           order_params: List[float],
                           susceptibilities: List[float]) -> List[PhaseTransition]:
        """Detect phase transitions from scan data."""
        transitions = []

        op = np.array(order_params)
        sus = np.array(susceptibilities)

        # Compute derivatives
        dop = np.gradient(op, values)
        d2op = np.gradient(dop, values)

        # Find peaks in susceptibility (fluctuations)
        sus_threshold = np.mean(sus) + 2 * np.std(sus)

        for i in range(1, len(values) - 1):
            # Check for susceptibility peak
            if sus[i] > sus_threshold and sus[i] > sus[i-1] and sus[i] > sus[i+1]:
                # Determine transition type
                if abs(d2op[i]) > np.std(d2op) * 2:
                    trans_type = "second_order"
                elif abs(dop[i]) > np.std(dop) * 3:
                    trans_type = "first_order"
                else:
                    trans_type = "crossover"

                confidence = min(1.0, sus[i] / sus_threshold)

                transition = PhaseTransition(
                    parameter=param_name,
                    critical_value=float(values[i]),
                    order_parameter_before=float(op[max(0, i-3):i].mean()),
                    order_parameter_after=float(op[i:min(len(op), i+3)].mean()),
                    transition_type=trans_type,
                    confidence=float(confidence)
                )
                transitions.append(transition)

        return transitions

    def scan_2d(self, param1: Tuple[str, float, float],
                param2: Tuple[str, float, float],
                resolution: int = 10) -> np.ndarray:
        """
        2D phase diagram scan.

        Args:
            param1: (name, min, max) for first parameter
            param2: (name, min, max) for second parameter
            resolution: Grid resolution
        """
        from tcs_engine.core.agent import TemporalConstraintPopulation

        name1, min1, max1 = param1
        name2, min2, max2 = param2

        vals1 = np.linspace(min1, max1, resolution)
        vals2 = np.linspace(min2, max2, resolution)

        phase_diagram = np.zeros((resolution, resolution))

        for i, v1 in enumerate(vals1):
            for j, v2 in enumerate(vals2):
                np.random.seed(42)

                population = TemporalConstraintPopulation(num_agents=self.num_agents)
                self._set_parameter(population, name1, v1)
                self._set_parameter(population, name2, v2)

                # Run to equilibrium
                for _ in range(self.num_steps // 2):
                    population.step()
                    for agent in population.agents:
                        agent.update_regret(
                            population.modules,
                            np.random.uniform(0, 5),
                            [np.random.uniform(0, 7) for _ in range(3)]
                        )

                phase_diagram[i, j] = population.get_summary()["sii"]

        return phase_diagram

    def get_critical_points(self) -> List[Dict[str, Any]]:
        """Get all detected critical points."""
        return [
            {
                "parameter": t.parameter,
                "critical_value": t.critical_value,
                "transition_type": t.transition_type,
                "confidence": t.confidence
            }
            for t in self.transitions
        ]
