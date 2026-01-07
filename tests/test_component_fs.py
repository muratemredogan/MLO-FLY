"""
Component tests using filesystem.

These tests use filesystem operations (creating temp files, reading them)
but do NOT use network or database.
"""
import os
import tempfile
import pytest
from app.feature_engineering import hash_airport_code


def test_read_airports_from_file():
    """
    Component test: Read airport codes from file and hash them.
    
    This test:
    1. Creates a temporary file with airport codes
    2. Reads the file
    3. Hashes each airport code
    4. Verifies output list length matches input
    """
    # Sample airport codes
    airport_codes = ["JFK", "LAX", "ORD", "ATL", "DFW"]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        # Write airport codes, one per line
        for code in airport_codes:
            f.write(f"{code}\n")
        temp_file_path = f.name
    
    try:
        # Read file and process
        with open(temp_file_path, 'r') as f:
            lines = f.readlines()
        
        # Strip newlines and filter empty lines
        read_codes = [line.strip() for line in lines if line.strip()]
        
        # Hash each airport code
        buckets = [hash_airport_code(code, num_buckets=100) for code in read_codes]
        
        # Verify output length matches input
        assert len(buckets) == len(airport_codes), \
            f"Expected {len(airport_codes)} buckets, got {len(buckets)}"
        
        # Verify all buckets are valid
        for bucket in buckets:
            assert 0 <= bucket < 100, f"Bucket {bucket} out of range"
        
        # Verify we got the expected codes
        assert read_codes == airport_codes, "Read codes should match written codes"
        
    finally:
        # Cleanup: delete temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def test_multiple_files_processing():
    """
    Component test: Process multiple files and aggregate results.
    """
    airport_files = [
        ["JFK", "LAX"],
        ["ORD", "ATL", "DFW"],
        ["DEN", "SEA"]
    ]
    
    temp_files = []
    all_buckets = []
    
    try:
        # Create multiple temp files
        for airports in airport_files:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                for code in airports:
                    f.write(f"{code}\n")
                temp_files.append(f.name)
        
        # Process each file
        for file_path in temp_files:
            with open(file_path, 'r') as f:
                codes = [line.strip() for line in f if line.strip()]
            
            buckets = [hash_airport_code(code, num_buckets=100) for code in codes]
            all_buckets.extend(buckets)
        
        # Verify total count
        expected_total = sum(len(airports) for airports in airport_files)
        assert len(all_buckets) == expected_total, \
            f"Expected {expected_total} buckets, got {len(all_buckets)}"
        
    finally:
        # Cleanup
        for file_path in temp_files:
            if os.path.exists(file_path):
                os.unlink(file_path)


def test_file_with_empty_lines():
    """Test handling of files with empty lines."""
    airport_codes = ["JFK", "", "LAX", "  ", "ORD"]
    valid_codes = ["JFK", "LAX", "ORD"]
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        for code in airport_codes:
            f.write(f"{code}\n")
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'r') as f:
            lines = f.readlines()
        
        # Filter empty lines
        read_codes = [line.strip() for line in lines if line.strip()]
        
        # Hash valid codes
        buckets = [hash_airport_code(code, num_buckets=100) for code in read_codes]
        
        assert len(buckets) == len(valid_codes)
        
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

