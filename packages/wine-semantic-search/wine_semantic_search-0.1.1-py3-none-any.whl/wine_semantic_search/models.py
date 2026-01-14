"""Data models for wine records and search results."""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass
class WineResult:
    """Wine search result with all wine fields and similarity score."""
    
    id: int
    designation: str  # Wine name/designation
    description: str
    country: Optional[str]
    province: Optional[str]
    region_1: Optional[str]
    region_2: Optional[str]
    variety: Optional[str]
    winery: Optional[str]
    points: Optional[int]  # Rating points
    price: Optional[Decimal]
    similarity_score: float


@dataclass
class WineRecord:
    """Database record model for wine table."""
    
    id: int
    csv_index: Optional[int]
    country: Optional[str]
    description: Optional[str]
    designation: Optional[str]
    points: Optional[int]
    price: Optional[Decimal]
    province: Optional[str]
    region_1: Optional[str]
    region_2: Optional[str]
    variety: Optional[str]
    winery: Optional[str]


@dataclass
class WineEmbeddingRecord:
    """Database record model for wine_embeddings table."""
    
    id: int
    wine_id: int
    embedding: List[float]