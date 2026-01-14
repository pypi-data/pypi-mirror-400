"""Tests for embedding service functionality."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from hypothesis import given, strategies as st, settings
import openai
import httpx
from wine_semantic_search.embedding import EmbeddingService


class TestEmbeddingService:
    """Test cases for EmbeddingService class."""
    
    def test_init_success(self):
        """Test successful EmbeddingService initialization."""
        api_key = "test-api-key"
        service = EmbeddingService(api_key)
        
        assert service.api_key == api_key
        assert service.model == "text-embedding-3-small"
        assert service.dimensions == 512
    
    def test_init_empty_api_key(self):
        """Test EmbeddingService initialization with empty API key."""
        with pytest.raises(ValueError, match="OpenAI API key cannot be empty"):
            EmbeddingService("")
    
    def test_init_whitespace_api_key(self):
        """Test EmbeddingService initialization with whitespace API key."""
        with pytest.raises(ValueError, match="OpenAI API key cannot be empty"):
            EmbeddingService("   ")
    
    @pytest.mark.asyncio
    async def test_generate_embedding_success(self):
        """Test successful embedding generation."""
        service = EmbeddingService("test-api-key")
        
        # Mock the OpenAI client response
        mock_embedding = [0.1, 0.2, 0.3] * 170 + [0.4, 0.5]  # 512 dimensions
        mock_response = AsyncMock()
        mock_response.data = [AsyncMock()]
        mock_response.data[0].embedding = mock_embedding
        
        with patch.object(service.client.embeddings, 'create', return_value=mock_response):
            result = await service.generate_embedding("test text")
            
        assert result == mock_embedding
        assert len(result) == 512
    
    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self):
        """Test embedding generation with empty text."""
        service = EmbeddingService("test-api-key")
        
        with pytest.raises(ValueError, match="Text cannot be empty for embedding generation"):
            await service.generate_embedding("")
    
    @pytest.mark.asyncio
    async def test_generate_embedding_whitespace_text(self):
        """Test embedding generation with whitespace-only text."""
        service = EmbeddingService("test-api-key")
        
        with pytest.raises(ValueError, match="Text cannot be empty for embedding generation"):
            await service.generate_embedding("   ")
    
    @pytest.mark.asyncio
    async def test_generate_embedding_api_failure(self):
        """Test embedding generation with API failure."""
        service = EmbeddingService("test-api-key")
        
        with patch.object(service.client.embeddings, 'create', side_effect=Exception("API Error")):
            with pytest.raises(Exception, match="Embedding generation failed"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_generate_embedding_empty_response(self):
        """Test embedding generation with empty API response."""
        service = EmbeddingService("test-api-key")
        
        mock_response = AsyncMock()
        mock_response.data = []
        
        with patch.object(service.client.embeddings, 'create', return_value=mock_response):
            with pytest.raises(Exception, match="OpenAI API returned empty embedding data"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_generate_embedding_wrong_dimensions(self):
        """Test embedding generation with wrong number of dimensions."""
        service = EmbeddingService("test-api-key")
        
        # Mock response with wrong number of dimensions
        mock_embedding = [0.1, 0.2, 0.3]  # Only 3 dimensions instead of 512
        mock_response = AsyncMock()
        mock_response.data = [AsyncMock()]
        mock_response.data[0].embedding = mock_embedding
        
        with patch.object(service.client.embeddings, 'create', return_value=mock_response):
            with pytest.raises(Exception, match="Expected 512 dimensions, got 3"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_validate_api_key_success(self):
        """Test successful API key validation."""
        service = EmbeddingService("test-api-key")
        
        # Mock successful validation response
        mock_embedding = [0.1] * 512
        mock_response = AsyncMock()
        mock_response.data = [AsyncMock()]
        mock_response.data[0].embedding = mock_embedding
        
        with patch.object(service.client.embeddings, 'create', return_value=mock_response):
            result = await service.validate_api_key()
            
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_api_key_failure(self):
        """Test API key validation failure."""
        service = EmbeddingService("test-api-key")
        
        with patch.object(service.client.embeddings, 'create', side_effect=Exception("Invalid API key")):
            result = await service.validate_api_key()
            
        assert result is False
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test service cleanup."""
        service = EmbeddingService("test-api-key")
        
        with patch.object(service.client, 'close') as mock_close:
            await service.close()
            mock_close.assert_called_once()


