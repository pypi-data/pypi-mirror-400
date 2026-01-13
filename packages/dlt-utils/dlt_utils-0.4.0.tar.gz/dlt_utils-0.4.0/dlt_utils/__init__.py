"""
dlt_utils: Shared utilities for dlt data pipelines with multi-company support.

This package provides common utilities for building dlt pipelines that work with
multiple companies/tenants, including:

- PartitionedIncremental: State tracking per partition key
- Date utilities: Generate (year, week) and (year, month) sequences
- Schema utilities: Ensure database tables exist
- CLI argument parsing with standard arguments
- Logging configuration
- Pipeline helpers
"""

from .incremental import PartitionedIncremental
from .dates import (
    generate_year_months,
    generate_year_weeks,
)
from .schema import (
    ensure_all_tables_exist,
    ensure_tables_for_resources,
    get_tables_for_resources,
)
from .args import (
    add_common_args,
    create_base_parser,
    CommonArgs,
    filter_by_indices,
    resolve_start_year,
)
from .azure_keyvault import AzureKeyVault
from .logging import configure_logging
from .pipeline import (
    cleanup_tombstones,
    filter_resources,
    get_resource_names,
    mask_sensitive_value,
    print_resources,
    validate_refresh_args,
)


__version__ = "0.4.0"

__all__ = [
    # Incremental
    "PartitionedIncremental",
    # Dates
    "generate_year_months",
    "generate_year_weeks",
    # Schema
    "ensure_all_tables_exist",
    "ensure_tables_for_resources",
    "get_tables_for_resources",
    # args
    "add_common_args",
    "CommonArgs",
    "create_base_parser",
    "filter_by_indices",
    "resolve_start_year",
    # azure_keyvault
    "AzureKeyVault",
    # logging
    "configure_logging",
    # pipeline
    "cleanup_tombstones",
    "filter_resources",
    "get_resource_names",
    "mask_sensitive_value",
    "print_resources",
    "validate_refresh_args",
]
