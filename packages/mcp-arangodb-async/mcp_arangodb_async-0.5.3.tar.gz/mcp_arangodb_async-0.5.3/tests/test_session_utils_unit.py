"""Unit tests for session utilities component."""

import pytest
from unittest.mock import Mock, MagicMock
from mcp_arangodb_async.session_utils import extract_session_id


class TestExtractSessionId:
    """Test session ID extraction for different transports."""

    def test_stdio_transport_no_session_attribute(self):
        """Test stdio transport when request_context has no session attribute."""
        request_context = Mock(spec=[])  # No session attribute
        
        result = extract_session_id(request_context)
        
        assert result == "stdio"

    def test_stdio_transport_session_is_none(self):
        """Test stdio transport when session attribute is None."""
        request_context = Mock()
        request_context.session = None
        
        result = extract_session_id(request_context)
        
        assert result == "stdio"

    def test_stdio_transport_session_is_false(self):
        """Test stdio transport when session attribute is falsy."""
        request_context = Mock()
        request_context.session = False
        
        result = extract_session_id(request_context)
        
        assert result == "stdio"

    def test_http_transport_with_session_id(self):
        """Test HTTP transport with valid session ID."""
        request_context = Mock()
        request_context.session = Mock()
        request_context.session.session_id = "http-session-12345"
        
        result = extract_session_id(request_context)
        
        assert result == "http-session-12345"

    def test_http_transport_with_uuid_session_id(self):
        """Test HTTP transport with UUID-style session ID."""
        uuid_session = "550e8400-e29b-41d4-a716-446655440000"
        request_context = Mock()
        request_context.session = Mock()
        request_context.session.session_id = uuid_session
        
        result = extract_session_id(request_context)
        
        assert result == uuid_session

    def test_http_transport_session_id_is_none(self):
        """Test HTTP transport when session_id is None."""
        request_context = Mock()
        request_context.session = Mock()
        request_context.session.session_id = None
        
        result = extract_session_id(request_context)
        
        assert result == "stdio"

    def test_http_transport_session_id_is_empty_string(self):
        """Test HTTP transport when session_id is empty string."""
        request_context = Mock()
        request_context.session = Mock()
        request_context.session.session_id = ""
        
        result = extract_session_id(request_context)
        
        assert result == "stdio"

    def test_http_transport_no_session_id_attribute(self):
        """Test HTTP transport when session has no session_id attribute."""
        request_context = Mock()
        request_context.session = Mock(spec=[])  # No session_id attribute
        
        result = extract_session_id(request_context)
        
        assert result == "stdio"

    def test_multiple_calls_same_context_consistent(self):
        """Test that multiple calls with same context return consistent results."""
        request_context = Mock()
        request_context.session = Mock()
        request_context.session.session_id = "consistent-session-id"
        
        result1 = extract_session_id(request_context)
        result2 = extract_session_id(request_context)
        
        assert result1 == result2 == "consistent-session-id"

    def test_different_contexts_different_ids(self):
        """Test that different contexts return different session IDs."""
        context1 = Mock()
        context1.session = Mock()
        context1.session.session_id = "session-1"
        
        context2 = Mock()
        context2.session = Mock()
        context2.session.session_id = "session-2"
        
        result1 = extract_session_id(context1)
        result2 = extract_session_id(context2)
        
        assert result1 == "session-1"
        assert result2 == "session-2"

    def test_simple_namespace_object(self):
        """Test with simple namespace-like object."""
        from types import SimpleNamespace
        
        session = SimpleNamespace(session_id="namespace-session")
        request_context = SimpleNamespace(session=session)
        
        result = extract_session_id(request_context)
        
        assert result == "namespace-session"

    def test_dict_like_object_with_getattr(self):
        """Test with object that supports getattr."""
        class CustomContext:
            def __init__(self):
                self.session = None
        
        request_context = CustomContext()
        
        result = extract_session_id(request_context)
        
        assert result == "stdio"

    def test_session_id_with_special_characters(self):
        """Test session ID with special characters."""
        special_id = "session-id-with-special-chars-!@#$%"
        request_context = Mock()
        request_context.session = Mock()
        request_context.session.session_id = special_id
        
        result = extract_session_id(request_context)
        
        assert result == special_id

    def test_long_session_id(self):
        """Test with very long session ID."""
        long_id = "x" * 1000
        request_context = Mock()
        request_context.session = Mock()
        request_context.session.session_id = long_id
        
        result = extract_session_id(request_context)
        
        assert result == long_id

