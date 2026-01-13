"""
Base solver interface and types.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

from pyoptima.models.config import OptimizationConfig


class SolverType(str, Enum):
    """Supported solver types."""

    CBC = "CBC"
    GUROBI = "GUROBI"
    GLPK = "GLPK"


class Solver(ABC):
    """Abstract base class for optimization solvers."""

    def __init__(self, time_limit_seconds: Optional[int] = None):
        """
        Initialize solver.

        Args:
            time_limit_seconds: Time limit for optimization in seconds
        """
        self.time_limit_seconds = time_limit_seconds

    @abstractmethod
    def solve(
        self, config: OptimizationConfig
    ) -> Dict[str, Any]:
        """
        Solve the optimization problem.

        Args:
            config: Optimization configuration

        Returns:
            Dictionary containing:
                - status: str - Status of the optimization (e.g., "optimal", "infeasible", "unbounded")
                - objective_value: float - Objective function value (if optimal)
                - variables: Dict[str, float] - Variable values (if optimal)
                - message: str - Status message
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the solver is available.

        Returns:
            True if solver is available, False otherwise
        """
        pass

