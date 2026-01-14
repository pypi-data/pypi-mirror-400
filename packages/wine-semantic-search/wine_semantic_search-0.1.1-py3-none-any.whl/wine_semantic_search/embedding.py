"""Embedding service for OpenAI integration."""

import asyncio
import logging
import time
from typing import List, Optional

from openai import AsyncOpenAI
from openai.types import CreateEmbeddingResponse

from .logging_config import log_request_start, log_request_success, log_request_error, sanitize_for_logging
from .errors import create_embedding_error, create_validation_error


logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using OpenAI's text-embedding-3-small model."""
    
    def __init__(self, api_key: str):
        """Initialize the embedding service with OpenAI API key.
        
        Args:
            api_key: OpenAI API key for authentication
            
        Raises:
            ValueError: If API key is empty or invalid
        """
        if not api_key or not api_key.strip():
            raise ValueError("OpenAI API key cannot be empty")
            
        self.api_key = api_key.strip()
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-small"
        self.dimensions = 512  # Configured to match database schema
        
        logger.info(f"EmbeddingService initialized", extra={
            "model": self.model,
            "dimensions": self.dimensions,
            "api_key_length": len(self.api_key)
        })
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate a vector embedding for the given text.
        
        Args:
            text: Input text to generate embedding for
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            ValueError: If text is empty or None
            Exception: If OpenAI API call fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for embedding generation")
        
        start_time = time.time()
        operation = "embedding_generation"
        text_stripped = text.strip()
        
        try:
            log_request_start(
                logger,
                operation,
                text_length=len(text_stripped),
                model=self.model,
                dimensions=self.dimensions
            )
            
            response: CreateEmbeddingResponse = await self.client.embeddings.create(
                model=self.model,
                input=text_stripped,
                dimensions=self.dimensions
            )
            
            if not response.data or len(response.data) == 0:
                raise create_embedding_error(
                    "openai_api_response",
                    Exception("OpenAI API returned empty embedding data")
                )
                
            embedding = response.data[0].embedding
            
            if len(embedding) != self.dimensions:
                raise create_embedding_error(
                    "embedding_dimensions",
                    Exception(f"Expected {self.dimensions} dimensions, got {len(embedding)}")
                )
            
            duration_ms = (time.time() - start_time) * 1000
            log_request_success(
                logger,
                operation,
                duration_ms=duration_ms,
                embedding_dimensions=len(embedding),
                tokens_used=response.usage.total_tokens if response.usage else None
            )
            
            return embedding
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
            
            # If it's already a WineSearchError, re-raise it
            if hasattr(e, 'error_code'):
                raise
            else:
                raise create_embedding_error("embedding_generation", e)
    
    async def validate_api_key(self) -> bool:
        """Validate that the API key is working by making a test call.
        
        Returns:
            True if API key is valid, False otherwise
        """
        start_time = time.time()
        operation = "api_key_validation"
        
        try:
            log_request_start(logger, operation)
            
            # Make a simple embedding call to validate the key
            test_response = await self.client.embeddings.create(
                model=self.model,
                input="test",
                dimensions=self.dimensions
            )
            
            if test_response.data and len(test_response.data) > 0:
                duration_ms = (time.time() - start_time) * 1000
                log_request_success(
                    logger,
                    operation,
                    duration_ms=duration_ms,
                    tokens_used=test_response.usage.total_tokens if test_response.usage else None
                )
                return True
            else:
                logger.error("OpenAI API key validation failed: empty response")
                return False
                
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
            return False
    
    async def close(self) -> None:
        """Close the OpenAI client and clean up resources."""
        try:
            logger.debug("Closing EmbeddingService")
            await self.client.close()
            logger.info("EmbeddingService closed successfully")
        except Exception as e:
            logger.warning(f"Error closing EmbeddingService: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()