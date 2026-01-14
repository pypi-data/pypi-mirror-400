"""Unit tests for per-tool database override functionality.

Tests verify that:
1. Per-tool database override works correctly (Level 1 of resolution)
2. Per-tool override does NOT mutate focused_database state
3. Database resolution respects the 6-level priority fallback
"""

import pytest
from unittest.mock import Mock, patch
from mcp_arangodb_async.db_resolver import resolve_database
from mcp_arangodb_async.session_state import SessionState
from mcp_arangodb_async.config_loader import ConfigFileLoader


class TestPerToolDatabaseOverride:
    """Test per-tool database override functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.session_state = SessionState()
        self.session_id = "test_session"
        self.session_state.initialize_session(self.session_id)

        # Create mock config loader
        self.config_loader = Mock(spec=ConfigFileLoader)
        self.config_loader.default_database = "default_db"
        self.config_loader.get_configured_databases.return_value = {
            "default_db": {},
            "analytics": {},
            "staging": {}
        }

    @pytest.mark.asyncio
    async def test_per_tool_override_takes_precedence(self):
        """Test that per-tool database override takes highest priority."""
        # Set focused database
        await self.session_state.set_focused_database(self.session_id, "staging")

        # Tool args with database override
        tool_args = {"database": "analytics", "query": "FOR doc IN users RETURN doc"}

        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )

        assert result == "analytics"

    @pytest.mark.asyncio
    async def test_per_tool_override_does_not_mutate_state(self):
        """Test that per-tool override does NOT mutate focused_database state.

        This is a critical requirement: per-tool overrides are temporary and
        should not affect the session's focused database.
        """
        # Set focused database
        await self.session_state.set_focused_database(self.session_id, "staging")
        
        # Verify initial state
        assert self.session_state.get_focused_database(self.session_id) == "staging"
        
        # Use per-tool override
        tool_args = {"database": "analytics", "query": "FOR doc IN users RETURN doc"}
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )
        
        # Verify override was used
        assert result == "analytics"
        
        # Verify focused database was NOT mutated
        assert self.session_state.get_focused_database(self.session_id) == "staging"

    @pytest.mark.asyncio
    async def test_per_tool_override_empty_string_skips_to_next_level(self):
        """Test that empty string database override skips to next level."""
        await self.session_state.set_focused_database(self.session_id, "staging")

        tool_args = {"database": "", "query": "FOR doc IN users RETURN doc"}
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )

        # Should fall back to focused database (Level 2)
        assert result == "staging"

    @pytest.mark.asyncio
    async def test_per_tool_override_none_skips_to_next_level(self):
        """Test that None database override skips to next level."""
        await self.session_state.set_focused_database(self.session_id, "staging")

        tool_args = {"database": None, "query": "FOR doc IN users RETURN doc"}
        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )

        # Should fall back to focused database (Level 2)
        assert result == "staging"

    def test_per_tool_override_without_focused_database(self):
        """Test per-tool override when no focused database is set."""
        # No focused database set
        tool_args = {"database": "analytics"}

        result = resolve_database(
            tool_args, self.session_state, self.session_id, self.config_loader
        )

        assert result == "analytics"

    @pytest.mark.asyncio
    async def test_multiple_tool_calls_with_different_overrides(self):
        """Test multiple tool calls with different database overrides."""
        await self.session_state.set_focused_database(self.session_id, "default_db")
        
        # First tool call with override
        tool_args_1 = {"database": "analytics"}
        result_1 = resolve_database(
            tool_args_1, self.session_state, self.session_id, self.config_loader
        )
        assert result_1 == "analytics"
        
        # Second tool call with different override
        tool_args_2 = {"database": "staging"}
        result_2 = resolve_database(
            tool_args_2, self.session_state, self.session_id, self.config_loader
        )
        assert result_2 == "staging"
        
        # Third tool call without override (should use focused)
        tool_args_3 = {}
        result_3 = resolve_database(
            tool_args_3, self.session_state, self.session_id, self.config_loader
        )
        assert result_3 == "default_db"
        
        # Verify focused database unchanged
        assert self.session_state.get_focused_database(self.session_id) == "default_db"

    def test_per_tool_override_with_all_model_types(self):
        """Test that database parameter works with different tool model types."""
        # Test with various tool argument patterns
        test_cases = [
            {"database": "analytics", "query": "FOR doc IN users RETURN doc"},
            {"database": "staging", "collection": "users"},
            {"database": "analytics", "collection": "orders", "document": {"name": "test"}},
            {"database": "staging", "graph": "social", "start_vertex": "users/1"},
        ]
        
        for tool_args in test_cases:
            result = resolve_database(
                tool_args, self.session_state, self.session_id, self.config_loader
            )
            assert result == tool_args["database"]

