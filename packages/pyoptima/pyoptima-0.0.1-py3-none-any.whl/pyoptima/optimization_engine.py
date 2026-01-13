"""
Main optimization engine that processes configurations and runs optimizations.
"""

from typing import Any, Dict, Optional

from pyoptima.config_parser import parse_config_file
from pyoptima.models.config import OptimizationConfig
from pyoptima.solvers import SolverType, get_solver


class OptimizationResult:
    """Result of an optimization run."""

    def __init__(
        self,
        status: str,
        objective_value: Optional[float],
        variables: Dict[str, float],
        message: str,
        job_id: str,
    ):
        """
        Initialize optimization result.

        Args:
            status: Status of the optimization
            objective_value: Objective function value (if optimal)
            variables: Variable values (if optimal)
            message: Status message
            job_id: Job ID
        """
        self.status = status
        self.objective_value = objective_value
        self.variables = variables
        self.message = message
        self.job_id = job_id

    def is_optimal(self) -> bool:
        """Check if the solution is optimal."""
        return self.status == "optimal"

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "job_id": self.job_id,
            "status": self.status,
            "objective_value": self.objective_value,
            "variables": self.variables,
            "message": self.message,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"OptimizationResult(job_id={self.job_id}, status={self.status}, "
            f"objective_value={self.objective_value})"
        )


class OptimizationEngine:
    """Main engine for running optimizations from configuration files."""

    def __init__(self):
        """Initialize the optimization engine."""
        pass

    def optimize_from_file(self, config_file: str) -> OptimizationResult:
        """
        Run optimization from a configuration file.

        Args:
            config_file: Path to configuration file

        Returns:
            OptimizationResult object
        """
        config = parse_config_file(config_file)
        return self.optimize(config)

    def optimize(self, config: OptimizationConfig) -> OptimizationResult:
        """
        Run optimization from a configuration object.

        Args:
            config: Optimization configuration

        Returns:
            OptimizationResult object
        """
        # Get solver type
        solver_type = SolverType(config.meta.solver)

        # Get solver instance
        solver = get_solver(
            solver_type=solver_type,
            time_limit_seconds=config.meta.time_limit_seconds,
        )

        # Solve
        result_dict = solver.solve(config)

        # Create result object
        return OptimizationResult(
            status=result_dict["status"],
            objective_value=result_dict.get("objective_value"),
            variables=result_dict.get("variables", {}),
            message=str(result_dict.get("message", "")),
            job_id=config.meta.job_id,
        )

