"""
Gurobi solver implementation.
"""

from typing import Any, Dict, Optional

try:
    import gurobipy as gp
    from gurobipy import GRB
    GUROBI_AVAILABLE = True
except ImportError:
    GUROBI_AVAILABLE = False

from pyoptima.models.config import OptimizationConfig
from pyoptima.solvers.base import Solver


class GurobiSolver(Solver):
    """Gurobi solver implementation."""

    def is_available(self) -> bool:
        """Check if Gurobi solver is available."""
        return GUROBI_AVAILABLE

    def solve(self, config: OptimizationConfig) -> Dict[str, Any]:
        """
        Solve the optimization problem using Gurobi.

        Args:
            config: Optimization configuration

        Returns:
            Dictionary with optimization results
        """
        if not self.is_available():
            raise RuntimeError(
                "Gurobi solver is not available. Install gurobipy: pip install gurobipy"
            )

        # Create Gurobi model
        model = gp.Model(config.meta.job_id)

        # Set time limit if specified
        if self.time_limit_seconds:
            model.setParam("TimeLimit", self.time_limit_seconds)

        # Create variables
        variables = {}
        for var_def in config.variables:
            if var_def.type == "Binary":
                var = model.addVar(vtype=GRB.BINARY, name=var_def.id)
            elif var_def.type == "Integer":
                var = model.addVar(
                    lb=var_def.lb if var_def.lb is not None else -GRB.INFINITY,
                    ub=var_def.ub if var_def.ub is not None else GRB.INFINITY,
                    vtype=GRB.INTEGER,
                    name=var_def.id,
                )
            else:  # Continuous
                var = model.addVar(
                    lb=var_def.lb if var_def.lb is not None else -GRB.INFINITY,
                    ub=var_def.ub if var_def.ub is not None else GRB.INFINITY,
                    vtype=GRB.CONTINUOUS,
                    name=var_def.id,
                )
            variables[var_def.id] = var

        # Add objective
        objective_terms = [
            term.coef * variables[term.var] for term in config.objective.terms
        ]
        if config.objective.direction == "Maximize":
            model.setObjective(gp.quicksum(objective_terms), GRB.MAXIMIZE)
        else:
            model.setObjective(gp.quicksum(objective_terms), GRB.MINIMIZE)

        # Add constraints
        for constraint in config.constraints:
            constraint_terms = [
                term.coef * variables[term.var] for term in constraint.terms
            ]
            expr = gp.quicksum(constraint_terms)

            if constraint.lower_bound is not None and constraint.upper_bound is not None:
                model.addConstr(expr >= constraint.lower_bound, name=f"{constraint.id}_lb")
                model.addConstr(expr <= constraint.upper_bound, name=f"{constraint.id}_ub")
            elif constraint.lower_bound is not None:
                model.addConstr(expr >= constraint.lower_bound, name=f"{constraint.id}_lb")
            elif constraint.upper_bound is not None:
                model.addConstr(expr <= constraint.upper_bound, name=f"{constraint.id}_ub")

        # Optimize
        model.optimize()

        # Extract results
        status_map = {
            GRB.OPTIMAL: "optimal",
            GRB.INFEASIBLE: "infeasible",
            GRB.UNBOUNDED: "unbounded",
            GRB.INF_OR_UNBD: "infeasible_or_unbounded",
            GRB.TIME_LIMIT: "time_limit",
        }

        status = status_map.get(model.status, "unknown")
        result = {
            "status": status,
            "message": model.status,
            "objective_value": None,
            "variables": {},
        }

        if status == "optimal":
            result["objective_value"] = model.ObjVal
            result["variables"] = {
                var_id: var.X for var_id, var in variables.items()
            }

        return result

