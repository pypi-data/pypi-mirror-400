"""Database service for PostgreSQL operations with pgvector."""

import asyncio
import logging
import time
from typing import List, Optional
import asyncpg
from .models import WineRecord, WineResult
from .config import ServerConfig
from .errors import create_database_error, format_error_response
from .logging_config import log_request_start, log_request_success, log_request_error


logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing PostgreSQL connections and wine search operations."""
    
    def __init__(self, database_url: str):
        """Initialize the database service.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        logger.debug("DatabaseService initialized")
        
    async def initialize(self) -> None:
        """Initialize the database connection pool and verify pgvector extension.
        
        Raises:
            ConnectionError: If database connection fails
            RuntimeError: If pgvector extension is not available
        """
        start_time = time.time()
        operation = "database_initialization"
        
        try:
            log_request_start(logger, operation)
            
            # Create connection pool
            logger.debug("Creating database connection pool")
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10,
                command_timeout=30,
                server_settings={
                    'application_name': 'wine-semantic-search-mcp'
                }
            )
            logger.info("Database connection pool created successfully", extra={
                "min_connections": 1,
                "max_connections": 10,
                "command_timeout": 30
            })
            
            # Verify pgvector extension is available
            await self._verify_pgvector_extension()
            logger.info("pgvector extension verified successfully")
            
            # Extract database name from URL
            db_name = self.database_url.split('/')[-1].split('?')[0]
            
            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Database initialization complete - Database: {db_name}, URL: {self.database_url}",
                extra={"duration_ms": duration_ms}
            )
            log_request_success(logger, operation, duration_ms=duration_ms)
            
        except asyncpg.PostgresError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
            # Format error for logging but raise RuntimeError for API consistency
            format_error_response(
                error=create_database_error("database_connection", e),
                operation=operation
            )
            raise RuntimeError("Database initialization failed")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
            # Format error for logging but raise RuntimeError for API consistency
            format_error_response(
                error=create_database_error("database_initialization", e),
                operation=operation
            )
            raise RuntimeError("Database initialization failed")
    
    async def _verify_pgvector_extension(self) -> None:
        """Verify that the pgvector extension is installed and available.
        
        Raises:
            RuntimeError: If pgvector extension is not available
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        async with self.pool.acquire() as conn:
            try:
                logger.debug("Checking pgvector extension availability")
                
                # Check if pgvector extension is installed
                result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                )
                
                if not result:
                    logger.error("pgvector extension is not installed")
                    # Format error for logging but raise RuntimeError for API consistency
                    format_error_response(
                        error=create_database_error(
                            "pgvector_extension_check",
                            Exception("pgvector extension is not installed. Please install it with: CREATE EXTENSION vector;")
                        ),
                        operation="pgvector_extension_check"
                    )
                    raise RuntimeError("pgvector extension is not installed")
                
                # Verify vector operations are available by testing a simple query
                logger.debug("Testing pgvector operations")
                test_result = await conn.fetchval("SELECT '[1,2,3]'::vector <-> '[1,2,4]'::vector")
                logger.debug(f"pgvector test query result: {test_result}")
                
            except asyncpg.UndefinedObjectError as e:
                logger.error(f"pgvector extension configuration error: {e}")
                # Format error for logging but raise RuntimeError for API consistency
                format_error_response(
                    error=create_database_error("pgvector_extension_config", e),
                    operation="pgvector_extension_config"
                )
                raise RuntimeError("pgvector extension is not installed")
            except Exception as e:
                logger.error(f"pgvector extension verification failed: {e}")
                # Format error for logging but raise RuntimeError for API consistency
                format_error_response(
                    error=create_database_error("pgvector_extension_verification", e),
                    operation="pgvector_extension_verification"
                )
                raise RuntimeError("pgvector extension is not installed")
    
    async def close(self) -> None:
        """Close the database connection pool."""
        if self.pool:
            logger.debug("Closing database connection pool")
            await self.pool.close()
            self.pool = None
            logger.info("Database connection pool closed successfully")
        else:
            logger.debug("Database connection pool already closed or not initialized")
    
    async def health_check(self) -> bool:
        """Check if the database connection is healthy.
        
        Returns:
            bool: True if database is accessible, False otherwise
        """
        if not self.pool:
            logger.warning("Database health check failed: pool not initialized")
            return False
            
        try:
            logger.debug("Performing database health check")
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False
    
    async def search_similar_wines(
        self, 
        query_embedding: List[float], 
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[WineResult]:
        """Search for wines similar to the query embedding.
        
        Uses pgvector cosine similarity to find semantically similar wines.
        Results are ordered by similarity score (descending) and filtered
        by the similarity threshold.
        
        Args:
            query_embedding: Vector embedding of the search query
            limit: Maximum number of results to return
            similarity_threshold: Minimum similarity score threshold
            
        Returns:
            List of wine results ordered by similarity score (most similar first)
            
        Raises:
            RuntimeError: If database pool is not initialized
            ValueError: If query_embedding is invalid
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
            
        if not query_embedding or len(query_embedding) == 0:
            raise ValueError("Query embedding cannot be empty")
        
        start_time = time.time()
        operation = "wine_similarity_search"
        
        try:
            log_request_start(
                logger, 
                operation,
                embedding_dimensions=len(query_embedding),
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            async with self.pool.acquire() as conn:
                # SQL query to join wine and wine_embeddings_oai tables
                # Uses pgvector cosine similarity operator (<->) 
                # Lower cosine distance means higher similarity
                query = """
                    SELECT 
                        w.id,
                        w.designation,
                        w.description,
                        w.country,
                        w.province,
                        w.region_1,
                        w.region_2,
                        w.variety,
                        w.winery,
                        w.points,
                        w.price,
                        (1 - (we.embedding <-> $1::vector)) as similarity_score
                    FROM wine w
                    INNER JOIN wine_embeddings_oai we ON w.id = we.wine_id
                    WHERE (1 - (we.embedding <-> $1::vector)) >= $2
                    ORDER BY we.embedding <-> $1::vector ASC
                    LIMIT $3
                """
                
                # Convert embedding to string format for pgvector
                embedding_str = f"[{','.join(map(str, query_embedding))}]"
                logger.debug(f"Executing similarity search query with {len(query_embedding)}-dimensional embedding")
                
                # Execute query with parameters
                query_start = time.time()
                rows = await conn.fetch(
                    query, 
                    embedding_str,
                    similarity_threshold,
                    limit
                )
                query_duration = (time.time() - query_start) * 1000
                
                logger.debug(f"Database query completed in {query_duration:.2f}ms", extra={
                    "rows_returned": len(rows)
                })
                
                # Convert database rows to WineResult objects
                results = []
                for row in rows:
                    wine_result = WineResult(
                        id=row['id'],
                        designation=row['designation'] or '',
                        description=row['description'] or '',
                        country=row['country'],
                        province=row['province'],
                        region_1=row['region_1'],
                        region_2=row['region_2'],
                        variety=row['variety'],
                        winery=row['winery'],
                        points=row['points'],
                        price=row['price'],
                        similarity_score=float(row['similarity_score'])
                    )
                    results.append(wine_result)
                
                duration_ms = (time.time() - start_time) * 1000
                log_request_success(
                    logger,
                    operation,
                    duration_ms=duration_ms,
                    results_found=len(results),
                    query_duration_ms=query_duration
                )
                
                return results
                
        except asyncpg.PostgresError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
            raise create_database_error("wine_similarity_search", e)
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_request_error(logger, operation, e, duration_ms=duration_ms)
            raise create_database_error("wine_similarity_search", e)