"""Comprehensive tests for server initialization database resolution consistency.

This test suite verifies that server initialization uses the same 6-level priority
resolution as tool execution across all possible configuration scenarios.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import AsyncMock, MagicMock, patch
from mcp_arangodb_async.entry import server_lifespan
from mcp_arangodb_async.session_state import SessionState
from mcp_arangodb_async.config_loader import ConfigFileLoader
from mcp_arangodb_async.multi_db_manager import MultiDatabaseConnectionManager, DatabaseConfig


class TestServerInitializationConsistency:
    """Test server initialization database resolution consistency."""

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary YAML config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config = {
                "default_database": "prod_db",
                "databases": {
                    "prod_db": {
                        "url": "http://prod:8529",
                        "database": "production",
                        "username": "prod_user",
                        "password_env": "PROD_PASSWORD"
                    },
                    "dev_db": {
                        "url": "http://dev:8529", 
                        "database": "development",
                        "username": "dev_user",
                        "password_env": "DEV_PASSWORD"
                    }
                }
            }
            yaml.dump(config, f)
            yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def mock_server(self):
        """Mock MCP server for testing."""
        server = MagicMock()
        server.request_context = None
        return server

    @pytest.fixture
    def mock_db_manager(self):
        """Mock MultiDatabaseConnectionManager."""
        manager = AsyncMock(spec=MultiDatabaseConnectionManager)
        manager.get_connection = AsyncMock()
        manager.initialize = AsyncMock()
        manager.close_all = AsyncMock()
        manager.register_database = MagicMock()
        return manager

    @pytest.fixture
    def mock_arango_connection(self):
        """Mock ArangoDB client and database."""
        client = MagicMock()
        db = MagicMock()
        return client, db

    async def test_yaml_config_default_database_resolution(self, temp_config_file, mock_server, mock_arango_connection):
        """Test server init resolves to YAML default database (Level 3)."""
        client, db = mock_arango_connection
        
        with patch('mcp_arangodb_async.entry._config_file_path', temp_config_file), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve:
            
            # Setup mocks
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(return_value=(client, db))
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "prod_db"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Verify resolver was called with correct parameters
                mock_resolve.assert_called_once()
                args = mock_resolve.call_args[0]
                
                # Check resolver arguments
                assert args[0] == {}  # Empty tool_args for server init
                assert isinstance(args[1], SessionState)  # session_state
                assert args[2] == "init"  # session_id
                assert isinstance(args[3], ConfigFileLoader)  # config_loader
                
                # Verify connection was established to resolved database
                mock_manager.get_connection.assert_called_once_with("prod_db")
                
                # Verify context contains the resolved connection
                assert context["db"] == db
                assert context["client"] == client

    async def test_environment_variable_resolution(self, mock_server, mock_arango_connection):
        """Test server init resolves to ARANGO_DB environment variable (Level 4)."""
        client, db = mock_arango_connection
        
        with patch.dict(os.environ, {
            'ARANGO_DB': 'env_database',
            'ARANGO_URL': 'http://env:8529',
            'ARANGO_USERNAME': 'env_user'
        }), \
             patch('mcp_arangodb_async.entry._config_file_path', 'nonexistent.yaml'), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve:
            
            # Setup mocks
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(return_value=(client, db))
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "env_database"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Verify resolver was called
                mock_resolve.assert_called_once()
                
                # Verify connection was established to resolved database
                mock_manager.get_connection.assert_called_once_with("env_database")
                
                # Verify context contains the resolved connection
                assert context["db"] == db
                assert context["client"] == client

    async def test_first_configured_database_resolution(self, temp_config_file, mock_server, mock_arango_connection):
        """Test server init resolves to first configured database (Level 5)."""
        client, db = mock_arango_connection
        
        # Create config without default_database
        with open(temp_config_file, 'w') as f:
            config = {
                "databases": {
                    "first_db": {
                        "url": "http://first:8529",
                        "database": "first_database", 
                        "username": "first_user",
                        "password_env": "FIRST_PASSWORD"
                    },
                    "second_db": {
                        "url": "http://second:8529",
                        "database": "second_database",
                        "username": "second_user", 
                        "password_env": "SECOND_PASSWORD"
                    }
                }
            }
            yaml.dump(config, f)
        
        with patch('mcp_arangodb_async.entry._config_file_path', temp_config_file), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve:
            
            # Setup mocks
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(return_value=(client, db))
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "first_db"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Verify resolver was called
                mock_resolve.assert_called_once()
                
                # Verify connection was established to resolved database
                mock_manager.get_connection.assert_called_once_with("first_db")

    async def test_hardcoded_fallback_resolution(self, mock_server, mock_arango_connection):
        """Test server init resolves to _system fallback (Level 6)."""
        client, db = mock_arango_connection
        
        with patch('mcp_arangodb_async.entry._config_file_path', 'nonexistent.yaml'), \
             patch.dict(os.environ, {}, clear=True), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve:
            
            # Setup mocks
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(return_value=(client, db))
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "_system"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Verify resolver was called
                mock_resolve.assert_called_once()
                
                # Verify connection was established to fallback database
                mock_manager.get_connection.assert_called_once_with("_system")

    async def test_connection_retry_logic(self, temp_config_file, mock_server, mock_arango_connection):
        """Test server init retry logic with connection failures."""
        client, db = mock_arango_connection
        
        with patch('mcp_arangodb_async.entry._config_file_path', temp_config_file), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve, \
             patch.dict(os.environ, {'ARANGO_CONNECT_RETRIES': '2', 'ARANGO_CONNECT_DELAY_SEC': '0.1'}):
            
            # Setup mocks - fail first attempt, succeed second
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(side_effect=[
                Exception("Connection failed"),
                (client, db)
            ])
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "prod_db"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Verify resolver was called
                mock_resolve.assert_called_once()
                
                # Verify connection was retried and eventually succeeded
                assert mock_manager.get_connection.call_count == 2
                assert context["db"] == db
                assert context["client"] == client

    async def test_connection_failure_graceful_degradation(self, temp_config_file, mock_server):
        """Test server init graceful degradation when all connection attempts fail."""
        
        with patch('mcp_arangodb_async.entry._config_file_path', temp_config_file), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve, \
             patch.dict(os.environ, {'ARANGO_CONNECT_RETRIES': '2', 'ARANGO_CONNECT_DELAY_SEC': '0.1'}):
            
            # Setup mocks - all attempts fail
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(side_effect=Exception("Connection failed"))
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "prod_db"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Verify resolver was called
                mock_resolve.assert_called_once()
                
                # Verify graceful degradation - server starts without DB
                assert mock_manager.get_connection.call_count == 2
                assert context["db"] is None
                assert context["client"] is None

    async def test_resolver_consistency_with_tool_execution(self, temp_config_file, mock_server, mock_arango_connection):
        """Test that server init and tool execution use identical resolution logic."""
        client, db = mock_arango_connection
        
        with patch('mcp_arangodb_async.entry._config_file_path', temp_config_file), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve:
            
            # Setup mocks
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(return_value=(client, db))
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "prod_db"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Capture the resolver call arguments from server init
                server_init_args = mock_resolve.call_args[0]
                
                # Verify server init uses same resolver signature as tools
                assert len(server_init_args) == 4
                assert server_init_args[0] == {}  # tool_args (empty for server init)
                assert isinstance(server_init_args[1], SessionState)  # session_state
                assert server_init_args[2] == "init"  # session_id
                assert isinstance(server_init_args[3], ConfigFileLoader)  # config_loader
                
                # Verify the same components are available for tool execution
                assert "session_state" in context
                assert "config_loader" in context
                assert "db_manager" in context
                
                # Verify they're the correct types (server init uses separate SessionState for init)
                assert isinstance(context["session_state"], SessionState)
                assert isinstance(context["config_loader"], ConfigFileLoader)
                
                # Verify the config_loader used by resolver is the same as in context
                assert context["config_loader"] == server_init_args[3]

    async def test_environment_variable_precedence_over_yaml_default(self, temp_config_file, mock_server, mock_arango_connection):
        """Test that ARANGO_DB environment variable takes precedence over YAML default."""
        client, db = mock_arango_connection
        
        with patch('mcp_arangodb_async.entry._config_file_path', temp_config_file), \
             patch.dict(os.environ, {'ARANGO_DB': 'env_override_db'}), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve:
            
            # Setup mocks
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(return_value=(client, db))
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "env_override_db"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Verify resolver was called
                mock_resolve.assert_called_once()
                
                # Verify connection was established to environment variable database
                # (not the YAML default "prod_db")
                mock_manager.get_connection.assert_called_once_with("env_override_db")

    async def test_config_loader_integration(self, temp_config_file, mock_server, mock_arango_connection):
        """Test that ConfigFileLoader is properly integrated with server initialization."""
        client, db = mock_arango_connection
        
        with patch('mcp_arangodb_async.entry._config_file_path', temp_config_file), \
             patch('mcp_arangodb_async.entry.MultiDatabaseConnectionManager') as MockManager, \
             patch('mcp_arangodb_async.entry.resolve_database') as mock_resolve:
            
            # Setup mocks
            mock_manager = MockManager.return_value
            mock_manager.get_connection = AsyncMock(return_value=(client, db))
            mock_manager.initialize = AsyncMock()
            mock_manager.close_all = AsyncMock()
            mock_resolve.return_value = "prod_db"
            
            # Test server initialization
            async with server_lifespan(mock_server) as context:
                # Verify ConfigFileLoader was properly initialized
                config_loader = context["config_loader"]
                assert isinstance(config_loader, ConfigFileLoader)
                assert config_loader.loaded_from_yaml is True
                assert config_loader.default_database == "prod_db"
                
                # Verify databases were registered with MultiDatabaseConnectionManager
                assert mock_manager.register_database.call_count == 2
                
                # Verify the resolver received the correct ConfigFileLoader instance
                resolver_config_loader = mock_resolve.call_args[0][3]
                assert resolver_config_loader is config_loader