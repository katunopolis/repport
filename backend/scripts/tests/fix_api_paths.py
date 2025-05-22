import requests
import json
import sys
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test configuration
TEST_API_URL = os.getenv("TEST_API_URL", "http://localhost:8000/api/v1")
TEST_ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "admin@example.com")
TEST_ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "placeholder_password")  # Replace hardcoded password

# List of endpoints that appeared in error logs
failing_endpoints = [
    "/auth/login",
    "/tickets",
    "/users",
    "/tickets/1",
    "/users/2",
    "/logout",
    "/tickets/4"
]

# Expected prefixes to test
prefixes_to_test = [
    "",              # No prefix
    "/api",          # API prefix only
    "/api/v1",       # API + version prefix (expected correct one)
    "/v1",           # Version prefix only
]

base_url = "http://localhost:8000"

def print_endpoint_status(endpoint, prefix, status, is_correct=False):
    """Print the status of an endpoint with consistent formatting"""
    color_code = "\033[92m" if is_correct else "\033[91m" if status >= 400 else "\033[93m"
    end_code = "\033[0m"
    print(f"{color_code}{prefix}{endpoint}: {status}{end_code}")

def check_endpoint(endpoint, method="GET", data=None, headers=None):
    """Check if an endpoint exists with different prefixes"""
    found_working = False
    best_prefix = None
    best_status = 999
    
    print(f"\nTesting endpoint: {endpoint}")
    print("-" * 50)
    
    for prefix in prefixes_to_test:
        url = f"{base_url}{prefix}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=2)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=2)
            else:
                print(f"Method {method} not supported")
                continue
                
            status = response.status_code
            
            # Lower status code is better (200s better than 400s)
            if status < best_status:
                best_status = status
                best_prefix = prefix
                
            is_correct = status < 400
            found_working = found_working or is_correct
            
            print_endpoint_status(endpoint, prefix, status, is_correct)
            
        except Exception as e:
            print(f"{prefix}{endpoint}: Error - {str(e)}")
    
    return found_working, best_prefix, best_status

def suggest_fix(endpoint, best_prefix, best_status):
    """Suggest a fix for a failing endpoint"""
    if best_status < 400:
        return f"Use '{best_prefix}{endpoint}' instead"
    elif best_prefix == "/api/v1":
        return f"Endpoint missing in API, needs to be implemented"
    else:
        return f"Try using '/api/v1{endpoint}' or check if implementation exists"

def test_login_endpoint():
    """Test the login endpoint with correct format."""
    print(f"\nTesting login endpoint...")
    login_data = {"username": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD}
    response = requests.post(f"{TEST_API_URL}/auth/login", data=login_data)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login endpoint working correctly")
    else:
        print("❌ Login endpoint failed")
        print(f"Response: {response.text}")

def main():
    print("=" * 50)
    print("API PATH ANALYZER")
    print("=" * 50)
    print("This script will check for the correct API paths for endpoints")
    print("that were showing errors in the logs.")
    print("=" * 50)
    
    print("\nWaiting for API to be available...")
    time.sleep(5)
    
    # Try to login to get an auth token
    auth_token = None
    login_url = f"{base_url}/api/v1/auth/login"
    try:
        login_data = {"username": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD}
        login_resp = requests.post(
            login_url, 
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        if login_resp.status_code == 200:
            print("Successfully logged in, will use auth token for tests")
            auth_token = login_resp.json().get("access_token")
        else:
            print(f"Login failed: {login_resp.status_code}")
    except Exception as e:
        print(f"Could not connect to {login_url}: {str(e)}")
    
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    
    # Special test for login
    login_data = {"username": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD}
    login_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    login_found, login_prefix, login_status = check_endpoint(
        "/auth/login", 
        method="POST",
        data=login_data,
        headers=login_headers
    )
    
    # Test regular endpoints
    results = {}
    for endpoint in failing_endpoints:
        if endpoint == "/auth/login":
            results[endpoint] = (login_found, login_prefix, login_status)
            continue
        
        found, best_prefix, best_status = check_endpoint(endpoint, headers=headers)
        results[endpoint] = (found, best_prefix, best_status)
    
    # Print summary
    print("\n" + "=" * 50)
    print("SUMMARY OF FINDINGS")
    print("=" * 50)
    
    working_count = 0
    for endpoint, (found, best_prefix, best_status) in results.items():
        status_text = "\033[92mWORKING\033[0m" if found else "\033[91mFAILING\033[0m"
        if found:
            working_count += 1
        
        fix = suggest_fix(endpoint, best_prefix, best_status)
        print(f"{endpoint}: {status_text}")
        print(f"  Best prefix: {best_prefix if best_prefix else 'None'}")
        print(f"  Best status: {best_status}")
        print(f"  Suggestion: {fix}")
    
    print("\n" + "=" * 50)
    print(f"ENDPOINTS WORKING: {working_count}/{len(results)}")
    print("=" * 50)
    
    if working_count == 0:
        print("\nCritical issues detected! Possible causes:")
        print("1. API server might not be running correctly")
        print("2. API prefix might have changed from /api/v1")
        print("3. Router paths might not be properly registered in main.py")
        print("\nSuggested actions:")
        print("1. Check backend logs for API startup errors")
        print("2. Verify backend/app/main.py router registration")
        print("3. Confirm the API_V1_STR value in core/config.py")
    
if __name__ == "__main__":
    main() 