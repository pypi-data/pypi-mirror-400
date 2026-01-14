"""Main entry point for the wine semantic search MCP server."""

import argparse
import asyncio
import logging
import os
import signal
import sys
from typing import Optional

from .config import ServerConfig
from .logging_config import setup_logging, log_request_start, log_request_success, log_request_error
from .server import WineSearchMCPServer


logger = logging.getLogger(__name__)

# Global server instance for signal handling
_server_instance: Optional[WineSearchMCPServer] = None
_shutdown_event: Optional[asyncio.Event] = None


def setup_signal_handlers() -> None:
    """Set up signal handlers for graceful shutdown."""
    global _shutdown_event
    
    def signal_handler(signum: int, frame) -> None:
        """Handle shutdown signals."""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name} signal, initiating graceful shutdown...")
        
        if _shutdown_event:
            _shutdown_event.set()
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    # On Unix systems, also handle SIGHUP for configuration reload
    if hasattr(signal, 'SIGHUP'):
        signal.signal(signal.SIGHUP, signal_handler)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Wine Semantic Search MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  DATABASE_URL          PostgreSQL connection URL (required)
  OPENAI_API_KEY        OpenAI API key for embeddings (required)
  MAX_RESULTS           Maximum search results to return (default: 50)
  SIMILARITY_THRESHOLD  Minimum similarity score for results (default: 0.7)
  LOG_LEVEL            Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  LOG_FILE             Path to log file (optional, logs to stdout if not set)
  LOG_FORMAT           Log format: 'structured' or 'simple' (default: structured)

Examples:
  wine-search-server                    # Start server with default settings
  wine-search-server --log-level DEBUG # Start with debug logging
  wine-search-server --validate-config # Validate configuration and exit
        """
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=None,
        help="Set logging level (overrides LOG_LEVEL environment variable)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Path to log file (overrides LOG_FILE environment variable)"
    )
    
    parser.add_argument(
        "--log-format",
        choices=["structured", "simple"],
        default=None,
        help="Log format type (overrides LOG_FORMAT environment variable)"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit without starting server"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Wine Semantic Search MCP Server 0.1.0"
    )
    
    return parser.parse_args()


async def validate_configuration() -> bool:
    """Validate server configuration without starting the server.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    try:
        print("Validating configuration...")
        
        # Load configuration
        config = ServerConfig.from_environment()
        print("✓ Configuration loaded from environment variables")
        
        # Validate configuration values
        config.validate()
        print("✓ Configuration values are valid")
        
        # Test database connection
        from .database import DatabaseService
        db_service = DatabaseService(config.database_url)
        try:
            await db_service.initialize()
            print("✓ Database connection successful")
            print("✓ pgvector extension is available")
            await db_service.close()
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
        
        # Test OpenAI API key
        from .embedding import EmbeddingService
        embedding_service = EmbeddingService(config.openai_api_key)
        try:
            api_key_valid = await embedding_service.validate_api_key()
            if api_key_valid:
                print("✓ OpenAI API key is valid")
            else:
                print("✗ OpenAI API key validation failed")
                return False
            await embedding_service.close()
        except Exception as e:
            print(f"✗ OpenAI API key validation failed: {e}")
            return False
        
        print("\n✓ All configuration checks passed!")
        print(f"  - Database URL: {config.database_url[:20]}...")
        print(f"  - Max results: {config.max_results}")
        print(f"  - Similarity threshold: {config.similarity_threshold}")
        
        return True
        
    except Exception as e:
        print(f"✗ Configuration validation failed: {e}")
        return False


async def main() -> None:
    """Main entry point for the wine semantic search MCP server."""
    global _server_instance, _shutdown_event
    
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up logging with command-line overrides
    log_level = args.log_level or os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = args.log_file or os.getenv("LOG_FILE")
    log_format = args.log_format or os.getenv("LOG_FORMAT", "structured")
    
    setup_logging(level=log_level, format_type=log_format, log_file=log_file)
    
    # Handle configuration validation mode
    if args.validate_config:
        success = await validate_configuration()
        sys.exit(0 if success else 1)
    
    logger.info("Starting Wine Semantic Search MCP Server")
    logger.info(f"Log level: {log_level}, Format: {log_format}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")
    
    # Set up signal handlers for graceful shutdown
    _shutdown_event = asyncio.Event()
    setup_signal_handlers()
    
    server = None
    try:
        # Load configuration from environment
        log_request_start(logger, "configuration_loading")
        config = ServerConfig.from_environment()
        log_request_success(logger, "configuration_loading")
        
        # Create and initialize server
        log_request_start(logger, "server_initialization")
        server = WineSearchMCPServer(config)
        _server_instance = server
        await server.initialize()
        log_request_success(logger, "server_initialization")
        
        # Run the server with graceful shutdown support
        logger.info("Wine Semantic Search MCP Server is ready to accept connections")
        logger.info("Press Ctrl+C to shutdown gracefully")
        
        # Create server task
        server_task = asyncio.create_task(server.run())
        
        # Wait for either server completion or shutdown signal
        done, pending = await asyncio.wait(
            [server_task, asyncio.create_task(_shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel any pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Check if server task completed with an exception
        for task in done:
            if task == server_task and not task.cancelled():
                try:
                    await task  # This will raise any exception that occurred
                except Exception as e:
                    logger.error(f"Server task failed: {e}")
                    raise
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal (Ctrl+C)")
    except Exception as e:
        log_request_error(logger, "server_startup", e)
        logger.critical("Server failed to start, exiting")
        sys.exit(1)
    finally:
        if server:
            logger.info("Shutting down server...")
            try:
                await server.cleanup()
                logger.info("Server cleanup completed successfully")
            except Exception as e:
                logger.error(f"Error during server cleanup: {e}")
        
        _server_instance = None
        logger.info("Wine Semantic Search MCP Server shutdown complete")


def run_server() -> None:
    """Synchronous entry point for running the server."""
    try:
        # Handle both Windows and Unix event loops
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass  # Handled in main()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_server()