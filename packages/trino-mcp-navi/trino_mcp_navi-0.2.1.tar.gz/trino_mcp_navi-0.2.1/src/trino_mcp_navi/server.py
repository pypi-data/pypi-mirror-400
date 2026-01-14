#!/usr/bin/env python3
"""
Trino MCP Server
Exposes Trino database capabilities as a Model Context Protocol (MCP) server.
Allows AI assistants to query, analyze, and explore the database directly.

Supports both:
- stdio transport (local execution)
- SSE transport (remote/hosted execution)

Features:
- Schema/table exploration
- Smart table exploration (schema + sample in one call)
- Query execution with automatic LIMIT for testing
- Multi-query support (semicolon-separated)
- Export to CSV, Excel, JSON, Parquet
- Connection testing
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP

from trino_mcp_navi.connection import (
    execute_query_with_stats,
    create_connection,
    list_schemas,
    get_table_info,
)
from trino_mcp_navi.utils.sql import split_queries
from trino_mcp_navi.utils.query import add_limit_to_query
from trino_mcp_navi.analytics import track_tool_call, track_server_start, track_event

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr so stdout is kept clean for MCP
)
logger = logging.getLogger("trino-mcp-server")

# Initialize FastMCP server
mcp = FastMCP("trino")

# Output directory for saved results
OUTPUT_DIR = Path.home() / ".trino-mcp" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_catalog() -> str:
    """Get the configured Trino catalog."""
    return os.getenv('TRINO_CATALOG', 'awsdatacatalog')


@mcp.tool()
@track_tool_call("get_all_schemas")
def get_all_schemas() -> str:
    """
    List all available schemas in the Trino catalog.
    Useful for initial exploration to see what data is available.
    """
    try:
        df = list_schemas()
        return df.to_string(index=False)
    except Exception as e:
        return f"Error listing schemas: {str(e)}"


@mcp.tool()
@track_tool_call("get_tables_in_schema")
def get_tables_in_schema(schema_name: str) -> str:
    """
    List all tables within a specific schema.
    
    Args:
        schema_name: Name of the schema to explore
    """
    try:
        catalog = get_catalog()
        query = f"SHOW TABLES FROM {catalog}.{schema_name}"
        df, _ = execute_query_with_stats(query)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error listing tables in {schema_name}: {str(e)}"


@mcp.tool()
@track_tool_call("describe_table")
def describe_table(table_name: str, schema_name: str) -> str:
    """
    Get detailed column information (DDL) for a table.
    Use this to understand the table structure before querying.
    
    Args:
        table_name: Name of the table
        schema_name: Schema containing the table
    """
    try:
        df = get_table_info(table_name, schema_name)
        if df.empty:
            return f"No information found for table {schema_name}.{table_name}"
        return df.to_string(index=False)
    except Exception as e:
        return f"Error describing table {schema_name}.{table_name}: {str(e)}"


@mcp.tool()
@track_tool_call("test_connection")
def test_connection() -> str:
    """
    Test the Trino database connection.
    Use this to verify connectivity before running queries.
    Returns connection status and server info.
    """
    try:
        df, stats = execute_query_with_stats("SELECT 1 as test_value")
        if not df.empty and df.iloc[0]['test_value'] == 1:
            info_df, _ = execute_query_with_stats(
                "SELECT current_catalog as catalog, current_schema as schema"
            )
            catalog = info_df.iloc[0]['catalog'] if not info_df.empty else 'unknown'
            schema = info_df.iloc[0]['schema'] if not info_df.empty else 'unknown'
            
            return f"""✅ **Connection Successful!**

