# PyOptima

> **Declarative Optimization Service - Accept configuration files and perform optimizations**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**PyOptima** is a Python package for declarative optimization that accepts configuration files and performs optimizations using various solvers (CBC, GUROBI, GLPK). It provides a simple, declarative interface for defining optimization problems without writing solver-specific code.

## Features

- 🚀 **Declarative Configuration** - Define optimization problems using JSON configuration files
- 🔧 **Multiple Solvers** - Support for CBC, GUROBI, and GLPK solvers
- 📋 **Type Safety** - Full type hints and Pydantic v2 compatibility
- 🎯 **Easy to Use** - Simple API for running optimizations
- 🔄 **Swappable Solvers** - Easily switch between different solvers via configuration

## Installation

### Core Library

```bash
pip install pyoptima
```

### With Solver Support

```bash
# For CBC and GLPK (using PuLP)
pip install pyoptima[cbc]
pip install pyoptima[glpk]

# For Gurobi (requires Gurobi license)
pip install pyoptima[gurobi]

# Install all solvers
pip install pyoptima[all]
```

## Quick Start

### 1. Create a Configuration File

Create a JSON file (e.g., `portfolio.json`) with your optimization problem:

```json
{
  "meta": {
    "job_id": "portfolio-rebalance-001",
    "solver": "CBC",
    "time_limit_seconds": 30
  },
  "variables": [
    { "id": "w_aapl", "type": "Continuous", "lb": 0, "ub": 0.5 },
    { "id": "w_msft", "type": "Continuous", "lb": 0, "ub": 0.5 }
  ],
  "objective": {
    "direction": "Maximize",
    "terms": [
      { "var": "w_aapl", "coef": 0.12 },
      { "var": "w_msft", "coef": 0.15 }
    ]
  },
  "constraints": [
    {
      "id": "budget_limit",
      "upper_bound": 1.0,
      "terms": [
        { "var": "w_aapl", "coef": 1 },
        { "var": "w_msft", "coef": 1 }
      ]
    }
  ]
}
```

### 2. Run Optimization

#### Using CLI

```bash
pyoptima optimize portfolio.json
```

With output file:

```bash
pyoptima optimize portfolio.json --output results.json --pretty
```

#### Using Python API

```python
from pyoptima import OptimizationEngine

# Create engine
engine = OptimizationEngine()

# Run optimization
result = engine.optimize_from_file("portfolio.json")

# Check results
if result.is_optimal():
    print(f"Optimal objective value: {result.objective_value}")
    print(f"Variable values: {result.variables}")
else:
    print(f"Optimization status: {result.status}")
```

## Configuration Format

### Meta

Metadata for the optimization job:

```json
{
  "meta": {
    "job_id": "unique-job-id",
    "solver": "CBC",  // "CBC", "GUROBI", or "GLPK"
    "time_limit_seconds": 30  // Optional
  }
}
```

### Variables

Define optimization variables:

```json
{
  "variables": [
    {
      "id": "w_aapl",
      "type": "Continuous",  // "Continuous", "Binary", or "Integer"
      "lb": 0,               // Optional lower bound
      "ub": 0.5              // Optional upper bound
    },
    {
      "id": "shift_john_1",
      "type": "Binary"       // Binary variables don't need bounds
    }
  ]
}
```

### Objective

Define the objective function:

```json
{
  "objective": {
    "direction": "Maximize",  // "Maximize" or "Minimize"
    "terms": [
      { "var": "w_aapl", "coef": 0.12 },
      { "var": "shift_john_1", "coef": -10 }
    ]
  }
}
```

### Constraints

Define constraints:

```json
{
  "constraints": [
    {
      "id": "budget_limit",
      "lower_bound": null,      // Optional
      "upper_bound": 1.0,        // Optional
      "terms": [
        { "var": "w_aapl", "coef": 1 },
        { "var": "w_msft", "coef": 1 }
      ]
    },
    {
      "id": "min_nurses",
      "lower_bound": 2.0,
      "upper_bound": null,
      "terms": [
        { "var": "shift_john_1", "coef": 1 },
        { "var": "shift_jane_1", "coef": 1 }
      ]
    }
  ]
}
```

