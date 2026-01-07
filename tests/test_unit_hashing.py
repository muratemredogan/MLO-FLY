"""
Unit tests for hash_airport_code function.

These tests are fast, have no external dependencies (no DB/network),
and test pure function behavior.
"""
import pytest
from app.feature_engineering import hash_airport_code


def test_deterministic_output():
    """Test that same input always produces same bucket."""
    airport = "JFK"
    bucket1 = hash_airport_code(airport, num_buckets=100)
    bucket2 = hash_airport_code(airport, num_buckets=100)
    
    assert bucket1 == bucket2, "Hash function should be deterministic"


def test_bucket_range():
    """Test that bucket is always in valid range [0, num_buckets)."""
    airports = ["JFK", "LAX", "ORD", "ATL", "DFW", "DEN", "SEA", "MIA"]
    num_buckets = 100
    
    for airport in airports:
        bucket = hash_airport_code(airport, num_buckets=num_buckets)
        assert 0 <= bucket < num_buckets, f"Bucket {bucket} out of range for {airport}"


def test_known_value_jfk():
    """
    Test known value for JFK airport.
    
    JFK with MD5 hash and 100 buckets should produce a specific value.
    This test ensures the hash function behavior is stable.
    
    We compute the expected value using the same logic to ensure consistency.
    """
    import hashlib
    
    # Compute expected bucket using same logic as function
    hash_object = hashlib.md5("JFK".encode('utf-8'))
    hash_int = int(hash_object.hexdigest(), 16)
    expected_bucket = hash_int % 100
    
    # Get actual bucket from function
    bucket = hash_airport_code("JFK", num_buckets=100)
    
    # Verify it's a valid bucket
    assert 0 <= bucket < 100
    
    # Verify it matches expected value (stability check)
    assert bucket == expected_bucket, \
        f"JFK should map to bucket {expected_bucket}, got {bucket}"
    
    # Verify it's always the same (deterministic)
    bucket2 = hash_airport_code("JFK", num_buckets=100)
    assert bucket == bucket2, "JFK should always map to same bucket"


def test_different_airports_different_buckets():
    """Test that different airports (usually) map to different buckets."""
    airports = ["JFK", "LAX", "ORD", "ATL", "DFW"]
    buckets = [hash_airport_code(airport, num_buckets=100) for airport in airports]
    
    # At least some should be different (collision is possible but unlikely)
    unique_buckets = len(set(buckets))
    assert unique_buckets >= 2, "Different airports should map to different buckets (mostly)"


def test_empty_string_raises_error():
    """Test that empty string raises ValueError."""
    with pytest.raises(ValueError, match="non-empty string"):
        hash_airport_code("", num_buckets=100)


def test_none_raises_error():
    """Test that None raises ValueError."""
    with pytest.raises(ValueError):
        hash_airport_code(None, num_buckets=100)


def test_invalid_num_buckets():
    """Test that invalid num_buckets raises ValueError."""
    with pytest.raises(ValueError, match="positive integer"):
        hash_airport_code("JFK", num_buckets=0)
    
    with pytest.raises(ValueError, match="positive integer"):
        hash_airport_code("JFK", num_buckets=-1)


def test_different_num_buckets():
    """Test that different num_buckets produce different ranges."""
    airport = "JFK"
    bucket_100 = hash_airport_code(airport, num_buckets=100)
    bucket_50 = hash_airport_code(airport, num_buckets=50)
    
    assert 0 <= bucket_100 < 100
    assert 0 <= bucket_50 < 50
    
    # With 50 buckets, bucket should be bucket_100 % 50 (approximately)
    # But exact relationship depends on hash modulo
    assert bucket_50 == bucket_100 % 50

