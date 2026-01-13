"""
Trace visualization fields for Perplexity AI API.

This module handles extraction and validation of trace visualization fields
for distributed tracing and analytics.
"""
import os
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("revenium_middleware.perplexity.trace_fields")


def get_environment() -> Optional[str]:
    """
    Get the deployment environment.
    
    Checks REVENIUM_ENVIRONMENT first, falls back to NODE_ENV/PYTHON_ENV.
    
    Returns:
        Environment string (production, staging, development) or None
    """
    env = os.getenv("REVENIUM_ENVIRONMENT") or os.getenv("PYTHON_ENV") or os.getenv("NODE_ENV")
    if env:
        logger.debug(f"Environment detected: {env}")
    return env


def get_region() -> Optional[str]:
    """
    Get the cloud region.
    
    Checks REVENIUM_REGION first, falls back to AWS_REGION.
    
    Returns:
        Region string (e.g., us-east-1) or None
    """
    region = os.getenv("REVENIUM_REGION") or os.getenv("AWS_REGION")
    if region:
        logger.debug(f"Region detected: {region}")
    return region


def get_credential_alias() -> Optional[str]:
    """
    Get the credential alias for human-readable credential identification.
    
    Returns:
        Credential alias string or None
    """
    alias = os.getenv("REVENIUM_CREDENTIAL_ALIAS")
    if alias:
        logger.debug(f"Credential alias: {alias}")
    return alias


def get_trace_type() -> Optional[str]:
    """
    Get the trace type (categorical identifier).
    
    Returns:
        Trace type string (max 128 chars, alphanumeric/hyphens/underscores) or None
    """
    trace_type = os.getenv("REVENIUM_TRACE_TYPE")
    if trace_type:
        validated = validate_trace_type(trace_type)
        logger.debug(f"Trace type: {validated}")
        return validated
    return None


def get_trace_name() -> Optional[str]:
    """
    Get the trace name (human-readable label).
    
    Returns:
        Trace name string (max 256 chars) or None
    """
    trace_name = os.getenv("REVENIUM_TRACE_NAME")
    if trace_name:
        validated = validate_trace_name(trace_name)
        logger.debug(f"Trace name: {validated}")
        return validated
    return None


def get_parent_transaction_id() -> Optional[str]:
    """
    Get the parent transaction ID for distributed tracing.
    
    Returns:
        Parent transaction ID string or None
    """
    parent_id = os.getenv("REVENIUM_PARENT_TRANSACTION_ID")
    if parent_id:
        logger.debug(f"Parent transaction ID: {parent_id}")
    return parent_id


def get_transaction_name() -> Optional[str]:
    """
    Get the transaction name (human-friendly operation label).
    
    Returns:
        Transaction name string or None
    """
    txn_name = os.getenv("REVENIUM_TRANSACTION_NAME")
    if txn_name:
        logger.debug(f"Transaction name: {txn_name}")
    return txn_name


def get_retry_number() -> int:
    """
    Get the retry attempt number.
    
    Returns:
        Retry number (0 for first attempt, 1+ for retries)
    """
    retry = os.getenv("REVENIUM_RETRY_NUMBER", "0")
    try:
        retry_num = int(retry)
        logger.debug(f"Retry number: {retry_num}")
        return retry_num
    except ValueError:
        logger.warning(f"Invalid retry number '{retry}', defaulting to 0")
        return 0


def validate_trace_type(trace_type: str) -> str:
    """
    Validate and sanitize trace type.
    
    Trace type must be alphanumeric with hyphens/underscores, max 128 chars.
    
    Args:
        trace_type: Raw trace type string
        
    Returns:
        Validated trace type string
    """
    # Remove invalid characters
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', trace_type)
    # Truncate to 128 chars
    truncated = sanitized[:128]
    
    if truncated != trace_type:
        logger.warning(f"Trace type sanitized: '{trace_type}' -> '{truncated}'")
    
    return truncated


def validate_trace_name(trace_name: str) -> str:
    """
    Validate and sanitize trace name.
    
    Trace name is truncated to 256 chars.
    
    Args:
        trace_name: Raw trace name string
        
    Returns:
        Validated trace name string
    """
    truncated = trace_name[:256]
    
    if len(trace_name) > 256:
        logger.warning(f"Trace name truncated from {len(trace_name)} to 256 chars")
    
    return truncated

