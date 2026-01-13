"""
Pipeline helper utilities for dlt pipelines.

This module provides common functionality for running dlt pipelines.

Usage:
    from dlt_utils import validate_refresh_args, filter_resources, print_resources
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)


def validate_refresh_args(
    refresh: str | None,
    resources_filter: list[str] | None,
) -> None:
    """
    Validate that refresh arguments are used correctly.
    
    Raises ValueError if drop_sources is used with a resource filter,
    as this would drop ALL tables but only reload selected resources.
    
    Args:
        refresh: The refresh mode ('drop_sources' or 'drop_resources').
        resources_filter: List of resources being loaded (None = all).
        
    Raises:
        ValueError: If drop_sources is used with a resource filter.
    """
    if refresh == "drop_sources" and resources_filter:
        raise ValueError(
            f"--refresh drop_sources cannot be used with --resources filter. "
            f"This would drop ALL tables but only reload selected resources. "
            f"Use --refresh drop_resources to only drop and rebuild specific resources, "
            f"or remove --resources to do a full rebuild of all resources."
        )


def filter_resources(
    available_resources: list[str],
    requested_resources: list[str] | None,
) -> list[str]:
    """
    Filter available resources based on requested resources.
    
    Args:
        available_resources: List of all available resource names.
        requested_resources: List of requested resources (None = all).
        
    Returns:
        List of valid resources to load.
        
    Raises:
        ValueError: If no valid resources are found.
    """
    if requested_resources is None:
        return available_resources
    
    valid_resources = [r for r in requested_resources if r in available_resources]
    
    if not valid_resources:
        raise ValueError(
            f"No valid resources found. "
            f"Requested: {requested_resources}. "
            f"Available: {available_resources}"
        )
    
    # Log any requested resources that weren't found
    invalid = set(requested_resources) - set(valid_resources)
    if invalid:
        logger.warning(f"Ignored invalid resources: {invalid}")
    
    return valid_resources


def print_resources(source: Any) -> None:
    """
    Print available resources from a dlt source and exit.
    
    Args:
        source: A dlt source object with a resources attribute.
    """
    available_resources = sorted(get_resource_names(source))
    
    print("\nAvailable resources:")
    print("-" * 40)
    for resource in available_resources:
        print(f"  - {resource}")
    print("-" * 40)
    print(f"\nTotal: {len(available_resources)} resources")


def get_resource_names(source: Any) -> list[str]:
    """
    Get list of resource names from a dlt source.
    
    Args:
        source: A dlt source object with a resources attribute.
        
    Returns:
        List of resource names.
    """
    return [r.name for r in source.resources.values()]


def mask_sensitive_value(value: str | None, show_chars: int = 2) -> str:
    """
    Mask a sensitive value (like API key) showing only first and middle characters.
    
    Args:
        value: The value to mask.
        show_chars: Number of characters to show at start and middle.
        
    Returns:
        Masked value like "ab..cd..***" or "N/A" if not set.
    """
    if not value:
        return "N/A"
    
    if len(value) < 6:
        return value[:1] + "***"
    
    mid = len(value) // 2
    return f"{value[:show_chars]}..{value[mid:mid+show_chars]}..***"


def cleanup_tombstones(
    pipeline: Any,
    resources: list[str],
    column_name: str = "_tt_is_tombstone",
) -> None:
    """
    Clean up tombstone records from tables after a successful pipeline run.
    
    Tombstones are placeholder records used to ensure delete-insert semantics
    work correctly for partitions that have no real data. After the pipeline
    completes, these tombstone records should be removed.
    
    Args:
        pipeline: A dlt pipeline object with sql_client() method.
        resources: List of resource/table names to clean tombstones from.
        column_name: The boolean column name that marks tombstone records.
                     Defaults to "_tt_is_tombstone".
    
    Example:
        # Clean up tombstones from all resources except 'customer'
        tombstone_resources = [r for r in sync_resources if r != "customer"]
        cleanup_tombstones(pipeline, tombstone_resources)
        
        # Clean up with a custom column name
        cleanup_tombstones(pipeline, ["my_table"], column_name="is_tombstone")
    """
    if not resources:
        logger.debug("No resources provided for tombstone cleanup")
        return
    
    with pipeline.sql_client() as sql_client:
        for resource_name in resources:
            table_name = sql_client.make_qualified_table_name(resource_name)
            delete_query = f"DELETE FROM {table_name} WHERE {column_name} = TRUE"
            
            try:
                sql_client.execute_sql(delete_query)
                logger.info(f"Cleaned up tombstone records from {table_name}")
            except Exception as e:
                # Table might not exist on first run or if resource wasn't selected
                logger.warning(
                    f"Could not clean tombstones from {table_name}: {e}"
                )
