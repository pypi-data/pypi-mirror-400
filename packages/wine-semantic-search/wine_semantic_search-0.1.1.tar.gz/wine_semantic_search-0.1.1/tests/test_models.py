"""Property-based tests for data models."""

import json
from decimal import Decimal
from typing import Any, Dict

import pytest
from hypothesis import given, strategies as st

from wine_semantic_search.models import WineResult, WineRecord, WineEmbeddingRecord


class TestWineResultSerialization:
    """Property-based tests for WineResult serialization."""

    @given(
        id=st.integers(min_value=1),
        designation=st.text(min_size=1, max_size=255),
        description=st.text(min_size=1, max_size=1000),
        country=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
        province=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
        region_1=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
        region_2=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
        variety=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
        winery=st.one_of(st.none(), st.text(min_size=1, max_size=150)),
        points=st.one_of(st.none(), st.integers(min_value=0, max_value=100)),
        price=st.one_of(st.none(), st.decimals(min_value=0, max_value=10000, places=2)),
        similarity_score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    def test_wine_result_response_structure_consistency(
        self, id, designation, description, country, province, region_1, 
        region_2, variety, winery, points, price, similarity_score
    ):
        """
        Property 6: Response Structure Consistency
        For any WineResult, the serialized response should include all required fields 
        in a properly structured JSON format.
        **Feature: wine-semantic-search, Property 6: Response Structure Consistency**
        **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
        """
        # Create WineResult instance
        wine_result = WineResult(
            id=id,
            designation=designation,
            description=description,
            country=country,
            province=province,
            region_1=region_1,
            region_2=region_2,
            variety=variety,
            winery=winery,
            points=points,
            price=price,
            similarity_score=similarity_score
        )
        
        # Convert to dictionary (simulating JSON serialization)
        result_dict = self._wine_result_to_dict(wine_result)
        
        # Verify all required fields are present
        assert "id" in result_dict
        assert "designation" in result_dict
        assert "description" in result_dict
        assert "similarity_score" in result_dict
        
        # Verify required fields have correct types and values
        assert isinstance(result_dict["id"], int)
        assert isinstance(result_dict["designation"], str)
        assert isinstance(result_dict["description"], str)
        assert isinstance(result_dict["similarity_score"], float)
        
        # Verify required fields match original values
        assert result_dict["id"] == id
        assert result_dict["designation"] == designation
        assert result_dict["description"] == description
        assert result_dict["similarity_score"] == similarity_score
        
        # Verify optional fields are properly handled
        optional_fields = ["country", "province", "region_1", "region_2", "variety", "winery", "points", "price"]
        for field in optional_fields:
            assert field in result_dict
            original_value = getattr(wine_result, field)
            if original_value is not None:
                if field == "price":
                    # Handle Decimal serialization
                    assert result_dict[field] == float(original_value)
                else:
                    assert result_dict[field] == original_value
            else:
                assert result_dict[field] is None
        
        # Verify the result can be JSON serialized
        json_str = json.dumps(result_dict, default=str)
        assert isinstance(json_str, str)
        
        # Verify JSON can be parsed back
        parsed_dict = json.loads(json_str)
        assert isinstance(parsed_dict, dict)
        
        # Verify essential structure is maintained after JSON round-trip
        assert parsed_dict["id"] == id
        assert parsed_dict["designation"] == designation
        assert parsed_dict["description"] == description
        assert abs(float(parsed_dict["similarity_score"]) - similarity_score) < 1e-10

    def _wine_result_to_dict(self, wine_result: WineResult) -> Dict[str, Any]:
        """Convert WineResult to dictionary for JSON serialization."""
        return {
            "id": wine_result.id,
            "designation": wine_result.designation,
            "description": wine_result.description,
            "country": wine_result.country,
            "province": wine_result.province,
            "region_1": wine_result.region_1,
            "region_2": wine_result.region_2,
            "variety": wine_result.variety,
            "winery": wine_result.winery,
            "points": wine_result.points,
            "price": float(wine_result.price) if wine_result.price is not None else None,
            "similarity_score": wine_result.similarity_score
        }


class TestWineRecordSerialization:
    """Unit tests for WineRecord and WineEmbeddingRecord."""

    def test_wine_record_creation(self):
        """Test WineRecord can be created with all fields."""
        record = WineRecord(
            id=1,
            csv_index=100,
            country="France",
            description="A fine wine",
            designation="Château Test",
            points=95,
            price=Decimal("50.00"),
            province="Bordeaux",
            region_1="Left Bank",
            region_2="Médoc",
            variety="Cabernet Sauvignon",
            winery="Test Winery"
        )
        
        assert record.id == 1
        assert record.country == "France"
        assert record.designation == "Château Test"

    def test_wine_embedding_record_creation(self):
        """Test WineEmbeddingRecord can be created."""
        embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        record = WineEmbeddingRecord(
            id=1,
            wine_id=123,
            embedding=embedding
        )
        
        assert record.id == 1
        assert record.wine_id == 123
        assert record.embedding == embedding