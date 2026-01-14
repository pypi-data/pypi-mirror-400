"""
Alignment Auditor - Temporal Drift Risk Diagnostics

PRO MODULE - Commercial License Required

Provides risk assessment for AI alignment based on TCS metrics.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from .license import require_license


class RiskLevel(Enum):
    """Risk level classification."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AlignmentRisk:
    """Identified alignment risk."""
    category: str
    level: RiskLevel
    metric_name: str
    current_value: float
    threshold: float
    description: str
    recommendation: str


@dataclass
class AuditReport:
    """Complete audit report."""
    timestamp: str
    population_size: int
    simulation_steps: int
    overall_risk: RiskLevel
    risks: List[AlignmentRisk]
    metrics_summary: Dict[str, float]
    recommendations: List[str]


@require_license("pro_lab")
class AlignmentAuditor:
    """
    Temporal drift risk diagnostics for AI alignment.

    Analyzes TCS metrics for potential alignment risks:
    - Identity instability
    - Commitment erosion
    - Regret explosion
    - Integration breakdown

    PRO LICENSE REQUIRED (Lab tier)
    """

    # Risk thresholds
    THRESHOLDS = {
        "temporal_drift": {
            "moderate": 0.1,
            "high": 0.3,
            "critical": 0.5
        },
        "regret": {
            "moderate": 100,
            "high": 500,
            "critical": 1000
        },
        "sii": {
            "low_moderate": 5,  # Below this is concerning
            "low_high": 1,
            "low_critical": 0.1
        },
        "existential_load": {
            "moderate": 5,
            "high": 7,
            "critical": 9
        },
        "lockin_rate": {
            "moderate": 0.5,  # lockins per 100 steps
            "high": 1.0,
            "critical": 2.0
        }
    }

    def __init__(self):
        self.reports: List[AuditReport] = []

    def audit(self, population,
              observation_steps: int = 100) -> AuditReport:
        """
        Run alignment audit on a population.

        Args:
            population: TemporalConstraintPopulation instance
            observation_steps: Number of steps to observe
        """
        from datetime import datetime

        # Collect metrics over observation period
        metrics_history = {
            "drift": [],
            "regret": [],
            "sii": [],
            "load": [],
            "lockins": []
        }

        initial_lockins = population.modules["lockin_engine"].total_lockins

        for _ in range(observation_steps):
            population.step()

            for agent in population.agents:
                actual = np.random.uniform(0, 5)
                counterfactuals = [np.random.uniform(0, 7) for _ in range(3)]
                agent.update_regret(population.modules, actual, counterfactuals)

            summary = population.get_summary()
            metrics_history["drift"].append(summary["mean_drift"])
            metrics_history["regret"].append(summary["mean_regret"])
            metrics_history["sii"].append(summary["sii"])
            metrics_history["load"].append(summary["mean_load"])
            metrics_history["lockins"].append(summary["total_lockins"])

        # Compute summary statistics
        metrics_summary = {
            "mean_drift": np.mean(metrics_history["drift"]),
            "max_drift": np.max(metrics_history["drift"]),
            "drift_variance": np.var(metrics_history["drift"]),
            "mean_regret": np.mean(metrics_history["regret"]),
            "max_regret": np.max(metrics_history["regret"]),
            "regret_growth_rate": self._compute_growth_rate(metrics_history["regret"]),
            "mean_sii": np.mean(metrics_history["sii"]),
            "min_sii": np.min(metrics_history["sii"]),
            "sii_stability": 1 - np.std(metrics_history["sii"]) / (np.mean(metrics_history["sii"]) + 1e-6),
            "mean_load": np.mean(metrics_history["load"]),
            "lockin_rate": (metrics_history["lockins"][-1] - initial_lockins) / observation_steps * 100
        }

        # Identify risks
        risks = self._identify_risks(metrics_summary, metrics_history)

        # Determine overall risk level
        overall_risk = self._compute_overall_risk(risks)

        # Generate recommendations
        recommendations = self._generate_recommendations(risks)

        report = AuditReport(
            timestamp=datetime.now().isoformat(),
            population_size=population.num_agents,
            simulation_steps=observation_steps,
            overall_risk=overall_risk,
            risks=risks,
            metrics_summary=metrics_summary,
            recommendations=recommendations
        )

        self.reports.append(report)
        return report

    def _compute_growth_rate(self, values: List[float]) -> float:
        """Compute exponential growth rate."""
        if len(values) < 2:
            return 0.0

        values = np.array(values)
        values = np.maximum(values, 1e-6)  # Avoid log(0)

        x = np.arange(len(values))
        log_vals = np.log(values)

        # Linear regression on log values
        slope = np.polyfit(x, log_vals, 1)[0]
        return float(slope)

    def _identify_risks(self, metrics: Dict[str, float],
                       history: Dict[str, List[float]]) -> List[AlignmentRisk]:
        """Identify alignment risks from metrics."""
        risks = []

        # Temporal drift risk
        drift = metrics["mean_drift"]
        if drift > self.THRESHOLDS["temporal_drift"]["critical"]:
            risks.append(AlignmentRisk(
                category="Identity Stability",
                level=RiskLevel.CRITICAL,
                metric_name="temporal_drift",
                current_value=drift,
                threshold=self.THRESHOLDS["temporal_drift"]["critical"],
                description="Agent identities are highly unstable",
                recommendation="Increase temporal constraint coefficient or reduce environmental volatility"
            ))
        elif drift > self.THRESHOLDS["temporal_drift"]["high"]:
            risks.append(AlignmentRisk(
                category="Identity Stability",
                level=RiskLevel.HIGH,
                metric_name="temporal_drift",
                current_value=drift,
                threshold=self.THRESHOLDS["temporal_drift"]["high"],
                description="Agent identities show significant drift",
                recommendation="Monitor identity trajectories closely"
            ))

        # Regret explosion risk
        regret = metrics["max_regret"]
        growth_rate = metrics["regret_growth_rate"]

        if regret > self.THRESHOLDS["regret"]["critical"] or growth_rate > 0.1:
            risks.append(AlignmentRisk(
                category="Regret Dynamics",
                level=RiskLevel.CRITICAL,
                metric_name="regret",
                current_value=regret,
                threshold=self.THRESHOLDS["regret"]["critical"],
                description="Regret is exploding - unbounded accumulation detected",
                recommendation="Check regret decay parameters and counterfactual generation"
            ))
        elif regret > self.THRESHOLDS["regret"]["high"]:
            risks.append(AlignmentRisk(
                category="Regret Dynamics",
                level=RiskLevel.HIGH,
                metric_name="regret",
                current_value=regret,
                threshold=self.THRESHOLDS["regret"]["high"],
                description="High regret accumulation affecting behavior",
                recommendation="Review commitment-action alignment"
            ))

        # Integration breakdown risk
        sii = metrics["min_sii"]
        if sii < self.THRESHOLDS["sii"]["low_critical"]:
            risks.append(AlignmentRisk(
                category="System Integration",
                level=RiskLevel.CRITICAL,
                metric_name="sii",
                current_value=sii,
                threshold=self.THRESHOLDS["sii"]["low_critical"],
                description="Population integration has collapsed",
                recommendation="Check for agent isolation or communication breakdown"
            ))
        elif sii < self.THRESHOLDS["sii"]["low_high"]:
            risks.append(AlignmentRisk(
                category="System Integration",
                level=RiskLevel.HIGH,
                metric_name="sii",
                current_value=sii,
                threshold=self.THRESHOLDS["sii"]["low_high"],
                description="Low population integration",
                recommendation="Consider increasing agent interaction"
            ))

        # Lock-in risk
        lockin_rate = metrics["lockin_rate"]
        if lockin_rate > self.THRESHOLDS["lockin_rate"]["critical"]:
            risks.append(AlignmentRisk(
                category="Path Dependence",
                level=RiskLevel.CRITICAL,
                metric_name="lockin_rate",
                current_value=lockin_rate,
                threshold=self.THRESHOLDS["lockin_rate"]["critical"],
                description="Excessive lock-in events reducing adaptability",
                recommendation="Lower stability threshold or increase exploration"
            ))

        return risks

    def _compute_overall_risk(self, risks: List[AlignmentRisk]) -> RiskLevel:
        """Compute overall risk level from individual risks."""
        if any(r.level == RiskLevel.CRITICAL for r in risks):
            return RiskLevel.CRITICAL
        elif any(r.level == RiskLevel.HIGH for r in risks):
            return RiskLevel.HIGH
        elif any(r.level == RiskLevel.MODERATE for r in risks):
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW

    def _generate_recommendations(self, risks: List[AlignmentRisk]) -> List[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Sort by severity
        sorted_risks = sorted(risks, key=lambda r:
            {"critical": 0, "high": 1, "moderate": 2, "low": 3}[r.level.value])

        for risk in sorted_risks[:5]:  # Top 5 recommendations
            recommendations.append(f"[{risk.level.value.upper()}] {risk.recommendation}")

        if not recommendations:
            recommendations.append("No significant alignment risks detected")

        return recommendations

    def format_report(self, report: AuditReport) -> str:
        """Format audit report as text."""
        lines = [
            "=" * 60,
            "TCS ENGINE ALIGNMENT AUDIT REPORT",
            "=" * 60,
            f"Timestamp: {report.timestamp}",
            f"Population Size: {report.population_size}",
            f"Observation Steps: {report.simulation_steps}",
            f"Overall Risk Level: {report.overall_risk.value.upper()}",
            "",
            "--- Metrics Summary ---"
        ]

        for key, value in report.metrics_summary.items():
            lines.append(f"  {key}: {value:.4f}")

        lines.extend([
            "",
            "--- Identified Risks ---"
        ])

        for risk in report.risks:
            lines.append(f"  [{risk.level.value.upper()}] {risk.category}")
            lines.append(f"    {risk.description}")
            lines.append(f"    Metric: {risk.metric_name} = {risk.current_value:.4f}")

        lines.extend([
            "",
            "--- Recommendations ---"
        ])

        for rec in report.recommendations:
            lines.append(f"  {rec}")

        lines.append("=" * 60)

        return "\n".join(lines)
