"""
Factory for creating solver instances.
"""

from typing import Optional

from pyoptima.models.config import OptimizationConfig
from pyoptima.solvers.base import Solver, SolverType
from pyoptima.solvers.cbc_solver import CBCSolver
from pyoptima.solvers.glpk_solver import GLPKSolver
from pyoptima.solvers.gurobi_solver import GurobiSolver


def get_solver(
    solver_type: SolverType, time_limit_seconds: Optional[int] = None
) -> Solver:
    """
    Get a solver instance for the specified solver type.

    Args:
        solver_type: Type of solver to create
        time_limit_seconds: Time limit for optimization in seconds

    Returns:
        Solver instance

    Raises:
        ValueError: If solver type is not supported
        RuntimeError: If solver is not available
    """
    solver_map = {
        SolverType.CBC: CBCSolver,
        SolverType.GUROBI: GurobiSolver,
        SolverType.GLPK: GLPKSolver,
    }

    if solver_type not in solver_map:
        raise ValueError(f"Unsupported solver type: {solver_type}")

    solver_class = solver_map[solver_type]
    solver = solver_class(time_limit_seconds=time_limit_seconds)

    if not solver.is_available():
        raise RuntimeError(
            f"Solver {solver_type.value} is not available. "
            f"Please install the required dependencies."
        )

    return solver