## Examples

### Portfolio Optimization

```json
{
  "meta": {
    "job_id": "portfolio-001",
    "solver": "CBC"
  },
  "variables": [
    { "id": "w_aapl", "type": "Continuous", "lb": 0, "ub": 0.4 },
    { "id": "w_msft", "type": "Continuous", "lb": 0, "ub": 0.4 },
    { "id": "w_goog", "type": "Continuous", "lb": 0, "ub": 0.4 }
  ],
  "objective": {
    "direction": "Maximize",
    "terms": [
      { "var": "w_aapl", "coef": 0.12 },
      { "var": "w_msft", "coef": 0.15 },
      { "var": "w_goog", "coef": 0.18 }
    ]
  },
  "constraints": [
    {
      "id": "budget",
      "upper_bound": 1.0,
      "terms": [
        { "var": "w_aapl", "coef": 1 },
        { "var": "w_msft", "coef": 1 },
        { "var": "w_goog", "coef": 1 }
      ]
    }
  ]
}
```

### Nurse Scheduling

```json
{
  "meta": {
    "job_id": "nurse-scheduling-001",
    "solver": "CBC"
  },
  "variables": [
    { "id": "shift_john_1", "type": "Binary" },
    { "id": "shift_john_2", "type": "Binary" },
    { "id": "shift_jane_1", "type": "Binary" },
    { "id": "shift_jane_2", "type": "Binary" }
  ],
  "objective": {
    "direction": "Minimize",
    "terms": [
      { "var": "shift_john_1", "coef": 1 },
      { "var": "shift_john_2", "coef": 1 },
      { "var": "shift_jane_1", "coef": 1 },
      { "var": "shift_jane_2", "coef": 1 }
    ]
  },
  "constraints": [
    {
      "id": "min_nurses_shift1",
      "lower_bound": 2.0,
      "terms": [
        { "var": "shift_john_1", "coef": 1 },
        { "var": "shift_jane_1", "coef": 1 }
      ]
    },
    {
      "id": "min_nurses_shift2",
      "lower_bound": 2.0,
      "terms": [
        { "var": "shift_john_2", "coef": 1 },
        { "var": "shift_jane_2", "coef": 1 }
      ]
    }
  ]
}
```

## API Reference

### OptimizationEngine

Main engine for running optimizations.

```python
from pyoptima import OptimizationEngine

engine = OptimizationEngine()

# From file
result = engine.optimize_from_file("config.json")

# From config object
from pyoptima import parse_config_file
config = parse_config_file("config.json")
result = engine.optimize(config)
```

### OptimizationResult

Result object containing optimization results.

```python
result.is_optimal()  # Check if solution is optimal
result.objective_value  # Objective function value
result.variables  # Dictionary of variable values
result.status  # Status string
result.to_dict()  # Convert to dictionary
```

## Supported Solvers

### CBC (COIN-OR Branch and Cut)

- **Installation**: `pip install pyoptima[cbc]`
- **Requirements**: PuLP library
- **Best for**: General-purpose linear and integer programming

### Gurobi

- **Installation**: `pip install pyoptima[gurobi]`
- **Requirements**: Gurobi license (academic or commercial)
- **Best for**: Large-scale optimization problems

### GLPK (GNU Linear Programming Kit)

- **Installation**: `pip install pyoptima[glpk]`
- **Requirements**: PuLP library
- **Best for**: Open-source alternative to commercial solvers

## Development Setup

### Quick Setup

```bash
# Clone repository
cd pyoptima

# Install in development mode
pip install -e ".[dev,all]"

# Run tests
pytest
```

## Requirements

- Python 3.10+
- Pydantic >= 2.0.0
- Solver-specific dependencies (see installation section)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

**Made with ❤️ for the Python optimization community**

