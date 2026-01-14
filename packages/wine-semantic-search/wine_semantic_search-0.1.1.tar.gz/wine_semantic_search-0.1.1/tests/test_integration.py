"""Integration tests for core services working together."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal
from wine_semantic_search.database import DatabaseService
from wine_semantic_search.embedding import EmbeddingService
from wine_semantic_search.config import ServerConfig
from wine_semantic_search.models import WineResult


class TestCoreServicesIntegration:
    """Integration tests for database and embedding services working together."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_search_flow(self):
        """Test complete end-to-end flow from query to embedding to search results."""
        # Setup configuration
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            max_results=10,
            similarity_threshold=0.7
        )
        
        # Initialize services
        embedding_service = EmbeddingService(config.openai_api_key)
        database_service = DatabaseService(config.database_url)
        
        # Mock embedding service response
        query_text = "fruity red wine from France"
        mock_embedding = [0.1, 0.2, 0.3] * 170 + [0.4, 0.5]  # 512 dimensions
        
        mock_embedding_response = AsyncMock()
        mock_embedding_response.data = [AsyncMock()]
        mock_embedding_response.data[0].embedding = mock_embedding
        
        # Mock database service response
        mock_wine_results = [
            {
                'id': 1,
                'designation': 'Château Margaux 2015',
                'description': 'A fruity and elegant red wine from Bordeaux with notes of blackcurrant and cedar',
                'country': 'France',
                'province': 'Bordeaux',
                'region_1': 'Margaux',
                'region_2': None,
                'variety': 'Cabernet Sauvignon Blend',
                'winery': 'Château Margaux',
                'points': 95,
                'price': Decimal('299.99'),
                'similarity_score': 0.92
            },
            {
                'id': 2,
                'designation': 'Domaine de la Côte Pinot Noir 2018',
                'description': 'Bright red fruit flavors with earthy undertones from Burgundy',
                'country': 'France',
                'province': 'Burgundy',
                'region_1': 'Côte de Beaune',
                'region_2': None,
                'variety': 'Pinot Noir',
                'winery': 'Domaine de la Côte',
                'points': 88,
                'price': Decimal('45.99'),
                'similarity_score': 0.85
            }
        ]
        
        # Setup database service mocks
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        mock_conn.fetch.return_value = mock_wine_results
        database_service.pool = mock_pool
        
        # Execute end-to-end flow
        with patch.object(embedding_service.client.embeddings, 'create', return_value=mock_embedding_response):
            # Step 1: Generate embedding from query
            query_embedding = await embedding_service.generate_embedding(query_text)
            
            # Step 2: Search for similar wines using the embedding
            search_results = await database_service.search_similar_wines(
                query_embedding=query_embedding,
                limit=config.max_results,
                similarity_threshold=config.similarity_threshold
            )
        
        # Verify the complete flow worked
        assert len(search_results) == 2
        
        # Verify first result
        first_result = search_results[0]
        assert first_result.id == 1
        assert first_result.designation == 'Château Margaux 2015'
        assert 'fruity' in first_result.description.lower()
        assert first_result.country == 'France'
        assert first_result.similarity_score == 0.92
        
        # Verify second result
        second_result = search_results[1]
        assert second_result.id == 2
        assert second_result.designation == 'Domaine de la Côte Pinot Noir 2018'
        assert 'red fruit' in second_result.description.lower()
        assert second_result.country == 'France'
        assert second_result.similarity_score == 0.85
        
        # Verify results are ordered by similarity (descending)
        assert first_result.similarity_score >= second_result.similarity_score
        
        # Verify embedding was generated correctly
        assert len(query_embedding) == 512
        assert query_embedding == mock_embedding
        
        # Verify database query was called with correct parameters
        mock_conn.fetch.assert_called_once()
        call_args = mock_conn.fetch.call_args[0]
        assert '[0.1,0.2,0.3' in call_args[1]  # embedding string starts correctly
        assert config.similarity_threshold in call_args  # similarity threshold passed
        assert config.max_results in call_args  # limit passed
    
    @pytest.mark.asyncio
    async def test_integration_with_empty_search_results(self):
        """Test integration when no wines match the similarity threshold."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            max_results=10,
            similarity_threshold=0.9  # High threshold
        )
        
        embedding_service = EmbeddingService(config.openai_api_key)
        database_service = DatabaseService(config.database_url)
        
        # Mock embedding generation
        query_text = "very specific wine that doesn't exist"
        mock_embedding = [0.5] * 512
        
        mock_embedding_response = AsyncMock()
        mock_embedding_response.data = [AsyncMock()]
        mock_embedding_response.data[0].embedding = mock_embedding
        
        # Mock empty database results
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        mock_conn.fetch.return_value = []  # No results
        database_service.pool = mock_pool
        
        # Execute flow
        with patch.object(embedding_service.client.embeddings, 'create', return_value=mock_embedding_response):
            query_embedding = await embedding_service.generate_embedding(query_text)
            search_results = await database_service.search_similar_wines(
                query_embedding=query_embedding,
                limit=config.max_results,
                similarity_threshold=config.similarity_threshold
            )
        
        # Verify empty results are handled correctly
        assert len(search_results) == 0
        assert isinstance(search_results, list)
        
        # Verify embedding was still generated
        assert len(query_embedding) == 512
        assert query_embedding == mock_embedding
    
    @pytest.mark.asyncio
    async def test_integration_error_handling_embedding_failure(self):
        """Test integration error handling when embedding generation fails."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="invalid-key",
            max_results=10,
            similarity_threshold=0.7
        )
        
        embedding_service = EmbeddingService(config.openai_api_key)
        database_service = DatabaseService(config.database_url)
        
        # Mock embedding service to fail
        with patch.object(embedding_service.client.embeddings, 'create', side_effect=Exception("API Error")):
            with pytest.raises(Exception, match="Embedding generation failed"):
                await embedding_service.generate_embedding("test query")
        
        # Database service should still be functional
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        mock_conn.fetch.return_value = []
        database_service.pool = mock_pool
        
        # Database search should work with pre-generated embedding
        test_embedding = [0.1] * 512
        results = await database_service.search_similar_wines(test_embedding)
        assert isinstance(results, list)
    
    @pytest.mark.asyncio
    async def test_integration_error_handling_database_failure(self):
        """Test integration error handling when database search fails."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            max_results=10,
            similarity_threshold=0.7
        )
        
        embedding_service = EmbeddingService(config.openai_api_key)
        database_service = DatabaseService(config.database_url)
        
        # Mock successful embedding generation
        mock_embedding = [0.1] * 512
        mock_embedding_response = AsyncMock()
        mock_embedding_response.data = [AsyncMock()]
        mock_embedding_response.data[0].embedding = mock_embedding
        
        # Mock database failure
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        mock_conn.fetch.side_effect = Exception("Database connection failed")
        database_service.pool = mock_pool
        
        # Test the flow
        with patch.object(embedding_service.client.embeddings, 'create', return_value=mock_embedding_response):
            # Embedding generation should succeed
            query_embedding = await embedding_service.generate_embedding("test query")
            assert len(query_embedding) == 512
            
            # Database search should fail gracefully
            with pytest.raises(RuntimeError, match="Wine search failed"):
                await database_service.search_similar_wines(query_embedding)
    
    @pytest.mark.asyncio
    async def test_integration_with_different_similarity_thresholds(self):
        """Test integration with various similarity thresholds."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            max_results=10,
            similarity_threshold=0.8
        )
        
        embedding_service = EmbeddingService(config.openai_api_key)
        database_service = DatabaseService(config.database_url)
        
        # Mock embedding generation
        mock_embedding = [0.2] * 512
        mock_embedding_response = AsyncMock()
        mock_embedding_response.data = [AsyncMock()]
        mock_embedding_response.data[0].embedding = mock_embedding
        
        # Mock database results with different similarity scores
        mock_results_high_threshold = [
            {
                'id': 1,
                'designation': 'High Similarity Wine',
                'description': 'Very similar wine',
                'country': 'France',
                'province': 'Bordeaux',
                'region_1': None,
                'region_2': None,
                'variety': 'Merlot',
                'winery': 'Test Winery',
                'points': 90,
                'price': Decimal('50.00'),
                'similarity_score': 0.95
            }
        ]
        
        mock_results_low_threshold = mock_results_high_threshold + [
            {
                'id': 2,
                'designation': 'Medium Similarity Wine',
                'description': 'Somewhat similar wine',
                'country': 'Italy',
                'province': 'Tuscany',
                'region_1': None,
                'region_2': None,
                'variety': 'Sangiovese',
                'winery': 'Test Winery 2',
                'points': 85,
                'price': Decimal('30.00'),
                'similarity_score': 0.75
            }
        ]
        
        # Setup database mocks
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        database_service.pool = mock_pool
        
        with patch.object(embedding_service.client.embeddings, 'create', return_value=mock_embedding_response):
            query_embedding = await embedding_service.generate_embedding("test wine")
            
            # Test with high threshold (0.8) - should return only high similarity wine
            mock_conn.fetch.return_value = mock_results_high_threshold
            results_high = await database_service.search_similar_wines(
                query_embedding=query_embedding,
                similarity_threshold=0.8
            )
            
            assert len(results_high) == 1
            assert results_high[0].similarity_score == 0.95
            
            # Test with low threshold (0.5) - should return both wines
            mock_conn.fetch.return_value = mock_results_low_threshold
            results_low = await database_service.search_similar_wines(
                query_embedding=query_embedding,
                similarity_threshold=0.5
            )
            
            assert len(results_low) == 2
            assert results_low[0].similarity_score >= results_low[1].similarity_score
    
    @pytest.mark.asyncio
    async def test_integration_with_result_limits(self):
        """Test integration with different result limits."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key",
            max_results=50,
            similarity_threshold=0.7
        )
        
        embedding_service = EmbeddingService(config.openai_api_key)
        database_service = DatabaseService(config.database_url)
        
        # Mock embedding generation
        mock_embedding = [0.3] * 512
        mock_embedding_response = AsyncMock()
        mock_embedding_response.data = [AsyncMock()]
        mock_embedding_response.data[0].embedding = mock_embedding
        
        # Create mock results for different limits
        def create_mock_wine(wine_id: int, score: float):
            return {
                'id': wine_id,
                'designation': f'Wine {wine_id}',
                'description': f'Description for wine {wine_id}',
                'country': 'France',
                'province': 'Bordeaux',
                'region_1': None,
                'region_2': None,
                'variety': 'Merlot',
                'winery': f'Winery {wine_id}',
                'points': 85,
                'price': Decimal('25.00'),
                'similarity_score': score
            }
        
        # Setup database mocks
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        database_service.pool = mock_pool
        
        with patch.object(embedding_service.client.embeddings, 'create', return_value=mock_embedding_response):
            query_embedding = await embedding_service.generate_embedding("test wine")
            
            # Test with limit of 3
            mock_results_3 = [create_mock_wine(i, 0.9 - (i-1)*0.05) for i in range(1, 4)]  # 0.9, 0.85, 0.8
            mock_conn.fetch.return_value = mock_results_3
            
            results_3 = await database_service.search_similar_wines(
                query_embedding=query_embedding,
                limit=3
            )
            
            assert len(results_3) == 3
            assert all(result.similarity_score >= 0.7 for result in results_3)
            
            # Test with limit of 1
            mock_results_1 = [create_mock_wine(1, 0.95)]
            mock_conn.fetch.return_value = mock_results_1
            
            results_1 = await database_service.search_similar_wines(
                query_embedding=query_embedding,
                limit=1
            )
            
            assert len(results_1) == 1
            assert results_1[0].id == 1
            assert results_1[0].similarity_score == 0.95
    
    @pytest.mark.asyncio
    async def test_integration_data_consistency(self):
        """Test that data flows correctly between services without corruption."""
        config = ServerConfig(
            database_url="postgresql://test:test@localhost/test",
            openai_api_key="test-api-key"
        )
        
        embedding_service = EmbeddingService(config.openai_api_key)
        database_service = DatabaseService(config.database_url)
        
        # Use specific embedding values to test data integrity
        specific_embedding = [round(i * 0.001, 6) for i in range(512)]
        
        mock_embedding_response = AsyncMock()
        mock_embedding_response.data = [AsyncMock()]
        mock_embedding_response.data[0].embedding = specific_embedding
        
        # Mock database with specific wine data
        mock_wine_data = {
            'id': 42,
            'designation': 'Test Wine with Special Characters: àéîôü',
            'description': 'Wine with "quotes" and special chars: $100 & more!',
            'country': 'France',
            'province': 'Champagne',
            'region_1': 'Épernay',
            'region_2': None,
            'variety': 'Pinot Noir',
            'winery': 'Maison d\'Excellence',
            'points': 92,
            'price': Decimal('125.50'),
            'similarity_score': 0.8765
        }
        
        # Setup database mocks
        mock_pool = MagicMock()
        mock_conn = AsyncMock()
        
        async_context_manager = AsyncMock()
        async_context_manager.__aenter__ = AsyncMock(return_value=mock_conn)
        async_context_manager.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = async_context_manager
        
        mock_conn.fetch.return_value = [mock_wine_data]
        database_service.pool = mock_pool
        
        # Execute integration test
        with patch.object(embedding_service.client.embeddings, 'create', return_value=mock_embedding_response):
            # Generate embedding
            query_embedding = await embedding_service.generate_embedding("special wine query")
            
            # Verify embedding data integrity
            assert len(query_embedding) == 512
            assert query_embedding[0] == 0.0
            assert query_embedding[100] == 0.1
            assert query_embedding[511] == 0.511
            
            # Search with the embedding
            results = await database_service.search_similar_wines(query_embedding)
            
            # Verify data integrity in results
            assert len(results) == 1
            wine = results[0]
            
            assert wine.id == 42
            assert wine.designation == 'Test Wine with Special Characters: àéîôü'
            assert wine.description == 'Wine with "quotes" and special chars: $100 & more!'
            assert wine.country == 'France'
            assert wine.province == 'Champagne'
            assert wine.region_1 == 'Épernay'
            assert wine.region_2 is None
            assert wine.variety == 'Pinot Noir'
            assert wine.winery == 'Maison d\'Excellence'
            assert wine.points == 92
            assert wine.price == Decimal('125.50')
            assert wine.similarity_score == 0.8765
            
            # Verify the database was called with the correct embedding
            mock_conn.fetch.assert_called_once()
            call_args = mock_conn.fetch.call_args[0]
            embedding_str = call_args[1]
            
            # Verify embedding string format
            assert embedding_str.startswith('[0.0,0.001,0.002')
            assert '0.511]' in embedding_str