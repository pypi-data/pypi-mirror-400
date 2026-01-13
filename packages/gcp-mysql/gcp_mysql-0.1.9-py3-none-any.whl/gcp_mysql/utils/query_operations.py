# src/gcp_mysql/utils/query_operations.py

import logging
import os
from typing import (
    Any, 
    Dict, 
    Optional, 
    Sequence, 
    Tuple
)

logger = logging.getLogger(__name__)


def _contains_drop_statement(sql: str) -> bool:
    """
    Conservative check for DROP statements.
    Blocks obvious destructive operations without full SQL parsing.
    """
    tokens = sql.upper().replace("\n", " ").split()
    return "DROP" in tokens


def execute_query(
    self,
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> list[Dict[str, Any]]:
    """
    Execute a SQL query (SELECT, CREATE, UPDATE, etc.).

    Returns:
        list of dicts for queries that return rows, otherwise empty list.
    """
    if not query or not query.strip():
        raise ValueError("Query must be a non-empty string")

    if _contains_drop_statement(query):
        raise ValueError("DROP statements are not allowed for safety")

    logger.debug("Executing query (first 100 chars): %s", query[:100])

    try:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params) if params else cur.execute(query)

                # If cursor.description is set, the query returned rows
                if cur.description is not None:
                    results = cur.fetchall()
                    logger.info("Query returned %d row(s)", len(results))
                    return results

                logger.info("Query executed successfully (no result set)")
                return []
    except Exception:
        logger.exception("Failed to execute query")
        raise


def insert(
    self,
    table_name: str,
    data: Dict[str, Any],
) -> int:
    """
    Insert a single row into a table.

    Returns:
        The auto-increment ID if available, otherwise 0.
    """
    if not data:
        raise ValueError("Data dictionary cannot be empty")

    columns = list(data.keys())
    values = tuple(data.values())

    column_names = ", ".join(f"`{col}`" for col in columns)
    placeholders = ", ".join(["%s"] * len(columns))

    query = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"

    logger.debug("Inserting into %s columns=%s", table_name, columns)

    try:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, values)
                return int(cur.lastrowid or 0)
    except Exception:
        logger.exception("Failed to insert row into %s", table_name)
        raise


def insert_from_file(
    self,
    table_name: str,
    file_path: str,
    columns: Optional[Sequence[str]] = None,
    fields_terminated_by: str = ",",
    fields_enclosed_by: Optional[str] = '"',
    fields_escaped_by: Optional[str] = None,
    lines_terminated_by: str = "\n",
    ignore_lines: int = 0,
    field_overrides: Optional[Dict[str, Any]] = None,
    replace: bool = False,
    ignore_duplicates: bool = False,
) -> int:
    """
    Load data from a local file using LOAD DATA LOCAL INFILE.
    """
    if not self.local_infile:
        raise RuntimeError("local_infile must be enabled on MySQLService")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(file_path)

    abs_file_path = os.path.abspath(file_path)
    escaped_file_path = abs_file_path.replace("\\", "\\\\").replace("'", "\\'")

    action = "REPLACE" if replace else ("IGNORE" if ignore_duplicates else "")
    column_clause = f"({', '.join(f'`{c}`' for c in columns)})" if columns else ""

    set_clause = ""
    if field_overrides:
        parts = []
        for k, v in field_overrides.items():
            if v is None:
                parts.append(f"`{k}` = NULL")
            elif isinstance(v, (int, float)):
                parts.append(f"`{k}` = {v}")
            elif isinstance(v, str) and v.upper() in {"CURRENT_TIMESTAMP", "NOW()"}:
                parts.append(f"`{k}` = {v}")
            else:
                escaped = str(v).replace("\\", "\\\\").replace("'", "\\'")
                parts.append(f"`{k}` = '{escaped}'")
        set_clause = f"SET {', '.join(parts)}"

    fields_clause = f"TERMINATED BY '{fields_terminated_by}'"
    if fields_enclosed_by:
        fields_clause += f" OPTIONALLY ENCLOSED BY '{fields_enclosed_by}'"

    query = f"""
        LOAD DATA LOCAL INFILE '{escaped_file_path}'
        {action}
        INTO TABLE `{table_name}`
        FIELDS {fields_clause}
        LINES TERMINATED BY '{lines_terminated_by}'
        IGNORE {ignore_lines} LINES
        {column_clause}
        {set_clause}
    """

    logger.debug("Executing LOAD DATA LOCAL INFILE:\n%s", query)

    try:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.rowcount
    except Exception:
        logger.exception("Failed to load data from file %s", file_path)
        raise


def update(
    self,
    table_name: str,
    data: Dict[str, Any],
    where_clause: str,
    where_params: Optional[Tuple[Any, ...]] = None,
) -> int:
    """
    Update rows in a table.
    """
    if not data:
        raise ValueError("Data dictionary cannot be empty")
    if not where_clause:
        raise ValueError("WHERE clause is required")

    set_clause = ", ".join(f"`{k}` = %s" for k in data.keys())
    params = tuple(data.values()) + (where_params or ())

    query = f"UPDATE `{table_name}` SET {set_clause} WHERE {where_clause}"

    try:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.rowcount
    except Exception:
        logger.exception("Failed to update %s", table_name)
        raise


def delete(
    self,
    table_name: str,
    where_clause: str,
    where_params: Optional[Tuple[Any, ...]] = None,
) -> int:
    """
    Delete rows from a table.
    """
    if not where_clause:
        raise ValueError("WHERE clause is required")

    query = f"DELETE FROM `{table_name}` WHERE {where_clause}"

    try:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, where_params)
                return cur.rowcount
    except Exception:
        logger.exception("Failed to delete from %s", table_name)
        raise


def executemany(
    self,
    query: str,
    params_list: Sequence[Tuple[Any, ...]],
) -> int:
    """
    Execute a query multiple times with different parameters.

    Note:
        rowcount semantics are driver-dependent for executemany().
    """
    if not params_list:
        raise ValueError("params_list cannot be empty")

    try:
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.executemany(query, params_list)
                return cur.rowcount
    except Exception:
        logger.exception("Failed to execute batch query")
        raise