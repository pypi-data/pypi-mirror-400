import os
import pytest
from unittest.mock import patch, MagicMock
from sqlmodel import SQLModel, Field, Session


class TestInitDatabase:
    """Tests for init_database function"""

    def test_init_database_with_direct_url(self):
        """Test init_database with direct database_url parameter"""
        from fastapi_toolbox.database import init_database

        url = "sqlite:///test_direct.db"
        engine = init_database(database_url=url)

        assert engine is not None
        assert str(engine.url) == url

    def test_init_database_with_settings_instance(self):
        """Test init_database with custom Settings instance"""
        from fastapi_toolbox.database import init_database
        from fastapi_toolbox.settings import Settings

        with patch.dict(os.environ, {}, clear=True):
            class CustomSettings(Settings):
                DATABASE_URL: str = "sqlite:///test_settings.db"

            custom_settings = CustomSettings(_env_file=None)
            engine = init_database(settings_instance=custom_settings)

            assert engine is not None
            assert str(engine.url) == "sqlite:///test_settings.db"

    def test_init_database_url_priority_over_settings(self):
        """Test that direct URL takes priority over settings instance"""
        from fastapi_toolbox.database import init_database
        from fastapi_toolbox.settings import Settings

        with patch.dict(os.environ, {}, clear=True):
            class CustomSettings(Settings):
                DATABASE_URL: str = "sqlite:///settings.db"

            custom_settings = CustomSettings(_env_file=None)
            direct_url = "sqlite:///direct.db"

            engine = init_database(
                database_url=direct_url,
                settings_instance=custom_settings
            )

            assert str(engine.url) == direct_url

    def test_init_database_with_engine_kwargs(self):
        """Test init_database passes kwargs to create_engine"""
        from fastapi_toolbox.database import init_database

        engine = init_database(
            database_url="sqlite:///test_kwargs.db",
            echo=True
        )

        assert engine is not None
        assert engine.echo is True


class TestGetEngine:
    """Tests for get_engine function"""

    def test_get_engine_returns_initialized_engine(self):
        """Test get_engine returns the initialized engine"""
        from fastapi_toolbox.database import init_database, get_engine

        init_database(database_url="sqlite:///test_get.db")
        engine = get_engine()

        assert engine is not None
        assert str(engine.url) == "sqlite:///test_get.db"

    def test_get_engine_auto_initializes(self):
        """Test get_engine auto-initializes if engine is None"""
        from fastapi_toolbox.database import get_engine
        import fastapi_toolbox.database as db_module

        db_module._engine = None

        with patch.object(db_module, 'init_database') as mock_init:
            mock_engine = MagicMock()
            mock_init.return_value = mock_engine
            db_module._engine = None

            def set_engine():
                db_module._engine = mock_engine
                return mock_engine

            mock_init.side_effect = set_engine

            engine = get_engine()
            mock_init.assert_called_once()


class TestGetSession:
    """Tests for get_session function"""

    def test_get_session_yields_session(self):
        """Test get_session yields a valid Session"""
        from fastapi_toolbox.database import init_database, get_session

        init_database(database_url="sqlite:///:memory:")

        session_gen = get_session()
        session = next(session_gen)

        assert isinstance(session, Session)

        try:
            next(session_gen)
        except StopIteration:
            pass

    def test_get_session_closes_session(self):
        """Test get_session properly closes the session"""
        from fastapi_toolbox.database import init_database, get_session

        init_database(database_url="sqlite:///:memory:")

        session_gen = get_session()
        session = next(session_gen)

        try:
            next(session_gen)
        except StopIteration:
            pass


class TestCreateDbAndTables:
    """Tests for create_db_and_tables function"""

    def test_create_db_and_tables(self):
        """Test create_db_and_tables creates tables"""
        from fastapi_toolbox.database import init_database, create_db_and_tables

        class TestModel(SQLModel, table=True):
            __tablename__ = "test_model_table"
            id: int = Field(default=None, primary_key=True)
            name: str

        init_database(database_url="sqlite:///:memory:")
        create_db_and_tables()

    def test_create_db_and_tables_idempotent(self):
        """Test create_db_and_tables can be called multiple times"""
        from fastapi_toolbox.database import init_database, create_db_and_tables

        init_database(database_url="sqlite:///:memory:")

        create_db_and_tables()
        create_db_and_tables()
