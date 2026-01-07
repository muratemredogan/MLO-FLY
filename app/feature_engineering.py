"""
Feature engineering module for airport code hashing.
"""
import hashlib


def hash_airport_code(iata_code: str, num_buckets: int = 100) -> int:
    """
    Hash an IATA airport code to a bucket index.
    
    Uses MD5 hash for deterministic mapping. Same input always produces
    same bucket number.
    
    Args:
        iata_code: String representing airport code (e.g., 'JFK')
        num_buckets: Number of hash buckets (default: 100)
    
    Returns:
        Bucket index (0 to num_buckets-1)
    
    Raises:
        ValueError: If iata_code is empty or None
    
    Example:
        >>> hash_airport_code('JFK', 100)
        42  # Example output - actual value depends on hash
    """
    if not iata_code or not isinstance(iata_code, str):
        raise ValueError("iata_code must be a non-empty string")
    
    if not isinstance(num_buckets, int) or num_buckets <= 0:
        raise ValueError("num_buckets must be a positive integer")
    
    # Convert to bytes and hash using MD5
    hash_object = hashlib.md5(iata_code.encode('utf-8'))
    hash_int = int(hash_object.hexdigest(), 16)
    
    # Map to bucket using modulo
    bucket = hash_int % num_buckets
    
    return bucket

