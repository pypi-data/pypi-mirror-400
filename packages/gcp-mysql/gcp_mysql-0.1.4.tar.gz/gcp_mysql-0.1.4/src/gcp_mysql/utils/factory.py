# src/gcp_mysql/utils/factory.py

from __future__ import annotations

import json
import logging
import os
import tempfile
from json import JSONDecodeError
from typing import Optional, Type, TYPE_CHECKING

try:
    from google.cloud import secretmanager  # type: ignore
    from google.auth.exceptions import RefreshError  # type: ignore
    from google.api_core.exceptions import ServiceUnavailable, RetryError  # type: ignore
    SECRET_MANAGER_AVAILABLE = True
except ImportError:  # pragma: no cover
    SECRET_MANAGER_AVAILABLE = False
    secretmanager = None  # type: ignore[assignment]
    RefreshError = None  # type: ignore[assignment, misc]
    ServiceUnavailable = None  # type: ignore[assignment, misc]
    RetryError = None  # type: ignore[assignment, misc]

if TYPE_CHECKING:
    from ..service import MySQLService

logger = logging.getLogger(__name__)

SUPPORTED_CONNECTION_MODES = {"cloudsql", "tcp"}


def _is_authentication_error(exc: Exception) -> bool:
    """
    Check if an exception indicates an authentication/credential issue.
    
    Returns True if the exception or its cause indicates that the user needs
    to run `gcloud auth application-default login`.
    """
    # Check for RefreshError (direct authentication failure)
    if RefreshError is not None and isinstance(exc, RefreshError):
        return True
    
    # Check for ServiceUnavailable with authentication message
    if ServiceUnavailable is not None and isinstance(exc, ServiceUnavailable):
        error_msg = str(exc).lower()
        if "reauthentication" in error_msg or "application-default login" in error_msg:
            return True
    
    # Check for RetryError wrapping an authentication error
    if RetryError is not None and isinstance(exc, RetryError):
        # Check the underlying cause (Python exception chaining)
        if exc.__cause__:
            return _is_authentication_error(exc.__cause__)
        # Check the error message itself (RetryError includes the last exception message)
        error_msg = str(exc).lower()
        if "reauthentication" in error_msg or "application-default login" in error_msg:
            return True
    
    # Check the error message for any exception type
    error_msg = str(exc).lower()
    if "reauthentication" in error_msg or "application-default login" in error_msg:
        return True
    
    return False


