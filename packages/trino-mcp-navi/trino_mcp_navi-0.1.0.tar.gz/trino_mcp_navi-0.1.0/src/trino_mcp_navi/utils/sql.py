#!/usr/bin/env python3
"""
SQL utilities for Trino MCP Server.
Handles query splitting and file execution.
"""

import logging

logger = logging.getLogger(__name__)


def split_queries(query_text: str) -> list:
    """
    Split multiple queries separated by semicolons.
    
    Args:
        query_text: SQL text containing one or more queries
        
    Returns:
        List of individual query strings
    """
    # Simple split by semicolon - remove empty queries
    queries = [q.strip() for q in query_text.split(';') if q.strip()]
    logger.debug(f"Split into {len(queries)} queries")
    return queries
