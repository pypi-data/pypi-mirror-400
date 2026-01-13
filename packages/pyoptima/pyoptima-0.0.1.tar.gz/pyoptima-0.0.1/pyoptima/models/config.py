"""
Pydantic models for optimization configuration.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Meta(BaseModel):
    """Metadata for the optimization job."""

    job_id: str = Field(..., description="Unique identifier for the optimization job")
    solver: Literal["CBC", "GUROBI", "GLPK"] = Field(
        ..., description="Solver to use for optimization"
    )
    time_limit_seconds: Optional[int] = Field(
        None, description="Time limit for optimization in seconds"
    )


class OptimizationVariable(BaseModel):
    """Definition of an optimization variable."""

    id: str = Field(..., description="Unique identifier for the variable")
    type: Literal["Continuous", "Binary", "Integer"] = Field(
        ..., description="Type of the variable"
    )
    lb: Optional[float] = Field(None, description="Lower bound for the variable")
    ub: Optional[float] = Field(None, description="Upper bound for the variable")


class Term(BaseModel):
    """A term in the objective or constraint expression."""

    var: str = Field(..., description="Variable ID")
    coef: float = Field(..., description="Coefficient for the variable")


class Objective(BaseModel):
    """Objective function definition."""

    direction: Literal["Maximize", "Minimize"] = Field(
        ..., description="Direction of optimization"
    )
    terms: List[Term] = Field(..., description="Terms in the objective function")


class Constraint(BaseModel):
    """A constraint in the optimization problem."""

    id: str = Field(..., description="Unique identifier for the constraint")
    lower_bound: Optional[float] = Field(
        None, description="Lower bound for the constraint"
    )
    upper_bound: Optional[float] = Field(
        None, description="Upper bound for the constraint"
    )
    terms: List[Term] = Field(..., description="Terms in the constraint expression")


class OptimizationConfig(BaseModel):
    """Complete optimization configuration."""

    meta: Meta = Field(..., description="Metadata for the optimization job")
    variables: List[OptimizationVariable] = Field(
        ..., description="List of optimization variables"
    )
    objective: Objective = Field(..., description="Objective function")
    constraints: List[Constraint] = Field(
        default_factory=list, description="List of constraints"
    )

    class Config:
        """Pydantic config."""

        extra = "forbid"
        json_schema_extra = {
            "example": {
                "meta": {
                    "job_id": "portfolio-rebalance-001",
                    "solver": "CBC",
                    "time_limit_seconds": 30,
                },
                "variables": [
                    {"id": "w_aapl", "type": "Continuous", "lb": 0, "ub": 0.5},
                    {"id": "shift_john_1", "type": "Binary"},
                ],
                "objective": {
                    "direction": "Maximize",
                    "terms": [
                        {"var": "w_aapl", "coef": 0.12},
                        {"var": "shift_john_1", "coef": -10},
                    ],
                },
                "constraints": [
                    {
                        "id": "budget_limit",
                        "upper_bound": 1.0,
                        "terms": [
                            {"var": "w_aapl", "coef": 1},
                            {"var": "w_msft", "coef": 1},
                        ],
                    },
                ],
            }
        }

