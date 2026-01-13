"""
GLPK (GNU Linear Programming Kit) solver implementation.
"""

from typing import Any, Dict, Optional

try:
    from pulp import LpMaximize, LpMinimize, LpProblem, LpStatus, lpSum, LpVariable
    PULP_AVAILABLE = True
except ImportError:
    PULP_AVAILABLE = False

from pyoptima.models.config import OptimizationConfig
from pyoptima.solvers.base import Solver


class GLPKSolver(Solver):
    """GLPK solver implementation using PuLP."""

    def is_available(self) -> bool:
        """Check if GLPK solver is available."""
        return PULP_AVAILABLE

    def solve(self, config: OptimizationConfig) -> Dict[str, Any]:
        """
        Solve the optimization problem using GLPK.

        Args:
            config: Optimization configuration

        Returns:
            Dictionary with optimization results
        """
        if not self.is_available():
            raise RuntimeError("GLPK solver is not available. Install pulp: pip install pulp")

        # Create PuLP problem
        sense = LpMaximize if config.objective.direction == "Maximize" else LpMinimize
        prob = LpProblem(config.meta.job_id, sense)

        # Create variables
        variables = {}
        for var_def in config.variables:
            if var_def.type == "Binary":
                var = LpVariable(var_def.id, cat="Binary")
            elif var_def.type == "Integer":
                var = LpVariable(
                    var_def.id,
                    lowBound=var_def.lb,
                    upBound=var_def.ub,
                    cat="Integer",
                )
            else:  # Continuous
                var = LpVariable(
                    var_def.id,
                    lowBound=var_def.lb,
                    upBound=var_def.ub,
                    cat="Continuous",
                )
            variables[var_def.id] = var

        # Add objective
        objective_terms = [
            term.coef * variables[term.var] for term in config.objective.terms
        ]
        prob += lpSum(objective_terms)

        # Add constraints
        for constraint in config.constraints:
            constraint_terms = [
                term.coef * variables[term.var] for term in constraint.terms
            ]
            expr = lpSum(constraint_terms)

            if constraint.lower_bound is not None and constraint.upper_bound is not None:
                prob += expr >= constraint.lower_bound
                prob += expr <= constraint.upper_bound
            elif constraint.lower_bound is not None:
                prob += expr >= constraint.lower_bound
            elif constraint.upper_bound is not None:
                prob += expr <= constraint.upper_bound

        # Solve
        prob.solve(solver="GLPK")

        # Extract results
        status_map = {
            "Optimal": "optimal",
            "Infeasible": "infeasible",
            "Unbounded": "unbounded",
            "Not Solved": "not_solved",
        }

        pulp_status = LpStatus[prob.status]
        status = status_map.get(pulp_status, "unknown")

        result = {
            "status": status,
            "message": pulp_status,
            "objective_value": None,
            "variables": {},
        }

        if status == "optimal":
            result["objective_value"] = prob.objective.value()
            result["variables"] = {
                var_id: var.varValue for var_id, var in variables.items()
            }

        return result

