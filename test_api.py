import requests
import json
import time
import sys
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8001"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.headers = {}

    def authenticate(self, email: str, password: str) -> Optional[str]:
        """Get authentication token and set up auth headers"""
        print("\nGetting access token:")
        data = {"email": email, "password": password}

        try:
            response = requests.post(f"{self.base_url}/users/token", json=data)
            self._print_response(response)

            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                return self.token
            return None
        except requests.RequestException as e:
            print(f"Authentication error: {e}")
            return None

    def register_user(self, email: str, password: str) -> Optional[int]:
        """Register a new user"""
        print("\n1. Testing Register User:")
        data = {"email": email, "password": password}

        try:
            response = requests.post(f"{self.base_url}/users/register", json=data)
            self._print_response(response)

            if response.status_code == 201:
                self.user_id = response.json().get("id")
                return self.user_id
            return None
        except requests.RequestException as e:
            print(f"Registration error: {e}")
            return None

    def get_users(self) -> Dict[str, Any]:
        """Get all users"""
        print("\n2. Testing Get All Users:")

        try:
            response = requests.get(f"{self.base_url}/users/", headers=self.headers)
            self._print_response(response)
            return response.json() if response.status_code == 200 else {}
        except requests.RequestException as e:
            print(f"Get users error: {e}")
            return {}

    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get a specific user by ID"""
        print(f"\n3. Testing Get User {user_id}:")

        try:
            response = requests.get(f"{self.base_url}/users/{user_id}", headers=self.headers)
            self._print_response(response)
            return response.json() if response.status_code == 200 else {}
        except requests.RequestException as e:
            print(f"Get user error: {e}")
            return {}

    def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user"""
        print(f"\n4. Testing Update User {user_id}:")

        try:
            response = requests.put(
                f"{self.base_url}/users/{user_id}",
                json=data,
                headers=self.headers
            )
            self._print_response(response)
            return response.json() if response.status_code == 200 else {}
        except requests.RequestException as e:
            print(f"Update user error: {e}")
            return {}

    def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        print(f"\n5. Testing Delete User {user_id}:")

        try:
            response = requests.delete(f"{self.base_url}/users/{user_id}", headers=self.headers)
            self._print_response(response)
            return response.status_code == 204
        except requests.RequestException as e:
            print(f"Delete user error: {e}")
            return False

    def _print_response(self, response):
        """Helper method to print response details"""
        print(f"Status Code: {response.status_code}")
        if response.text:
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except json.JSONDecodeError:
                print(f"Response: {response.text}")


def wait_for_server():
    """Wait for the server to be ready"""
    print("Waiting for server to be ready...")
    for i in range(MAX_RETRIES):
        try:
            print(f"Attempt {i + 1}/{MAX_RETRIES}: Trying to connect to {BASE_URL}/docs")
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("Server is ready!")
                return True
            else:
                print(f"Server responded with status code: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            print(f"Attempt {i + 1}/{MAX_RETRIES}: Server not ready, retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            time.sleep(RETRY_DELAY)
    return False


def test_register_user() -> Optional[str]:
    """Test user registration and return the user's email if successful"""
    print("\n1. Testing Register User:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/users/register",
            json={
                "email": "test2@example.com",
                "password": "testpassword123"
            }
        )
        response.raise_for_status()
        print("Registration successful!")
        return "test2@example.com"
    except requests.exceptions.RequestException as e:
        print(f"Registration error: {str(e)}")
        return None


def test_login(email: str) -> Optional[str]:
    """Test user login and return the access token if successful"""
    print("\n2. Testing Login:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/users/token",
            json={
                "email": email,
                "password": "testpassword123"
            }
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        print("Login successful!")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Login error: {str(e)}")
        return None


def test_get_groups(token: str):
    """Test getting groups with authentication"""
    print("\n3. Testing Get Groups:")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/groups", headers=headers)
        response.raise_for_status()
        print("Successfully retrieved groups!")
        print(f"Groups: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Get groups error: {str(e)}")


def test_create_group(token: str):
    """Test creating a new group"""
    print("\n4. Testing Create Group:")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/api/v1/groups",
            headers=headers,
            json={
                "name": "Test Group",
                "description": "This is a test group"
            }
        )
        response.raise_for_status()
        print("Successfully created group!")
        print(f"Created group: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Create group error: {str(e)}")


def main():
    print("Starting API Tests...")

    # Wait for server to be ready
    if not wait_for_server():
        print("Could not connect to server. Please make sure the server is running.")
        sys.exit(1)

    # Test registration
    email = test_register_user()
    if not email:
        print("Failed to register user. Stopping tests.")
        sys.exit(1)

    # Test login
    token = test_login(email)
    if not token:
        print("Failed to login. Stopping tests.")
        sys.exit(1)

    # Test groups endpoints
    test_get_groups(token)
    test_create_group(token)

    print("\nAll tests completed!")


if __name__ == "__main__":
    main()
