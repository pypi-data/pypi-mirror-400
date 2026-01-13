# PyOptima Examples

This directory contains example optimization configuration files.

## Portfolio Optimization

`portfolio_optimization.json` - A simple portfolio rebalancing problem that maximizes expected return subject to budget constraints.

Run with:
```bash
pyoptima optimize portfolio_optimization.json
```

## Nurse Scheduling

`nurse_scheduling.json` - A binary optimization problem for scheduling nurses across shifts with minimum staffing requirements.

Run with:
```bash
pyoptima optimize nurse_scheduling.json
```

## Running Examples

From the project root:

```bash
# Run portfolio optimization
pyoptima optimize examples/portfolio_optimization.json --output results.json --pretty

# Run nurse scheduling
pyoptima optimize examples/nurse_scheduling.json --output results.json --pretty
```

