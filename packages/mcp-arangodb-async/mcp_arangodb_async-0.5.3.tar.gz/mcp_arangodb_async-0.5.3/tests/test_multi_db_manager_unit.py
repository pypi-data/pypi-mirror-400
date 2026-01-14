"""Unit tests for MultiDatabaseConnectionManager component."""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from mcp_arangodb_async.multi_db_manager import MultiDatabaseConnectionManager, DatabaseConfig


class TestMultiDatabaseConnectionManager:
    """Test MultiDatabaseConnectionManager for multi-database connection pooling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.db_configs = {
            "production": DatabaseConfig(
                url="http://prod:8529",
                database="prod_db",
                username="prod_user",
                password_env="PROD_PASSWORD",
                timeout=60.0
            ),
            "staging": DatabaseConfig(
                url="http://staging:8529",
                database="staging_db",
                username="staging_user",
                password_env="STAGING_PASSWORD",
                timeout=30.0
            )
        }

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PROD_PASSWORD": "prod_pass", "STAGING_PASSWORD": "staging_pass"})
    @patch('mcp_arangodb_async.multi_db_manager.ArangoClient')
    async def test_initialize(self, mock_arango_client):
        """Test initialization with database configurations."""
        manager = MultiDatabaseConnectionManager()
        
        for key, config in self.db_configs.items():
            manager.register_database(key, config)
        
        await manager.initialize()
        
        assert len(manager.get_configured_databases()) == 2
        assert "production" in manager.get_configured_databases()
        assert "staging" in manager.get_configured_databases()

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PROD_PASSWORD": "prod_pass"})
    @patch('mcp_arangodb_async.multi_db_manager.ArangoClient')
    async def test_get_connection_creates_new(self, mock_arango_client):
        """Test get_connection creates new connection if not in pool."""
        mock_client = Mock()
        mock_db = Mock()
        mock_db.version.return_value = "3.11.0"
        mock_client.db.return_value = mock_db
        mock_arango_client.return_value = mock_client
        
        manager = MultiDatabaseConnectionManager()
        manager.register_database("production", self.db_configs["production"])
        await manager.initialize()
        
        client, db = await manager.get_connection("production")
        
        assert client == mock_client
        assert db == mock_db
        mock_arango_client.assert_called_once_with(
            hosts="http://prod:8529",
            request_timeout=60.0
        )
        mock_client.db.assert_called_once_with(
            "prod_db",
            username="prod_user",
            password="prod_pass"
        )

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PROD_PASSWORD": "prod_pass"})
    @patch('mcp_arangodb_async.multi_db_manager.ArangoClient')
    async def test_get_connection_reuses_existing(self, mock_arango_client):
        """Test get_connection reuses existing connection from pool."""
        mock_client = Mock()
        mock_db = Mock()
        mock_db.version.return_value = "3.11.0"
        mock_client.db.return_value = mock_db
        mock_arango_client.return_value = mock_client
        
        manager = MultiDatabaseConnectionManager()
        manager.register_database("production", self.db_configs["production"])
        await manager.initialize()
        
        # First call creates connection
        client1, db1 = await manager.get_connection("production")
        
        # Second call reuses connection
        client2, db2 = await manager.get_connection("production")
        
        assert client1 is client2
        assert db1 is db2
        # ArangoClient should only be called once
        assert mock_arango_client.call_count == 1

    @pytest.mark.asyncio
    async def test_get_connection_unknown_database(self):
        """Test get_connection raises error for unknown database."""
        manager = MultiDatabaseConnectionManager()
        await manager.initialize()
        
        with pytest.raises(KeyError, match="unknown_db"):
            await manager.get_connection("unknown_db")

    def test_get_configured_databases(self):
        """Test get_configured_databases returns all registered databases."""
        manager = MultiDatabaseConnectionManager()
        
        for key, config in self.db_configs.items():
            manager.register_database(key, config)
        
        configs = manager.get_configured_databases()
        
        assert len(configs) == 2
        assert "production" in configs
        assert "staging" in configs
        assert configs["production"].url == "http://prod:8529"
        assert configs["staging"].url == "http://staging:8529"

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PROD_PASSWORD": "prod_pass"})
    @patch('mcp_arangodb_async.multi_db_manager.ArangoClient')
    async def test_test_connection_success(self, mock_arango_client):
        """Test test_connection returns version on success."""
        mock_client = Mock()
        mock_db = Mock()
        mock_db.version.return_value = "3.11.0"
        mock_client.db.return_value = mock_db
        mock_arango_client.return_value = mock_client
        
        manager = MultiDatabaseConnectionManager()
        manager.register_database("production", self.db_configs["production"])
        await manager.initialize()
        
        result = await manager.test_connection("production")
        
        assert result["connected"] is True
        assert result["version"] == "3.11.0"
        assert "error" not in result

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PROD_PASSWORD": "prod_pass"})
    @patch('mcp_arangodb_async.multi_db_manager.ArangoClient')
    async def test_test_connection_failure(self, mock_arango_client):
        """Test test_connection returns error on failure."""
        mock_client = Mock()
        mock_db = Mock()
        mock_db.version.side_effect = Exception("Connection failed")
        mock_client.db.return_value = mock_db
        mock_arango_client.return_value = mock_client

        manager = MultiDatabaseConnectionManager()
        manager.register_database("production", self.db_configs["production"])
        await manager.initialize()

        result = await manager.test_connection("production")

        assert result["connected"] is False
        assert "error" in result
        assert "Connection failed" in result["error"]

    def test_register_database(self):
        """Test register_database adds configuration."""
        manager = MultiDatabaseConnectionManager()

        manager.register_database("test_db", self.db_configs["production"])

        configs = manager.get_configured_databases()
        assert "test_db" in configs
        assert configs["test_db"].url == "http://prod:8529"

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PROD_PASSWORD": "prod_pass"})
    @patch('mcp_arangodb_async.multi_db_manager.ArangoClient')
    async def test_close_all(self, mock_arango_client):
        """Test close_all closes all connections."""
        mock_client = Mock()
        mock_db = Mock()
        mock_db.version.return_value = "3.11.0"
        mock_client.db.return_value = mock_db
        mock_client.close = Mock()
        mock_arango_client.return_value = mock_client

        manager = MultiDatabaseConnectionManager()
        manager.register_database("production", self.db_configs["production"])
        await manager.initialize()

        # Create connection
        await manager.get_connection("production")

        # Close all
        await manager.close_all()

        # Verify client.close() was called
        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    @patch.dict(os.environ, {"PROD_PASSWORD": "prod_pass", "STAGING_PASSWORD": "staging_pass"})
    @patch('mcp_arangodb_async.multi_db_manager.ArangoClient')
    async def test_concurrent_access_safety(self, mock_arango_client):
        """Test async lock safety with concurrent access."""
        mock_client = Mock()
        mock_db = Mock()
        mock_db.version.return_value = "3.11.0"
        mock_client.db.return_value = mock_db
        mock_arango_client.return_value = mock_client

        manager = MultiDatabaseConnectionManager()
        manager.register_database("production", self.db_configs["production"])
        await manager.initialize()

        # Simulate concurrent connection requests
        async def get_conn():
            return await manager.get_connection("production")

        # Run concurrent operations
        results = await asyncio.gather(
            get_conn(),
            get_conn(),
            get_conn()
        )

        # All should return the same connection
        assert all(r[0] is results[0][0] for r in results)
        assert all(r[1] is results[0][1] for r in results)
        # ArangoClient should only be called once despite concurrent requests
        assert mock_arango_client.call_count == 1

