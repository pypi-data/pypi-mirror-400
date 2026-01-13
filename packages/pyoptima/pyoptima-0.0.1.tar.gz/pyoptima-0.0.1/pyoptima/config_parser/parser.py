"""
Parser for optimization configuration files.
"""

import json
from pathlib import Path
from typing import Dict, Any

from pyoptima.models.config import OptimizationConfig


def parse_config(config_data: Dict[str, Any]) -> OptimizationConfig:
    """
    Parse optimization configuration from a dictionary.

    Args:
        config_data: Dictionary containing optimization configuration

    Returns:
        OptimizationConfig object

    Raises:
        ValueError: If configuration is invalid
    """
    try:
        return OptimizationConfig(**config_data)
    except Exception as e:
        raise ValueError(f"Invalid optimization configuration: {e}") from e


def parse_config_file(file_path: str) -> OptimizationConfig:
    """
    Load and parse an optimization configuration file (JSON).

    Args:
        file_path: Path to configuration file

    Returns:
        OptimizationConfig object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported or invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    # Determine file format
    suffix = path.suffix.lower()

    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    else:
        raise ValueError(
            f"Unsupported file format: {suffix}. Supported formats: .json"
        )

    if not isinstance(config_data, dict):
        raise ValueError(
            f"Configuration file must contain a dictionary/object, got {type(config_data)}"
        )

    return parse_config(config_data)

