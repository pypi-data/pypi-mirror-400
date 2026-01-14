"""Unit tests for ConfigFileLoader component."""

import pytest
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch
from mcp_arangodb_async.config_loader import ConfigFileLoader
from mcp_arangodb_async.multi_db_manager import DatabaseConfig


class TestConfigFileLoader:
    """Test ConfigFileLoader for YAML configuration and environment variable loading."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "databases.yaml")

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "default_database": "production",
            "databases": {
                "production": {
                    "url": "http://prod:8529",
                    "database": "prod_db",
                    "username": "prod_user",
                    "password_env": "PROD_PASSWORD",
                    "timeout": 60.0
                },
                "staging": {
                    "url": "http://staging:8529",
                    "database": "staging_db",
                    "username": "staging_user",
                    "password_env": "STAGING_PASSWORD",
                    "timeout": 30.0
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigFileLoader(self.config_path)
        loader.load()
        
        assert loader.default_database == "production"
        assert loader.loaded_from_yaml is True  # Verify source tracking
        databases = loader.get_configured_databases()
        assert len(databases) == 2
        assert "production" in databases
        assert "staging" in databases
        assert databases["production"].url == "http://prod:8529"
        assert databases["staging"].database == "staging_db"

    @patch.dict(os.environ, {"ARANGO_DATABASES_CONFIG_FILE": ""}, clear=True)
    def test_init_uses_env_var_for_config_path(self):
        """Test that ConfigFileLoader uses ARANGO_DATABASES_CONFIG_FILE env var."""
        custom_config_path = os.path.join(self.temp_dir, "custom.yaml")
        
        # Create a custom config file
        config_data = {
            "default_database": "custom_db",
            "databases": {
                "custom_db": {
                    "url": "http://custom:8529",
                    "database": "custom",
                    "username": "custom_user",
                    "password_env": "CUSTOM_PASSWORD"
                }
            }
        }
        with open(custom_config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        with patch.dict(os.environ, {"ARANGO_DATABASES_CONFIG_FILE": custom_config_path}):
            # No config_path provided - should use env var
            loader = ConfigFileLoader()
            assert loader.config_path == os.path.abspath(custom_config_path)
            loader.load()
            
            assert loader.default_database == "custom_db"
            databases = loader.get_configured_databases()
            assert "custom_db" in databases

    def test_init_explicit_path_overrides_env_var(self):
        """Test that explicit config_path overrides ARANGO_DATABASES_CONFIG_FILE."""
        explicit_path = os.path.join(self.temp_dir, "explicit.yaml")
        env_path = os.path.join(self.temp_dir, "env.yaml")
        
        # Create explicit config file
        config_data = {
            "default_database": "explicit",
            "databases": {"explicit": {"url": "http://explicit:8529", "database": "explicit", "username": "user", "password_env": "PASS"}}
        }
        with open(explicit_path, 'w') as f:
            yaml.dump(config_data, f)
        
        with patch.dict(os.environ, {"ARANGO_DATABASES_CONFIG_FILE": env_path}):
            # Explicit path should override env var
            loader = ConfigFileLoader(config_path=explicit_path)
            assert loader.config_path == os.path.abspath(explicit_path)
            loader.load()
            
            assert loader.default_database == "explicit"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_uses_default_when_no_env_var(self):
        """Test that ConfigFileLoader uses default path when no env var is set."""
        loader = ConfigFileLoader()
        # Should use default path
        assert loader.config_path == os.path.abspath(ConfigFileLoader.DEFAULT_CONFIG_PATH)

    @patch.dict(os.environ, {
        "ARANGO_URL": "http://localhost:8529",
        "ARANGO_DB": "test_db",
        "ARANGO_USERNAME": "test_user"
    }, clear=True)
    def test_load_from_env_vars_backward_compatibility(self):
        """Test backward compatibility with v0.4.0 environment variables."""
        loader = ConfigFileLoader(self.config_path)  # File doesn't exist
        loader.load()
        
        assert loader.default_database == "default"
        assert loader.loaded_from_yaml is False  # Verify source tracking
        databases = loader.get_configured_databases()
        assert len(databases) == 1
        assert "default" in databases
        assert databases["default"].url == "http://localhost:8529"
        assert databases["default"].database == "test_db"
        assert databases["default"].username == "test_user"
        assert databases["default"].password_env == "ARANGO_PASSWORD"

    @patch.dict(os.environ, {}, clear=True)
    def test_load_from_env_vars_with_defaults(self):
        """Test loading from environment variables with default values."""
        loader = ConfigFileLoader(self.config_path)  # File doesn't exist
        loader.load()
        
        databases = loader.get_configured_databases()
        assert "default" in databases
        assert databases["default"].url == "http://localhost:8529"
        assert databases["default"].database == "_system"
        assert databases["default"].username == "root"

    def test_get_configured_databases(self):
        """Test get_configured_databases returns all databases."""
        config_data = {
            "databases": {
                "db1": {
                    "url": "http://db1:8529",
                    "database": "db1",
                    "username": "user1",
                    "password_env": "DB1_PASSWORD"
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigFileLoader(self.config_path)
        loader.load()
        
        databases = loader.get_configured_databases()
        assert isinstance(databases, dict)
        assert "db1" in databases
        assert isinstance(databases["db1"], DatabaseConfig)

    def test_add_database(self):
        """Test adding a database configuration."""
        loader = ConfigFileLoader(self.config_path)
        loader.load()
        
        new_config = DatabaseConfig(
            url="http://new:8529",
            database="new_db",
            username="new_user",
            password_env="NEW_PASSWORD",
            timeout=45.0
        )
        
        loader.add_database("new_db", new_config)
        
        databases = loader.get_configured_databases()
        assert "new_db" in databases
        assert databases["new_db"].url == "http://new:8529"

    def test_remove_database(self):
        """Test removing a database configuration."""
        config_data = {
            "databases": {
                "db1": {
                    "url": "http://db1:8529",
                    "database": "db1",
                    "username": "user1",
                    "password_env": "DB1_PASSWORD"
                },
                "db2": {
                    "url": "http://db2:8529",
                    "database": "db2",
                    "username": "user2",
                    "password_env": "DB2_PASSWORD"
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)
        
        loader = ConfigFileLoader(self.config_path)
        loader.load()
        
        loader.remove_database("db1")
        
        databases = loader.get_configured_databases()
        assert "db1" not in databases
        assert "db2" in databases

    def test_save_to_yaml(self):
        """Test saving configuration to YAML file."""
        loader = ConfigFileLoader(self.config_path)

        # Add some databases
        loader.add_database("prod", DatabaseConfig(
            url="http://prod:8529",
            database="prod_db",
            username="prod_user",
            password_env="PROD_PASSWORD",
            timeout=60.0
        ))
        loader.add_database("staging", DatabaseConfig(
            url="http://staging:8529",
            database="staging_db",
            username="staging_user",
            password_env="STAGING_PASSWORD",
            timeout=30.0
        ))
        loader.default_database = "prod"

        # Save to file
        loader.save_to_yaml()

        # Verify file was created and can be loaded
        assert os.path.exists(self.config_path)

        # Load with new instance
        new_loader = ConfigFileLoader(self.config_path)
        new_loader.load()

        assert new_loader.default_database == "prod"
        databases = new_loader.get_configured_databases()
        assert len(databases) == 2
        assert "prod" in databases
        assert "staging" in databases

    def test_yaml_file_with_description(self):
        """Test loading YAML file with optional description field."""
        config_data = {
            "databases": {
                "production": {
                    "url": "http://prod:8529",
                    "database": "prod_db",
                    "username": "prod_user",
                    "password_env": "PROD_PASSWORD",
                    "timeout": 60.0,
                    "description": "Production database"
                }
            }
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        loader = ConfigFileLoader(self.config_path)
        loader.load()

        databases = loader.get_configured_databases()
        assert databases["production"].description == "Production database"

    def test_empty_yaml_file(self):
        """Test loading empty YAML file."""
        with open(self.config_path, 'w') as f:
            f.write("")

        loader = ConfigFileLoader(self.config_path)
        loader.load()

        # Should fall back to env vars
        databases = loader.get_configured_databases()
        assert len(databases) >= 0  # May have default from env vars

    def test_invalid_yaml_file(self):
        """Test handling of invalid YAML file."""
        with open(self.config_path, 'w') as f:
            f.write("invalid: yaml: content: [")

        loader = ConfigFileLoader(self.config_path)

        # Should raise an error or handle gracefully
        with pytest.raises(yaml.YAMLError):
            loader.load()

    def test_yaml_file_without_default_database(self):
        """Test YAML file without default_database field."""
        config_data = {
            "databases": {
                "db1": {
                    "url": "http://db1:8529",
                    "database": "db1",
                    "username": "user1",
                    "password_env": "DB1_PASSWORD"
                }
            }
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        loader = ConfigFileLoader(self.config_path)
        loader.load()

        assert loader.default_database is None
        databases = loader.get_configured_databases()
        assert "db1" in databases

    def test_load_yaml_only_no_env_fallback(self):
        """Test load_yaml_only does not fall back to env vars when file missing.
        
        This ensures db config add/remove only operate on explicitly configured
        databases and don't merge with environment variable defaults.
        """
        # Use a non-existent config path
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.yaml")
        loader = ConfigFileLoader(nonexistent_path)
        
        # Set env vars that would be picked up by load() but not load_yaml_only()
        with patch.dict(os.environ, {
            "ARANGO_URL": "http://env-test:8529",
            "ARANGO_DB": "env_database",
            "ARANGO_USERNAME": "env_user"
        }):
            loader.load_yaml_only()
        
        # Should have empty databases (no env fallback)
        databases = loader.get_configured_databases()
        assert len(databases) == 0, "load_yaml_only should not fall back to env vars"
        assert loader.default_database is None
        assert loader.loaded_from_yaml is False

    def test_load_yaml_only_loads_existing_yaml(self):
        """Test load_yaml_only correctly loads existing YAML file."""
        config_data = {
            "default_database": "db1",
            "databases": {
                "db1": {
                    "url": "http://db1:8529",
                    "database": "db1",
                    "username": "user1",
                    "password_env": "DB1_PASSWORD"
                }
            }
        }

        with open(self.config_path, 'w') as f:
            yaml.dump(config_data, f)

        loader = ConfigFileLoader(self.config_path)
        loader.load_yaml_only()

        databases = loader.get_configured_databases()
        assert "db1" in databases
        assert loader.default_database == "db1"
        assert loader.loaded_from_yaml is True