**Catalog:** {catalog}
**Schema:** {schema}
**Host:** {os.getenv('TRINO_HOST', 'unknown')}"""
        else:
            return "❌ Connection test returned unexpected result"
    except Exception as e:
        return f"❌ Connection failed: {str(e)}"


@mcp.tool()
@track_tool_call("explore_table")
def explore_table(table_name: str, schema_name: str, sample_rows: int = 5) -> str:
    """
    Smart table exploration - get schema AND sample data in one call.
    RECOMMENDED: Use this before writing queries for unfamiliar tables.
    
    Returns:
    - Column names and data types
    - Sample rows to understand actual data values
    - Row count estimate
    
    Args:
        table_name: Name of the table to explore
        schema_name: Schema containing the table
        sample_rows: Number of sample rows to fetch (default 5)
    """
    try:
        catalog = get_catalog()
        full_table = f"{catalog}.{schema_name}.{table_name}"
        results = []
        
        results.append(f"## Table: {full_table}\n")
        results.append("### Schema (Columns)")
        
        df_schema = get_table_info(table_name, schema_name)
        if not df_schema.empty:
            results.append(df_schema.to_markdown(index=False))
        else:
            results.append("Could not retrieve schema information.")
        
        results.append(f"\n### Sample Data ({sample_rows} rows)")
        sample_query = f"SELECT * FROM {full_table} LIMIT {sample_rows}"
        
        df_sample, stats = execute_query_with_stats(sample_query)
        if not df_sample.empty:
            results.append(df_sample.to_markdown(index=False))
            results.append(
                f"\n**Stats:** {stats.get('rows', 0)} rows returned | "
                f"Data scanned: {stats.get('data_scanned', 'N/A')}"
            )
        else:
            results.append("Table appears to be empty.")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Error exploring table {schema_name}.{table_name}: {str(e)}"


@mcp.tool()
@track_tool_call("test_query")
def test_query(query: str, limit: int = 50) -> str:
    """
    Quick test a query with automatic LIMIT.
    Use this for development/exploration - automatically adds LIMIT to prevent large result sets.
    Supports multiple queries separated by semicolons.
    
    Args:
        query: SQL query to test (can be multiple queries separated by ;)
        limit: Maximum rows to return (default 50)
    """
    try:
        queries = split_queries(query)
        if not queries:
            return "No valid queries found."
        
        results_output = []
        conn = None
        
        try:
            conn = create_connection()
            
            for i, single_query in enumerate(queries):
                limited_query = add_limit_to_query(single_query.strip(), limit)
                df, stats = execute_query_with_stats(limited_query, conn=conn)
                
                header = f"### Query {i+1} Results" if len(queries) > 1 else "### Results"
                stats_str = (
                    f"**Rows:** {stats.get('rows', 0)} | "
                    f"**Scanned:** {stats.get('data_scanned', 'N/A')} | "
                    f"**Time:** {stats.get('execution_time', 'N/A')}"
                )
                
                table_str = df.to_markdown(index=False) if not df.empty else "No results returned."
                results_output.append(f"{header}\n{stats_str}\n\n{table_str}")
            
            return "\n\n".join(results_output)
            
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        return f"Query test failed: {str(e)}"


@mcp.tool()
@track_tool_call("run_trino_query")
def run_trino_query(query: str, limit: int = 50) -> str:
    """
    Execute a SQL query against the Trino database.
    Supports multiple queries separated by semicolons.
    Automatically handles connection reuse for batch queries.
    
    Args:
        query: SQL query string (can be multiple queries separated by ;)
        limit: Max rows to return (default 50) - applied automatically if missing
    """
    try:
        queries = split_queries(query)
        
        if not queries:
            return "No valid queries found."
        
        results_output = []
        conn = None
        
        try:
            conn = create_connection()
            
            for i, single_query in enumerate(queries):
                final_query = single_query.strip()
                df, stats = execute_query_with_stats(final_query, conn=conn)
                
                header = f"### Query {i+1} Results" if len(queries) > 1 else "### Results"
                stats_str = (
                    f"**Rows:** {stats.get('rows', 0)} | "
                    f"**Scanned:** {stats.get('data_scanned', 'N/A')} | "
                    f"**Time:** {stats.get('execution_time', 'N/A')}"
                )
                
                table_str = (
                    df.head(limit).to_markdown(index=False) 
                    if not df.empty else "No results returned."
                )
                results_output.append(f"{header}\n{stats_str}\n\n{table_str}")
                
            return "\n\n".join(results_output)
            
        finally:
            if conn:
                conn.close()
                
    except Exception as e:
        return f"Query execution failed: {str(e)}"


@mcp.tool()
@track_tool_call("save_query_results")
def save_query_results(query: str, format: str = "csv", filename: str = None) -> str:
    """
    Execute a query and save results to a file.
    Use this for full query execution with export (no automatic LIMIT).
    
    Supported formats: csv, excel, json, parquet
    
    Args:
        query: SQL query to execute
        format: Output format - 'csv', 'excel', 'json', or 'parquet' (default: csv)
        filename: Optional custom filename (without extension). If not provided, auto-generated.
    """
    try:
        queries = split_queries(query)
        if not queries:
            return "No valid queries found."
        
        conn = None
        df = None
        stats = None
        
        try:
            conn = create_connection()
            for single_query in queries:
                df, stats = execute_query_with_stats(single_query.strip(), conn=conn)
        finally:
            if conn:
                conn.close()
        
        if df is None or df.empty:
            return "Query returned no results to save."
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = filename if filename else f"query_result_{timestamp}"
        
        format_lower = format.lower()
        if format_lower == "csv":
            file_path = OUTPUT_DIR / f"{base_name}.csv"
            df.to_csv(file_path, index=False)
        elif format_lower == "excel":
            file_path = OUTPUT_DIR / f"{base_name}.xlsx"
            df.to_excel(file_path, index=False, engine='openpyxl')
        elif format_lower == "json":
            file_path = OUTPUT_DIR / f"{base_name}.json"
            df.to_json(file_path, orient='records', indent=2)
        elif format_lower == "parquet":
            file_path = OUTPUT_DIR / f"{base_name}.parquet"
            df.to_parquet(file_path, index=False)
        else:
            return f"Unsupported format: {format}. Use: csv, excel, json, parquet"
        
        return f"""### Query Executed Successfully

