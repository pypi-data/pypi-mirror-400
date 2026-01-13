import pytest


class TestPackageImports:
    """Tests for package imports from fastapi_toolbox"""

    def test_import_static_files_cache(self):
        """Test StaticFilesCache can be imported"""
        from fastapi_toolbox import StaticFilesCache

        assert StaticFilesCache is not None

    def test_import_uvicorn_config(self):
        """Test UvicornConfig can be imported"""
        from fastapi_toolbox import UvicornConfig

        assert UvicornConfig is not None

    def test_import_logging_components(self):
        """Test logging components can be imported"""
        from fastapi_toolbox import (
            logger,
            setup_logging,
            add_file_log,
            InterceptHandler,
            Rotator,
            get_log_level,
            LOG_LEVEL,
            JSON_LOGS
        )

        assert logger is not None
        assert setup_logging is not None
        assert add_file_log is not None
        assert InterceptHandler is not None
        assert Rotator is not None
        assert get_log_level is not None

    def test_import_run_server(self):
        """Test run_server can be imported"""
        from fastapi_toolbox import run_server

        assert run_server is not None

    def test_import_middleware(self):
        """Test NextJSRouteMiddleware can be imported"""
        from fastapi_toolbox import NextJSRouteMiddleware

        assert NextJSRouteMiddleware is not None

    def test_import_settings(self):
        """Test Settings and settings can be imported"""
        from fastapi_toolbox import Settings, settings

        assert Settings is not None
        assert settings is not None

    def test_import_database_components(self):
        """Test database components can be imported"""
        from fastapi_toolbox import (
            init_database,
            get_engine,
            get_session,
            create_db_and_tables
        )

        assert init_database is not None
        assert get_engine is not None
        assert get_session is not None
        assert create_db_and_tables is not None


class TestAllExports:
    """Tests for __all__ exports"""

    def test_all_exports_exist(self):
        """Test all items in __all__ are actually exported"""
        import fastapi_toolbox

        expected_exports = [
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

        for export in expected_exports:
            assert hasattr(fastapi_toolbox, export), f"{export} not found in fastapi_toolbox"

    def test_all_matches_expected(self):
        """Test __all__ contains expected items"""
        import fastapi_toolbox

        assert hasattr(fastapi_toolbox, '__all__')
        assert len(fastapi_toolbox.__all__) == 18
