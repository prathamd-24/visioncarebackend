"""
Test script for Flask Supabase API
Tests all endpoints: health, login, data insert, and get data
"""

import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000"

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test_header(test_name):
    """Print a formatted test header"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}Testing: {test_name}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")


def print_success(message):
    """Print success message in green"""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message in red"""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message in yellow"""
    print(f"{YELLOW}ℹ {message}{RESET}")


def print_response(response):
    """Print formatted response"""
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)


# Test 1: Health Check
def test_health():
    print_test_header("Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print_success("Health check passed!")
                return True
            else:
                print_error("Health check returned unexpected status")
                return False
        else:
            print_error(f"Health check failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


# Test 2: Login - Invalid Credentials
def test_login_invalid():
    print_test_header("Login Endpoint - Invalid Credentials")
    try:
        payload = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        print_response(response)
        
        if response.status_code == 401:
            print_success("Invalid login correctly rejected!")
            return True
        else:
            print_error(f"Expected 401 status, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Login test error: {str(e)}")
        return False


# Test 3: Login - Missing Fields
def test_login_missing_fields():
    print_test_header("Login Endpoint - Missing Fields")
    try:
        payload = {
            "email": "user@example.com"
            # Missing password
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        print_response(response)
        
        if response.status_code == 400:
            print_success("Missing fields correctly rejected!")
            return True
        else:
            print_error(f"Expected 400 status, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Login test error: {str(e)}")
        return False


# Test 4: Create Test User (helper function)
def create_test_user():
    """Create a test user in the database for login testing"""
    print_test_header("Creating Test User")
    try:
        # First check if test user already exists
        import requests
        from supabase import create_client
        
        SUPABASE_URL = "https://ubmfikxfcupqhpwtuctl.supabase.co"
        SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVibWZpa3hmY3VwcWhwd3R1Y3RsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MzE0MzkxMCwiZXhwIjoyMDc4NzE5OTEwfQ.6wgNifeuiuLDG9tXFalEsuBnllvL_4BJBlJb5If1U0g"
        
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        test_email = "test_user@example.com"
        test_password = "test123"
        test_user_id = 999  # Use a high number to avoid conflicts
        
        print_info(f"Checking if test user exists: {test_email}")
        
        # Check if user exists
        response = supabase.table('users').select('*').eq('email', test_email).execute()
        
        if response.data and len(response.data) > 0:
            print_success("Test user already exists!")
            return test_email, test_password, response.data[0]['user_id']
        
        # Create test user
        print_info("Creating new test user...")
        response = supabase.table('users').insert({
            "user_id": test_user_id,
            "email": test_email,
            "password": test_password
        }).execute()
        
        if response.data:
            print_success(f"Test user created successfully! user_id: {test_user_id}")
            return test_email, test_password, test_user_id
        else:
            print_error("Failed to create test user")
            return None, None, None
            
    except Exception as e:
        print_error(f"Error creating test user: {str(e)}")
        return None, None, None


# Test 5: Login - Valid Credentials (now automated)
def test_login_valid():
    print_test_header("Login Endpoint - Valid Credentials")
    
    # Create test user first
    email, password, user_id = create_test_user()
    
    if not email or not password:
        print_error("Cannot test login - test user creation failed")
        return False
    
    try:
        payload = {
            "email": email,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/login", json=payload)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('user_id') and data.get('email') == email:
                print_success(f"Valid login successful! Logged in as user_id: {data.get('user_id')}")
                return True
            else:
                print_error("Login returned unexpected data")
                return False
        else:
            print_error(f"Login failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Login test error: {str(e)}")
        return False


# Test 6: Data Insert - Missing Fields
def test_data_insert_missing_fields():
    print_test_header("Data Insert Endpoint - Missing Fields")
    try:
        payload = {
            "client_id": 1,
            "avg_blink_rate": 15
            # Missing required fields
        }
        response = requests.post(f"{BASE_URL}/data", json=payload)
        print_response(response)
        
        if response.status_code == 400:
            print_success("Missing fields correctly rejected!")
            return True
        else:
            print_error(f"Expected 400 status, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Data insert test error: {str(e)}")
        return False


# Test 7: Data Insert - Valid Data (now automated)
def test_data_insert_valid():
    print_test_header("Data Insert Endpoint - Valid Data")
    
    # Use the test user created earlier
    email, password, user_id = create_test_user()
    
    if not user_id:
        print_error("Cannot test data insert - test user not available")
        return False
    
    try:
        payload = {
            "client_id": user_id,
            "avg_blink_rate": 15,
            "avg_temp": 36,
            "left_eye_redness": 5,
            "right_eye_redness": 4
        }
        response = requests.post(f"{BASE_URL}/data", json=payload)
        print_response(response)
        
        if response.status_code == 201:
            data = response.json()
            if data.get('message') == 'Data inserted successfully':
                print_success("Data inserted successfully!")
                return True
            else:
                print_error("Data insert returned unexpected response")
                return False
        else:
            print_error(f"Data insert failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Data insert test error: {str(e)}")
        return False


# Test 8: Get Data - All Data (now uses test user)
def test_get_data_all():
    print_test_header("Get Data Endpoint - All Data")
    
    # Get test user ID
    _, _, user_id = create_test_user()
    if not user_id:
        print_error("Cannot test - test user not available")
        return False
    
    print_info(f"Testing with client_id={user_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/data/{user_id}?range=all")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Successfully retrieved {data.get('count', 0)} records!")
            return True
        else:
            print_error(f"Get data failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get data test error: {str(e)}")
        return False


# Test 9: Get Data - Day Range
def test_get_data_day():
    print_test_header("Get Data Endpoint - Last Day")
    
    # Get test user ID
    _, _, user_id = create_test_user()
    if not user_id:
        print_error("Cannot test - test user not available")
        return False
    
    print_info(f"Testing with client_id={user_id} and range=day")
    
    try:
        response = requests.get(f"{BASE_URL}/data/{user_id}?range=day")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Successfully retrieved {data.get('count', 0)} records from last 24 hours!")
            return True
        else:
            print_error(f"Get data failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get data test error: {str(e)}")
        return False


# Test 10: Get Data - Week Range
def test_get_data_week():
    print_test_header("Get Data Endpoint - Last Week")
    
    # Get test user ID
    _, _, user_id = create_test_user()
    if not user_id:
        print_error("Cannot test - test user not available")
        return False
    
    print_info(f"Testing with client_id={user_id} and range=week")
    
    try:
        response = requests.get(f"{BASE_URL}/data/{user_id}?range=week")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Successfully retrieved {data.get('count', 0)} records from last week!")
            return True
        else:
            print_error(f"Get data failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get data test error: {str(e)}")
        return False


# Test 11: Get Data - Month Range
def test_get_data_month():
    print_test_header("Get Data Endpoint - Last Month")
    
    # Get test user ID
    _, _, user_id = create_test_user()
    if not user_id:
        print_error("Cannot test - test user not available")
        return False
    
    print_info(f"Testing with client_id={user_id} and range=month")
    
    try:
        response = requests.get(f"{BASE_URL}/data/{user_id}?range=month")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Successfully retrieved {data.get('count', 0)} records from last month!")
            return True
        else:
            print_error(f"Get data failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get data test error: {str(e)}")
        return False


# Test 12: Get Data - Custom Date Range
def test_get_data_custom_range():
    print_test_header("Get Data Endpoint - Custom Date Range")
    
    # Get test user ID
    _, _, user_id = create_test_user()
    if not user_id:
        print_error("Cannot test - test user not available")
        return False
    
    print_info(f"Testing with client_id={user_id} and custom date range")
    
    try:
        start_date = "2025-01-01"
        end_date = "2025-12-31"
        response = requests.get(f"{BASE_URL}/data/{user_id}?start_date={start_date}&end_date={end_date}")
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Successfully retrieved {data.get('count', 0)} records for custom range!")
            return True
        else:
            print_error(f"Get data failed with status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get data test error: {str(e)}")
        return False


# Test 13: Get Data - Invalid Range
def test_get_data_invalid_range():
    print_test_header("Get Data Endpoint - Invalid Range")
    
    # Get test user ID
    _, _, user_id = create_test_user()
    if not user_id:
        print_error("Cannot test - test user not available")
        return False
    
    print_info(f"Testing with client_id={user_id} and invalid range parameter")
    
    try:
        response = requests.get(f"{BASE_URL}/data/{user_id}?range=invalid")
        print_response(response)
        
        if response.status_code == 400:
            print_success("Invalid range correctly rejected!")
            return True
        else:
            print_error(f"Expected 400 status, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Get data test error: {str(e)}")
        return False


# Test 14: 404 Error
def test_404_error():
    print_test_header("404 Error Handler")
    try:
        response = requests.get(f"{BASE_URL}/nonexistent")
        print_response(response)
        
        if response.status_code == 404:
            print_success("404 error handler working correctly!")
            return True
        else:
            print_error(f"Expected 404 status, got {response.status_code}")
            return False
    except Exception as e:
        print_error(f"404 test error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests and print summary"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}Starting API Test Suite{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    tests = [
        ("Health Check", test_health),
        ("Login - Invalid Credentials", test_login_invalid),
        ("Login - Missing Fields", test_login_missing_fields),
        ("Login - Valid Credentials", test_login_valid),
        ("Data Insert - Missing Fields", test_data_insert_missing_fields),
        ("Data Insert - Valid Data", test_data_insert_valid),
        ("Get Data - All Records", test_get_data_all),
        ("Get Data - Last Day", test_get_data_day),
        ("Get Data - Last Week", test_get_data_week),
        ("Get Data - Last Month", test_get_data_month),
        ("Get Data - Custom Range", test_get_data_custom_range),
        ("Get Data - Invalid Range", test_get_data_invalid_range),
        ("404 Error Handler", test_404_error),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Print summary
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    total = len(results)
    
    for test_name, result in results:
        if result is True:
            print_success(f"{test_name}")
        elif result is False:
            print_error(f"{test_name}")
        else:
            print_info(f"{test_name} (Skipped)")
    
    print(f"\n{BLUE}Total Tests: {total}{RESET}")
    print_success(f"Passed: {passed}")
    print_error(f"Failed: {failed}")
    print_info(f"Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print(f"\n{GREEN}All automated tests passed! 🎉{RESET}")
    elif failed > 0:
        print(f"\n{RED}Some tests failed. Please review the output above.{RESET}")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Test suite error: {str(e)}")