**File saved:** `{file_path}`
**Format:** {format_lower.upper()}
**Rows:** {len(df)}
**Columns:** {len(df.columns)}
**Data scanned:** {stats.get('data_scanned', 'N/A')}

**Preview (first 5 rows):**

{df.head(5).to_markdown(index=False)}"""
        
    except Exception as e:
        return f"Failed to save query results: {str(e)}"


@mcp.tool()
@track_tool_call("execute_sql_file")
def execute_sql_file(file_path: str, format: str = None) -> str:
    """
    Execute a SQL file and optionally save results.
    
    Args:
        file_path: Path to the SQL file (absolute or relative)
        format: Optional output format to save results ('csv', 'excel', 'json', 'parquet'). 
                If not provided, just displays results.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"SQL file not found: {file_path}"
        
        sql_content = path.read_text()
        
        if format:
            base_name = path.stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{base_name}"
            return save_query_results(sql_content, format, filename)
        else:
            return run_trino_query(sql_content)
            
    except Exception as e:
        return f"Failed to execute SQL file: {str(e)}"


@mcp.tool()
@track_tool_call("search_catalog")
def search_catalog(
    search_term: str, 
    object_type: str = "both", 
    schema_filter: str = None
) -> str:
    """
    Search for tables or columns across all schemas in the catalog.
    Use this when you need to find "where is customer_id stored?" or "which tables contain user data?"
    
    ⚠️ PERFORMANCE WARNING: Without schema_filter, this searches ALL schemas and can be SLOW.
    RECOMMENDED: Always provide schema_filter for faster results.
    
    Args:
        search_term: Text to search for (case-insensitive, supports partial matching)
        object_type: What to search - 'table', 'column', or 'both' (default: both)
        schema_filter: Optional schema name to limit search (HIGHLY RECOMMENDED for performance)
    
    Returns:
        Matching tables and/or columns with their locations
    """
    try:
        catalog = get_catalog()
        results = []
        object_type_lower = object_type.lower()
        
        if not schema_filter:
            results.append(
                "⚠️ **Performance Warning:** Searching entire catalog. "
                "This may take 30-60 seconds."
            )
            results.append("**Tip:** Use `schema_filter` parameter for faster results.\n")
        
        # Search tables
        if object_type_lower in ['table', 'both']:
            table_query = f"""
                SELECT 
                    table_schema,
                    table_name,
                    table_type
                FROM information_schema.tables
                WHERE table_catalog = '{catalog}'
                  AND LOWER(table_name) LIKE LOWER('%{search_term}%')
            """
            if schema_filter:
                table_query += f" AND table_schema = '{schema_filter}'"
            else:
                table_query += " AND table_schema NOT IN ('information_schema', 'sys')"
            table_query += " ORDER BY table_schema, table_name LIMIT 100"
            
            df_tables, stats = execute_query_with_stats(table_query)
            if not df_tables.empty:
                results.append(
                    f"### 📋 Tables matching '{search_term}' ({len(df_tables)} found)"
                )
                results.append(df_tables.to_markdown(index=False))
                if not schema_filter:
                    results.append(f"\n_Query time: {stats.get('execution_time', 'N/A')}_")
        
        # Search columns
        if object_type_lower in ['column', 'both']:
            if not schema_filter and object_type_lower == 'both':
                results.append(f"\n### ⚠️ Column Search Skipped")
                results.append(
                    "Column search across entire catalog is too slow without `schema_filter`."
                )
                results.append(
                    "**Please specify a schema** to search columns."
                )
            else:
                column_query = f"""
                    SELECT 
                        table_schema,
                        table_name,
                        column_name,
                        data_type
                    FROM information_schema.columns
                    WHERE table_catalog = '{catalog}'
                      AND LOWER(column_name) LIKE LOWER('%{search_term}%')
                """
                if schema_filter:
                    column_query += f" AND table_schema = '{schema_filter}'"
                else:
                    column_query += " AND table_schema NOT IN ('information_schema', 'sys')"
                column_query += " ORDER BY table_schema, table_name, ordinal_position LIMIT 200"
                
                df_columns, stats = execute_query_with_stats(column_query)
                if not df_columns.empty:
                    results.append(
                        f"\n### 📊 Columns matching '{search_term}' ({len(df_columns)} found)"
                    )
                    results.append(df_columns.to_markdown(index=False))
        
        if not results or (len(results) == 2 and "Performance Warning" in results[0]):
            return f"No tables or columns found matching '{search_term}'"
        
        return "\n\n".join(results)
        
    except Exception as e:
        return f"Search failed: {str(e)}"


