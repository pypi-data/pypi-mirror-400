# src/gcp_mysql/service.py

from __future__ import annotations

from contextlib import contextmanager
import logging
from typing import (
    Any, Optional,
)

import pymysql
from pymysql.err import OperationalError

from .utils import (
    delete as _delete,
    executemany as _executemany,
    execute_query as _execute_query,
    from_gcp_secret as _from_gcp_secret,
    insert as _insert,
    insert_from_file as _insert_from_file,
    update as _update,
)

logger = logging.getLogger(__name__)


class MySQLService:
    """
    Thin wrapper around PyMySQL providing:
      - safe connection handling (TCP or Unix domain socket)
      - query execution helpers
      - insert / update / delete convenience methods

    Note:
      - This class opens a new connection per operation via a context manager.
        For high-throughput workloads, consider connection pooling at a higher level.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 3306,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        unix_socket: Optional[str] = None,
        table_name: Optional[str] = None,
        ssl_ca_path: Optional[str] = None,
        connect_timeout: int = 10,
        read_timeout: int = 30,
        write_timeout: int = 30,
        autocommit: bool = True,
        local_infile: bool = False,
    ):
        # If using unix_socket, host/port are ignored by PyMySQL.
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.ssl_ca_path = ssl_ca_path
        self.unix_socket = unix_socket
        self.table_name = table_name

        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.autocommit = autocommit
        self.local_infile = local_infile

        if not all([self.user, self.password, self.database]):
            raise RuntimeError("Missing MySQL params (user/password/database).")

    # Class factory (bound below)
    from_gcp_secret = classmethod(_from_gcp_secret)

    @contextmanager
    def _conn(self):
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                ssl={"ca": self.ssl_ca_path} if self.ssl_ca_path else None,
                unix_socket=self.unix_socket,
                connect_timeout=self.connect_timeout,
                read_timeout=self.read_timeout,
                write_timeout=self.write_timeout,
                autocommit=self.autocommit,
                local_infile=self.local_infile,
                cursorclass=pymysql.cursors.DictCursor,
            )
        except OperationalError as e:
            mode = "cloudsql" if self.unix_socket else "tcp"
            target = (
                self.unix_socket
                if self.unix_socket
                else f"{self.host}:{self.port}"
            )

            raise RuntimeError(
                f"MySQL connection failed ({mode} mode → {target}). "
                "Ensure the database is reachable and any required proxy is running."
            ) from e

        try:
            yield conn
        finally:
            conn.close()

    # -------------------------
    # Explicit delegation wrappers (better typing/IDE support than attribute grafting)
    # -------------------------
    def execute_query(self, *args: Any, **kwargs: Any) -> Any:
        return _execute_query(self, *args, **kwargs)

    def insert(self, *args: Any, **kwargs: Any) -> Any:
        return _insert(self, *args, **kwargs)

    def insert_from_file(self, *args: Any, **kwargs: Any) -> Any:
        return _insert_from_file(self, *args, **kwargs)

    def update(self, *args: Any, **kwargs: Any) -> Any:
        return _update(self, *args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        return _delete(self, *args, **kwargs)

    def executemany(self, *args: Any, **kwargs: Any) -> Any:
        return _executemany(self, *args, **kwargs)

    def test_connection(self) -> bool:
        """
        Test the database connection by executing a simple query.

        Returns:
            bool: True if connection is successful, False otherwise.

        Raises:
            Exception: Re-raises any connection or query errors.
        """
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 as test")
                result = cur.fetchone()
                logger.debug("Test connection successful, result: %s", result)
                return bool(result) and result.get("test") == 1