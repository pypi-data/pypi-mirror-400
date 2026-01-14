"""Unit tests for database resolver component."""

import os
import pytest
from unittest.mock import Mock, patch
from mcp_arangodb_async.db_resolver import resolve_database
from mcp_arangodb_async.session_state import SessionState
from mcp_arangodb_async.config_loader import ConfigFileLoader
from mcp_arangodb_async.multi_db_manager import DatabaseConfig


class TestResolveDatabase:
    """Test database resolution with 6-level priority fallback."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session_state = SessionState()
        self.session_id = "test_session"
        self.session_state.initialize_session(self.session_id)
        
        # Create mock config loader
        self.config_loader = Mock(spec=ConfigFileLoader)
        self.config_loader.default_database = None
        self.config_loader.get_configured_databases.return_value = {}

    def test_level_1_per_tool_override(self):
        """Test Level 1: Per-tool override takes highest priority."""
        tool_args = {"database": "analytics"}
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "analytics"

    def test_level_1_empty_override_skips_to_level_2(self):
        """Test Level 1: Empty database string skips to next level."""
        tool_args = {"database": ""}
        self.session_state._focused_database[self.session_id] = "production"
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "production"

    def test_level_2_focused_database(self):
        """Test Level 2: Focused database when no tool override."""
        tool_args = {}
        self.session_state._focused_database[self.session_id] = "staging"
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "staging"

    def test_level_3_config_default(self):
        """Test Level 3: Config default when no focused database."""
        tool_args = {}
        self.config_loader.default_database = "production"
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "production"

    @patch.dict(os.environ, {"ARANGO_DB": "env_default"})
    def test_level_4_environment_variable(self):
        """Test Level 4: Environment variable when no config default."""
        tool_args = {}
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "env_default"

    @patch.dict(os.environ, {}, clear=False)
    def test_level_5_first_configured_database(self):
        """Test Level 5: First configured database."""
        # Clear ARANGO_DB to ensure we test level 5 fallback
        if 'ARANGO_DB' in os.environ:
            del os.environ['ARANGO_DB']
            
        tool_args = {}
        config1 = DatabaseConfig(
            url="http://localhost:8529",
            database="db1",
            username="user",
            password_env="PASS"
        )
        config2 = DatabaseConfig(
            url="http://localhost:8529",
            database="db2",
            username="user",
            password_env="PASS"
        )
        self.config_loader.get_configured_databases.return_value = {
            "first": config1,
            "second": config2
        }
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "first"

    @patch.dict(os.environ, {}, clear=False)
    def test_level_6_hardcoded_fallback(self):
        """Test Level 6: Hardcoded fallback to _system."""
        # Clear ARANGO_DB to ensure we test level 6 fallback
        if 'ARANGO_DB' in os.environ:
            del os.environ['ARANGO_DB']
            
        tool_args = {}
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "_system"

    def test_priority_chain_level_1_overrides_all(self):
        """Test that Level 1 override takes precedence over all others."""
        tool_args = {"database": "override"}
        self.session_state._focused_database[self.session_id] = "focused"
        self.config_loader.default_database = "config_default"
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "override"

    def test_priority_chain_level_2_overrides_lower(self):
        """Test that Level 2 focused database overrides lower levels."""
        tool_args = {}
        self.session_state._focused_database[self.session_id] = "focused"
        self.config_loader.default_database = "config_default"
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "focused"

    def test_no_database_key_in_args(self):
        """Test resolution when database key is not in tool_args."""
        tool_args = {"query": "FOR doc IN users RETURN doc"}
        self.config_loader.default_database = "production"
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "production"

    def test_none_focused_database_skips_to_next_level(self):
        """Test that None focused database skips to next level."""
        tool_args = {}
        self.session_state._focused_database[self.session_id] = None
        self.config_loader.default_database = "production"
        
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        assert result == "production"