@mcp.tool()
@track_tool_call("profile_column")
def profile_column(table_name: str, column_name: str, schema_name: str) -> str:
    """
    Perform data quality profiling on a specific column.
    Returns: null %, distinct count, min/max, top 5 values.
    Use this to understand data quality before analysis.
    
    Args:
        table_name: Name of the table
        column_name: Name of the column to profile
        schema_name: Schema containing the table
    """
    try:
        catalog = get_catalog()
        full_table = f"{catalog}.{schema_name}.{table_name}"
        results = []
        
        results.append(f"## Column Profile: {full_table}.{column_name}\n")
        
        stats_query = f"""
            SELECT
                COUNT(*) as total_rows,
                COUNT({column_name}) as non_null_rows,
                COUNT(*) - COUNT({column_name}) as null_rows,
                ROUND(100.0 * (COUNT(*) - COUNT({column_name})) / COUNT(*), 2) as null_percentage,
                COUNT(DISTINCT {column_name}) as distinct_values
            FROM {full_table}
        """
        
        df_stats, _ = execute_query_with_stats(stats_query)
        if not df_stats.empty:
            results.append("### 📊 Basic Statistics")
            results.append(df_stats.to_markdown(index=False))
        
        # Min/Max
        try:
            minmax_query = f"""
                SELECT
                    MIN({column_name}) as min_value,
                    MAX({column_name}) as max_value
                FROM {full_table}
                WHERE {column_name} IS NOT NULL
            """
            df_minmax, _ = execute_query_with_stats(minmax_query)
            if not df_minmax.empty:
                results.append("\n### 📈 Range")
                results.append(df_minmax.to_markdown(index=False))
        except:
            pass
        
        # Top 5 values
        top_query = f"""
            SELECT
                {column_name} as value,
                COUNT(*) as frequency,
                ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM {full_table}), 2) as percentage
            FROM {full_table}
            WHERE {column_name} IS NOT NULL
            GROUP BY {column_name}
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """
        df_top, _ = execute_query_with_stats(top_query)
        if not df_top.empty:
            results.append("\n### 🔝 Top 5 Most Frequent Values")
            results.append(df_top.to_markdown(index=False))
        
        return "\n\n".join(results)
        
    except Exception as e:
        return f"Column profiling failed: {str(e)}"


@mcp.tool()
@track_tool_call("profile_table")
def profile_table(table_name: str, schema_name: str) -> str:
    """
    Perform data quality profiling on an entire table.
    Returns: row count, column count, null % for each column, data completeness.
    Use this for a quick health check of a table.
    
    Args:
        table_name: Name of the table
        schema_name: Schema containing the table
    """
    try:
        catalog = get_catalog()
        full_table = f"{catalog}.{schema_name}.{table_name}"
        results = []
        
        results.append(f"## Table Profile: {full_table}\n")
        
        row_count_query = f"SELECT COUNT(*) as row_count FROM {full_table}"
        df_rows, _ = execute_query_with_stats(row_count_query)
        row_count = df_rows.iloc[0]['row_count'] if not df_rows.empty else 0
        
        df_schema = get_table_info(table_name, schema_name)
        col_count = len(df_schema) if not df_schema.empty else 0
        
        results.append(f"**Total Rows:** {row_count:,}")
        results.append(f"**Total Columns:** {col_count}\n")
        
        if not df_schema.empty:
            columns = df_schema['column_name'].head(20).tolist()
            null_checks = []
            
            for col in columns:
                null_checks.append(f"COUNT(*) - COUNT({col}) as null_{col}")
            
            null_query = f"SELECT {', '.join(null_checks)} FROM {full_table}"
            df_nulls, _ = execute_query_with_stats(null_query)
            
            if not df_nulls.empty:
                null_data = []
                for col in columns:
                    null_count = df_nulls.iloc[0][f'null_{col}']
                    null_pct = round(100.0 * null_count / row_count, 2) if row_count > 0 else 0
                    null_data.append({
                        'column_name': col,
                        'null_count': null_count,
                        'null_percentage': null_pct
                    })
                
                df_null_summary = pd.DataFrame(null_data)
                results.append("### 🔍 Null Analysis (First 20 Columns)")
                results.append(df_null_summary.to_markdown(index=False))
        
        return "\n\n".join(results)
        
    except Exception as e:
        return f"Table profiling failed: {str(e)}"


