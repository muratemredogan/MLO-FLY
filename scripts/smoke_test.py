"""
End-to-end smoke test script.

This script:
1. Builds Docker image
2. Runs container
3. Waits for health endpoint
4. Sends POST /predict request
5. Asserts HTTP 200 OK
6. Cleans up container
"""
import subprocess
import time
import requests
import sys


def run_command(cmd, check=True):
    """Run shell command and return result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result


def wait_for_health(url, max_retries=30, delay=1):
    """Wait for health endpoint to be ready."""
    print(f"Waiting for health endpoint at {url}...")
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"Health check passed! (attempt {i+1})")
                return True
        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                print(f"Attempt {i+1}/{max_retries} failed: {e}, retrying...")
                time.sleep(delay)
            else:
                print(f"Health check failed after {max_retries} attempts")
                return False
    return False


def main():
    """Main smoke test execution."""
    image_name = "mlops-hw2"
    container_name = "mlops-hw2-container"
    port = 8000
    base_url = f"http://localhost:{port}"
    
    print("=" * 60)
    print("Starting Smoke Test")
    print("=" * 60)
    
    # Step 1: Build Docker image
    print("\n[1/5] Building Docker image...")
    run_command(["docker", "build", "-t", image_name, "."])
    print("✓ Docker image built successfully")
    
    # Step 2: Run container
    print("\n[2/5] Starting container...")
    # Stop and remove existing container if it exists
    subprocess.run(["docker", "stop", container_name], capture_output=True)
    subprocess.run(["docker", "rm", container_name], capture_output=True)
    
    run_command([
        "docker", "run", "-d",
        "-p", f"{port}:8000",
        "--name", container_name,
        image_name
    ])
    print("✓ Container started")
    
    try:
        # Step 3: Wait for health endpoint
        print("\n[3/5] Waiting for service to be ready...")
        if not wait_for_health(f"{base_url}/health"):
            print("✗ Service failed to become ready")
            sys.exit(1)
        
        # Step 4: Test health endpoint
        print("\n[4/5] Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.json()["status"] == "ok", "Expected status='ok'"
        print("✓ Health endpoint working")
        
        # Step 5: Test /predict endpoint
        print("\n[5/5] Testing /predict endpoint...")
        predict_data = {"departure_airport": "JFK"}
        response = requests.post(
            f"{base_url}/predict",
            json=predict_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        result = response.json()
        assert "bucket" in result, "Response should contain 'bucket' field"
        assert isinstance(result["bucket"], int), "Bucket should be integer"
        assert 0 <= result["bucket"] < 100, f"Bucket {result['bucket']} out of range"
        print(f"✓ Predict endpoint working (JFK -> bucket {result['bucket']})")
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - Smoke test successful!")
        print("=" * 60)
        
    finally:
        # Cleanup: Stop and remove container
        print("\nCleaning up...")
        subprocess.run(["docker", "stop", container_name], capture_output=True)
        subprocess.run(["docker", "rm", container_name], capture_output=True)
        print("✓ Container cleaned up")


if __name__ == "__main__":
    main()

