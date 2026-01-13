import os
import pytest
from unittest.mock import patch


class TestSettings:
    """Tests for Settings class"""

    def test_default_database_url(self):
        """Test that Settings has default DATABASE_URL"""
        from fastapi_toolbox.settings import Settings

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)
            assert settings.DATABASE_URL == "postgresql://user:password@localhost:5432/db"

    def test_database_url_from_env(self):
        """Test that Settings loads DATABASE_URL from environment variable"""
        from fastapi_toolbox.settings import Settings

        custom_url = "postgresql://custom:pass@myhost:5432/mydb"
        with patch.dict(os.environ, {"DATABASE_URL": custom_url}, clear=True):
            settings = Settings(_env_file=None)
            assert settings.DATABASE_URL == custom_url

    def test_settings_inheritance(self):
        """Test that Settings can be inherited with custom defaults"""
        from fastapi_toolbox.settings import Settings

        class CustomSettings(Settings):
            DATABASE_URL: str = "sqlite:///custom.db"
            CUSTOM_FIELD: str = "custom_value"

        with patch.dict(os.environ, {}, clear=True):
            custom_settings = CustomSettings(_env_file=None)
            assert custom_settings.DATABASE_URL == "sqlite:///custom.db"
            assert custom_settings.CUSTOM_FIELD == "custom_value"

    def test_settings_env_override_inheritance(self):
        """Test that env vars override inherited defaults"""
        from fastapi_toolbox.settings import Settings

        class CustomSettings(Settings):
            DATABASE_URL: str = "sqlite:///custom.db"

        env_url = "postgresql://env:pass@envhost:5432/envdb"
        with patch.dict(os.environ, {"DATABASE_URL": env_url}, clear=True):
            custom_settings = CustomSettings(_env_file=None)
            assert custom_settings.DATABASE_URL == env_url


class TestDefaultSettingsInstance:
    """Tests for the default settings instance"""

    def test_settings_instance_exists(self):
        """Test that a default settings instance is exported"""
        from fastapi_toolbox.settings import settings

        assert settings is not None

    def test_settings_instance_type(self):
        """Test that the default settings instance is of correct type"""
        from fastapi_toolbox.settings import settings, Settings

        assert isinstance(settings, Settings)