@mcp.tool()
@track_tool_call("get_table_stats")
def get_table_stats(
    table_name: str, 
    schema_name: str, 
    sample_distinct: int = 25
) -> str:
    """
    Advanced table statistics with partition detection and column distinct value analysis.
    Returns comprehensive metadata about table structure, partitions, and data distribution.
    
    Use this to understand:
    - Partition keys and active partitions (crucial for query optimization)
    - Distinct value counts and samples for each column
    - Data distribution patterns
    
    Args:
        table_name: Name of the table
        schema_name: Schema containing the table
        sample_distinct: Number of distinct values to fetch per column (default 25)
    """
    try:
        catalog = get_catalog()
        full_table = f"{catalog}.{schema_name}.{table_name}"
        results = []
        
        results.append(f"## Advanced Table Statistics: {full_table}\n")
        
        describe_query = f"DESCRIBE {full_table}"
        df_describe, _ = execute_query_with_stats(describe_query)
        
        if df_describe.empty:
            return f"Could not retrieve schema for {full_table}"
        
        partition_cols = []
        if 'Extra' in df_describe.columns:
            partition_cols = df_describe[
                df_describe['Extra'].str.contains('partition', case=False, na=False)
            ]['Column'].tolist()
        
        if partition_cols:
            results.append(f"### 🗂️ Partition Information")
            results.append(f"**Partition Keys:** {', '.join(partition_cols)}\n")
            
            try:
                partition_col = partition_cols[0]
                partition_query = f"""
                    SELECT DISTINCT {partition_col}
                    FROM {full_table}
                    ORDER BY {partition_col} DESC
                    LIMIT 10
                """
                df_partitions, _ = execute_query_with_stats(partition_query)
                if not df_partitions.empty:
                    results.append(
                        f"**Active Partitions (Top 10 for '{partition_col}'):**"
                    )
                    results.append(
                        ", ".join([str(v) for v in df_partitions[partition_col].tolist()])
                    )
                    results.append("")
            except Exception as e:
                results.append(f"Could not fetch partition values: {str(e)}\n")
        else:
            results.append("### 🗂️ Partition Information")
            results.append("**No partitions detected** (table is not partitioned)\n")
        
        try:
            count_query = f"SELECT COUNT(*) as total_rows FROM {full_table}"
            df_count, _ = execute_query_with_stats(count_query)
            total_rows = df_count.iloc[0]['total_rows'] if not df_count.empty else 0
            results.append(f"### 📊 Table Size")
            results.append(f"**Total Rows:** {total_rows:,}\n")
        except:
            total_rows = 0
        
        results.append(f"### 🔍 Column Distribution Analysis (Top 15 columns)\n")
        
        df_columns = df_describe[
            ~df_describe['Column'].str.contains('_hoodie_|__', case=False, na=False)
        ].head(15)
        
        column_stats = []
        for _, row in df_columns.iterrows():
            col_name = row['Column']
            col_type = row['Type']
            
            try:
                distinct_query = (
                    f"SELECT COUNT(DISTINCT {col_name}) as distinct_count "
                    f"FROM {full_table}"
                )
                df_distinct, _ = execute_query_with_stats(distinct_query)
                distinct_count = (
                    df_distinct.iloc[0]['distinct_count'] 
                    if not df_distinct.empty else 0
                )
                
                sample_query = (
                    f"SELECT DISTINCT {col_name} FROM {full_table} "
                    f"WHERE {col_name} IS NOT NULL LIMIT {sample_distinct}"
                )
                df_sample, _ = execute_query_with_stats(sample_query)
                
                sample_values = []
                if not df_sample.empty:
                    sample_values = [str(v) for v in df_sample[col_name].tolist()[:10]]
                
                column_stats.append({
                    'column_name': col_name,
                    'data_type': col_type,
                    'distinct_count': distinct_count,
                    'sample_values': ', '.join(sample_values) if sample_values else 'N/A'
                })
                
            except Exception as e:
                column_stats.append({
                    'column_name': col_name,
                    'data_type': col_type,
                    'distinct_count': 'Error',
                    'sample_values': f'Could not analyze: {str(e)[:50]}'
                })
        
        if column_stats:
            df_stats = pd.DataFrame(column_stats)
            results.append(df_stats.to_markdown(index=False))
        
        results.append(
            f"\n**Note:** Analysis limited to 15 columns. "
            f"Use `profile_column` for detailed analysis of specific columns."
        )
        
        return "\n\n".join(results)
        
    except Exception as e:
        return f"Table statistics failed: {str(e)}"


