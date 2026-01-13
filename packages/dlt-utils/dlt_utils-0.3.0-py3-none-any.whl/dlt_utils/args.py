"""
Common CLI arguments for dlt pipelines.

This module provides reusable argument definitions that can be added to any
dlt pipeline's argument parser.

Usage:
    from dlt_utils import create_base_parser, add_common_args
    
    # Option 1: Use pre-configured base parser
    parser = create_base_parser(description="My pipeline")
    parser.add_argument("--my-custom-arg", ...)
    args = parser.parse_args()
    
    # Option 2: Add common args to existing parser
    parser = argparse.ArgumentParser(description="My pipeline")
    add_common_args(parser)
    parser.add_argument("--my-custom-arg", ...)
    args = parser.parse_args()
"""
import argparse
from dataclasses import dataclass
from typing import Literal


@dataclass
class CommonArgs:
    """
    Dataclass representing common CLI arguments.
    
    Attributes:
        debug: Enable debug logging
        destination: Target database type
        dev_mode: Reset schema between runs
        resources: List of resources to load (None = all)
        refresh: Refresh mode for tables
        list_resources: Show available resources and exit
    """
    debug: bool = False
    destination: Literal["duckdb", "mssql"] = "mssql"
    dev_mode: bool = False
    resources: list[str] | None = None
    refresh: Literal["drop_sources", "drop_resources"] | None = None
    list_resources: bool = False


def add_common_args(
    parser: argparse.ArgumentParser,
    default_destination: str = "mssql",
    destinations: list[str] | None = None,
) -> None:
    """
    Add common dlt pipeline arguments to an existing parser.
    
    Args:
        parser: The argument parser to add arguments to.
        default_destination: Default destination database (default: mssql).
        destinations: List of allowed destinations (default: ["duckdb", "mssql"]).
    
    Added arguments:
        --debug: Enable debug logging
        --resources: List of resources to load
        --destination: Target database
        --dev-mode: Reset schema between runs
        --refresh: Refresh mode (drop_sources or drop_resources)
        --list-resources: Show available resources and exit
    """
    if destinations is None:
        destinations = ["duckdb", "mssql"]
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--resources",
        nargs="*",
        default=None,
        help="List of resources to load (default: all)",
    )
    parser.add_argument(
        "--destination",
        choices=destinations,
        default=default_destination,
        help=f"Destination database (default: {default_destination})",
    )
    parser.add_argument(
        "--dev-mode",
        action="store_true",
        default=False,
        help="Enable dev mode (resets schema between runs)",
    )
    parser.add_argument(
        "--refresh",
        choices=["drop_sources", "drop_resources"],
        default=None,
        help=(
            "Refresh mode: 'drop_sources' drops all tables and state for the source "
            "(full rebuild), 'drop_resources' only drops tables and state for "
            "selected resources"
        ),
    )
    parser.add_argument(
        "--list-resources",
        action="store_true",
        help="List all available resources and exit",
    )


def create_base_parser(
    description: str = "DLT data pipeline",
    default_destination: str = "mssql",
    destinations: list[str] | None = None,
) -> argparse.ArgumentParser:
    """
    Create an argument parser with common dlt pipeline arguments pre-configured.
    
    Args:
        description: Description for the argument parser.
        default_destination: Default destination database (default: mssql).
        destinations: List of allowed destinations (default: ["duckdb", "mssql"]).
    
    Returns:
        ArgumentParser with common arguments already added.
    
    Example:
        parser = create_base_parser("My Pipeline")
        parser.add_argument("--my-custom-arg", type=int, default=10)
        args = parser.parse_args()
    """
    parser = argparse.ArgumentParser(description=description)
    add_common_args(parser, default_destination, destinations)
    return parser


def get_common_args(args: argparse.Namespace) -> CommonArgs:
    """
    Extract common arguments from a parsed Namespace into a CommonArgs dataclass.
    
    Args:
        args: Parsed argument namespace.
        
    Returns:
        CommonArgs dataclass with extracted values.
    """
    return CommonArgs(
        debug=getattr(args, "debug", False),
        destination=getattr(args, "destination", "mssql"),
        dev_mode=getattr(args, "dev_mode", False),
        resources=getattr(args, "resources", None),
        refresh=getattr(args, "refresh", None),
        list_resources=getattr(args, "list_resources", False),
    )