class TestEmbeddingServiceOpenAIErrorHandling:
    """Test cases for OpenAI API error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_authentication_error_during_embedding_generation(self):
        """Test handling of authentication errors during embedding generation."""
        service = EmbeddingService("invalid-api-key")
        
        # Mock OpenAI AuthenticationError with proper response object
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 401
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        auth_error = openai.AuthenticationError(
            message="Invalid API key provided",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=auth_error):
            with pytest.raises(Exception, match="Embedding generation failed.*Invalid API key provided"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_authentication_error_during_api_key_validation(self):
        """Test handling of authentication errors during API key validation."""
        service = EmbeddingService("invalid-api-key")
        
        # Mock OpenAI AuthenticationError with proper response object
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 401
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        auth_error = openai.AuthenticationError(
            message="Invalid API key provided",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=auth_error):
            result = await service.validate_api_key()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_during_embedding_generation(self):
        """Test handling of rate limit errors during embedding generation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI RateLimitError with proper response object
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 429
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        rate_limit_error = openai.RateLimitError(
            message="Rate limit exceeded. Please try again later.",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=rate_limit_error):
            with pytest.raises(Exception, match="Embedding generation failed.*Rate limit exceeded"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_rate_limit_error_during_api_key_validation(self):
        """Test handling of rate limit errors during API key validation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI RateLimitError with proper response object
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 429
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        rate_limit_error = openai.RateLimitError(
            message="Rate limit exceeded. Please try again later.",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=rate_limit_error):
            result = await service.validate_api_key()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_api_connection_error_during_embedding_generation(self):
        """Test handling of network connection errors during embedding generation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI APIConnectionError with proper request object
        mock_request = MagicMock(spec=httpx.Request)
        
        connection_error = openai.APIConnectionError(
            message="Connection error: Unable to connect to OpenAI API",
            request=mock_request
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=connection_error):
            with pytest.raises(Exception, match="Embedding generation failed.*Connection error"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_api_connection_error_during_api_key_validation(self):
        """Test handling of network connection errors during API key validation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI APIConnectionError with proper request object
        mock_request = MagicMock(spec=httpx.Request)
        
        connection_error = openai.APIConnectionError(
            message="Connection error: Unable to connect to OpenAI API",
            request=mock_request
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=connection_error):
            result = await service.validate_api_key()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_api_timeout_error_during_embedding_generation(self):
        """Test handling of timeout errors during embedding generation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI APITimeoutError with proper request object
        mock_request = MagicMock(spec=httpx.Request)
        
        timeout_error = openai.APITimeoutError(request=mock_request)
        
        with patch.object(service.client.embeddings, 'create', side_effect=timeout_error):
            with pytest.raises(Exception, match="Embedding generation failed.*Request timed out"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_api_timeout_error_during_api_key_validation(self):
        """Test handling of timeout errors during API key validation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI APITimeoutError with proper request object
        mock_request = MagicMock(spec=httpx.Request)
        
        timeout_error = openai.APITimeoutError(request=mock_request)
        
        with patch.object(service.client.embeddings, 'create', side_effect=timeout_error):
            result = await service.validate_api_key()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_api_status_error_during_embedding_generation(self):
        """Test handling of API status errors (4xx/5xx) during embedding generation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI APIStatusError (covers various HTTP status errors)
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 500
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        status_error = openai.APIStatusError(
            message="The server had an error while processing your request",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=status_error):
            with pytest.raises(Exception, match="Embedding generation failed.*server had an error"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_api_status_error_during_api_key_validation(self):
        """Test handling of API status errors during API key validation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI APIStatusError
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 500
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        status_error = openai.APIStatusError(
            message="The server had an error while processing your request",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=status_error):
            result = await service.validate_api_key()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_bad_request_error_during_embedding_generation(self):
        """Test handling of bad request errors during embedding generation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI BadRequestError
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 400
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        bad_request_error = openai.BadRequestError(
            message="Invalid request: model not found",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=bad_request_error):
            with pytest.raises(Exception, match="Embedding generation failed.*Invalid request"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_permission_denied_error_during_embedding_generation(self):
        """Test handling of permission denied errors during embedding generation."""
        service = EmbeddingService("test-api-key")
        
        # Mock OpenAI PermissionDeniedError
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 403
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        permission_error = openai.PermissionDeniedError(
            message="You don't have access to this model",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=permission_error):
            with pytest.raises(Exception, match="Embedding generation failed.*don't have access"):
                await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_multiple_consecutive_errors(self):
        """Test handling of multiple consecutive API errors."""
        service = EmbeddingService("test-api-key")
        
        # Create mock objects for different error types
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 429
        mock_response.headers = {"x-request-id": "test-request-id"}
        mock_request = MagicMock(spec=httpx.Request)
        
        # Test sequence of different errors
        errors = [
            openai.RateLimitError(message="Rate limit exceeded", response=mock_response, body=None),
            openai.APIConnectionError(message="Connection failed", request=mock_request),
            openai.AuthenticationError(message="Invalid API key", response=mock_response, body=None)
        ]
        
        for error in errors:
            with patch.object(service.client.embeddings, 'create', side_effect=error):
                with pytest.raises(Exception, match="Embedding generation failed"):
                    await service.generate_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_error_logging_during_failures(self):
        """Test that errors are properly logged during API failures."""
        service = EmbeddingService("test-api-key")
        
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.request = MagicMock(spec=httpx.Request)
        mock_response.status_code = 401
        mock_response.headers = {"x-request-id": "test-request-id"}
        
        auth_error = openai.AuthenticationError(
            message="Invalid API key provided",
            response=mock_response,
            body=None
        )
        
        with patch.object(service.client.embeddings, 'create', side_effect=auth_error):
            with patch('wine_semantic_search.embedding.logger') as mock_logger:
                with pytest.raises(Exception):
                    await service.generate_embedding("test text")
                
                # Verify error was logged
                mock_logger.error.assert_called()
                error_call_args = mock_logger.error.call_args[0][0]
                assert "Failed to generate embedding" in error_call_args


class TestEmbeddingServicePropertyBased:
    """Property-based tests for EmbeddingService."""

    @given(
        text=st.text(min_size=1, max_size=1000).filter(lambda x: x.strip())
    )
    @settings(deadline=None, max_examples=100)
    @pytest.mark.asyncio
    async def test_embedding_generation_consistency(self, text):
        """
        Property 1: Embedding Generation Consistency
        For any search query text, generating embeddings multiple times with the same 
        parameters should produce identical vector representations.
        **Feature: wine-semantic-search, Property 1: Embedding Generation Consistency**
        **Validates: Requirements 2.1, 3.4**
        """
        service = EmbeddingService("test-api-key")
        
        # Create a consistent mock embedding based on the text
        # Use hash of text to ensure consistency while still being deterministic
        text_hash = hash(text) % 1000000
        mock_embedding = [(text_hash + i) / 1000000.0 for i in range(512)]
        
        mock_response = AsyncMock()
        mock_response.data = [AsyncMock()]
        mock_response.data[0].embedding = mock_embedding
        
        with patch.object(service.client.embeddings, 'create', return_value=mock_response) as mock_create:
            # Generate embedding first time
            embedding1 = await service.generate_embedding(text)
            
            # Generate embedding second time with same text
            embedding2 = await service.generate_embedding(text)
            
            # Property: Both embeddings should be identical
            assert embedding1 == embedding2, (
                f"Embedding generation not consistent for text: '{text[:50]}...'\n"
                f"First embedding: {embedding1[:5]}...\n"
                f"Second embedding: {embedding2[:5]}..."
            )
            
            # Verify both calls used the same parameters
            assert mock_create.call_count == 2
            call1_kwargs = mock_create.call_args_list[0][1]
            call2_kwargs = mock_create.call_args_list[1][1]
            
            # Verify consistent model parameters
            assert call1_kwargs['model'] == call2_kwargs['model']
            assert call1_kwargs['dimensions'] == call2_kwargs['dimensions']
            assert call1_kwargs['input'] == call2_kwargs['input']
            
            # Verify expected model configuration
            assert call1_kwargs['model'] == "text-embedding-3-small"
            assert call1_kwargs['dimensions'] == 512
            assert call1_kwargs['input'] == text.strip()
            
            # Verify embedding properties
            assert len(embedding1) == 512
            assert len(embedding2) == 512
            assert all(isinstance(x, float) for x in embedding1)
            assert all(isinstance(x, float) for x in embedding2)

    @given(
        texts=st.lists(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            min_size=2,
            max_size=5,
            unique=True
        )
    )
    @settings(deadline=None, max_examples=50)
    @pytest.mark.asyncio
    async def test_embedding_generation_consistency_multiple_texts(self, texts):
        """
        Property 1: Embedding Generation Consistency (Multiple Texts)
        For any set of different texts, each text should consistently produce 
        the same embedding when generated multiple times.
        **Feature: wine-semantic-search, Property 1: Embedding Generation Consistency**
        **Validates: Requirements 2.1, 3.4**
        """
        service = EmbeddingService("test-api-key")
        
        # Store embeddings for each text
        first_embeddings = {}
        second_embeddings = {}
        
        for text in texts:
            # Create consistent mock embedding for this text
            text_hash = hash(text) % 1000000
            mock_embedding = [(text_hash + i) / 1000000.0 for i in range(512)]
            
            mock_response = AsyncMock()
            mock_response.data = [AsyncMock()]
            mock_response.data[0].embedding = mock_embedding
            
            with patch.object(service.client.embeddings, 'create', return_value=mock_response):
                # Generate first embedding
                first_embeddings[text] = await service.generate_embedding(text)
                
                # Generate second embedding for same text
                second_embeddings[text] = await service.generate_embedding(text)
        
        # Property: Each text should produce consistent embeddings
        for text in texts:
            assert first_embeddings[text] == second_embeddings[text], (
                f"Inconsistent embeddings for text: '{text}'\n"
                f"First: {first_embeddings[text][:3]}...\n"
                f"Second: {second_embeddings[text][:3]}..."
            )
            
            # Verify embedding properties
            assert len(first_embeddings[text]) == 512
            assert len(second_embeddings[text]) == 512
            assert all(isinstance(x, float) for x in first_embeddings[text])
            assert all(isinstance(x, float) for x in second_embeddings[text])

    @given(
        api_key=st.one_of(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            st.just(""),
            st.text(max_size=10).map(lambda x: " " * len(x))  # whitespace-only strings
        ),
        text=st.one_of(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            st.just(""),
            st.text(max_size=10).map(lambda x: " " * len(x))  # whitespace-only strings
        )
    )
    @settings(deadline=None, max_examples=50)
    @pytest.mark.asyncio
    async def test_embedding_input_validation_consistency(self, api_key, text):
        """
        Property 1: Embedding Generation Consistency (Input Validation)
        For any invalid inputs, the service should consistently reject them 
        with appropriate error messages.
        **Feature: wine-semantic-search, Property 1: Embedding Generation Consistency**
        **Validates: Requirements 2.1, 3.4**
        """
        # Test API key validation during initialization
        is_valid_api_key = api_key and api_key.strip()
        
        if is_valid_api_key:
            service = EmbeddingService(api_key)
            
            # Test text validation during embedding generation
            is_valid_text = text and text.strip()
            
            if is_valid_text:
                # Valid inputs - should work with proper mocking
                mock_embedding = [0.1] * 512
                mock_response = AsyncMock()
                mock_response.data = [AsyncMock()]
                mock_response.data[0].embedding = mock_embedding
                
                with patch.object(service.client.embeddings, 'create', return_value=mock_response):
                    result = await service.generate_embedding(text)
                    assert len(result) == 512
                    assert all(isinstance(x, float) for x in result)
            else:
                # Invalid text - should consistently raise ValueError
                with pytest.raises(ValueError, match="Text cannot be empty for embedding generation"):
                    await service.generate_embedding(text)
        else:
            # Invalid API key - should consistently raise ValueError during initialization
            with pytest.raises(ValueError, match="OpenAI API key cannot be empty"):
                EmbeddingService(api_key)