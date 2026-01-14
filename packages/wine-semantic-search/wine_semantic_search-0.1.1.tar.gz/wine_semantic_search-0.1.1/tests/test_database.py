"""Tests for database service functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from hypothesis import given, strategies as st
from decimal import Decimal
from wine_semantic_search.database import DatabaseService
from wine_semantic_search.models import WineResult


class TestDatabaseService:
    """Test cases for DatabaseService class."""
    
    def test_init(self):
        """Test DatabaseService initialization."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        assert service.database_url == database_url
        assert service.pool is None
    
    @pytest.mark.asyncio
    async def test_initialize_success(self):
        """Test successful database initialization."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        # Create a proper async mock for the pool
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        # Mock the async context manager properly
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        # Mock pgvector extension check
        mock_conn.fetchval.side_effect = [True, 0.5]  # Extension exists, vector operation works
        
        with patch('wine_semantic_search.database.asyncpg.create_pool') as mock_create_pool:
            # Make create_pool return a coroutine that resolves to mock_pool
            async def create_pool_coro(*args, **kwargs):
                return mock_pool
            mock_create_pool.return_value = create_pool_coro()
            
            await service.initialize()
            
        assert service.pool == mock_pool
        # Verify pgvector extension was checked
        assert mock_conn.fetchval.call_count == 2
    
    @pytest.mark.asyncio
    async def test_initialize_connection_failure(self):
        """Test database initialization with connection failure."""
        database_url = "postgresql://invalid:invalid@localhost/invalid"
        service = DatabaseService(database_url)
        
        with patch('wine_semantic_search.database.asyncpg.create_pool', side_effect=Exception("Connection failed")):
            with pytest.raises(RuntimeError, match="Database initialization failed"):
                await service.initialize()
    
    @pytest.mark.asyncio
    async def test_verify_pgvector_extension_missing(self):
        """Test pgvector extension verification when extension is missing."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        # Mock the async context manager properly
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        # Mock extension not found
        mock_conn.fetchval.return_value = False
        
        service.pool = mock_pool
        
        with pytest.raises(RuntimeError, match="pgvector extension is not installed"):
            await service._verify_pgvector_extension()
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test database connection pool closure."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        mock_pool = AsyncMock()
        service.pool = mock_pool
        
        await service.close()
        
        mock_pool.close.assert_called_once()
        assert service.pool is None
    
    @pytest.mark.asyncio
    async def test_health_check_success(self):
        """Test successful health check."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        # Mock the async context manager properly
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        mock_conn.fetchval.return_value = 1
        
        service.pool = mock_pool
        
        result = await service.health_check()
        
        assert result is True
        mock_conn.fetchval.assert_called_once_with("SELECT 1")
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check with database failure."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        # Mock the async context manager properly
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        mock_conn.fetchval.side_effect = Exception("Database error")
        
        service.pool = mock_pool
        
        result = await service.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_no_pool(self):
        """Test health check when pool is not initialized."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        result = await service.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_search_similar_wines_success(self):
        """Test successful wine search with mock database results."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        # Mock the async context manager properly
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        # Mock database query results
        mock_rows = [
            {
                'id': 1,
                'designation': 'Test Wine',
                'description': 'A test wine description',
                'country': 'France',
                'province': 'Bordeaux',
                'region_1': 'Left Bank',
                'region_2': None,
                'variety': 'Cabernet Sauvignon',
                'winery': 'Test Winery',
                'points': 90,
                'price': 25.99,
                'similarity_score': 0.85
            }
        ]
        mock_conn.fetch.return_value = mock_rows
        
        service.pool = mock_pool
        
        results = await service.search_similar_wines([1.0, 2.0, 3.0], limit=10, similarity_threshold=0.7)
        
        assert len(results) == 1
        assert results[0].id == 1
        assert results[0].designation == 'Test Wine'
        assert results[0].similarity_score == 0.85
        
        # Verify the SQL query was called with correct parameters
        mock_conn.fetch.assert_called_once()
        call_args = mock_conn.fetch.call_args
        assert '[1.0,2.0,3.0]' in call_args[0]  # embedding string
        assert 0.7 in call_args[0]  # similarity threshold
        assert 10 in call_args[0]  # limit
    
    @pytest.mark.asyncio
    async def test_search_similar_wines_empty_embedding(self):
        """Test search_similar_wines with empty embedding."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        mock_pool = AsyncMock()
        service.pool = mock_pool
        
        with pytest.raises(ValueError, match="Query embedding cannot be empty"):
            await service.search_similar_wines([])
    
    @pytest.mark.asyncio
    async def test_search_similar_wines_no_pool(self):
        """Test search_similar_wines when pool is not initialized."""
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        with pytest.raises(RuntimeError, match="Database pool not initialized"):
            await service.search_similar_wines([1.0, 2.0, 3.0])

    @given(
        wine_results=st.lists(
            st.builds(
                WineResult,
                id=st.integers(min_value=1, max_value=1000),
                designation=st.text(min_size=1, max_size=100),
                description=st.text(min_size=1, max_size=500),
                country=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
                province=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
                region_1=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
                region_2=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
                variety=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
                winery=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
                points=st.one_of(st.none(), st.integers(min_value=0, max_value=100)),
                price=st.one_of(st.none(), st.decimals(min_value=0, max_value=1000, places=2)),
                similarity_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
            ),
            min_size=2,  # Need at least 2 results to test ordering
            max_size=20
        )
    )
    @pytest.mark.asyncio
    async def test_property_search_result_ordering(self, wine_results):
        """
        Property test: Search results should be ordered by similarity score in descending order.
        
        Feature: wine-semantic-search, Property 2: Search Result Ordering
        Validates: Requirements 2.3
        """
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        # Mock the async context manager properly
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        # Convert WineResult objects to mock database rows
        # Sort by similarity score descending to simulate correct database ordering
        sorted_results = sorted(wine_results, key=lambda x: x.similarity_score, reverse=True)
        mock_rows = []
        for result in sorted_results:
            mock_rows.append({
                'id': result.id,
                'designation': result.designation,
                'description': result.description,
                'country': result.country,
                'province': result.province,
                'region_1': result.region_1,
                'region_2': result.region_2,
                'variety': result.variety,
                'winery': result.winery,
                'points': result.points,
                'price': result.price,
                'similarity_score': result.similarity_score
            })
        
        mock_conn.fetch.return_value = mock_rows
        service.pool = mock_pool
        
        # Execute the search
        results = await service.search_similar_wines([1.0, 2.0, 3.0], limit=len(wine_results))
        
        # Property: Results should be ordered by similarity score in descending order
        for i in range(len(results) - 1):
            assert results[i].similarity_score >= results[i + 1].similarity_score, (
                f"Results not properly ordered: result[{i}].similarity_score "
                f"({results[i].similarity_score}) < result[{i+1}].similarity_score "
                f"({results[i + 1].similarity_score})"
            )

    @given(
        query_embedding=st.one_of(
            # Small embeddings for faster testing
            st.lists(
                st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
                min_size=3,
                max_size=10
            ),
            # Occasionally test with larger embeddings
            st.lists(
                st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
                min_size=512,
                max_size=512
            )
        ),
        limit=st.integers(min_value=1, max_value=50),
        similarity_threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @pytest.mark.asyncio
    async def test_property_vector_similarity_search(self, query_embedding, limit, similarity_threshold):
        """
        Property 4: Vector Similarity Search
        For any search query, the system should use vector similarity operations (not text matching) 
        to find semantically related wines.
        
        Feature: wine-semantic-search, Property 4: Vector Similarity Search
        Validates: Requirements 2.2
        """
        database_url = "postgresql://test:test@localhost/test"
        service = DatabaseService(database_url)
        
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        # Mock the async context manager properly
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        # Mock database query results - simulate vector similarity search results
        mock_rows = [
            {
                'id': 1,
                'designation': 'Vector Wine 1',
                'description': 'A wine found through vector similarity',
                'country': 'France',
                'province': 'Bordeaux',
                'region_1': 'Left Bank',
                'region_2': None,
                'variety': 'Cabernet Sauvignon',
                'winery': 'Vector Winery',
                'points': 90,
                'price': 25.99,
                'similarity_score': 0.85
            }
        ]
        mock_conn.fetch.return_value = mock_rows
        
        service.pool = mock_pool
        
        # Execute the search
        results = await service.search_similar_wines(
            query_embedding=query_embedding,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        # Verify that the search uses vector similarity operations
        mock_conn.fetch.assert_called_once()
        call_args = mock_conn.fetch.call_args
        sql_query = call_args[0][0]
        
        # Property: The system should use vector similarity operations (not text matching)
        # Verify that the SQL query uses pgvector similarity operators
        assert "<->" in sql_query, "Query should use pgvector cosine distance operator (<->)"
        assert "vector" in sql_query.lower(), "Query should reference vector data type"
        assert "embedding" in sql_query.lower(), "Query should use embedding column for similarity"
        
        # Verify that the query uses vector similarity calculation for scoring
        assert "(1 - (we.embedding <-> $1::vector))" in sql_query, (
            "Query should calculate similarity score using vector distance"
        )
        
        # Verify that results are ordered by vector similarity (not text matching)
        assert "ORDER BY we.embedding <-> $1::vector" in sql_query, (
            "Results should be ordered by vector similarity distance"
        )
        
        # Verify that the embedding parameter is properly formatted as a vector
        embedding_param = call_args[0][1]  # The embedding string parameter
        assert embedding_param.startswith('[') and embedding_param.endswith(']'), (
            "Embedding should be formatted as vector array"
        )
        
        # Verify that similarity threshold is applied using vector operations
        assert similarity_threshold in call_args[0], (
            "Similarity threshold should be applied to vector similarity score"
        )
        
        # Verify that the WHERE clause filters by vector similarity score
        assert "WHERE (1 - (we.embedding <-> $1::vector)) >= $2" in sql_query, (
            "Query should filter results by vector similarity threshold"
        )
        
        # Verify that the query joins wine and wine_embeddings tables for vector search
        assert "INNER JOIN wine_embeddings we ON w.id = we.wine_id" in sql_query, (
            "Query should join wine data with embeddings for vector search"
        )
        
        # Verify that no text-based matching operations are used
        assert "LIKE" not in sql_query.upper(), "Query should not use text LIKE operations"
        assert "ILIKE" not in sql_query.upper(), "Query should not use case-insensitive text matching"
        assert "MATCH" not in sql_query.upper(), "Query should not use full-text search matching"
        assert "SIMILAR TO" not in sql_query.upper(), "Query should not use regex text matching"
        
        # Verify that the results contain similarity scores calculated from vector operations
        if results:
            for result in results:
                assert hasattr(result, 'similarity_score'), "Results should include vector similarity scores"
                assert 0.0 <= result.similarity_score <= 1.0, (
                    f"Similarity score should be between 0 and 1, got {result.similarity_score}"
                )