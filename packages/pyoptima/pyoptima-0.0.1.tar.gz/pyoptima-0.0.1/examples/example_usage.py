"""
Example usage of PyOptima.

This script demonstrates how to use PyOptima programmatically.
"""

from pyoptima import OptimizationEngine, parse_config_file

# Example 1: Run optimization from file
print("Example 1: Running optimization from file")
print("=" * 50)

engine = OptimizationEngine()
result = engine.optimize_from_file("portfolio_optimization.json")

print(f"Job ID: {result.job_id}")
print(f"Status: {result.status}")
if result.is_optimal():
    print(f"Optimal objective value: {result.objective_value}")
    print("Variable values:")
    for var_id, var_value in result.variables.items():
        print(f"  {var_id}: {var_value}")
else:
    print(f"Message: {result.message}")

print("\n")

# Example 2: Parse config and run optimization
print("Example 2: Parsing config and running optimization")
print("=" * 50)

config = parse_config_file("nurse_scheduling.json")
result = engine.optimize(config)

print(f"Job ID: {result.job_id}")
print(f"Status: {result.status}")
if result.is_optimal():
    print(f"Optimal objective value: {result.objective_value}")
    print("Variable values:")
    for var_id, var_value in result.variables.items():
        print(f"  {var_id}: {var_value}")

print("\n")

# Example 3: Convert result to dictionary
print("Example 3: Converting result to dictionary")
print("=" * 50)

result_dict = result.to_dict()
print(f"Result as dictionary: {result_dict}")

