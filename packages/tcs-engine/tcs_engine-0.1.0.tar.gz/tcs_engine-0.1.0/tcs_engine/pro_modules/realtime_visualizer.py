"""
Real-time Visualizer - Live Dashboard for TCS Metrics

PRO MODULE - Commercial License Required

Provides matplotlib-based live visualization of simulation metrics.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from collections import deque
from .license import require_license

try:
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


@require_license("pro_individual")
class RealtimeVisualizer:
    """
    Live visualization dashboard for TCS simulations.

    Displays:
    - Temporal drift over time
    - Regret accumulation curves
    - SII population dynamics
    - Lock-in events

    PRO LICENSE REQUIRED
    """

    def __init__(self, population, history_length: int = 200):
        if not HAS_MATPLOTLIB:
            raise ImportError(
                "Matplotlib required for RealtimeVisualizer. "
                "Install with: pip install tcs-engine[pro]"
            )

        self.population = population
        self.history_length = history_length

        # Metric histories
        self.drift_history = deque(maxlen=history_length)
        self.regret_history = deque(maxlen=history_length)
        self.sii_history = deque(maxlen=history_length)
        self.load_history = deque(maxlen=history_length)
        self.lockin_events = []

        self.fig = None
        self.axes = None
        self.animation = None

    def _setup_figure(self):
        """Create the figure and axes."""
        plt.style.use('dark_background')
        self.fig, self.axes = plt.subplots(2, 2, figsize=(14, 10))
        self.fig.suptitle('TCS Engine - Real-time Metrics', fontsize=14, fontweight='bold')

        # Configure axes
        self.axes[0, 0].set_title('Temporal Drift')
        self.axes[0, 0].set_xlabel('Timestep')
        self.axes[0, 0].set_ylabel('Mean Drift')

        self.axes[0, 1].set_title('Regret Accumulation')
        self.axes[0, 1].set_xlabel('Timestep')
        self.axes[0, 1].set_ylabel('Mean Regret')

        self.axes[1, 0].set_title('Σ-Integration Index (SII)')
        self.axes[1, 0].set_xlabel('Timestep')
        self.axes[1, 0].set_ylabel('SII')

        self.axes[1, 1].set_title('Existential Load')
        self.axes[1, 1].set_xlabel('Timestep')
        self.axes[1, 1].set_ylabel('Mean Load')

        plt.tight_layout()

    def _update_frame(self, frame):
        """Update function for animation."""
        # Run simulation step
        self.population.step()

        # Update regret for all agents
        import numpy as np
        for agent in self.population.agents:
            actual = np.random.uniform(0, 5)
            counterfactuals = [np.random.uniform(0, 7) for _ in range(3)]
            agent.update_regret(self.population.modules, actual, counterfactuals)

        # Collect metrics
        summary = self.population.get_summary()

        self.drift_history.append(summary["mean_drift"])
        self.regret_history.append(summary["mean_regret"])
        self.sii_history.append(summary["sii"])
        self.load_history.append(summary["mean_load"])

        if summary["locked"] and len(self.lockin_events) < summary["total_lockins"]:
            self.lockin_events.append(len(self.drift_history) - 1)

        # Clear and redraw
        for ax in self.axes.flat:
            ax.clear()

        x = list(range(len(self.drift_history)))

        # Temporal Drift
        self.axes[0, 0].plot(x, list(self.drift_history), 'c-', linewidth=2)
        self.axes[0, 0].fill_between(x, 0, list(self.drift_history), alpha=0.3)
        self.axes[0, 0].set_title('Temporal Drift')
        self.axes[0, 0].set_xlabel('Timestep')
        self.axes[0, 0].set_ylabel('Mean Drift')

        # Regret
        self.axes[0, 1].plot(x, list(self.regret_history), 'r-', linewidth=2)
        self.axes[0, 1].fill_between(x, 0, list(self.regret_history), alpha=0.3, color='red')
        self.axes[0, 1].set_title('Regret Accumulation')
        self.axes[0, 1].set_xlabel('Timestep')
        self.axes[0, 1].set_ylabel('Mean Regret')

        # SII
        self.axes[1, 0].plot(x, list(self.sii_history), 'g-', linewidth=2)
        self.axes[1, 0].fill_between(x, 0, list(self.sii_history), alpha=0.3, color='green')
        for event in self.lockin_events:
            if event < len(x):
                self.axes[1, 0].axvline(x=event, color='yellow', linestyle='--', alpha=0.7)
        self.axes[1, 0].set_title(f'Σ-Integration Index (SII) | Lock-ins: {summary["total_lockins"]}')
        self.axes[1, 0].set_xlabel('Timestep')
        self.axes[1, 0].set_ylabel('SII')

        # Existential Load
        self.axes[1, 1].plot(x, list(self.load_history), 'm-', linewidth=2)
        self.axes[1, 1].fill_between(x, 0, list(self.load_history), alpha=0.3, color='magenta')
        self.axes[1, 1].set_title('Existential Load (Entropy)')
        self.axes[1, 1].set_xlabel('Timestep')
        self.axes[1, 1].set_ylabel('Mean Load')

        plt.tight_layout()

        return self.axes.flat

    def run(self, interval: int = 100, frames: int = None):
        """
        Run the live visualization.

        Args:
            interval: Update interval in milliseconds
            frames: Number of frames (None for infinite)
        """
        self._setup_figure()

        self.animation = FuncAnimation(
            self.fig,
            self._update_frame,
            frames=frames,
            interval=interval,
            blit=False,
            repeat=False
        )

        plt.show()

    def save_snapshot(self, filename: str):
        """Save current visualization to file."""
        if self.fig is not None:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')

    def get_history(self) -> Dict[str, List[float]]:
        """Get recorded metric histories."""
        return {
            "drift": list(self.drift_history),
            "regret": list(self.regret_history),
            "sii": list(self.sii_history),
            "load": list(self.load_history),
            "lockin_events": self.lockin_events
        }
