"""Property-based tests for MCP server protocol compliance."""

import json
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

import pytest
from hypothesis import given, strategies as st

from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)

from wine_semantic_search.server import WineSearchMCPServer
from wine_semantic_search.config import ServerConfig
from wine_semantic_search.models import WineResult


class TestMCPProtocolCompliance:
    """Property-based tests for MCP protocol compliance."""

    def create_test_server(self) -> WineSearchMCPServer:
        """Create a test server instance with mocked dependencies."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            max_results=50,
            similarity_threshold=0.7
        )
        
        server = WineSearchMCPServer(config)
        
        # Mock the embedding service
        server.embedding_service = AsyncMock()
        server.embedding_service.generate_embedding = AsyncMock()
        server.embedding_service.validate_api_key = AsyncMock(return_value=True)
        server.embedding_service.close = AsyncMock()
        
        # Mock the database service
        server.database_service = AsyncMock()
        server.database_service.initialize = AsyncMock()
        server.database_service.search_similar_wines = AsyncMock()
        server.database_service.close = AsyncMock()
        
        return server

    @given(
        query=st.text(min_size=1, max_size=500),
        limit=st.integers(min_value=1, max_value=50)
    )
    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_tool_execution(self, query: str, limit: int):
        """
        Property 5: MCP Protocol Compliance
        For any MCP protocol interaction (tool discovery, execution, initialization), 
        the server should respond with properly formatted messages according to the MCP specification.
        **Feature: wine-semantic-search, Property 5: MCP Protocol Compliance**
        **Validates: Requirements 4.1, 4.3, 4.4**
        """
        server = self.create_test_server()
        
        # Mock embedding generation
        mock_embedding = [0.1] * 512
        server.embedding_service.generate_embedding.return_value = mock_embedding
        
        # Mock database search results
        mock_wine_results = [
            WineResult(
                id=1,
                designation="Test Wine",
                description="A test wine description",
                country="France",
                province="Bordeaux",
                region_1="Margaux",
                region_2=None,
                variety="Cabernet Sauvignon",
                winery="Test Winery",
                points=90,
                price=Decimal("50.00"),
                similarity_score=0.85
            )
        ]
        server.database_service.search_similar_wines.return_value = mock_wine_results
        
        # Test tool execution with valid arguments
        arguments = {"query": query.strip() or "default query", "limit": limit}
        
        try:
            result = await server._handle_search_wines(arguments)
            
            # Verify MCP protocol compliance for successful responses
            assert isinstance(result, CallToolResult)
            assert hasattr(result, 'content')
            assert isinstance(result.content, list)
            assert len(result.content) >= 1
            
            # Verify content structure
            content = result.content[0]
            assert isinstance(content, TextContent)
            assert content.type == "text"
            assert isinstance(content.text, str)
            assert len(content.text) > 0
            
            # Verify the response contains expected wine information
            if mock_wine_results:
                assert "Test Wine" in content.text
                assert "Test Winery" in content.text
                assert "0.850" in content.text  # similarity score
            
            # Verify embedding service was called correctly
            server.embedding_service.generate_embedding.assert_called_once()
            call_args = server.embedding_service.generate_embedding.call_args[0]
            assert isinstance(call_args[0], str)
            assert len(call_args[0].strip()) > 0
            
            # Verify database service was called correctly
            server.database_service.search_similar_wines.assert_called_once()
            db_call_args = server.database_service.search_similar_wines.call_args
            assert db_call_args[1]['query_embedding'] == mock_embedding
            assert db_call_args[1]['limit'] == limit
            assert 'similarity_threshold' in db_call_args[1]
            
        except ValueError as e:
            # For invalid inputs, verify proper error handling
            assert "Invalid arguments" in str(e) or "Query parameter" in str(e) or "Limit must be" in str(e)
        except RuntimeError as e:
            # For runtime errors, verify proper error handling
            assert "Search operation failed" in str(e)

    @given(
        invalid_query=st.one_of(
            st.none(),
            st.just(""),
            st.just("   "),  # whitespace only
            st.integers(),  # wrong type
            st.lists(st.text())  # wrong type
        ),
        invalid_limit=st.one_of(
            st.integers(max_value=0),  # too small
            st.integers(min_value=51),  # too large
            st.text(),  # wrong type
            st.none()  # when required
        )
    )
    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_error_handling(self, invalid_query: Any, invalid_limit: Any):
        """
        Property 5: MCP Protocol Compliance - Error Handling
        For any invalid MCP tool parameters, the server should handle errors gracefully 
        and return meaningful error messages according to MCP specification.
        **Feature: wine-semantic-search, Property 5: MCP Protocol Compliance**
        **Validates: Requirements 4.3, 4.4**
        """
        server = self.create_test_server()
        
        # Test with invalid query
        if invalid_query is not None:
            arguments = {"query": invalid_query, "limit": 10}
        else:
            arguments = {"limit": 10}  # missing required query
        
        with pytest.raises(ValueError) as exc_info:
            await server._handle_search_wines(arguments)
        
        # Verify error message is meaningful and doesn't expose internal details
        error_message = str(exc_info.value)
        assert "Invalid arguments" in error_message
        assert len(error_message) > 0
        assert "Query parameter" in error_message or "required" in error_message.lower()
        
        # Test with invalid limit (if query is valid)
        if isinstance(invalid_query, str) and invalid_query.strip():
            arguments = {"query": invalid_query.strip(), "limit": invalid_limit}
            
            with pytest.raises(ValueError) as exc_info:
                await server._handle_search_wines(arguments)
            
            error_message = str(exc_info.value)
            assert "Invalid arguments" in error_message
            assert "Limit must be" in error_message or "integer" in error_message.lower()

    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_tool_discovery(self):
        """
        Property 5: MCP Protocol Compliance - Tool Discovery
        For any tool discovery request, the server should return properly formatted 
        tool definitions according to MCP specification.
        **Feature: wine-semantic-search, Property 5: MCP Protocol Compliance**
        **Validates: Requirements 4.1, 4.2**
        """
        server = self.create_test_server()
        
        # Get the list_tools handler from the server
        list_tools_handler = None
        for handler_info in server.server._list_tools_handlers:
            list_tools_handler = handler_info.handler
            break
        
        assert list_tools_handler is not None, "list_tools handler should be registered"
        
        # Call the handler
        result = await list_tools_handler()
        
        # Verify MCP protocol compliance for tool discovery
        assert isinstance(result, ListToolsResult)
        assert hasattr(result, 'tools')
        assert isinstance(result.tools, list)
        assert len(result.tools) == 1  # Should have exactly one tool
        
        # Verify tool definition structure
        tool = result.tools[0]
        assert isinstance(tool, Tool)
        assert tool.name == "search_wines"
        assert isinstance(tool.description, str)
        assert len(tool.description) > 0
        
        # Verify input schema structure
        assert hasattr(tool, 'inputSchema')
        schema = tool.inputSchema
        assert isinstance(schema, dict)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        
        # Verify query parameter definition
        properties = schema["properties"]
        assert "query" in properties
        query_prop = properties["query"]
        assert query_prop["type"] == "string"
        assert isinstance(query_prop["description"], str)
        assert len(query_prop["description"]) > 0
        
        # Verify limit parameter definition
        assert "limit" in properties
        limit_prop = properties["limit"]
        assert limit_prop["type"] == "integer"
        assert limit_prop["minimum"] == 1
        assert limit_prop["maximum"] == 50
        assert limit_prop["default"] == 10
        assert isinstance(limit_prop["description"], str)
        
        # Verify required fields
        assert schema["required"] == ["query"]

    @given(
        wine_count=st.integers(min_value=0, max_value=10),
        similarity_scores=st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=0,
            max_size=10
        )
    )
    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_response_format(self, wine_count: int, similarity_scores: List[float]):
        """
        Property 5: MCP Protocol Compliance - Response Format
        For any search results, the server should return responses in the standard MCP format 
        with proper content structure.
        **Feature: wine-semantic-search, Property 5: MCP Protocol Compliance**
        **Validates: Requirements 4.4, 5.2**
        """
        server = self.create_test_server()
        
        # Mock embedding generation
        mock_embedding = [0.2] * 512
        server.embedding_service.generate_embedding.return_value = mock_embedding
        
        # Create mock wine results based on generated data
        mock_wine_results = []
        for i in range(min(wine_count, len(similarity_scores))):
            wine = WineResult(
                id=i + 1,
                designation=f"Generated Wine {i + 1}",
                description=f"Generated description for wine {i + 1}",
                country="France",
                province="Bordeaux",
                region_1=f"Region {i + 1}",
                region_2=None,
                variety="Merlot",
                winery=f"Winery {i + 1}",
                points=85 + i,
                price=Decimal(f"{25.00 + i * 5:.2f}"),
                similarity_score=similarity_scores[i] if i < len(similarity_scores) else 0.8
            )
            mock_wine_results.append(wine)
        
        server.database_service.search_similar_wines.return_value = mock_wine_results
        
        # Test with valid arguments
        arguments = {"query": "test wine query", "limit": 10}
        result = await server._handle_search_wines(arguments)
        
        # Verify MCP protocol compliance for response format
        assert isinstance(result, CallToolResult)
        assert hasattr(result, 'content')
        assert isinstance(result.content, list)
        assert len(result.content) == 1
        
        # Verify content structure
        content = result.content[0]
        assert isinstance(content, TextContent)
        assert content.type == "text"
        assert isinstance(content.text, str)
        
        if wine_count == 0 or len(similarity_scores) == 0:
            # Verify empty results message
            assert "No wines found" in content.text
            assert "test wine query" in content.text
        else:
            # Verify results are properly formatted
            result_count = min(wine_count, len(similarity_scores))
            assert f"Found {result_count} wine(s)" in content.text
            
            # Verify each wine result is included
            for i in range(result_count):
                assert f"Generated Wine {i + 1}" in content.text
                assert f"Generated description for wine {i + 1}" in content.text
                assert f"Winery {i + 1}" in content.text
                
                # Verify similarity score is formatted correctly
                expected_score = similarity_scores[i] if i < len(similarity_scores) else 0.8
                score_str = f"{expected_score:.3f}"
                assert score_str in content.text

    @given(
        embedding_failure=st.booleans(),
        database_failure=st.booleans()
    )
    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_service_failures(self, embedding_failure: bool, database_failure: bool):
        """
        Property 5: MCP Protocol Compliance - Service Failure Handling
        For any service failures (embedding or database), the server should handle errors 
        gracefully according to MCP specification without exposing internal details.
        **Feature: wine-semantic-search, Property 5: MCP Protocol Compliance**
        **Validates: Requirements 4.4, 6.3, 6.5**
        """
        server = self.create_test_server()
        
        # Configure service failures
        if embedding_failure:
            server.embedding_service.generate_embedding.side_effect = Exception("Embedding service error")
        else:
            server.embedding_service.generate_embedding.return_value = [0.3] * 512
        
        if database_failure:
            server.database_service.search_similar_wines.side_effect = Exception("Database connection failed")
        else:
            server.database_service.search_similar_wines.return_value = []
        
        # Test with valid arguments
        arguments = {"query": "test query", "limit": 5}
        
        if embedding_failure or database_failure:
            # Should raise RuntimeError for service failures
            with pytest.raises(RuntimeError) as exc_info:
                await server._handle_search_wines(arguments)
            
            # Verify error message is appropriate and doesn't expose internal details
            error_message = str(exc_info.value)
            assert "Search operation failed" in error_message
            assert len(error_message) > 0
            
            # Verify internal error details are not exposed
            assert "Embedding service error" not in error_message
            assert "Database connection failed" not in error_message
            assert "traceback" not in error_message.lower()
            assert "exception" not in error_message.lower()
        else:
            # Should succeed with empty results
            result = await server._handle_search_wines(arguments)
            
            assert isinstance(result, CallToolResult)
            assert len(result.content) == 1
            content = result.content[0]
            assert isinstance(content, TextContent)
            assert "No wines found" in content.text

    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_initialization(self):
        """
        Property 5: MCP Protocol Compliance - Server Initialization
        For any server initialization, the server should properly initialize all components 
        and handle initialization failures gracefully.
        **Feature: wine-semantic-search, Property 5: MCP Protocol Compliance**
        **Validates: Requirements 4.5, 7.3**
        """
        # Test successful initialization
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            max_results=50,
            similarity_threshold=0.7
        )
        
        server = WineSearchMCPServer(config)
        
        # Mock successful service initialization
        server.embedding_service = AsyncMock()
        server.embedding_service.validate_api_key = AsyncMock(return_value=True)
        server.embedding_service.close = AsyncMock()
        
        server.database_service = AsyncMock()
        server.database_service.initialize = AsyncMock()
        server.database_service.close = AsyncMock()
        
        # Test successful initialization
        await server.initialize()
        
        # Verify services were initialized
        server.embedding_service.validate_api_key.assert_called_once()
        server.database_service.initialize.assert_called_once()
        
        # Test cleanup
        await server.cleanup()
        server.embedding_service.close.assert_called_once()
        server.database_service.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_initialization_failures(self):
        """
        Property 5: MCP Protocol Compliance - Initialization Failure Handling
        For any initialization failures, the server should handle them gracefully 
        and provide meaningful error messages.
        **Feature: wine-semantic-search, Property 5: MCP Protocol Compliance**
        **Validates: Requirements 4.5, 7.3, 7.4**
        """
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="invalid-key",
            max_results=50,
            similarity_threshold=0.7
        )
        
        server = WineSearchMCPServer(config)
        
        # Mock API key validation failure
        server.embedding_service = AsyncMock()
        server.embedding_service.validate_api_key = AsyncMock(return_value=False)
        server.embedding_service.close = AsyncMock()
        
        server.database_service = AsyncMock()
        server.database_service.initialize = AsyncMock()
        server.database_service.close = AsyncMock()
        
        # Test initialization failure
        with pytest.raises(RuntimeError) as exc_info:
            await server.initialize()
        
        # Verify error message is meaningful
        error_message = str(exc_info.value)
        assert "Server initialization failed" in error_message
        assert "OpenAI API key validation failed" in error_message
        
        # Verify cleanup was called even on failure
        server.embedding_service.close.assert_called_once()
        server.database_service.close.assert_called_once()

    @given(
        tool_name=st.text(min_size=1, max_size=100),
        arguments=st.dictionaries(
            st.text(min_size=1, max_size=50),
            st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
            min_size=0,
            max_size=5
        )
    )
    @pytest.mark.asyncio
    async def test_mcp_protocol_compliance_unknown_tool_handling(self, tool_name: str, arguments: Dict[str, Any]):
        """
        Property 5: MCP Protocol Compliance - Unknown Tool Handling
        For any unknown tool requests, the server should handle them gracefully 
        with appropriate error messages.
        **Feature: wine-semantic-search, Property 5: MCP Protocol Compliance**
        **Validates: Requirements 4.3, 4.4**
        """
        server = self.create_test_server()
        
        # Skip if tool name is the valid one
        if tool_name == "search_wines":
            return
        
        # Get the call_tool handler from the server
        call_tool_handler = None
        for handler_info in server.server._call_tool_handlers:
            call_tool_handler = handler_info.handler
            break
        
        assert call_tool_handler is not None, "call_tool handler should be registered"
        
        # Test with unknown tool name
        with pytest.raises(ValueError) as exc_info:
            await call_tool_handler(tool_name, arguments)
        
        # Verify error message is appropriate
        error_message = str(exc_info.value)
        assert "Unknown tool" in error_message
        assert tool_name in error_message
        assert len(error_message) > 0