@mcp.tool()
@track_tool_call("get_frequent_queries")
def get_frequent_queries(
    table_name: str, 
    schema_name: str = None, 
    days_back: int = 60, 
    limit: int = 5
) -> str:
    """
    Analyze query logs to find the most frequently run queries against a table.
    Shows "social proof" - how other team members actually use this table.
    
    IMPORTANT: Requires access to data_platform.trino_generic_logs_tbl
    
    Args:
        table_name: Name of the table to analyze
        schema_name: Optional schema name (if not provided, searches across all schemas)
        days_back: How many days of query history to analyze (default 60)
        limit: Number of top queries to return (default 5)
    
    Returns:
        Most common query patterns with execution counts
    """
    try:
        if schema_name:
            search_pattern = f"{schema_name}.{table_name}"
        else:
            search_pattern = table_name
        
        log_query = f"""
            SELECT 
                COALESCE(
                    regexp_extract(query, '(?is)(SELECT.*|WITH.*)', 1),
                    query
                ) as query_text,
                COUNT(*) as execution_count,
                COUNT(DISTINCT "user") as unique_users
            FROM data_platform.trino_generic_logs_tbl
            WHERE date(date_parse(p_create_time_dt, '%Y%m%d')) >= date_add('day', -{days_back}, current_date)
                AND query_state = 'FINISHED'
                AND failure_info IS NULL
                AND LOWER(query) LIKE '%{search_pattern.lower()}%'
                AND LOWER(query) NOT LIKE '%athena_daily_stats%'
                AND LOWER(query) NOT LIKE '%analysis.%'
                AND LENGTH(COALESCE(
                    regexp_extract(query, '(?is)(SELECT.*|WITH.*)', 1),
                    query
                )) >= 100
            GROUP BY 1
            ORDER BY execution_count DESC
            LIMIT {limit}
        """
        
        df, _ = execute_query_with_stats(log_query)
        
        if df.empty:
            return f"""### 📊 Query Usage Analysis for {search_pattern}

**No query patterns found** in the last {days_back} days.

This could mean:
- The table is newly created
- The table is rarely used
- Access to query logs is restricted

**Tip:** Try without schema_name to search across all schemas."""
        
        results = []
        results.append(f"### 📊 Top {len(df)} Query Patterns for {search_pattern}")
        results.append(f"**Analysis Period:** Last {days_back} days")
        results.append(f"**Total Patterns Found:** {len(df)}\n")
        
        for idx, row in df.iterrows():
            query_text = row['query_text']
            exec_count = row['execution_count']
            users = row['unique_users']
            
            if len(query_text) > 500:
                query_display = query_text[:500] + "..."
            else:
                query_display = query_text
            
            results.append(f"#### Query Pattern #{idx + 1}")
            results.append(f"**Executed:** {exec_count} times by {users} user(s)")
            results.append(f"```sql\n{query_display}\n```")
            results.append("")
        
        results.append("\n**Tip:** Copy these queries as templates for your own analysis.")
        
        return "\n\n".join(results)
        
    except Exception as e:
        error_msg = str(e)
        if "data_platform.trino_generic_logs_tbl" in error_msg or "does not exist" in error_msg.lower():
            return f"""### ❌ Query Logs Not Accessible

The query log table (`data_platform.trino_generic_logs_tbl`) is not accessible.

**Possible reasons:**
- The table doesn't exist in your Trino environment
- You don't have permissions to access query logs

**Error:** {error_msg}"""
        else:
            return f"Query analysis failed: {error_msg}"


