# src/gcp_mysql/_internal/table_creation.py

from __future__ import annotations

import logging
import re
from typing import ( 
    Dict, 
    List, 
    Optional, 
    Tuple, 
    Type, 
    get_args, 
    get_origin, 
    get_type_hints,
)

from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Type mapping helpers
# ---------------------------------------------------------------------------

def _is_optional(t: Type) -> Tuple[bool, Type]:
    origin = get_origin(t)
    if origin is not None:
        args = get_args(t)
        if type(None) in args:
            non_none = [a for a in args if a is not type(None)]
            return True, non_none[0] if non_none else str
    return False, t


def _python_type_to_mysql(field_type: Type, field_name: str) -> str:
    nullable, base_type = _is_optional(field_type)
    null_sql = "NULL" if nullable else "NOT NULL"

    origin = get_origin(base_type)

    # JSON-like
    if origin in (list, dict):
        return f"JSON {null_sql}"

    type_name = getattr(base_type, "__name__", str(base_type)).lower()
    fname = field_name.lower()

    # Primary key
    if fname == "id":
        return "BIGINT UNSIGNED NOT NULL AUTO_INCREMENT"

    # Strings
    if type_name == "str":
        if fname.endswith("_id"):
            return f"VARCHAR(255) {null_sql}"
        if "url" in fname or "link" in fname:
            return f"VARCHAR(2048) {null_sql}"
        if "name" in fname:
            return f"VARCHAR(1024) {null_sql}"
        if "description" in fname:
            return f"TEXT {null_sql}"
        return f"VARCHAR(255) {null_sql}"

    # Numbers
    if type_name == "int":
        return f"INT {null_sql}"
    if type_name == "float":
        return f"DECIMAL(10,2) {null_sql}"

    # Booleans
    if type_name == "bool":
        return "TINYINT(1) NOT NULL DEFAULT 0"

    # Dates
    if "datetime" in type_name or "timestamp" in type_name:
        return f"TIMESTAMP {null_sql}"
    if "date" in type_name:
        return f"DATE {null_sql}"

    # Fallback
    logger.warning("Falling back to VARCHAR for %s (%s)", field_name, field_type)
    return f"VARCHAR(255) {null_sql}"


# ---------------------------------------------------------------------------
# Model inspection
# ---------------------------------------------------------------------------

def _extract_model_fields(model_class: Type) -> Dict[str, Type]:
    if issubclass(model_class, BaseModel):
        if hasattr(model_class, "model_fields"):  # Pydantic v2
            return {
                name: field.annotation or str
                for name, field in model_class.model_fields.items()
            }
        if hasattr(model_class, "__fields__"):  # Pydantic v1
            return {
                name: field.type_ or str
                for name, field in model_class.__fields__.items()
            }

    hints = get_type_hints(model_class)
    if hints:
        return hints

    raise TypeError(
        f"{model_class.__name__} must be a Pydantic model or have type annotations"
    )


# ---------------------------------------------------------------------------
# Table creation
# ---------------------------------------------------------------------------

def create_table_if_not_exists(
    self,
    model_class: Type,
    table_name: Optional[str] = None,
) -> None:
    table_name = table_name or self.table_name
    if not table_name:
        table_name = re.sub(r"(?<!^)(?=[A-Z])", "_", model_class.__name__).lower()

    fields = _extract_model_fields(model_class)

    columns = []
    primary_key = None

    for name, ftype in fields.items():
        mysql_type = _python_type_to_mysql(ftype, name)
        if name.lower() == "id":
            primary_key = name
        columns.append(f"  `{name}` {mysql_type}")

    if not any("created_at" in c.lower() for c in columns):
        columns.append("  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP")
    if not any("updated_at" in c.lower() for c in columns):
        columns.append(
            "  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
        )

    pk_sql = f",\n  PRIMARY KEY (`{primary_key}`)" if primary_key else ""

    ddl = f"""
CREATE TABLE IF NOT EXISTS `{table_name}` (
{",\n".join(columns)}{pk_sql}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip()

    logger.info("Ensuring table exists: %s", table_name)
    logger.debug("DDL:\n%s", ddl)

    with self._conn() as conn, conn.cursor() as cur:
        cur.execute(ddl)


# ---------------------------------------------------------------------------
# Schema migration (additive only)
# ---------------------------------------------------------------------------

def update_table_schema(
    self,
    model_class: Type,
    table_name: Optional[str] = None,
) -> None:
    table_name = table_name or self.table_name
    if not table_name:
        raise RuntimeError("Table name must be provided")

    fields = _extract_model_fields(model_class)

    with self._conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COLUMN_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
            """,
            (self.database, table_name),
        )
        existing = {row["COLUMN_NAME"].lower() for row in cur.fetchall()}

        for name, ftype in fields.items():
            if name.lower() in existing:
                continue

            mysql_type = _python_type_to_mysql(ftype, name)
            alter = f"ALTER TABLE `{table_name}` ADD COLUMN `{name}` {mysql_type}"
            logger.info("Adding column %s to %s", name, table_name)
            logger.debug("ALTER:\n%s", alter)
            cur.execute(alter)


# ---------------------------------------------------------------------------
# Column type migration (dangerous by design)
# ---------------------------------------------------------------------------

def migrate_column_types(
    self,
    model_class: Type,
    table_name: Optional[str] = None,
    dry_run: bool = False,
) -> List[Tuple[str, str, str]]:
    """
    Migrate column types to match the model.
    WARNING: This is a destructive operation if misused.
    """
    table_name = table_name or self.table_name
    if not table_name:
        raise RuntimeError("Table name must be provided")

    fields = _extract_model_fields(model_class)
    migrated: List[Tuple[str, str, str]] = []

    with self._conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT COLUMN_NAME, COLUMN_TYPE
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s
            """,
            (self.database, table_name),
        )
        existing = {row["COLUMN_NAME"].lower(): row["COLUMN_TYPE"] for row in cur.fetchall()}

        for name, ftype in fields.items():
            lname = name.lower()
            if lname not in existing:
                continue

            old_type = existing[lname]
            new_type = _python_type_to_mysql(ftype, name)

            if old_type.split("(")[0].upper() == new_type.split("(")[0].upper():
                continue

            logger.info("Column %s type change: %s -> %s", name, old_type, new_type)
            migrated.append((name, old_type, new_type))

            if not dry_run:
                alter = f"ALTER TABLE `{table_name}` MODIFY COLUMN `{name}` {new_type}"
                logger.debug("ALTER:\n%s", alter)
                cur.execute(alter)

    return migrated