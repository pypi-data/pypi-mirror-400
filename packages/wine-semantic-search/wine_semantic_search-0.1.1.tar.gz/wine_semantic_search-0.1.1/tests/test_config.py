"""Tests for configuration management."""

import os
import pytest
from hypothesis import given, strategies as st
from wine_semantic_search.config import ServerConfig


class TestServerConfig:
    """Test cases for ServerConfig class."""
    
    def test_from_environment_success(self, monkeypatch):
        """Test successful configuration loading from environment."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        
        config = ServerConfig.from_environment()
        
        assert config.database_url == "postgresql://test:test@localhost/test"
        assert config.openai_api_key == "test-api-key"
        assert config.max_results == 50
        assert config.similarity_threshold == 0.7
    
    def test_from_environment_with_optional_params(self, monkeypatch):
        """Test configuration loading with optional parameters."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        monkeypatch.setenv("MAX_RESULTS", "100")
        monkeypatch.setenv("SIMILARITY_THRESHOLD", "0.8")
        
        config = ServerConfig.from_environment()
        
        assert config.max_results == 100
        assert config.similarity_threshold == 0.8
    
    def test_from_environment_missing_database_url(self, monkeypatch):
        """Test error when DATABASE_URL is missing."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
        monkeypatch.delenv("DATABASE_URL", raising=False)
        
        with pytest.raises(ValueError, match="DATABASE_URL environment variable is required"):
            ServerConfig.from_environment()
    
    def test_from_environment_missing_openai_key(self, monkeypatch):
        """Test error when OPENAI_API_KEY is missing."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is required"):
            ServerConfig.from_environment()
    
    def test_validate_success(self):
        """Test successful validation."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key"
        )
        
        # Should not raise any exception
        config.validate()
    
    def test_validate_empty_database_url(self):
        """Test validation error for empty database URL."""
        config = ServerConfig(
            database_url="   ",
            openai_api_key="test-api-key"
        )
        
        with pytest.raises(ValueError, match="Database URL cannot be empty"):
            config.validate()
    
    def test_validate_empty_api_key(self):
        """Test validation error for empty API key."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="   "
        )
        
        with pytest.raises(ValueError, match="OpenAI API key cannot be empty"):
            config.validate()
    
    def test_validate_invalid_max_results(self):
        """Test validation error for invalid max results."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            max_results=0
        )
        
        with pytest.raises(ValueError, match="Max results must be positive"):
            config.validate()
    
    def test_validate_invalid_similarity_threshold(self):
        """Test validation error for invalid similarity threshold."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            similarity_threshold=1.5
        )
        
        with pytest.raises(ValueError, match="Similarity threshold must be between 0.0 and 1.0"):
            config.validate()


class TestServerConfigPropertyBased:
    """Property-based tests for ServerConfig validation."""

    @given(
        database_url=st.one_of(
            st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
            st.just(""),
            st.text(max_size=10).map(lambda x: " " * len(x))  # whitespace-only strings
        ),
        openai_api_key=st.one_of(
            st.text(min_size=1, max_size=200).filter(lambda x: x.strip()),
            st.just(""),
            st.text(max_size=10).map(lambda x: " " * len(x))  # whitespace-only strings
        ),
        max_results=st.integers(),
        similarity_threshold=st.floats(allow_nan=False, allow_infinity=False)
    )
    def test_configuration_validation_property(self, database_url, openai_api_key, max_results, similarity_threshold):
        """
        Property 8: Configuration Validation
        For any invalid or missing configuration, the server should fail to start 
        with clear error messages indicating what configuration is needed.
        **Feature: wine-semantic-search, Property 8: Configuration Validation**
        **Validates: Requirements 7.3, 7.4**
        """
        config = ServerConfig(
            database_url=database_url,
            openai_api_key=openai_api_key,
            max_results=max_results,
            similarity_threshold=similarity_threshold
        )
        
        # Determine if configuration should be valid
        is_valid_db_url = database_url and database_url.strip()
        is_valid_api_key = openai_api_key and openai_api_key.strip()
        is_valid_max_results = max_results > 0
        is_valid_threshold = 0.0 <= similarity_threshold <= 1.0
        
        should_be_valid = (
            is_valid_db_url and 
            is_valid_api_key and 
            is_valid_max_results and 
            is_valid_threshold
        )
        
        if should_be_valid:
            # Should not raise any exception
            config.validate()
        else:
            # Should raise ValueError with descriptive message
            with pytest.raises(ValueError) as exc_info:
                config.validate()
            
            error_message = str(exc_info.value)
            
            # Verify error message is descriptive and indicates what's wrong
            if not is_valid_db_url:
                assert "Database URL" in error_message or "database" in error_message.lower()
            elif not is_valid_api_key:
                assert "API key" in error_message or "openai" in error_message.lower()
            elif not is_valid_max_results:
                assert "results" in error_message.lower() and "positive" in error_message.lower()
            elif not is_valid_threshold:
                assert "threshold" in error_message.lower() and ("0.0" in error_message or "1.0" in error_message)

    @given(
        env_vars=st.dictionaries(
            keys=st.sampled_from(["DATABASE_URL", "OPENAI_API_KEY", "MAX_RESULTS", "SIMILARITY_THRESHOLD"]),
            values=st.one_of(
                st.text(min_size=1, max_size=100).filter(lambda x: '\x00' not in x),
                st.just(""),
                st.none()
            ),
            min_size=0,
            max_size=4
        )
    )
    def test_from_environment_validation_property(self, env_vars):
        """
        Property 8: Configuration Validation (Environment Loading)
        For any missing required environment variables, from_environment should 
        fail with clear error messages.
        **Feature: wine-semantic-search, Property 8: Configuration Validation**
        **Validates: Requirements 7.3, 7.4**
        """
        import os
        
        # Store original environment values
        original_env = {}
        env_keys = ["DATABASE_URL", "OPENAI_API_KEY", "MAX_RESULTS", "SIMILARITY_THRESHOLD"]
        for key in env_keys:
            original_env[key] = os.environ.get(key)
        
        try:
            # Clear all relevant environment variables first
            for key in env_keys:
                if key in os.environ:
                    del os.environ[key]
            
            # Set the provided environment variables
            for key, value in env_vars.items():
                if value is not None:
                    os.environ[key] = value
            
            # Check if required variables are present and non-empty
            has_database_url = env_vars.get("DATABASE_URL") and env_vars["DATABASE_URL"].strip()
            has_openai_key = env_vars.get("OPENAI_API_KEY") and env_vars["OPENAI_API_KEY"].strip()
            
            if has_database_url and has_openai_key:
                # Should succeed (optional params have defaults)
                try:
                    config = ServerConfig.from_environment()
                    assert config.database_url == env_vars["DATABASE_URL"]
                    assert config.openai_api_key == env_vars["OPENAI_API_KEY"]
                except ValueError:
                    # May fail due to invalid optional parameter values, which is acceptable
                    pass
            else:
                # Should fail with descriptive error
                with pytest.raises(ValueError) as exc_info:
                    ServerConfig.from_environment()
                
                error_message = str(exc_info.value)
                
                # Verify error message indicates which required variable is missing
                if not has_database_url:
                    assert "DATABASE_URL" in error_message
                elif not has_openai_key:
                    assert "OPENAI_API_KEY" in error_message
        
        finally:
            # Restore original environment
            for key in env_keys:
                if key in os.environ:
                    del os.environ[key]
                if original_env[key] is not None:
                    os.environ[key] = original_env[key]