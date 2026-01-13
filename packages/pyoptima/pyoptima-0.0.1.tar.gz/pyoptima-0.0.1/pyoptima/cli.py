"""
Main CLI entry point for pyoptima commands.
"""

import argparse
import json
import sys
from pathlib import Path

from pyoptima.optimization_engine import OptimizationEngine


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PyOptima - Declarative Optimization Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # optimize subcommand
    optimize_parser = subparsers.add_parser(
        "optimize", help="Run optimization from configuration file"
    )
    optimize_parser.add_argument(
        "config_file",
        type=str,
        help="Path to optimization configuration file (JSON)",
    )
    optimize_parser.add_argument(
        "--output",
        type=str,
        help="Output file path for results (JSON format)",
    )
    optimize_parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print output",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "optimize":
        return cmd_optimize(
            config_file=args.config_file,
            output=args.output,
            pretty=args.pretty,
        )
    else:
        parser.print_help()
        return 1


def cmd_optimize(config_file: str, output: str = None, pretty: bool = False) -> int:
    """
    Run optimization from configuration file.

    Args:
        config_file: Path to configuration file
        output: Optional output file path
        pretty: Whether to pretty print output

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Create engine
        engine = OptimizationEngine()

        # Run optimization
        result = engine.optimize_from_file(config_file)

        # Convert to dictionary
        result_dict = result.to_dict()

        # Output results
        if output:
            with open(output, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(result_dict, f, indent=2)
                else:
                    json.dump(result_dict, f)
            print(f"✓ Results written to {output}")
        else:
            if pretty:
                print(json.dumps(result_dict, indent=2))
            else:
                print(json.dumps(result_dict))

        # Return appropriate exit code
        if result.is_optimal():
            return 0
        else:
            print(
                f"⚠ Warning: Optimization did not find optimal solution. Status: {result.status}",
                file=sys.stderr,
            )
            return 1

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