def from_gcp_secret(
    cls: Type["MySQLService"],
    *,
    project_id: str,
    secret_id: str,
    version_id: str = "latest",
    ssl_ca_secret_id: Optional[str] = None,
    connection_mode: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> "MySQLService":
    """
    Create a MySQLService using credentials from GCP Secret Manager.

    Connection behavior is resolved in the following order:
      1. Explicit method arguments
      2. Environment variables
      3. Library defaults

    Supported connection modes:

    Local development (Cloud SQL Proxy / TCP):
        connection_mode="tcp"
        host="127.0.0.1"
        port=3306

    Or via environment:
        MYSQL_CONNECTION_MODE=tcp
        MYSQL_HOST=127.0.0.1
        MYSQL_PORT=3306

    Cloud Run / production:
        MYSQL_CONNECTION_MODE=cloudsql
        CLOUDSQL_INSTANCE=project:region:instance

    The secret must contain ONLY credentials:
        {
          "USER": "...",
          "PASSWORD": "...",
          "DATABASE": "...",
          "PORT": 3306
        }
    """
    # ------------------------------------------------------------------
    # Defensive guard
    # ------------------------------------------------------------------
    if not isinstance(cls, type):
        raise TypeError(
            "from_gcp_secret must be called as a classmethod "
            "(e.g., MySQLService.from_gcp_secret(...))"
        )

    if not SECRET_MANAGER_AVAILABLE:
        raise RuntimeError("google-cloud-secret-manager is not installed")

    # ------------------------------------------------------------------
    # Load secret
    # ------------------------------------------------------------------
    secret_path = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    try:
        client = secretmanager.SecretManagerServiceClient()
    except Exception as e:
        if _is_authentication_error(e):
            logger.exception("GCP authentication failed when creating Secret Manager client")
            raise RuntimeError(
                "GCP authentication failed. Run "
                "`gcloud auth application-default login`."
            ) from e
        logger.exception("Failed to create Secret Manager client")
        raise RuntimeError("Failed to create Secret Manager client") from e

    try:
        response = client.access_secret_version(request={"name": secret_path})
        raw = response.payload.data.decode("utf-8")
        cfg = json.loads(raw)
    except (UnicodeDecodeError, JSONDecodeError, ValueError) as e:
        logger.exception("Failed to decode/parse MySQL secret '%s'", secret_id)
        raise RuntimeError(f"Invalid MySQL secret format: {e}") from e
    except Exception as e:
        if _is_authentication_error(e):
            logger.exception("GCP authentication failed when accessing MySQL secret '%s'", secret_id)
            raise RuntimeError(
                "GCP authentication failed. Run "
                "`gcloud auth application-default login`."
            ) from e
        logger.exception("Failed to load MySQL secret '%s'", secret_id)
        raise RuntimeError(f"Failed to load MySQL secret '{secret_id}'") from e

    # ------------------------------------------------------------------
    # Validate secret contents
    # ------------------------------------------------------------------
    try:
        user = cfg["USER"]
        password = cfg["PASSWORD"]
        database = cfg["DATABASE"]
        secret_port = int(cfg.get("PORT", 3306))
    except KeyError as e:
        raise RuntimeError(f"Missing required key in MySQL secret: {e}") from e
    except (TypeError, ValueError) as e:
        raise RuntimeError(f"Invalid PORT value in MySQL secret: {e}") from e

    # ------------------------------------------------------------------
    # Resolve connection mode (explicit > env > default)
    # ------------------------------------------------------------------
    mode = (
        connection_mode
        or os.getenv("MYSQL_CONNECTION_MODE")
        or "cloudsql"
    ).strip().lower()

    if mode not in SUPPORTED_CONNECTION_MODES:
        raise RuntimeError(
            f"Invalid connection_mode={mode}. "
            f"Expected one of {sorted(SUPPORTED_CONNECTION_MODES)}"
        )

    kwargs: dict = {
        "user": user,
        "password": password,
        "database": database,
        "port": port or int(os.getenv("MYSQL_PORT", secret_port)),
    }

    # ------------------------------------------------------------------
    # Connection mode handling
    # ------------------------------------------------------------------
    if mode == "cloudsql":
        instance = os.getenv("CLOUDSQL_INSTANCE")
        if not instance:
            raise RuntimeError(
                "CLOUDSQL_INSTANCE must be set for cloudsql mode"
            )

        kwargs["unix_socket"] = f"/cloudsql/{instance}"
        logger.debug(
            "MySQL connection mode: cloudsql (unix socket: %s)",
            instance,
        )

    elif mode == "tcp":
        resolved_host = host or os.getenv("MYSQL_HOST", "127.0.0.1")
        resolved_port = kwargs["port"]

        kwargs["host"] = resolved_host
        kwargs["port"] = resolved_port

        logger.debug(
            "MySQL connection mode: tcp (%s:%s)",
            resolved_host,
            resolved_port,
        )

    # ------------------------------------------------------------------
    # Optional SSL CA support
    # ------------------------------------------------------------------
    if ssl_ca_secret_id:
        ssl_path = f"projects/{project_id}/secrets/{ssl_ca_secret_id}/versions/{version_id}"
        try:
            ssl_resp = client.access_secret_version(request={"name": ssl_path})
            ca_bytes = ssl_resp.payload.data

            # PyMySQL expects a file path, not raw PEM bytes
            with tempfile.NamedTemporaryFile(
                prefix="gcp_mysql_ca_",
                suffix=".pem",
                delete=False,
            ) as f:
                f.write(ca_bytes)
                kwargs["ssl_ca_path"] = f.name

            logger.debug(
                "Loaded MySQL SSL CA from secret '%s'",
                ssl_ca_secret_id,
            )
        except Exception as e:
            logger.warning(
                "Failed to load optional SSL CA secret '%s': %s",
                ssl_ca_secret_id,
                e,
            )

    # ------------------------------------------------------------------
    # Final safety guard
    # ------------------------------------------------------------------
    if "unix_socket" in kwargs and "host" in kwargs:
        raise RuntimeError(
            "Invalid MySQL configuration: "
            "host and unix_socket are both set"
        )

    # ------------------------------------------------------------------
    # Create service
    # ------------------------------------------------------------------
    try:
        return cls(**kwargs)
    except TypeError:
        logger.exception(
            "Failed to create MySQLService due to invalid constructor arguments"
        )
        raise
    except Exception:
        logger.exception("Failed to create MySQLService")
        raise