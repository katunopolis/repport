import requests
import json
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration - can be changed via command line arguments
BASE_URL = os.getenv("TEST_API_URL", "http://localhost:8000/api/v1")
ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("TEST_ADMIN_PASSWORD", "placeholder_password")  # Replace hardcoded password
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test_user@example.com")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "placeholder_password")  # Replace hardcoded password
wait_time = 5  # seconds to wait for server startup

# Parse command line arguments
if len(sys.argv) > 1:
    BASE_URL = sys.argv[1]

# Utility functions
def print_response(resp, test_name):
    """Print the response details with better formatting for test results"""
    success = 200 <= resp.status_code < 300
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n--- {test_name}: {status} ---")
    print(f"URL: {resp.url}")
    print(f"Status code: {resp.status_code}")
    try:
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except:
        print(f"Raw response: {resp.text}")
    return success

def run_test(method, endpoint, test_name, **kwargs):
    """Run a test with the given method and endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.lower() == 'get':
            resp = requests.get(url, **kwargs)
        elif method.lower() == 'post':
            resp = requests.post(url, **kwargs)
        elif method.lower() == 'patch':
            resp = requests.patch(url, **kwargs)
        elif method.lower() == 'put':
            resp = requests.put(url, **kwargs)
        elif method.lower() == 'delete':
            resp = requests.delete(url, **kwargs)
        else:
            print(f"Unknown method: {method}")
            return False
        return print_response(resp, test_name)
    except Exception as e:
        print(f"\n--- {test_name}: ❌ ERROR ---")
        print(f"URL: {url}")
        print(f"Exception: {str(e)}")
        return False

# Initialize test results
tests_total = 0
tests_passed = 0

def track_result(result):
    """Track test results"""
    global tests_total, tests_passed
    tests_total += 1
    if result:
        tests_passed += 1

print("\n=== REPPORT API TEST SUITE ===")
print(f"Target API: {BASE_URL}")
print(f"WAITING FOR SERVER STARTUP... ({wait_time} seconds)")
time.sleep(wait_time)  # Give server time to start

# -----------------------------------------------------------------
# TEST 1: Debug Endpoint
# Purpose: Verify the API is accessible and the API prefix is working
# Expected: 200 OK response with status and prefix information
# -----------------------------------------------------------------
track_result(run_test('get', '/debug', "Debug Endpoint"))

# -----------------------------------------------------------------
# AUTHENTICATION TESTS
# -----------------------------------------------------------------

# TEST 2: Admin Login
# Purpose: Authenticate as admin to get a token for subsequent admin-only tests
# Expected: 200 OK response with access_token in the response body
# Note: This is a critical test - many others depend on it
# -----------------------------------------------------------------
login_data = {"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
login_resp = requests.post(
    f"{BASE_URL}/auth/login", 
    data=login_data,
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)
admin_token = None
if print_response(login_resp, "Admin Login"):
    admin_token = login_resp.json().get("access_token")
    print(f"Retrieved admin token: {admin_token[:10]}..." if admin_token else "No token received")
    track_result(True)
else:
    track_result(False)
    print("CRITICAL ERROR: Admin login failed - many subsequent tests will fail")
    print("Check that the admin user exists and credentials are correct")

# Authentication headers
admin_headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

# -----------------------------------------------------------------
# TEST 3: Get Current User Profile
# Purpose: Verify the current user (me) endpoint works with the auth token
# Expected: 200 OK with the admin user details
# Confirms: Authentication is working and token is valid
# -----------------------------------------------------------------
track_result(run_test('get', '/users/me', "Get Current User", headers=admin_headers))

# -----------------------------------------------------------------
# USER MANAGEMENT TESTS
# -----------------------------------------------------------------

# TEST 4: List All Users
# Purpose: Test admin-only endpoint to list all users in the system
# Expected: 200 OK with array of user objects
# Confirms: Admin permissions are working correctly
# -----------------------------------------------------------------
track_result(run_test('get', '/users', "List All Users", headers=admin_headers))

# -----------------------------------------------------------------
# TEST 5: Create Test User
# Purpose: Test user creation functionality (admin-only)
# Expected: 200 OK with the created user details including an ID
# Confirms: User management is working correctly
# -----------------------------------------------------------------
test_user_data = {
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD,
    "is_superuser": False,
    "is_active": True
}
create_user_resp = requests.post(
    f"{BASE_URL}/users", 
    json=test_user_data, 
    headers=admin_headers
)
test_user_id = None
if print_response(create_user_resp, "Create Test User"):
    try:
        test_user_id = create_user_resp.json().get("id")
    except:
        print("Could not get user ID from response")
    track_result(True)
else:
    # User might already exist, try to find them in the user list
    users_resp = requests.get(
        f"{BASE_URL}/users", 
        headers=admin_headers
    )
    if 200 <= users_resp.status_code < 300:
        try:
            for user in users_resp.json():
                if user.get("email") == TEST_USER_EMAIL:
                    test_user_id = user.get("id")
                    print(f"Found existing test user with ID: {test_user_id}")
                    break
        except:
            pass
    track_result(False)

# -----------------------------------------------------------------
# TEST 6: Get Specific User
# Purpose: Test getting a specific user by ID (admin-only)
# Expected: 200 OK with the requested user's details
# Confirms: User retrieval by ID is working
# -----------------------------------------------------------------
if test_user_id:
    track_result(run_test('get', f'/users/{test_user_id}', "Get Specific User", headers=admin_headers))
else:
    print("\n--- Get Specific User: ⚠️ SKIPPED (no user ID) ---")

# -----------------------------------------------------------------
# TEST 7: Promote User to Admin
# Purpose: Test updating a user's permissions (admin-only)
# Expected: 200 OK with the updated user details showing is_superuser=true
# Confirms: User updates are working correctly
# -----------------------------------------------------------------
if test_user_id:
    track_result(run_test(
        'patch', 
        f'/users/{test_user_id}/promote', 
        "Promote User to Admin",
        json={"is_superuser": True},
        headers=admin_headers
    ))
else:
    print("\n--- Promote User to Admin: ⚠️ SKIPPED (no user ID) ---")

# -----------------------------------------------------------------
# TEST 8: Test User Login
# Purpose: Test login with the newly created (or existing) test user
# Expected: 200 OK with access_token for the test user
# Confirms: Regular user authentication is working
# -----------------------------------------------------------------
if test_user_id:
    test_login_data = {"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    test_login_resp = requests.post(
        f"{BASE_URL}/auth/login", 
        data=test_login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    test_token = None
    if print_response(test_login_resp, "Test User Login"):
        test_token = test_login_resp.json().get("access_token")
        test_headers = {"Authorization": f"Bearer {test_token}"} if test_token else {}
        track_result(True)
    else:
        test_headers = {}
        track_result(False)
else:
    test_headers = {}
    print("\n--- Test User Login: ⚠️ SKIPPED (no user ID) ---")

# -----------------------------------------------------------------
# TICKET MANAGEMENT TESTS
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# TEST 9: Create Ticket
# Purpose: Test ticket creation functionality
# Expected: 200 OK with the created ticket details including an ID
# Confirms: Ticket creation is working correctly
# -----------------------------------------------------------------
test_ticket = {
    "title": "Test Ticket",
    "description": "This is a test ticket created by the API test script",
    "created_by": ADMIN_EMAIL
}
create_ticket_resp = requests.post(
    f"{BASE_URL}/tickets", 
    json=test_ticket, 
    headers=admin_headers
)
ticket_id = None
if print_response(create_ticket_resp, "Create Ticket"):
    try:
        ticket_id = create_ticket_resp.json().get("id")
    except:
        print("Could not get ticket ID from response")
    track_result(True)
else:
    track_result(False)

# -----------------------------------------------------------------
# TEST 10: List All Tickets
# Purpose: Test getting a list of all tickets
# Expected: 200 OK with array of ticket objects
# Confirms: Ticket retrieval is working correctly
# -----------------------------------------------------------------
track_result(run_test('get', '/tickets', "List All Tickets", headers=admin_headers))

# -----------------------------------------------------------------
# TEST 11: Get Specific Ticket
# Purpose: Test getting a specific ticket by ID
# Expected: 200 OK with the requested ticket's details
# Confirms: Ticket retrieval by ID is working
# -----------------------------------------------------------------
if ticket_id:
    track_result(run_test('get', f'/tickets/{ticket_id}', "Get Specific Ticket", headers=admin_headers))
else:
    print("\n--- Get Specific Ticket: ⚠️ SKIPPED (no ticket ID) ---")

# -----------------------------------------------------------------
# TEST 12: Respond to Ticket
# Purpose: Test adding a response to a ticket
# Expected: 200 OK with a success message
# Confirms: Ticket response functionality is working
# -----------------------------------------------------------------
if ticket_id:
    track_result(run_test(
        'post', 
        f'/tickets/{ticket_id}/respond', 
        "Respond to Ticket",
        json={"response": "This is a test response"},
        headers=admin_headers
    ))
else:
    print("\n--- Respond to Ticket: ⚠️ SKIPPED (no ticket ID) ---")

# -----------------------------------------------------------------
# TEST 13: Update Ticket Status
# Purpose: Test changing a ticket's status
# Expected: 200 OK with a success message
# Confirms: Ticket status updates are working
# -----------------------------------------------------------------
if ticket_id:
    track_result(run_test(
        'put', 
        f'/tickets/{ticket_id}/status', 
        "Update Ticket Status",
        json={"status": "in_progress"},
        headers=admin_headers
    ))
else:
    print("\n--- Update Ticket Status: ⚠️ SKIPPED (no ticket ID) ---")

# -----------------------------------------------------------------
# TEST 14: Request Password Reset
# Purpose: Test password reset request functionality
# Expected: 200 OK with a message (even if email doesn't exist)
# Confirms: Password reset flow initial step is working
# Note: Actual email delivery can't be tested automatically
# -----------------------------------------------------------------
track_result(run_test(
    'post', 
    '/auth/forgot-password', 
    "Request Password Reset",
    json={"email": ADMIN_EMAIL}
))

# -----------------------------------------------------------------
# TEST 15: Logout
# Purpose: Test the logout endpoint
# Expected: 200 OK with a success message
# Confirms: Logout functionality is working
# Note: JWT-based logout is client-side, this just confirms the endpoint responds
# -----------------------------------------------------------------
track_result(run_test('post', '/logout', "Admin Logout", headers=admin_headers))

# -----------------------------------------------------------------
# CLEANUP TESTS
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# TEST 16: Delete Test User
# Purpose: Clean up by deleting the test user created earlier
# Expected: 204 No Content response
# Confirms: User deletion is working correctly
# -----------------------------------------------------------------
if test_user_id and admin_token:
    track_result(run_test('delete', f'/users/{test_user_id}', "Delete Test User", headers=admin_headers))
else:
    print("\n--- Delete Test User: ⚠️ SKIPPED (no user ID or admin token) ---")

# -----------------------------------------------------------------
# TEST 17: Change Password
# Purpose: Test the password change functionality for authenticated users
# Expected: 200 OK with success message
# Confirms: Password change is working correctly
# -----------------------------------------------------------------
if admin_token:
    track_result(run_test(
        'post', 
        '/users/me/change-password', 
        "Change Password",
        json={"current_password": ADMIN_PASSWORD, "new_password": ADMIN_PASSWORD},
        headers=admin_headers
    ))
else:
    print("\n--- Change Password: ⚠️ SKIPPED (no admin token) ---")

# Print summary
print("\n=== TEST SUMMARY ===")
print(f"Tests passed: {tests_passed}/{tests_total} ({tests_passed/tests_total*100:.1f}%)")
if tests_passed == tests_total:
    print("🎉 All tests passed!")
    sys.exit(0)
else:
    print(f"❌ {tests_total - tests_passed} tests failed.")
    sys.exit(1) 