import requests
import time

API_BASE = "http://localhost:8000"

print("Waiting for server...")
time.sleep(2)

print("Checking port 8000...")
try:
    response = requests.get(f"{API_BASE}/openapi.json")
    if response.ok:
        paths = response.json().get("paths", {})
        print(f"Found {len(paths)} endpoints")
        if "/api/analyze/detect-sheets" in paths:
             print("SUCCESS: detect-sheets found!")
        else:
             print("FAIL: detect-sheets NOT found")
    else:
        print("Failed to get OpenAPI specs")
except Exception as e:
    print(f"Error: {e}")
