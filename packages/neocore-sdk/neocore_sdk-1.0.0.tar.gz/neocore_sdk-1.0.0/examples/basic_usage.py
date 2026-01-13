"""
Basic usage examples for NeoCore Security SDK.

This example demonstrates:
1. Initializing the NeoCoreClient
2. Making simple GET requests
3. Making POST requests with data
4. Making PUT, PATCH, DELETE requests
5. Handling responses

Prerequisites:
- Generate keys: neocore-keygen
- Register your public key and get a key_id
- Set KEY_ID environment variable or modify the code below
"""

import os
from neocore_sdk import NeoCoreClient

# Configuration
# Replace with your actual key_id from registration
KEY_ID = os.getenv("KEY_ID", "YOUR-KEY-ID-HERE")
BASE_URL = os.getenv("NEOCORE_API_URL", "https://api.neosapien.xyz")


def main():
    print("=" * 70)
    print("NeoCore SDK - Basic Usage Examples".center(70))
    print("=" * 70)

    # Step 1: Initialize the client
    print("\n[1] Initializing NeoCoreClient...")
    print(f"    Base URL: {BASE_URL}")
    print(f"    Key ID: {KEY_ID[:8]}...")

    try:
        client = NeoCoreClient(
            key_id=KEY_ID,
            base_url=BASE_URL
        )
        print("    Client initialized successfully!")
    except Exception as e:
        print(f"    Error: {e}")
        print("\nMake sure you have:")
        print("  1. Generated keys: neocore-keygen")
        print("  2. Registered your public key")
        print("  3. Set KEY_ID environment variable")
        return

    # Step 2: Making a GET request
    print("\n[2] Making a GET request...")
    print("    Endpoint: /api/v1/users")

    try:
        response = client.get("/api/v1/users")
        print(f"    Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"    Response: {data}")
        else:
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"    Exception: {e}")

    # Step 3: Making a GET request with query parameters
    print("\n[3] Making a GET request with query parameters...")
    print("    Endpoint: /api/v1/users?page=1&limit=10")

    try:
        response = client.get("/api/v1/users", params={
            "page": 1,
            "limit": 10,
            "sort": "created_at",
            "order": "desc"
        })
        print(f"    Status Code: {response.status_code}")

        if response.status_code == 200:
            print(f"    Success! Received user data")
        else:
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"    Exception: {e}")

    # Step 4: Making a POST request
    print("\n[4] Making a POST request...")
    print("    Endpoint: /api/v1/users")

    try:
        new_user = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "role": "developer"
        }
        response = client.post("/api/v1/users", data=new_user)
        print(f"    Status Code: {response.status_code}")

        if response.status_code == 201:
            print("    User created successfully!")
            created_user = response.json()
            print(f"    Created user ID: {created_user.get('id')}")
        elif response.status_code == 200:
            print("    Success!")
        else:
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"    Exception: {e}")

    # Step 5: Making a PUT request (full update)
    print("\n[5] Making a PUT request...")
    print("    Endpoint: /api/v1/users/123")

    try:
        updated_user = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "role": "admin"
        }
        response = client.put("/api/v1/users/123", data=updated_user)
        print(f"    Status Code: {response.status_code}")

        if response.status_code in [200, 204]:
            print("    User updated successfully!")
        else:
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"    Exception: {e}")

    # Step 6: Making a PATCH request (partial update)
    print("\n[6] Making a PATCH request...")
    print("    Endpoint: /api/v1/users/123")

    try:
        partial_update = {
            "email": "newemail@example.com"
        }
        response = client.patch("/api/v1/users/123", data=partial_update)
        print(f"    Status Code: {response.status_code}")

        if response.status_code in [200, 204]:
            print("    User email updated successfully!")
        else:
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"    Exception: {e}")

    # Step 7: Making a DELETE request
    print("\n[7] Making a DELETE request...")
    print("    Endpoint: /api/v1/users/123")

    try:
        response = client.delete("/api/v1/users/123")
        print(f"    Status Code: {response.status_code}")

        if response.status_code in [200, 204]:
            print("    User deleted successfully!")
        else:
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"    Exception: {e}")

    print("\n" + "=" * 70)
    print("All examples completed!".center(70))
    print("=" * 70)


if __name__ == "__main__":
    main()
