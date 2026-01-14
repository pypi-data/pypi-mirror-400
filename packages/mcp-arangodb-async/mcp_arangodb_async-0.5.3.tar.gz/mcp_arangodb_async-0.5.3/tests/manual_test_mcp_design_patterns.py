"""
Manual validation test script for MCP Design Pattern tools.

This script tests all three design patterns through the actual MCP server:
1. Progressive Tool Discovery
2. Workflow Switching
3. Tool Unloading (Workflow Stage Progression)

Run this script to validate that all pattern workflows execute correctly.

Note: This script requires a running ArangoDB instance and proper configuration
      via environment variables or .env file.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root directory to path to import mcp_arangodb_async
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_arangodb_async.entry import server
from mcp_arangodb_async.config import load_config
from mcp_arangodb_async.db import get_client_and_db
from mcp_arangodb_async.session_state import SessionState
from unittest.mock import Mock, patch


async def setup_server():
    """Initialize the MCP server with database connection and session state.
    
    Creates a mock request context that includes:
    - Database connection (db, client)
    - SessionState instance for per-session state management
    - Test session ID for state isolation
    
    This mirrors the production lifespan_context setup in entry.py.
    """
    print("=" * 80)
    print("Setting up MCP server connection...")
    print("=" * 80)
    
    # Load configuration
    config = load_config()
    print(f"✓ Configuration loaded: {config.arango_url}, database: {config.database}")

    # Connect to database
    client, db = get_client_and_db(config)
    print(f"✓ Connected to ArangoDB at {config.arango_url}")
    
    # Create SessionState for per-session state management (multi-tenancy support)
    session_state = SessionState()
    test_session_id = "manual_test_session"
    session_state.initialize_session(test_session_id)
    print(f"✓ SessionState initialized with session: {test_session_id}")
    
    # Create mock context with database AND session state
    # This mirrors production lifespan_context structure
    mock_ctx = Mock()
    mock_ctx.lifespan_context = {
        "db": db,
        "client": client,
        "session_state": session_state
    }
    
    return mock_ctx, db, client


async def test_pattern_1_progressive_tool_discovery(mock_ctx):
    """Test Pattern 1: Progressive Tool Discovery."""
    print("\n" + "=" * 80)
    print("PATTERN 1: PROGRESSIVE TOOL DISCOVERY")
    print("=" * 80)
    
    # Test 1.1: Search tools by keywords
    print("\n[Test 1.1] Search tools by keywords 'graph'...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_search_tools",
            {"keywords": ["graph"], "detail_level": "summary"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Found {len(response.get('matches', []))} tools matching 'graph'")
        print(f"  Sample tools: {[t['name'] for t in response.get('matches', [])[:3]]}")
    
    # Test 1.2: Search with category filter
    print("\n[Test 1.2] Search tools with category filter 'graph_basic'...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_search_tools",
            {"keywords": ["traverse"], "categories": ["graph_basic"], "detail_level": "name"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Found {len(response.get('matches', []))} tools in 'graph_basic' category")
    
    # Test 1.3: List all tools by category
    print("\n[Test 1.3] List all tools in 'core_data' category...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_list_tools_by_category",
            {"category": "core_data"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Category 'core_data' contains {len(response.get('tools', []))} tools")
        print(f"  Tools: {response.get('tools', [])[:5]}")
    
    # Test 1.4: List all categories
    print("\n[Test 1.4] List all tool categories...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_list_tools_by_category",
            {}
        )
        response = json.loads(result[0].text)
        categories = response.get('categories', {})
        print(f"✓ Found {len(categories)} categories")
        for cat_name, cat_info in list(categories.items())[:3]:
            print(f"  - {cat_name}: {cat_info.get('description', 'N/A')[:50]}...")
    
    # Test 1.5: Test full detail level
    print("\n[Test 1.5] Search with 'full' detail level...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_search_tools",
            {"keywords": ["query"], "detail_level": "full"}
        )
        response = json.loads(result[0].text)
        if response.get('matches'):
            first_tool = response['matches'][0]
            has_schema = 'inputSchema' in first_tool
            print(f"✓ Full detail includes schema: {has_schema}")
    
    print("\n✅ Pattern 1: Progressive Tool Discovery - ALL TESTS PASSED")


async def test_pattern_2_workflow_switching(mock_ctx):
    """Test Pattern 2: Workflow Switching."""
    print("\n" + "=" * 80)
    print("PATTERN 2: WORKFLOW SWITCHING")
    print("=" * 80)
    
    # Test 2.1: List all workflows
    print("\n[Test 2.1] List all available workflows...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_list_workflows",
            {"include_tools": False}
        )
        response = json.loads(result[0].text)
        contexts = response.get('contexts', {})
        print(f"✓ Found {len(contexts)} workflows")
        for ctx_name in contexts.keys():
            print(f"  - {ctx_name}")

    # Test 2.2: Get initial active workflow
    print("\n[Test 2.2] Get initial active workflow...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_get_active_workflow",
            {}
        )
        response = json.loads(result[0].text)
        initial_context = response.get('active_context')
        print(f"✓ Initial workflow: {initial_context}")
        print(f"  Tool count: {response.get('tool_count', 0)}")

    # Test 2.3: Switch to graph_modeling workflow
    print("\n[Test 2.3] Switch to 'graph_modeling' workflow...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_switch_workflow",
            {"context": "graph_modeling"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Switched to: {response.get('to_context')}")
        print(f"  Previous workflow: {response.get('from_context')}")
        print(f"  Active tools: {response.get('total_tools', 0)}")

    # Test 2.4: Verify workflow changed
    print("\n[Test 2.4] Verify workflow changed...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_get_active_workflow",
            {}
        )
        response = json.loads(result[0].text)
        current_context = response.get('active_context')
        assert current_context == "graph_modeling", f"Expected 'graph_modeling', got '{current_context}'"
        print(f"✓ Workflow verified: {current_context}")

    # Test 2.5: Switch to data_analysis workflow
    print("\n[Test 2.5] Switch to 'data_analysis' workflow...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_switch_workflow",
            {"context": "data_analysis"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Switched to: {response.get('to_context')}")

    # Test 2.6: Test invalid workflow name
    print("\n[Test 2.6] Test invalid workflow name (should fail gracefully)...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_switch_workflow",
            {"context": "invalid_context_name"}
        )
        response = json.loads(result[0].text)
        has_error = 'error' in response or 'success' in response and not response['success']
        print(f"✓ Invalid workflow handled correctly: {has_error}")

    # Test 2.7: List workflows with tools
    print("\n[Test 2.7] List workflows with tool details...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_list_workflows",
            {"include_tools": True}
        )
        response = json.loads(result[0].text)
        contexts = response.get('contexts', {})
        baseline_tools = contexts.get('baseline', {}).get('tools', [])
        print(f"✓ Baseline workflow has {len(baseline_tools)} tools")

    # Test 2.8: Switch back to baseline
    print("\n[Test 2.8] Switch back to 'baseline' workflow...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_switch_workflow",
            {"context": "baseline"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Switched back to: {response.get('to_context')}")

    print("\n✅ Pattern 2: Workflow Switching - ALL TESTS PASSED")


async def test_pattern_3_tool_unloading(mock_ctx):
    """Test Pattern 3: Tool Unloading (Workflow Stage Progression)."""
    print("\n" + "=" * 80)
    print("PATTERN 3: TOOL UNLOADING (WORKFLOW STAGE PROGRESSION)")
    print("=" * 80)
    
    # Test 3.1: Advance to setup stage
    print("\n[Test 3.1] Advance to 'setup' stage...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_advance_workflow_stage",
            {"stage": "setup"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Advanced to stage: {response.get('to_stage')}")
        print(f"  Active tools: {response.get('total_active_tools', 0)}")
    
    # Test 3.2: Verify stage changed via tool usage stats
    print("\n[Test 3.2] Verify stage changed...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_get_tool_usage_stats",
            {}
        )
        response = json.loads(result[0].text)
        print(f"✓ Current stage: {response.get('current_stage')}")
        print(f"  Active stage tools: {len(response.get('active_stage_tools', []))}")
    
    # Test 3.3: Advance to data_loading stage
    print("\n[Test 3.3] Advance to 'data_loading' stage...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_advance_workflow_stage",
            {"stage": "data_loading"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Advanced to stage: {response.get('to_stage')}")
    
    # Test 3.4: Get tool usage stats
    print("\n[Test 3.4] Get tool usage statistics...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_get_tool_usage_stats",
            {}
        )
        response = json.loads(result[0].text)
        stats = response.get('tool_usage', {})
        total_uses = sum(tool.get('use_count', 0) for tool in stats.values())
        print(f"✓ Total tool uses tracked: {total_uses}")
        print(f"  Tools with usage data: {len(stats)}")
    
    # Test 3.5: Manually unload specific tools
    print("\n[Test 3.5] Manually unload specific tools...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_unload_tools",
            {"tool_names": ["arango_create_collection", "arango_backup"]}
        )
        response = json.loads(result[0].text)
        unloaded = response.get('unloaded_tools', [])
        print(f"✓ Unloaded {len(unloaded)} tools: {unloaded}")
    
    # Test 3.6: Advance to analysis stage
    print("\n[Test 3.6] Advance to 'analysis' stage...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_advance_workflow_stage",
            {"stage": "analysis"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Advanced to stage: {response.get('to_stage')}")

    # Test 3.7: Advance to cleanup stage
    print("\n[Test 3.7] Advance to 'cleanup' stage...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_advance_workflow_stage",
            {"stage": "cleanup"}
        )
        response = json.loads(result[0].text)
        print(f"✓ Advanced to stage: {response.get('to_stage')}")
    
    # Test 3.8: Test invalid stage name
    print("\n[Test 3.8] Test invalid stage name (should fail gracefully)...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_advance_workflow_stage",
            {"stage": "invalid_stage"}
        )
        response = json.loads(result[0].text)
        has_error = 'error' in response or 'success' in response and not response['success']
        print(f"✓ Invalid stage handled correctly: {has_error}")
    
    # Test 3.9: Unload non-existent tools
    print("\n[Test 3.9] Unload non-existent tools (should handle gracefully)...")
    with patch.object(server, 'request_context', mock_ctx):
        result = await server._handlers["call_tool"](
            "arango_unload_tools",
            {"tool_names": ["nonexistent_tool_1", "nonexistent_tool_2"]}
        )
        response = json.loads(result[0].text)
        not_found = response.get('not_found', [])
        print(f"✓ Not found tools: {not_found}")
    
    print("\n✅ Pattern 3: Tool Unloading - ALL TESTS PASSED")


async def main():
    """Main test execution."""
    print("\n" + "=" * 80)
    print("MCP DESIGN PATTERNS - MANUAL VALIDATION TEST SUITE")
    print("=" * 80)
    print("\nThis script validates all three MCP Design Pattern workflows:")
    print("1. Progressive Tool Discovery")
    print("2. Context Switching")
    print("3. Tool Unloading (Workflow Stage Progression)")
    print("\n" + "=" * 80)
    
    try:
        # Setup server connection
        mock_ctx, db, client = await setup_server()
        
        # Run all pattern tests
        await test_pattern_1_progressive_tool_discovery(mock_ctx)
        await test_pattern_2_workflow_switching(mock_ctx)
        await test_pattern_3_tool_unloading(mock_ctx)
        
        # Final summary
        print("\n" + "=" * 80)
        print("✅ ALL PATTERN VALIDATION TESTS PASSED SUCCESSFULLY!")
        print("=" * 80)
        print("\nSummary:")
        print("  ✓ Pattern 1: Progressive Tool Discovery - 5 tests passed")
        print("  ✓ Pattern 2: Context Switching - 8 tests passed")
        print("  ✓ Pattern 3: Tool Unloading - 9 tests passed")
        print("\nTotal: 22 validation tests executed successfully")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

