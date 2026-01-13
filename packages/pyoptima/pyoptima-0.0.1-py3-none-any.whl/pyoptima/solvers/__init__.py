"""
Solver abstraction layer for different optimization solvers.
"""

from pyoptima.solvers.base import Solver, SolverType
from pyoptima.solvers.factory import get_solver

__all__ = ["Solver", "SolverType", "get_solver"]

