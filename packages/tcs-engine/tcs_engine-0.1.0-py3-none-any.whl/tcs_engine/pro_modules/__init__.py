"""
TCS Engine PRO Modules (Commercial License Required)

These modules require a valid PRO license.
See LICENSE-PRO.txt for licensing terms.

Available PRO Features:
- Dashboard API (REST endpoints for metrics)
- Real-time Visualizer (Live matplotlib/websocket dashboard)
- Experiment Manager (Batch experiment runner)
- Phase Transition Scanner (Lambda sweep & bifurcation detection)
- Alignment Auditor (Temporal drift risk diagnostics)
"""

from .license import verify_license, LicenseError, get_license_info

__all__ = [
    "verify_license",
    "LicenseError",
    "get_license_info",
]

# Lazy imports for PRO modules (only load if license is valid)
def __getattr__(name):
    pro_modules = {
        "DashboardAPI": "dashboard_api",
        "RealtimeVisualizer": "realtime_visualizer",
        "ExperimentManager": "experiment_manager",
        "PhaseTransitionScanner": "phase_transition_scan",
        "AlignmentAuditor": "alignment_audit",
    }

    if name in pro_modules:
        if not verify_license():
            raise LicenseError(
                f"PRO license required for {name}. "
                "Visit https://tcs-engine.dev/pricing to purchase."
            )

        module = __import__(
            f"tcs_engine.pro_modules.{pro_modules[name]}",
            fromlist=[name]
        )
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
