"""
FastAPI utilities package
"""

from .static_files import StaticFilesCache
from .config import UvicornConfig
from .logging import (
    logger,
    setup_logging,
    add_file_log,
    InterceptHandler,
    Rotator,
    get_log_level,
    LOG_LEVEL,
    JSON_LOGS
)
from .server import run_server
from .middleware import NextJSRouteMiddleware
from .settings import Settings, settings
from .database import (
    init_database,
    get_engine,
    get_session,
    create_db_and_tables
)

__all__ = [
    "StaticFilesCache",
    "UvicornConfig",
    "logger",
    "setup_logging",
    "add_file_log",
    "InterceptHandler",
    "Rotator",
    "get_log_level",
    "LOG_LEVEL",
    "JSON_LOGS",
    "run_server",
    "NextJSRouteMiddleware",
    "Settings",
    "settings",
    "init_database",
    "get_engine",
    "get_session",
    "create_db_and_tables"
]