@mcp.tool()
@track_tool_call("check_encryption")
def check_encryption(table_name: str, schema_name: str) -> str:
    """
    Check if a table has encrypted columns and retrieve encryption configuration.
    Essential for compliance and understanding data security requirements.
    
    Args:
        table_name: Name of the table
        schema_name: Schema containing the table (also known as service_name in encryption mapping)
    
    Returns:
        Encryption configuration and entity mapping details
    """
    try:
        encryption_query = f"""
            SELECT 
                entity_name,
                encryption_config
            FROM taurus.all_table_and_entity_mapping_view
            WHERE LOWER(service_name) = LOWER('{schema_name}')
                AND LOWER(table_name) = LOWER('{table_name}')
        """
        
        df, _ = execute_query_with_stats(encryption_query)
        
        if df.empty:
            return f"""### 🔓 Encryption Status for {schema_name}.{table_name}

**Status:** No encryption configuration found

This means either:
- The table does not have encrypted columns
- The table is not registered in the encryption mapping system
- The encryption metadata table is not accessible"""
        
        results = []
        results.append(f"### 🔐 Encryption Configuration for {schema_name}.{table_name}\n")
        results.append(f"**Total Encrypted Entities:** {len(df)}\n")
        results.append(df.to_markdown(index=False))
        results.append(f"\n**Decryption Function:**")
        results.append("```sql")
        
        for _, row in df.iterrows():
            entity_name = row['entity_name']
            results.append(f"-- For entity '{entity_name}':")
            results.append(f"entity_decrypt(column_name, '{entity_name}', 'COL', '')")
        
        results.append("```")
        
        return "\n\n".join(results)
        
    except Exception as e:
        error_msg = str(e)
        if "taurus.all_table_and_entity_mapping_view" in error_msg or "does not exist" in error_msg.lower():
            return f"""### ❌ Encryption Metadata Not Accessible

The encryption mapping table is not accessible.

**Possible reasons:**
- The table doesn't exist in your Trino environment
- You don't have permissions to access encryption metadata

**Error:** {error_msg}"""
        else:
            return f"Encryption check failed: {error_msg}"


@mcp.tool()
@track_tool_call("explain_query")
def explain_query(query: str, analyze: bool = False) -> str:
    """
    Analyze query performance and execution plan.
    Use this BEFORE running expensive queries to optimize them.
    
    Args:
        query: SQL query to explain
        analyze: If True, uses EXPLAIN ANALYZE (actually runs the query). Default: False
    
    Returns:
        Query execution plan with cost estimates
    """
    try:
        explain_cmd = "EXPLAIN ANALYZE" if analyze else "EXPLAIN"
        explain_query_text = f"{explain_cmd} {query.strip()}"
        
        df, stats = execute_query_with_stats(explain_query_text)
        
        if df.empty:
            return "No execution plan returned"
        
        results = []
        title = (
            '⚡ Query Execution Analysis (with actual run)' 
            if analyze else '📊 Query Execution Plan (estimate)'
        )
        results.append(f"### {title}\n")
        results.append(f"**Data scanned:** {stats.get('data_scanned', 'N/A')}")
        results.append(f"**Execution time:** {stats.get('execution_time', 'N/A')}\n")
        results.append("### Execution Plan")
        
        if 'Query Plan' in df.columns:
            for line in df['Query Plan']:
                results.append(line)
        else:
            results.append(df.to_string(index=False))
        
        return "\n".join(results)
        
    except Exception as e:
        return f"Query explanation failed: {str(e)}"


@mcp.tool()
@track_tool_call("get_table_ddl")
def get_table_ddl(table_name: str, schema_name: str) -> str:
    """
    Get the CREATE TABLE statement (DDL) for a table.
    Use this to understand partitioning, format, and full schema definition.
    
    Args:
        table_name: Name of the table
        schema_name: Schema containing the table
    """
    try:
        catalog = get_catalog()
        full_table = f"{catalog}.{schema_name}.{table_name}"
        
        ddl_query = f"SHOW CREATE TABLE {full_table}"
        df, _ = execute_query_with_stats(ddl_query)
        
        if df.empty:
            return f"Could not retrieve DDL for {full_table}"
        
        ddl_col = df.columns[0]
        ddl_text = df.iloc[0][ddl_col]
        
        return f"""### DDL for {full_table}

```sql
{ddl_text}
```"""
        
    except Exception as e:
        return f"Failed to get DDL: {str(e)}"


