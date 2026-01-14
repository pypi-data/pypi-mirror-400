"""Main MCP server implementation for wine semantic search."""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ServerCapabilities,
)

from .config import ServerConfig
from .database import DatabaseService
from .embedding import EmbeddingService
from .errors import format_error_response, create_validation_error, create_database_error, create_embedding_error
from .logging_config import log_request_start, log_request_success, log_request_error, sanitize_for_logging
from .models import WineResult


logger = logging.getLogger(__name__)


class WineSearchMCPServer:
    """MCP server for wine semantic search functionality."""
    
    def __init__(self, config: ServerConfig):
        """Initialize the wine search MCP server.
        
        Args:
            config: Server configuration with database and API settings
        """
        logger.info("Initializing WineSearchMCPServer")
        logger.debug(f"Configuration: {sanitize_for_logging(config.__dict__)}")
        
        self.config = config
        self.server = Server("wine-semantic-search")
        self.embedding_service = EmbeddingService(config.openai_api_key)
        self.database_service = DatabaseService(config.database_url)
        
        # Register MCP protocol handlers
        self._register_handlers()
        
        logger.info("WineSearchMCPServer initialized successfully")
    
    def _register_handlers(self) -> None:
        """Register MCP protocol handlers and tools."""
        logger.debug("Registering MCP protocol handlers")
        
        # Register tool list handler
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """Handle MCP list_tools request."""
            logger.debug("Handling list_tools request")
            tools = [
                Tool(
                    name="search_wines",
                    description="Search for wines using natural language descriptions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language description of desired wine characteristics"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return (default: 10, max: 50)",
                                "minimum": 1,
                                "maximum": 50,
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]
            logger.debug(f"Returning {len(tools)} available tools")
            return ListToolsResult(tools=tools)
        
        # Register tool call handler
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle MCP call_tool request."""
            logger.info(f"Handling call_tool request for tool: {name}")
            logger.debug(f"Tool arguments: {sanitize_for_logging(arguments)}")
            
            try:
                if name == "search_wines":
                    return await self._handle_search_wines(arguments)
                else:
                    logger.error(f"Unknown tool requested: {name}")
                    raise create_validation_error(
                        field="tool_name",
                        message=f"Unknown tool: {name}",
                        value=name
                    )
            except Exception as e:
                # Format error using the new error response system
                error_response = format_error_response(
                    error=e,
                    operation=f"call_tool_{name}",
                    request_id=None  # MCP doesn't provide request ID in this context
                )
                # Re-raise as ValueError for MCP to handle consistently
                if hasattr(e, 'error_code'):  # WineSearchError
                    raise ValueError(e.message)
                else:
                    raise ValueError(str(e))
        
        logger.debug("MCP protocol handlers registered successfully")
    
    async def _handle_search_wines(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle search_wines tool execution.
        
        Args:
            arguments: Tool arguments containing query and optional limit
            
        Returns:
            CallToolResult with wine search results
            
        Raises:
            ValueError: If arguments are invalid
            RuntimeError: If search operation fails
        """
        start_time = time.time()
        operation = "search_wines_tool"
        
        try:
            # Log request start with sanitized arguments
            log_request_start(
                logger, 
                operation,
                arguments=sanitize_for_logging(arguments)
            )
            
            # Validate and extract arguments
            query = arguments.get("query")
            if not query or not isinstance(query, str) or not query.strip():
                raise create_validation_error(
                    field="query",
                    message="Query parameter is required and must be a non-empty string",
                    value=query
                )
            
            limit = arguments.get("limit", 10)
            if not isinstance(limit, int) or limit < 1 or limit > self.config.max_results:
                raise create_validation_error(
                    field="limit",
                    message=f"Limit must be an integer between 1 and {self.config.max_results}",
                    value=limit
                )
            
            query = query.strip()
            logger.info(f"Processing wine search query", extra={
                "query_length": len(query),
                "limit": limit,
                "similarity_threshold": self.config.similarity_threshold
            })
            
            # Generate embedding for the query
            embedding_start = time.time()
            try:
                query_embedding = await self.embedding_service.generate_embedding(query)
            except Exception as e:
                raise create_embedding_error("generate_query_embedding", e)
            embedding_duration = (time.time() - embedding_start) * 1000
            
            logger.debug(f"Generated embedding in {embedding_duration:.2f}ms", extra={
                "embedding_dimensions": len(query_embedding)
            })
            
            # Search for similar wines
            search_start = time.time()
            try:
                wine_results = await self.database_service.search_similar_wines(
                    query_embedding=query_embedding,
                    limit=limit,
                    similarity_threshold=self.config.similarity_threshold
                )
            except Exception as e:
                raise create_database_error("search_similar_wines", e)
            search_duration = (time.time() - search_start) * 1000
            
            logger.info(f"Database search completed in {search_duration:.2f}ms", extra={
                "results_found": len(wine_results),
                "limit_requested": limit
            })
            
            # Format results for MCP response
            if not wine_results:
                logger.info("No wines found matching search criteria")
                content = TextContent(
                    type="text",
                    text=f"No wines found matching the query: '{query}'. Try adjusting your search terms or criteria."
                )
            else:
                # Log result statistics
                if wine_results:
                    similarity_scores = [w.similarity_score for w in wine_results]
                    logger.debug("Search result statistics", extra={
                        "min_similarity": min(similarity_scores),
                        "max_similarity": max(similarity_scores),
                        "avg_similarity": sum(similarity_scores) / len(similarity_scores)
                    })
                
                # Format wine results as structured text
                result_text = f"Found {len(wine_results)} wine(s) matching '{query}':\n\n"
                
                for i, wine in enumerate(wine_results, 1):
                    result_text += f"{i}. {wine.designation}\n"
                    result_text += f"   Description: {wine.description}\n"
                    result_text += f"   Winery: {wine.winery or 'Unknown'}\n"
                    result_text += f"   Variety: {wine.variety or 'Unknown'}\n"
                    result_text += f"   Country: {wine.country or 'Unknown'}\n"
                    if wine.province:
                        result_text += f"   Province: {wine.province}\n"
                    if wine.region_1:
                        result_text += f"   Region: {wine.region_1}\n"
                    if wine.points:
                        result_text += f"   Rating: {wine.points}/100\n"
                    if wine.price:
                        result_text += f"   Price: ${wine.price}\n"
                    result_text += f"   Similarity Score: {wine.similarity_score:.3f}\n\n"
                
                content = TextContent(
                    type="text",
                    text=result_text.strip()
                )
            
            # Log successful completion
            total_duration = (time.time() - start_time) * 1000
            log_request_success(
                logger,
                operation,
                duration_ms=total_duration,
                results_returned=len(wine_results),
                embedding_duration_ms=embedding_duration,
                search_duration_ms=search_duration
            )
            
            return CallToolResult(content=[content])
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
            
            # Format error using the new error response system
            error_response = format_error_response(
                error=e,
                operation=operation,
                request_id=None  # MCP doesn't provide request ID in this context
            )
            
            # Re-raise the original exception for MCP to handle
            # The error formatting and logging has already been done
            if hasattr(e, 'error_code'):  # WineSearchError
                raise ValueError(e.message)
            else:
                raise ValueError(str(e))
    
    async def initialize(self) -> None:
        """Initialize the server and its services.
        
        This method should be called before starting the server to ensure
        all dependencies are properly initialized.
        
        Raises:
            RuntimeError: If initialization fails
        """
        start_time = time.time()
        operation = "server_initialization"
        
        try:
            log_request_start(logger, operation)
            
            # Validate configuration
            logger.debug("Validating server configuration")
            self.config.validate()
            logger.info("Configuration validated successfully")
            
            # Initialize embedding service (validate API key)
            logger.debug("Validating OpenAI API key")
            try:
                api_key_valid = await self.embedding_service.validate_api_key()
                if not api_key_valid:
                    raise create_embedding_error("api_key_validation", 
                                                Exception("OpenAI API key validation failed"))
            except Exception as e:
                if hasattr(e, 'error_code'):  # Already a WineSearchError
                    raise
                else:
                    raise create_embedding_error("api_key_validation", e)
            logger.info("OpenAI API key validated successfully")
            
            # Initialize database service
            logger.debug("Initializing database service")
            try:
                await self.database_service.initialize()
            except Exception as e:
                raise create_database_error("database_initialization", e)
            logger.info("Database service initialized successfully")
            
            duration_ms = (time.time() - start_time) * 1000
            log_request_success(logger, operation, duration_ms=duration_ms)
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
            await self.cleanup()
            
            # Format error using the new error response system
            error_response = format_error_response(
                error=e,
                operation=operation,
                request_id=None
            )
            
            # Re-raise as RuntimeError for consistency with existing API
            if hasattr(e, 'error_code'):  # Already a WineSearchError
                raise RuntimeError(f"Server initialization failed: {e.message}")
            else:
                raise RuntimeError(f"Server initialization failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up server resources."""
        operation = "server_cleanup"
        start_time = time.time()
        
        try:
            log_request_start(logger, operation)
            
            # Close database service
            if self.database_service:
                logger.debug("Closing database service")
                await self.database_service.close()
            
            # Close embedding service
            if self.embedding_service:
                logger.debug("Closing embedding service")
                await self.embedding_service.close()
            
            duration_ms = (time.time() - start_time) * 1000
            log_request_success(logger, operation, duration_ms=duration_ms)
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
    
    async def run(self, transport_options: Optional[Dict[str, Any]] = None) -> None:
        """Run the MCP server with stdio transport.
        
        Args:
            transport_options: Optional transport configuration
        """
        operation = "server_run"
        
        try:
            # Initialize server before running
            await self.initialize()
            
            # Run the MCP server with stdio transport
            logger.info("Starting WineSearchMCPServer - ready to accept connections")
            logger.debug(f"Transport options: {sanitize_for_logging(transport_options or {})}")
            
            # Use stdio_server context manager for communication with Claude Desktop
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="wine-semantic-search",
                        server_version="0.1.0",
                        capabilities=ServerCapabilities(tools={})
                    )
                )
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            log_request_error(logger, operation, e)
            raise
        finally:
            await self.cleanup()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()