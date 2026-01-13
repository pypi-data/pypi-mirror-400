"""
PyOptima - Declarative Optimization Service

A Python package for declarative optimization that accepts configuration files
and performs optimizations using various solvers (CBC, GUROBI, GLPK).
"""

__version__ = "0.0.1"

# Main optimization engine
from pyoptima.optimization_engine import OptimizationEngine, OptimizationResult

# Config parser
from pyoptima.config_parser import parse_config, parse_config_file

# Models
from pyoptima.models.config import OptimizationConfig

# Solvers
from pyoptima.solvers import SolverType, get_solver

__all__ = [
    # Optimization Engine
    "OptimizationEngine",
    "OptimizationResult",
    # Config Parser
    "OptimizationConfig",
    "parse_config",
    "parse_config_file",
    # Solvers
    "SolverType",
    "get_solver",
]

