#!/usr/bin/env python3
"""
Query utilities for Trino MCP Server.
Handles LIMIT injection for safe query testing.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Pre-compile regex patterns for performance
LIMIT_PATTERN = re.compile(r'\bLIMIT\s+\d+', re.IGNORECASE)
TRAILING_SEMICOLON = re.compile(r';\s*$')


def add_limit_to_query(query: str, limit: int = 50) -> str:
    """
    Add LIMIT clause to query if not already present.
    Skips queries that don't support LIMIT (SHOW, DESCRIBE, EXPLAIN, etc.)
    
    Args:
        query: SQL query string
        limit: Maximum rows to return (default: 50)
        
    Returns:
        Query with LIMIT clause added (if applicable)
    """
    # Remove trailing semicolon
    query = TRAILING_SEMICOLON.sub('', query.strip())
    
    # Check if LIMIT already exists
    if LIMIT_PATTERN.search(query):
        logger.debug("Query already has LIMIT clause")
        return query
    
    # Check if query type doesn't support LIMIT
    query_upper = query.upper().lstrip()
    skip_limit_keywords = [
        'SHOW', 'DESCRIBE', 'DESC', 'EXPLAIN', 
        'CREATE', 'DROP', 'ALTER', 
        'INSERT', 'UPDATE', 'DELETE', 
        'SET', 'USE'
    ]
    
    for keyword in skip_limit_keywords:
        if query_upper.startswith(keyword + ' ') or query_upper == keyword:
            logger.debug(f"Query type '{keyword}' doesn't support LIMIT - skipping")
            return query
    
    query_with_limit = f"{query}\nLIMIT {limit}"
    logger.debug(f"Added LIMIT {limit} to query for testing")
    return query_with_limit
