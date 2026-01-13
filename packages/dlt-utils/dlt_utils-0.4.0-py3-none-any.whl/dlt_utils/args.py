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
    
    # Option 3: Exclude certain args and include optional ones
    parser = create_base_parser(
        description="My pipeline",
        exclude=["dev_mode", "refresh"],
        include=["companies", "start_year"],
    )
    args = parser.parse_args()
    
    # Option 4: Filter items by indices from --companies
    all_configs = get_company_configs()
    selected = filter_by_indices(all_configs, args.companies)
"""
import argparse
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# All available argument names for validation
CORE_ARGS = {"debug", "resources", "destination", "dev_mode", "refresh", "list_resources"}
OPTIONAL_ARGS = {"companies", "start_year"}
ALL_ARGS = CORE_ARGS | OPTIONAL_ARGS


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
        companies: List of company indices to load (None = all)
        start_year: Start year for partitioned resources (None = source default)
    """
    debug: bool = False
    destination: Literal["duckdb", "mssql"] = "mssql"
    dev_mode: bool = False
    resources: list[str] | None = None
    refresh: Literal["drop_sources", "drop_resources"] | None = None
    list_resources: bool = False
    companies: list[int] | None = None
    start_year: int | None = None


def add_common_args(
    parser: argparse.ArgumentParser,
    default_destination: str = "mssql",
    destinations: list[str] | None = None,
    exclude: list[str] | None = None,
    include: list[str] | None = None,
) -> None:
    """
    Add common dlt pipeline arguments to an existing parser.
    
    Args:
        parser: The argument parser to add arguments to.
        default_destination: Default destination database (default: mssql).
        destinations: List of allowed destinations (default: ["duckdb", "mssql"]).
        exclude: List of argument names to exclude from core args.
            Valid names: debug, resources, destination, dev_mode, refresh, list_resources
        include: List of optional argument names to include.
            Valid names: companies, start_year
    
    Core arguments (added by default unless excluded):
        --debug: Enable debug logging
        --resources: List of resources to load
        --destination: Target database
        --dev-mode: Reset schema between runs
        --refresh: Refresh mode (drop_sources or drop_resources)
        --list-resources: Show available resources and exit
    
    Optional arguments (only added when included):
        --companies: List of company indices to load
        --start-year: Start year for partitioned resources
    
    Raises:
        ValueError: If invalid argument names are provided in exclude or include.
    """
    if destinations is None:
        destinations = ["duckdb", "mssql"]
    
    exclude_set = set(exclude) if exclude else set()
    include_set = set(include) if include else set()
    
    # Validate exclude names
    invalid_exclude = exclude_set - CORE_ARGS
    if invalid_exclude:
        raise ValueError(
            f"Invalid exclude argument(s): {invalid_exclude}. "
            f"Valid options: {CORE_ARGS}"
        )
    
    # Validate include names
    invalid_include = include_set - OPTIONAL_ARGS
    if invalid_include:
        raise ValueError(
            f"Invalid include argument(s): {invalid_include}. "
            f"Valid options: {OPTIONAL_ARGS}"
        )
    
    # Core arguments (added unless excluded)
    if "debug" not in exclude_set:
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging",
        )
    
    if "resources" not in exclude_set:
        parser.add_argument(
            "--resources",
            nargs="*",
            default=None,
            help="List of resources to load (default: all)",
        )
    
    if "destination" not in exclude_set:
        parser.add_argument(
            "--destination",
            choices=destinations,
            default=default_destination,
            help=f"Destination database (default: {default_destination})",
        )
    
    if "dev_mode" not in exclude_set:
        parser.add_argument(
            "--dev-mode",
            action="store_true",
            default=False,
            help="Enable dev mode (resets schema between runs)",
        )
    
    if "refresh" not in exclude_set:
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
    
    if "list_resources" not in exclude_set:
        parser.add_argument(
            "--list-resources",
            action="store_true",
            help="List all available resources and exit",
        )
    
    # Optional arguments (only added when included)
    if "companies" in include_set:
        parser.add_argument(
            "--companies",
            nargs="*",
            type=int,
            default=None,
            help="List of company indices to load (default: all), e.g. 1 2",
        )
    
    if "start_year" in include_set:
        parser.add_argument(
            "--start-year",
            type=int,
            default=None,
            help=(
                "Start year for partitioned resources. "
                "Can be an absolute year (e.g., 2023) or a negative number for years back "
                "(e.g., -0 = current year, -1 = last year, -3 = 3 years ago). "
                "Defaults to source default if not set."
            ),
        )


