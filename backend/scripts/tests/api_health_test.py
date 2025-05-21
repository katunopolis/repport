import requests
import json
import sys
import os
import time
from colorama import init, Fore, Style

# Initialize colorama for colored console output
init()

# Configuration
BASE_URL = "http://localhost:8000"
wait_time = 5  # seconds to wait for server startup

# Parse command line arguments
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")

def print_test_header(name):
    print(f"\n{Fore.CYAN}Running test: {name}{Style.RESET_ALL}")
    print("=" * 50)

def test_health_endpoint():
    print_test_header("Health Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            print_success(f"Health endpoint returned status code {response.status_code}")
            
            data = response.json()
            if data.get("status") == "healthy":
                print_success("Health status is 'healthy'")
            else:
                print_error(f"Health status is not 'healthy': {data.get('status')}")
                
            if "version" in data:
                print_success(f"Version information present: {data.get('version')}")
            else:
                print_error("Version information missing")
                
            if "api_prefix" in data:
                print_success(f"API prefix information present: {data.get('api_prefix')}")
            else:
                print_error("API prefix information missing")
        else:
            print_error(f"Health endpoint returned status code {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing health endpoint: {str(e)}")
        return False
        
    return True

def test_error_handling():
    print_test_header("Error Handling")
    
    # Test 404 error
    try:
        response = requests.get(f"{BASE_URL}/nonexistent-endpoint")
        
        if response.status_code == 404:
            print_success(f"Non-existent endpoint returned status code {response.status_code}")
            
            data = response.json()
            if "detail" in data:
                print_success(f"Error response contains expected fields: {json.dumps(data)}")
            else:
                print_error(f"Error response missing 'detail' field: {json.dumps(data)}")
        else:
            print_error(f"Non-existent endpoint returned unexpected status code {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing 404 handling: {str(e)}")
        return False
    
    # Test validation error (422)
    try:
        # Call an endpoint that requires parameters but don't provide them
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={})
        
        if response.status_code == 422:
            print_success(f"Invalid request returned status code {response.status_code}")
            
            data = response.json()
            if "detail" in data and "status_code" in data and "message" in data:
                print_success(f"Validation error contains expected fields")
            else:
                print_error(f"Validation error missing expected fields: {json.dumps(data)}")
        else:
            print_error(f"Invalid request returned unexpected status code {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing validation error handling: {str(e)}")
        return False
        
    return True

def test_debug_endpoint():
    print_test_header("Debug Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/debug")
        
        if response.status_code == 200:
            print_success(f"Debug endpoint returned status code {response.status_code}")
            
            data = response.json()
            if data.get("status") == "API is accessible":
                print_success("Debug status is correct")
            else:
                print_error(f"Debug status is incorrect: {data.get('status')}")
                
            if "prefix" in data:
                print_success(f"API prefix information present: {data.get('prefix')}")
            else:
                print_error("API prefix information missing")
        else:
            print_error(f"Debug endpoint returned status code {response.status_code}")
            
    except Exception as e:
        print_error(f"Error testing debug endpoint: {str(e)}")
        return False
        
    return True

def main():
    print_info("Starting API Health and Error Handling Tests")
    print_info("=" * 50)
    print_info(f"Target API: {BASE_URL}")
    print_info(f"WAITING FOR SERVER STARTUP... ({wait_time} seconds)")
    time.sleep(wait_time)  # Give server time to start
    
    tests = [
        test_health_endpoint,
        test_debug_endpoint,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    if failed == 0:
        print_success(f"All tests passed ({passed}/{len(tests)})")
    else:
        print_error(f"Tests: {passed} passed, {failed} failed")
        
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 