@mcp.tool()
@track_tool_call("get_query_history")
def get_query_history(limit: int = 10, user_filter: str = None) -> str:
    """
    Retrieve recent query history from system tables.
    Use this to find queries you ran earlier or see what others are running.
    
    Args:
        limit: Number of recent queries to return (default: 10, max: 50)
        user_filter: Optional username to filter by (default: current user)
    
    Returns:
        Recent queries with execution stats
    """
    try:
        limit = min(limit, 50)
        current_user = os.getenv('TRINO_USER', 'unknown')
        filter_user = user_filter if user_filter else current_user
        
        history_query = f"""
            SELECT
                query_id,
                "user",
                state,
                query,
                format_datetime(created, 'yyyy-MM-dd HH:mm:ss') as executed_at,
                format_datetime("end", 'yyyy-MM-dd HH:mm:ss') as completed_at,
                date_diff('second', created, "end") as duration_seconds
            FROM system.runtime.queries
            WHERE "user" = '{filter_user}'
              AND query NOT LIKE '%system.runtime.queries%'
            ORDER BY created DESC
            LIMIT {limit}
        """
        
        df, _ = execute_query_with_stats(history_query)
        
        if df.empty:
            return f"No query history found for user: {filter_user}"
        
        return f"""### 🕒 Recent Queries for {filter_user} (Last {len(df)})

{df.to_markdown(index=False)}

**Tip:** Copy a query_id and use it with Trino's query detail views for more info."""
        
    except Exception as e:
        return f"Query history not available: {str(e)}\n\nNote: This requires access to system.runtime.queries table."


@mcp.tool()
@track_tool_call("compare_tables")
def compare_tables(
    table1: str, 
    table2: str, 
    schema1: str = None, 
    schema2: str = None
) -> str:
    """
    Compare the schemas of two tables.
    Use this to spot differences between prod/staging or after migrations.
    
    Args:
        table1: First table name
        table2: Second table name
        schema1: Schema for table1 (if None, uses table1 as schema.table format)
        schema2: Schema for table2 (if None, uses table2 as schema.table format)
    
    Returns:
        Side-by-side comparison showing differences
    """
    try:
        # Parse table names if they include schema
        if '.' in table1 and not schema1:
            parts = table1.split('.')
            schema1, table1 = parts[0], parts[1]
        if '.' in table2 and not schema2:
            parts = table2.split('.')
            schema2, table2 = parts[0], parts[1]
        
        if not schema1 or not schema2:
            return "Please provide schema names for both tables"
        
        df1 = get_table_info(table1, schema1)
        df2 = get_table_info(table2, schema2)
        
        if df1.empty:
            return f"Table {schema1}.{table1} not found"
        if df2.empty:
            return f"Table {schema2}.{table2} not found"
        
        results = []
        results.append(f"## Schema Comparison\n")
        results.append(f"**Table 1:** {schema1}.{table1} ({len(df1)} columns)")
        results.append(f"**Table 2:** {schema2}.{table2} ({len(df2)} columns)\n")
        
        cols1 = set(df1['column_name'])
        cols2 = set(df2['column_name'])
        
        only_in_1 = cols1 - cols2
        only_in_2 = cols2 - cols1
        common = cols1 & cols2
        
        if only_in_1:
            results.append(
                f"### ➖ Columns only in {schema1}.{table1} ({len(only_in_1)})"
            )
            results.append(", ".join(sorted(only_in_1)))
        
        if only_in_2:
            results.append(
                f"\n### ➕ Columns only in {schema2}.{table2} ({len(only_in_2)})"
            )
            results.append(", ".join(sorted(only_in_2)))
        
        type_diffs = []
        for col in common:
            type1 = df1[df1['column_name'] == col]['data_type'].iloc[0]
            type2 = df2[df2['column_name'] == col]['data_type'].iloc[0]
            if type1 != type2:
                type_diffs.append({
                    'column': col,
                    f'{schema1}.{table1}': type1,
                    f'{schema2}.{table2}': type2
                })
        
        if type_diffs:
            results.append(f"\n### ⚠️ Type Mismatches ({len(type_diffs)})")
            df_diffs = pd.DataFrame(type_diffs)
            results.append(df_diffs.to_markdown(index=False))
        
        if not only_in_1 and not only_in_2 and not type_diffs:
            results.append("\n### ✅ Tables are identical")
        
        return "\n\n".join(results)
        
    except Exception as e:
        return f"Table comparison failed: {str(e)}"


def main():
    """Entry point for the MCP server."""
    # Track server start
    track_server_start()
    
    # Check for transport mode from environment or command line
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    if transport == "sse":
        # SSE transport for remote hosting
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        logger.info(f"Starting MCP server with SSE transport on {host}:{port}")
        mcp.run(transport="sse", host=host, port=port)
    else:
        # Default stdio transport for local execution
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
