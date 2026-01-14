#!/usr/bin/env python3
"""
Trino Database Connection Module.
Provides functions to connect to Trino and execute queries.
"""

import os
import logging
from typing import Optional, Dict, Any

import pandas as pd
from trino import dbapi, auth

logger = logging.getLogger(__name__)


def get_connection_params() -> Dict[str, Any]:
    """Get Trino connection parameters from environment variables."""
    params = {
        'host': os.getenv('TRINO_HOST', 'localhost'),
        'port': int(os.getenv('TRINO_PORT', '8080')),
        'user': os.getenv('TRINO_USER', 'trino'),
        'catalog': os.getenv('TRINO_CATALOG', 'awsdatacatalog'),
        'schema': os.getenv('TRINO_DEFAULT_SCHEMA', 'default'),
        'http_scheme': os.getenv('TRINO_HTTP_SCHEME', 'https')
    }
    
    # Add authentication if password is provided
    password = os.getenv('TRINO_PASSWORD')
    if password:
        params['auth'] = auth.BasicAuthentication(params['user'], password)
    
    return params


def create_connection():
    """Create and return a Trino database connection."""
    try:
        params = get_connection_params()
        logger.info(f"Connecting to Trino at {params['host']}:{params['port']}")
        
        conn = dbapi.connect(
            host=params['host'],
            port=params['port'],
            user=params['user'],
            catalog=params['catalog'],
            schema=params['schema'],
            http_scheme=params['http_scheme'],
            auth=params.get('auth')
        )
        
        logger.info("Successfully connected to Trino")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to Trino: {str(e)}")
        
        # Try fallback host if configured
        fallback_host = os.getenv('TRINO_FALLBACK_HOST')
        if fallback_host and params['host'] != fallback_host:
            logger.info(f"Trying fallback host: {fallback_host}")
            params['host'] = fallback_host
            try:
                conn = dbapi.connect(
                    host=params['host'],
                    port=params['port'],
                    user=params['user'],
                    catalog=params['catalog'],
                    schema=params['schema'],
                    http_scheme=params['http_scheme'],
                    auth=params.get('auth')
                )
                logger.info("Successfully connected to Trino using fallback host")
                return conn
            except Exception as fallback_error:
                logger.error(f"Fallback connection also failed: {str(fallback_error)}")
                raise
        raise


def format_bytes(bytes_val: int) -> str:
    """Format bytes into human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


def execute_query_to_dataframe(
    query: str, 
    params: Optional[Dict] = None, 
    verbose: bool = True, 
    conn=None
) -> pd.DataFrame:
    """
    Execute a query and return results as a pandas DataFrame.
    
    Args:
        query: SQL query to execute
        params: Optional query parameters
        verbose: Whether to log detailed information
        conn: Optional existing connection to reuse
        
    Returns:
        pandas DataFrame containing query results
    """
    should_close_conn = False
    cursor = None
    try:
        if conn is None:
            conn = create_connection()
            should_close_conn = True
            
        cursor = conn.cursor()
        
        if verbose:
            logger.info(f"Executing query: {query[:100]}...")
        cursor.execute(query, params)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch results
        results = cursor.fetchall()
        if verbose:
            logger.info(f"Query returned {len(results)} rows")
        
        # Create DataFrame
        df = pd.DataFrame(results, columns=columns)
        return df
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if should_close_conn and conn:
            conn.close()


def execute_query_with_stats(
    query: str, 
    params: Optional[Dict] = None, 
    verbose: bool = True, 
    conn=None
) -> tuple:
    """
    Execute a query and return results with statistics.
    
    Args:
        query: SQL query to execute
        params: Optional query parameters
        verbose: Whether to log detailed information
        conn: Optional existing connection to reuse
        
    Returns:
        tuple: (DataFrame, stats_dict)
    """
    should_close_conn = False
    cursor = None
    try:
        if conn is None:
            conn = create_connection()
            should_close_conn = True
            
        cursor = conn.cursor()
        
        if verbose:
            logger.debug(f"Executing query: {query[:100]}...")
        cursor.execute(query, params)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch results
        results = cursor.fetchall()
        
        # Get query statistics
        stats = {
            'rows': len(results),
            'columns': len(columns),
            'data_scanned': 'N/A',
            'query_id': getattr(cursor, '_query_id', 'N/A'),
            'status': 'COMPLETED'
        }
        
        # Try to get stats from cursor
        if hasattr(cursor, 'stats'):
            cursor_stats = cursor.stats
            if cursor_stats:
                if 'processedBytes' in cursor_stats:
                    bytes_processed = cursor_stats['processedBytes']
                    stats['data_scanned'] = format_bytes(bytes_processed)
                elif 'rawInputDataSize' in cursor_stats:
                    bytes_processed = cursor_stats['rawInputDataSize']
                    stats['data_scanned'] = format_bytes(bytes_processed)
        
        if verbose:
            logger.debug(f"Query returned {len(results)} rows")
        
        df = pd.DataFrame(results, columns=columns)
        return df, stats
        
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if should_close_conn and conn:
            conn.close()


def get_table_info(table_name: str, schema: Optional[str] = None) -> pd.DataFrame:
    """
    Get column information for a specific table.
    
    Args:
        table_name: Name of the table
        schema: Schema name (uses default if not provided)
        
    Returns:
        DataFrame with column information
    """
    if not schema:
        schema = os.getenv('TRINO_DEFAULT_SCHEMA', 'default')
    
    catalog = os.getenv('TRINO_CATALOG', 'awsdatacatalog')
    
    query = f"""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns
        WHERE table_catalog = '{catalog}'
          AND table_schema = '{schema}'
          AND table_name = '{table_name}'
        ORDER BY ordinal_position
    """
    
    return execute_query_to_dataframe(query, verbose=False)


def list_schemas() -> pd.DataFrame:
    """List all available schemas in the catalog."""
    catalog = os.getenv('TRINO_CATALOG', 'awsdatacatalog')
    query = f"SHOW SCHEMAS FROM {catalog}"
    return execute_query_to_dataframe(query, verbose=False)


def list_tables(schema: Optional[str] = None) -> pd.DataFrame:
    """
    List all tables in a schema.
    
    Args:
        schema: Schema name (uses default if not provided)
        
    Returns:
        DataFrame with table names
    """
    if not schema:
        schema = os.getenv('TRINO_DEFAULT_SCHEMA', 'default')
    
    catalog = os.getenv('TRINO_CATALOG', 'awsdatacatalog')
    query = f"SHOW TABLES FROM {catalog}.{schema}"
    return execute_query_to_dataframe(query, verbose=False)
