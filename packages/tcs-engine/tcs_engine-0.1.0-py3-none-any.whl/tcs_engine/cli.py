"""
TCS Engine Command Line Interface

Usage:
    tcs run --agents 50 --steps 500 --scan temporal_drift
    tcs dashboard
    tcs audit alignment
    tcs license status
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import numpy as np

console = Console(force_terminal=True, legacy_windows=True, no_color=False)


@click.group()
@click.version_option(version="0.1.0", prog_name="TCS Engine")
def main():
    """
    TCS Engine - Temporal Computational Selfhood

    The first irreversible temporal identity engine for multi-agent AI systems.
    """
    pass


@main.command()
@click.option("--agents", "-a", default=10, help="Number of agents")
@click.option("--steps", "-s", default=100, help="Number of simulation steps")
@click.option("--scan", type=str, default=None, help="Metric to highlight (temporal_drift, regret, sii)")
@click.option("--seed", default=None, type=int, help="Random seed")
@click.option("--output", "-o", default=None, help="Output file for metrics (JSON)")
def run(agents: int, steps: int, scan: str, seed: int, output: str):
    """Run a TCS simulation."""
    from tcs_engine.core.agent import TemporalConstraintPopulation
    import json

    if seed is not None:
        np.random.seed(seed)

    console.print(Panel.fit(
        f"[bold cyan]TCS Engine Simulation[/bold cyan]\n"
        f"Agents: {agents} | Steps: {steps}",
        box=box.ROUNDED
    ))

    population = TemporalConstraintPopulation(num_agents=agents)

    metrics_history = []

    console.print("  Running simulation...")

    for step in range(steps):
        population.step()

        # Update regret
        for agent in population.agents:
            actual = np.random.uniform(0, 5)
            counterfactuals = [np.random.uniform(0, 7) for _ in range(3)]
            agent.update_regret(population.modules, actual, counterfactuals)

        # Random commitments
        if np.random.rand() < 0.05:
            agent_id = np.random.randint(0, agents)
            decision = np.random.randint(0, 5)
            population.agents[agent_id].make_commitment(population.modules, decision)

        if (step + 1) % 10 == 0:
            metrics_history.append(population.get_metrics())

        # Show progress every 25%
        if steps >= 20 and (step + 1) % (steps // 4) == 0:
            pct = int((step + 1) / steps * 100)
            console.print(f"  Progress: {pct}%")

    # Display results
    console.print()
    summary = population.get_summary()

    # Create results table
    table = Table(title="Simulation Results", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")

    # Add rows with status indicators (ASCII-compatible)
    drift = summary["mean_drift"]
    drift_status = "[OK]" if drift < 0.1 else "[WARN]" if drift < 0.3 else "[HIGH]"
    table.add_row("Mean Drift", f"{drift:.4f}", drift_status)

    regret = summary["mean_regret"]
    regret_status = "[OK]" if regret < 100 else "[WARN]" if regret < 500 else "[HIGH]"
    table.add_row("Mean Regret", f"{regret:.2f}", regret_status)

    sii = summary["sii"]
    sii_status = "[OK]" if sii > 5 else "[WARN]" if sii > 1 else "[LOW]"
    table.add_row("SII", f"{sii:.4f}", sii_status)

    table.add_row("Existential Load", f"{summary['mean_load']:.4f}", "")
    table.add_row("Total Lock-ins", str(summary["total_lockins"]), "")
    table.add_row("Locked", "Yes" if summary["locked"] else "No", "")
    table.add_row("Total Commitments", str(summary["total_commitments"]), "")

    console.print(table)

    # Highlight scanned metric
    if scan:
        console.print()
        if scan == "temporal_drift":
            console.print(Panel(
                f"[bold]Temporal Drift Analysis[/bold]\n\n"
                f"Mean: {summary['mean_drift']:.4f}\n"
                f"Stability: {'High' if drift < 0.1 else 'Medium' if drift < 0.3 else 'Low'}\n\n"
                f"Temporal drift measures deviation from historical identity mean.\n"
                f"Lower values indicate more stable agent identities.",
                title="[cyan]Temporal Drift[/cyan]",
                box=box.ROUNDED
            ))
        elif scan == "regret":
            console.print(Panel(
                f"[bold]Regret Accumulation Analysis[/bold]\n\n"
                f"Mean: {summary['mean_regret']:.2f}\n"
                f"Max: {summary['max_regret']:.2f}\n\n"
                f"Regret is bounded monotonic - cannot substantially decrease.\n"
                f"High regret indicates persistent counterfactual gaps.",
                title="[red]Regret[/red]",
                box=box.ROUNDED
            ))
        elif scan == "sii":
            console.print(Panel(
                f"[bold]Sigma-Integration Index Analysis[/bold]\n\n"
                f"Current: {summary['sii']:.4f}\n"
                f"Mean: {summary['mean_sii']:.4f}\n\n"
                f"SII measures statistical coupling between agents.\n"
                f"Higher values indicate more integrated population dynamics.",
                title="[green]SII[/green]",
                box=box.ROUNDED
            ))

    # Save output if requested
    if output:
        output_data = {
            "config": {"agents": agents, "steps": steps, "seed": seed},
            "final_summary": summary,
            "metrics_history": metrics_history
        }
        with open(output, "w") as f:
            json.dump(output_data, f, indent=2)
        console.print(f"\n[dim]Results saved to {output}[/dim]")


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, type=int, help="Port to bind to")
def dashboard(host: str, port: int):
    """Launch the TCS Dashboard API server (PRO feature)."""
    try:
        from tcs_engine.pro_modules.license import verify_license, LicenseError

        if not verify_license():
            console.print("[red]PRO license required for dashboard.[/red]")
            console.print("Visit https://tcs-engine.dev/pricing to purchase.")
            console.print("\nTo enable trial mode: export TCS_TRIAL_MODE=enabled")
            return

        from tcs_engine.pro_modules.dashboard_api import DashboardAPI
        from tcs_engine.core.agent import TemporalConstraintPopulation

        console.print(Panel.fit(
            f"[bold cyan]TCS Dashboard API[/bold cyan]\n"
            f"Starting server at http://{host}:{port}",
            box=box.ROUNDED
        ))

        population = TemporalConstraintPopulation(num_agents=10)
        api = DashboardAPI(population)
        api.run(host=host, port=port)

    except ImportError as e:
        console.print(f"[red]Missing dependency: {e}[/red]")
        console.print("Install PRO dependencies: pip install tcs-engine[pro]")


@main.command()
@click.argument("type", type=click.Choice(["alignment"]))
@click.option("--agents", "-a", default=20, help="Number of agents")
@click.option("--steps", "-s", default=100, help="Observation steps")
def audit(type: str, agents: int, steps: int):
    """Run alignment audit (PRO feature)."""
    try:
        from tcs_engine.pro_modules.license import verify_license

        if not verify_license():
            console.print("[red]PRO license required for audit.[/red]")
            console.print("Visit https://tcs-engine.dev/pricing to purchase.")
            console.print("\nTo enable trial mode: export TCS_TRIAL_MODE=enabled")
            return

        from tcs_engine.pro_modules.alignment_audit import AlignmentAuditor
        from tcs_engine.core.agent import TemporalConstraintPopulation

        console.print(Panel.fit(
            f"[bold cyan]TCS Alignment Audit[/bold cyan]\n"
            f"Running {type} audit...",
            box=box.ROUNDED
        ))

        population = TemporalConstraintPopulation(num_agents=agents)
        auditor = AlignmentAuditor()

        console.print("  Running audit...")
        report = auditor.audit(population, observation_steps=steps)
        console.print("  Audit complete.")

        console.print()
        console.print(auditor.format_report(report))

    except ImportError as e:
        console.print(f"[red]Missing dependency: {e}[/red]")


@main.group()
def license():
    """Manage TCS Engine license."""
    pass


@license.command()
def status():
    """Show current license status."""
    from tcs_engine.pro_modules.license import get_license_info

    info = get_license_info()

    if info["status"] == "active":
        console.print(Panel.fit(
            f"[bold green]License Active[/bold green]\n\n"
            f"Tier: {info['tier']}\n"
            f"Email: {info['email']}\n"
            f"Expires: {info['expires']}\n"
            f"Max Agents: {info['max_agents'] or 'Unlimited'}\n"
            f"Max Steps: {info['max_steps'] or 'Unlimited'}",
            box=box.ROUNDED
        ))
    else:
        console.print(Panel.fit(
            f"[bold yellow]No License Found[/bold yellow]\n\n"
            f"{info['message']}\n\n"
            f"[dim]Trial mode: export TCS_TRIAL_MODE=enabled[/dim]",
            box=box.ROUNDED
        ))


@license.command()
@click.argument("key")
def activate(key: str):
    """Activate a license key."""
    from tcs_engine.pro_modules.license import activate_license, LicenseError

    try:
        activate_license(key)
        console.print("[green]License activated successfully![/green]")
    except LicenseError as e:
        console.print(f"[red]Activation failed: {e}[/red]")


@license.command()
def upgrade():
    """Upgrade to TCS-Pro license."""
    console.print(Panel.fit(
        "[bold cyan]TCS Engine PRO[/bold cyan]\n"
        "[dim]Unlock advanced capabilities[/dim]\n\n"
        "[bold]Pricing Tiers:[/bold]\n\n"
        "  [yellow]Academic Pro[/yellow]     $29/month\n"
        "    - Single researcher\n"
        "    - Non-commercial use\n"
        "    - All PRO modules\n\n"
        "  [green]Research Lab[/green]     $99/month\n"
        "    - Up to 10 users\n"
        "    - Commercial research\n"
        "    - Priority support\n\n"
        "  [magenta]Enterprise[/magenta]        Custom\n"
        "    - Unlimited users\n"
        "    - SLA & dedicated support\n"
        "    - Custom integrations\n\n"
        "[bold]Purchase:[/bold] https://tcs-engine.dev/pricing\n\n"
        "[dim]After purchase, activate with:[/dim]\n"
        "[bold]tcs license activate YOUR_LICENSE_KEY[/bold]",
        box=box.ROUNDED
    ))


@main.command()
@click.option("--demo", is_flag=True, help="Run quick demo simulation")
def info(demo: bool):
    """Show TCS Engine information."""
    from tcs_engine import __version__

    console.print(Panel.fit(
        "[bold cyan]TCS Engine[/bold cyan]\n"
        "[dim]Temporal Computational Selfhood[/dim]\n\n"
        f"Version: {__version__}\n\n"
        "[bold]Core Modules (MIT):[/bold]\n"
        "  - Temporal Drift\n"
        "  - Commitment Ledger\n"
        "  - Regret Accumulator\n"
        "  - Self-Prediction Loss\n"
        "  - Existential Load\n"
        "  - Lock-In Engine\n"
        "  - Sigma-Integration Index\n\n"
        "[bold]PRO Modules (Commercial):[/bold]\n"
        "  - Dashboard API\n"
        "  - Real-time Visualizer\n"
        "  - Experiment Manager\n"
        "  - Phase Transition Scanner\n"
        "  - Alignment Auditor\n\n"
        "[dim]https://tcs-engine.dev[/dim]",
        box=box.ROUNDED
    ))

    # Demo simulation with metrics
    if demo:
        from tcs_engine.core.agent import TemporalConstraintPopulation

        console.print("\n[bold]Quick Demo (10 agents, 50 steps):[/bold]")
        population = TemporalConstraintPopulation(num_agents=10)

        for _ in range(50):
            population.step()
            for agent in population.agents:
                actual = np.random.uniform(0, 5)
                counterfactuals = [np.random.uniform(0, 7) for _ in range(3)]
                agent.update_regret(population.modules, actual, counterfactuals)

        summary = population.get_summary()

        # Metrics table
        table = Table(title="Live Metrics", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Status", style="yellow")

        sii = summary["sii"]
        table.add_row("SII", f"{sii:.2f}", "[OK]" if sii > 5 else "[LOW]")

        drift = summary["mean_drift"]
        drift_label = "Stable" if drift < 0.1 else "Drifting" if drift < 0.3 else "Unstable"
        table.add_row("Drift Stability", drift_label, "[OK]" if drift < 0.1 else "[WARN]")

        locked = summary["locked"]
        table.add_row("Lock-In Status", "LOCKED" if locked else "Unlocked", "[OK]" if locked else "")

        console.print(table)

    # Upgrade hook
    console.print()
    console.print(Panel(
        "[bold yellow]Upgrade to TCS-Pro for:[/bold yellow]\n\n"
        "  [green]+[/green] Phase Transition Detection\n"
        "  [green]+[/green] Alignment Audits\n"
        "  [green]+[/green] Real-Time Visualization\n"
        "  [green]+[/green] Experiment Manager\n"
        "  [green]+[/green] Priority Support\n\n"
        "[bold]Run:[/bold] tcs license upgrade\n"
        "[dim]Or visit: https://tcs-engine.dev/pricing[/dim]",
        title="[yellow]PRO[/yellow]",
        box=box.ROUNDED
    ))


if __name__ == "__main__":
    main()
