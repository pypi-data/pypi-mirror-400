"""Configuration management with environment variable support."""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .logging_config import sanitize_for_logging
from .errors import create_validation_error


logger = logging.getLogger(__name__)

# Load .env file from project root if it exists
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    load_dotenv(_env_file)


@dataclass
class ServerConfig:
    """Configuration for the wine semantic search MCP server."""
    
    database_url: str
    openai_api_key: str
    max_results: int = 50
    similarity_threshold: float = 0.7
    
    @classmethod
    def from_environment(cls) -> 'ServerConfig':
        """Load configuration from environment variables.
        
        Returns:
            ServerConfig: Configuration instance with values from environment
            
        Raises:
            ValueError: If required environment variables are missing
        """
        logger.debug("Loading configuration from environment variables")
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable is missing")
            raise ValueError("DATABASE_URL environment variable is required")
            
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            logger.error("OPENAI_API_KEY environment variable is missing")
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        # Optional configuration with defaults
        max_results = int(os.getenv('MAX_RESULTS', '50'))
        similarity_threshold = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))
        
        config = cls(
            database_url=database_url,
            openai_api_key=openai_api_key,
            max_results=max_results,
            similarity_threshold=similarity_threshold
        )
        
        logger.info("Configuration loaded successfully", extra={
            "config": sanitize_for_logging(config.__dict__)
        })
        
        return config
    
    def validate(self) -> None:
        """Validate configuration values.
        
        Raises:
            ValueError: If configuration values are invalid
        """
        logger.debug("Validating configuration values")
        
        if not self.database_url.strip():
            logger.error("Database URL is empty")
            raise ValueError("Database URL cannot be empty")
            
        if not self.openai_api_key.strip():
            logger.error("OpenAI API key is empty")
            raise ValueError("OpenAI API key cannot be empty")
            
        if self.max_results <= 0:
            logger.error(f"Invalid max_results value: {self.max_results}")
            raise ValueError("Max results must be positive")
            
        if not 0.0 <= self.similarity_threshold <= 1.0:
            logger.error(f"Invalid similarity_threshold value: {self.similarity_threshold}")
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        
        logger.debug("Configuration validation passed")