"""Unit tests for entry point integration with multi-tenancy components."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from types import SimpleNamespace
from mcp_arangodb_async.session_state import SessionState
from mcp_arangodb_async.multi_db_manager import MultiDatabaseConnectionManager, DatabaseConfig
from mcp_arangodb_async.config_loader import ConfigFileLoader
from mcp_arangodb_async.db_resolver import resolve_database
from mcp_arangodb_async.session_utils import extract_session_id


class TestEntryPointIntegration:
    """Test entry point integration with multi-tenancy components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session_state = SessionState()
        self.config_loader = Mock(spec=ConfigFileLoader)
        self.config_loader.default_database = "production"
        self.config_loader.get_configured_databases.return_value = {}

    def test_implicit_session_creation(self):
        """Test implicit session creation on first tool call."""
        session_id = "test-session"
        
        # Session should not exist initially
        assert not self.session_state.has_session(session_id)
        
        # Initialize session (simulating implicit creation)
        self.session_state.initialize_session(session_id)
        
        # Session should now exist
        assert self.session_state.has_session(session_id)
        assert self.session_state.get_focused_database(session_id) is None
        assert self.session_state.get_active_workflow(session_id) == "baseline"

    def test_session_isolation_across_sessions(self):
        """Test that different sessions have isolated state."""
        session1 = "session-1"
        session2 = "session-2"
        
        self.session_state.initialize_session(session1)
        self.session_state.initialize_session(session2)
        
        # Set different focused databases for each session
        asyncio.run(self.session_state.set_focused_database(session1, "db1"))
        asyncio.run(self.session_state.set_focused_database(session2, "db2"))
        
        # Verify isolation
        assert self.session_state.get_focused_database(session1) == "db1"
        assert self.session_state.get_focused_database(session2) == "db2"

    def test_database_resolution_in_context(self):
        """Test database resolution with session state and config."""
        session_id = "test-session"
        self.session_state.initialize_session(session_id)
        
        # Set focused database
        asyncio.run(self.session_state.set_focused_database(session_id, "staging"))
        
        # Resolve database without tool override
        tool_args = {}
        result = resolve_database(
            tool_args, self.session_state, session_id, self.config_loader
        )
        
        # Should use focused database
        assert result == "staging"

    def test_per_tool_override_does_not_mutate_state(self):
        """Test that per-tool override doesn't change focused database."""
        session_id = "test-session"
        self.session_state.initialize_session(session_id)
        
        # Set focused database
        asyncio.run(self.session_state.set_focused_database(session_id, "production"))
        
        # Use per-tool override
        tool_args = {"database": "analytics"}
        result = resolve_database(
            tool_args, self.session_state, session_id, self.config_loader
        )
        
        # Should use override
        assert result == "analytics"
        
        # Focused database should remain unchanged
        assert self.session_state.get_focused_database(session_id) == "production"

    def test_database_resolution_after_unset(self):
        """Test database resolution falls back to config default after unsetting focused database."""
        session_id = "test-session"
        self.session_state.initialize_session(session_id)

        # Set focused database
        asyncio.run(self.session_state.set_focused_database(session_id, "staging"))
        assert self.session_state.get_focused_database(session_id) == "staging"

        # Verify it uses focused database
        result = resolve_database(
            {}, self.session_state, session_id, self.config_loader
        )
        assert result == "staging"

        # Unset focused database
        asyncio.run(self.session_state.set_focused_database(session_id, None))
        assert self.session_state.get_focused_database(session_id) is None

        # Verify it falls back to config default
        result = resolve_database(
            {}, self.session_state, session_id, self.config_loader
        )
        assert result == "production"  # config_loader.default_database

    def test_session_id_extraction_stdio(self):
        """Test session ID extraction for stdio transport."""
        request_context = SimpleNamespace(session=None)
        
        session_id = extract_session_id(request_context)
        
        assert session_id == "stdio"

    def test_session_id_extraction_http(self):
        """Test session ID extraction for HTTP transport."""
        request_context = SimpleNamespace(
            session=SimpleNamespace(session_id="http-session-123")
        )
        
        session_id = extract_session_id(request_context)
        
        assert session_id == "http-session-123"

    def test_tool_usage_tracking(self):
        """Test tool usage tracking in session state."""
        session_id = "test-session"
        self.session_state.initialize_session(session_id)
        
        # Track tool usage
        self.session_state.track_tool_usage(session_id, "arango_query")
        self.session_state.track_tool_usage(session_id, "arango_query")
        self.session_state.track_tool_usage(session_id, "arango_insert")
        
        # Get stats
        stats = self.session_state.get_tool_usage_stats(session_id)
        
        assert "arango_query" in stats
        assert stats["arango_query"]["use_count"] == 2
        assert "arango_insert" in stats
        assert stats["arango_insert"]["use_count"] == 1

    def test_session_cleanup(self):
        """Test session cleanup on disconnect."""
        session_id = "test-session"
        self.session_state.initialize_session(session_id)
        
        # Set some state
        asyncio.run(self.session_state.set_focused_database(session_id, "production"))
        self.session_state.track_tool_usage(session_id, "arango_query")
        
        # Verify state exists
        assert self.session_state.has_session(session_id)
        
        # Cleanup
        self.session_state.cleanup_session(session_id)
        
        # Verify state is cleaned up
        assert not self.session_state.has_session(session_id)
        assert self.session_state.get_focused_database(session_id) is None

    def test_multiple_concurrent_sessions(self):
        """Test multiple concurrent sessions with independent state."""
        sessions = ["session-1", "session-2", "session-3"]
        
        for session_id in sessions:
            self.session_state.initialize_session(session_id)
        
        # Set different focused databases
        for i, session_id in enumerate(sessions):
            asyncio.run(
                self.session_state.set_focused_database(session_id, f"db-{i}")
            )
        
        # Verify each session has correct state
        for i, session_id in enumerate(sessions):
            assert self.session_state.get_focused_database(session_id) == f"db-{i}"

    def test_lifespan_context_structure(self):
        """Test that lifespan context has all required components."""
        # Simulate what server_lifespan yields
        lifespan_context = {
            "db": None,
            "client": None,
            "session_state": self.session_state,
            "db_manager": Mock(spec=MultiDatabaseConnectionManager),
            "config_loader": self.config_loader,
        }
        
        # Verify all components are present
        assert "session_state" in lifespan_context
        assert "db_manager" in lifespan_context
        assert "config_loader" in lifespan_context
        assert isinstance(lifespan_context["session_state"], SessionState)