def create_base_parser(
    description: str = "DLT data pipeline",
    default_destination: str = "mssql",
    destinations: list[str] | None = None,
    exclude: list[str] | None = None,
    include: list[str] | None = None,
) -> argparse.ArgumentParser:
    """
    Create an argument parser with common dlt pipeline arguments pre-configured.
    
    Args:
        description: Description for the argument parser.
        default_destination: Default destination database (default: mssql).
        destinations: List of allowed destinations (default: ["duckdb", "mssql"]).
        exclude: List of argument names to exclude from core args.
            Valid names: debug, resources, destination, dev_mode, refresh, list_resources
        include: List of optional argument names to include.
            Valid names: companies, start_year
    
    Returns:
        ArgumentParser with common arguments already added.
    
    Example:
        # Basic usage
        parser = create_base_parser("My Pipeline")
        args = parser.parse_args()
        
        # With custom args and exclusions
        parser = create_base_parser(
            "My Pipeline",
            exclude=["dev_mode"],
            include=["companies", "start_year"],
        )
        parser.add_argument("--my-custom-arg", type=int, default=10)
        args = parser.parse_args()
    """
    parser = argparse.ArgumentParser(description=description)
    add_common_args(parser, default_destination, destinations, exclude, include)
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
        companies=getattr(args, "companies", None),
        start_year=getattr(args, "start_year", None),
    )


def resolve_start_year(start_year: int | None) -> int | None:
    """
    Resolve start_year argument to an absolute year.

    Supports both absolute years (e.g., 2023) and negative offsets
    (e.g., -0 = current year, -1 = last year, -3 = 3 years ago).

    Args:
        start_year: The start year argument from CLI. Can be:
            - None: Returns None (let the source use its default)
            - Positive int: Interpreted as absolute year
            - Zero or negative int: Interpreted as years back from current year
              (-0 = current year, -1 = last year, -2 = 2 years ago, etc.)

    Returns:
        Resolved absolute year, or None if not specified.
    
    Example:
        # Assuming current year is 2026
        resolve_start_year(None)   # Returns None
        resolve_start_year(2023)   # Returns 2023
        resolve_start_year(0)      # Returns 2026 (current year)
        resolve_start_year(-1)     # Returns 2025 (last year)
        resolve_start_year(-3)     # Returns 2023 (3 years ago)
    """
    if start_year is None:
        return None

    current_year = datetime.now(timezone.utc).year

    if start_year <= 0:
        # Negative or zero: interpret as years back
        # 0 = current year, -1 = last year, etc.
        resolved = current_year + start_year  # start_year is negative, so this subtracts
        logger.debug(
            f"Resolved start_year {start_year} to {resolved} (current year: {current_year})"
        )
        return resolved
    else:
        # Positive: interpret as absolute year
        return start_year


def filter_by_indices(
    items: list[T],
    indices: list[int] | None,
    item_name: str = "item",
) -> list[T]:
    """
    Filter a list of items by 1-based indices.
    
    If indices is None or empty, returns all items.
    
    Args:
        items: The list of items to filter.
        indices: List of 1-based indices to select, or None for all items.
        item_name: Name of the items for error messages (e.g., "company", "resource").
    
    Returns:
        Filtered list of items.
    
    Raises:
        ValueError: If no items are available or no valid indices are provided.
    
    Example:
        configs = [config1, config2, config3]
        
        # Select all
        filter_by_indices(configs, None)  # Returns [config1, config2, config3]
        
        # Select specific items
        filter_by_indices(configs, [1, 3])  # Returns [config1, config3]
        
        # With custom name for errors
        filter_by_indices(configs, [5], item_name="company")
        # Raises: ValueError: No valid companies. Available: 1-3
    """
    if not items:
        raise ValueError(f"No {item_name}s available.")
    
    if not indices:
        logger.info(f"Loading all {len(items)} {item_name}(s)")
        return items
    
    # Filter by 1-based indices
    selected = [
        items[i - 1]
        for i in indices
        if 0 < i <= len(items)
    ]
    
    if not selected:
        raise ValueError(
            f"No valid {item_name}s. Available: 1-{len(items)}"
        )
    
    # Log any invalid indices
    invalid = [i for i in indices if i < 1 or i > len(items)]
    if invalid:
        logger.warning(
            f"Ignored invalid {item_name} indices: {invalid}. "
            f"Valid range: 1-{len(items)}"
        )
    
    logger.info(f"Selected {item_name}(s): {indices}")
    return selected
