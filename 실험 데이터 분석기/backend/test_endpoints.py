"""
Test script to check if endpoints are working
"""
import requests

API_BASE = "http://localhost:8000"

print("Testing API Endpoints...")
print("=" * 50)

# Test 1: Health Check
print("\n1. Health Check")
try:
    response = requests.get(f"{API_BASE}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: List all endpoints
print("\n2. Available Endpoints (from OpenAPI)")
try:
    response = requests.get(f"{API_BASE}/openapi.json")
    if response.ok:
        data = response.json()
        paths = data.get("paths", {})
        print(f"Found {len(paths)} endpoints:")
        for path in sorted(paths.keys()):
            methods = list(paths[path].keys())
            print(f"  {path} - {methods}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Check if detect-sheets endpoint exists
print("\n3. Test detect-sheets endpoint")
try:
    # Try with a test file
    with open("test_data/electron_em_experiment.xlsx", "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_BASE}/api/analyze/detect-sheets", files=files)
        print(f"Status: {response.status_code}")
        if response.ok:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
except FileNotFoundError:
    print("Test file not found, skipping...")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
