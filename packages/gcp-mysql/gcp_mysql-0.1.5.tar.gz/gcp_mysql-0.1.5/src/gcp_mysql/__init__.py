# src/gcp_mysql/__init__.py

import logging

from .service import MySQLService

__all__ = [
    "MySQLService",
]

# Prevent "No handler found" warnings for library users
logging.getLogger(__name__).addHandler(logging.NullHandler())