"""
Dashboard API - REST API for TCS Metrics

PRO MODULE - Commercial License Required

Provides FastAPI endpoints for real-time metrics access.
"""

from typing import Dict, Any, Optional
from .license import require_license, LicenseError

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


class SimulationConfig(BaseModel):
    """Configuration for simulation."""
    num_agents: int = 10
    num_steps: int = 100
    identity_dim: int = 10
    num_actions: int = 5


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""
    timestep: int
    num_agents: int
    mean_drift: float
    mean_regret: float
    max_regret: float
    mean_load: float
    sii: float
    locked: bool
    total_lockins: int


@require_license("pro_individual")
class DashboardAPI:
    """
    REST API Dashboard for TCS Engine.

    Provides endpoints for:
    - Running simulations
    - Retrieving real-time metrics
    - Configuring experiments

    PRO LICENSE REQUIRED
    """

    def __init__(self, population=None):
        if not HAS_FASTAPI:
            raise ImportError(
                "FastAPI required for DashboardAPI. "
                "Install with: pip install tcs-engine[pro]"
            )

        self.app = FastAPI(
            title="TCS Engine Dashboard API",
            description="Real-time metrics for Temporal Computational Selfhood simulations",
            version="0.1.0"
        )
        self.population = population
        self._setup_routes()

    def _setup_routes(self):
        """Set up API routes."""

        @self.app.get("/")
        async def root():
            return {"message": "TCS Engine Dashboard API", "version": "0.1.0"}

        @self.app.get("/health")
        async def health():
            return {"status": "healthy"}

        @self.app.get("/metrics", response_model=MetricsResponse)
        async def get_metrics():
            if self.population is None:
                raise HTTPException(status_code=400, detail="No simulation running")

            summary = self.population.get_summary()
            return MetricsResponse(**summary)

        @self.app.post("/simulation/start")
        async def start_simulation(config: SimulationConfig):
            from tcs_engine.core.agent import TemporalConstraintPopulation

            self.population = TemporalConstraintPopulation(
                num_agents=config.num_agents,
                identity_dim=config.identity_dim,
                num_actions=config.num_actions
            )
            return {"status": "started", "config": config.dict()}

        @self.app.post("/simulation/step")
        async def step_simulation(steps: int = 1):
            if self.population is None:
                raise HTTPException(status_code=400, detail="No simulation running")

            for _ in range(steps):
                self.population.step()

            return {"status": "ok", "timestep": self.population.timestep}

        @self.app.get("/agents/{agent_id}")
        async def get_agent(agent_id: int):
            if self.population is None:
                raise HTTPException(status_code=400, detail="No simulation running")

            if agent_id >= len(self.population.agents):
                raise HTTPException(status_code=404, detail="Agent not found")

            agent = self.population.agents[agent_id]
            return agent.get_state()

        @self.app.get("/modules/sii/history")
        async def get_sii_history():
            if self.population is None:
                raise HTTPException(status_code=400, detail="No simulation running")

            return {"history": self.population.modules["sii"].history}

        @self.app.get("/modules/lockin/states")
        async def get_locked_states():
            if self.population is None:
                raise HTTPException(status_code=400, detail="No simulation running")

            lockin = self.population.modules["lockin_engine"]
            return {
                "total_lockins": lockin.total_lockins,
                "inertia": lockin.inertia,
                "locked_states": [
                    {"timestamp": s.timestamp, "strength": s.strength}
                    for s in lockin.locked_states
                ]
            }

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the API server."""
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)

    def get_app(self):
        """Get FastAPI app for external serving."""
        return self.app
