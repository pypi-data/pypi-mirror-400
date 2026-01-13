"""CLI tool for running YAML-defined ML experiments.

This tool loads a YAML configuration file, selects one or more experiments,
and executes them using the Runner class. It also provides inspection options
to view configuration and dataset information without running experiments.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import traceback
from typing import Any

from dotenv import load_dotenv
import yaml

from .config import YamlConfig
from .dataset import Dataset
from .experiment import Experiment
from .runner import Runner

load_dotenv()

# Constants
MAX_COLUMNS_TO_DISPLAY = 10


def parse_kv_pairs(kv_list: list[str]) -> dict[str, str]:
    """Parse key=value pairs from command line arguments.

    Parameters
    ----------
    kv_list : list[str]
        List of "key=value" strings

    Returns
    -------
    dict[str, str]
        Dictionary of parsed key-value pairs

    Raises
    ------
    argparse.ArgumentTypeError
        If a pair is not in "key=value" format
    """
    variables: dict[str, str] = {}
    for item in kv_list:
        if "=" not in item:
            raise argparse.ArgumentTypeError(  # noqa: TRY003
                f"Invalid variable format {item!r}, expected key=value"
            )
        key, value = item.split("=", 1)
        variables[key.strip()] = value.strip()
    return variables


def _basic_stats_for_dataset(name: str, cfg: YamlConfig) -> dict[str, Any]:
    """Get basic statistics for a dataset using the Dataset class.

    Parameters
    ----------
    name : str
        Dataset name
    cfg : YamlConfig
        Configuration object

    Returns
    -------
    dict[str, Any]
        Dictionary with dataset statistics including name, description, format,
        type, path, num_columns, num_rows, column_names, and is_combined flag
    """
    try:
        ds = Dataset(name, cfg)

        result: dict[str, Any] = {
            "name": name,
            "description": ds.description,
            "format": ds.format,
            "type": ds.type,
            "path": ds.path,
            "is_combined": ds.is_combined,
        }

        # Try to read and get statistics
        try:
            stats = ds.get_statistics()
            result.update({
                "num_columns": stats["num_columns"],
                "num_rows": stats["num_rows"],
                "column_names": stats["column_names"],
            })
        except Exception as exc:
            # If reading fails, still return basic info with error
            result.update({
                "num_columns": None,
                "num_rows": None,
                "column_names": None,
                "error": str(exc),
            })

    except Exception as exc:
        # If dataset creation fails, return minimal info
        return {
            "name": name,
            "error": f"Failed to create dataset: {exc}",
        }
    else:
        return result


def filter_sections(data: dict, sections: list[str]) -> dict:
    """Filter configuration to include only specified sections.

    Parameters
    ----------
    data : dict
        Full configuration dictionary
    sections : list[str]
        List of section names to include

    Returns
    -------
    dict
        Filtered configuration with only specified sections
    """
    result = {}
    for section in sections:
        if section in data:
            result[section] = data[section]
        else:
            print(f"Warning: Section '{section}' not found", file=sys.stderr)  # noqa: T201
    return result


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        prog="cli-experiment",
        description="Run YAML-defined ML experiments or inspect configuration and datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all experiments defined in the YAML file
  %(prog)s experiment.yaml

  # Run specific experiment(s)
  %(prog)s experiment.yaml --experiments house_prices_prediction_simple

  # Run multiple specific experiments
  %(prog)s experiment.yaml --experiments exp1 exp2 exp3

  # Run with variable substitution
  %(prog)s experiment.yaml --var path=/data --var env=production

  # Inspect configuration
  %(prog)s experiment.yaml --show-config

  # Inspect configuration as JSON
  %(prog)s experiment.yaml --show-config --json

  # Inspect specific sections
  %(prog)s experiment.yaml --show-config --section experiments --section datasets

  # Inspect datasets
  %(prog)s experiment.yaml --show-datasets

  # Inspect datasets as JSON
  %(prog)s experiment.yaml --show-datasets --json
        """,
    )

    parser.add_argument(
        "yaml",
        type=Path,
        help="Path to the YAML configuration file containing experiment definitions",
    )

    parser.add_argument(
        "--experiments",
        action="append",
        dest="experiments",
        metavar="EXPERIMENT",
        help="Name(s) of experiment(s) to run (can be specified multiple times). "
        "If not specified, all experiments in the YAML will be run. "
        "Ignored if --show-config or --show-datasets is used.",
    )

    parser.add_argument(
        "--var",
        action="append",
        dest="vars",
        metavar="KEY=VALUE",
        help="Variable for interpolation (can be specified multiple times)",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress verbose output from Runner",
    )

    # Inspection options
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show processed configuration . When used, experiments are not run.",
    )

    parser.add_argument(
        "--show-datasets",
        action="store_true",
        help="Show dataset statistics . When used, experiments are not run.",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of YAML/text (used with --show-config or --show-datasets)",
    )

    parser.add_argument(
        "--section",
        action="append",
        dest="sections",
        metavar="SECTION",
        help="Output only specific section(s) when using --show-config "
        "(can be specified multiple times)",
    )

    parser.add_argument(
        "--show-variables",
        action="store_true",
        help="Show resolved variables when using --show-config",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Parameters
    ----------
    argv : Optional[list[str]]
        Command line arguments (default: sys.argv)

    Returns
    -------
    int
        Exit code (0 for success, non-zero for error)
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    exit_code = 0  # Initialize exit code
    try:
        # Parse variable substitutions
        variables = parse_kv_pairs(list(args.vars)) if args.vars else {}

        # Load configuration
        if not args.yaml.exists():
            print(f"YAML file not found: {args.yaml}", file=sys.stderr)  # noqa: T201
            return 1

        config = YamlConfig(args.yaml, **variables)

        # Handle inspection modes (these don't run experiments)
        if args.show_config:
            # Show configuration
            data = config.to_dict()

            # Filter sections if specified
            if args.sections:
                data = filter_sections(data, args.sections)

            # Show variables if requested
            if args.show_variables:
                print("# Resolved Variables:", file=sys.stderr)  # noqa: T201
                for key, value in sorted(config.variables.items()):
                    print(f"  {key}={value}", file=sys.stderr)  # noqa: T201

            # Format output
            if args.json:
                print(json.dumps(data, indent=2))  # noqa: T201
            else:
                print(yaml.dump(  # noqa: T201
                    data,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                ))

            return 0

        if args.show_datasets:
            # Show dataset statistics
            dataset_names = config.get_datasets_list()
            results = [_basic_stats_for_dataset(name, config) for name in dataset_names]

            if args.json:
                print(json.dumps({"datasets": results}, indent=2))  # noqa: T201
            else:
                for item in results:
                    if "error" in item:
                        continue
                    print(f"\nDataset: {item['name']}")  # noqa: T201
                    if item.get("is_combined"):
                        print("  Type: Combined")  # noqa: T201
                    if item.get("description"):
                        print(f"  Description: {item['description']}")  # noqa: T201
                    if item.get("format"):
                        print(f"  format: {item['format']}")  # noqa: T201
                    if item.get("num_rows") is not None:
                        print(f"  Rows: {item['num_rows']}")  # noqa: T201
                    if item.get("num_columns") is not None:
                        print(f"  Columns: {item['num_columns']}")  # noqa: T201
                    # Print column names if available
                    column_names = item.get("column_names")
                    if column_names:
                        print(f"  Column names: {', '.join(column_names[:MAX_COLUMNS_TO_DISPLAY])}")  # noqa: T201
                        if len(column_names) > MAX_COLUMNS_TO_DISPLAY:
                            print(f"    ... and {len(column_names) - MAX_COLUMNS_TO_DISPLAY} more")  # noqa: T201

            return 0

        # Normal mode: run experiments
        # Get list of available experiments
        all_experiment_names = Experiment.list_experiment_names(config)

        if not all_experiment_names:
            print("No experiments found in configuration", file=sys.stderr)  # noqa: T201
            return 1

        # Determine which experiments to run
        if args.experiments:
            # User specified experiments to run
            experiments_to_run = args.experiments
            # Check if all specified experiments exist
            missing_experiments = [
                exp for exp in experiments_to_run if exp not in all_experiment_names
            ]
            if missing_experiments:
                print(f"Experiment(s) not found: {', '.join(missing_experiments)}", file=sys.stderr)  # noqa: T201
                return 1
        else:
            # Run all experiments by default
            experiments_to_run = all_experiment_names

        # Verify configuration before running
        try:
            Experiment.verify_config(config)
        except Exception as e:
            if not args.quiet:
                print(f"Configuration validation failed: {e}", file=sys.stderr)  # noqa: T201
            return 1

        # Run each experiment
        verbose = not args.quiet
        exit_code = 0

        for exp_name in experiments_to_run:
            try:
                if verbose:
                    pass

                # Create experiment object
                experiment = Experiment(config, exp_name)

                # Create and run runner
                runner = Runner(experiment, verbose=verbose)
                results = runner.run()

                if verbose:
                    pass

            except KeyboardInterrupt:
                return 130
            except Exception as e:
                print(f"Error running experiment: {e}", file=sys.stderr)  # noqa: T201
                if verbose:
                    traceback.print_exc()
                exit_code = 1

        if verbose and len(experiments_to_run) > 1:
            pass

    except FileNotFoundError as e:
        print(f"YAML file not found: {e}", file=sys.stderr)  # noqa: T201
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa: T201
        return 1
    except Exception as e:
        if "--debug" in (argv or sys.argv):
            raise  # noqa: TRY003
        print(f"Error: {e}", file=sys.stderr)  # noqa: T201
        return 1
    else:
        return exit_code


if __name__ == "__main__":
    sys.exit(main())
