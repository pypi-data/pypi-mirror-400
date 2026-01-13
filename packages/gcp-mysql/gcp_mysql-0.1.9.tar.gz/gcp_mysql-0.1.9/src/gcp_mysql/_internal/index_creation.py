# src/gcp_mysql/_internal/index_creation.py

import logging
from typing import Sequence

logger = logging.getLogger(__name__)


def create_index_if_not_exists(
    self,
    table_name: str,
    index_name: str,
    columns: Sequence[str],
    unique: bool = False,
) -> None:
    """
    Create an index on a table if it does not already exist.

    Notes:
        - Index names are scoped to the table in MySQL.
        - Uses information_schema.STATISTICS for compatibility with MySQL < 8.0.13.
        - This operation is idempotent.

    Args:
        table_name: Name of the table
        index_name: Name of the index (table-scoped)
        columns: One or more column names to index
        unique: Whether the index should enforce uniqueness
    """
    if not columns:
        raise ValueError("columns must contain at least one column name")

    columns_sql = ", ".join(f"`{col}`" for col in columns)
    unique_sql = "UNIQUE" if unique else ""

    try:
        with self._conn() as conn, conn.cursor() as cur:
            # Check for existing index
            cur.execute(
                """
                SELECT 1
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = %s
                  AND TABLE_NAME = %s
                  AND INDEX_NAME = %s
                LIMIT 1
                """,
                (self.database, table_name, index_name),
            )

            if cur.fetchone():
                logger.debug(
                    "Index '%s' already exists on table '%s'; skipping",
                    index_name,
                    table_name,
                )
                return

            create_sql = (
                f"CREATE {unique_sql} INDEX `{index_name}` "
                f"ON `{table_name}` ({columns_sql})"
            )

            logger.info(
                "Creating %sindex '%s' on table '%s' (%s)",
                "UNIQUE " if unique else "",
                index_name,
                table_name,
                columns_sql,
            )
            logger.debug("DDL:\n%s", create_sql)

            cur.execute(create_sql)

            logger.info(
                "Successfully created index '%s' on table '%s'",
                index_name,
                table_name,
            )

    except Exception as e:
        logger.error(
            "Failed to create index '%s' on table '%s'",
            index_name,
            table_name,
            exc_info=True,
        )
        raise