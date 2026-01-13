"""
Complete workflow example for NeoCore Security SDK.

This example demonstrates the entire workflow from start to finish:
1. Key generation (using CLI tool)
2. Public key registration
3. SDK initialization
4. Making authenticated requests (CRUD operations)
5. Error handling

This is a comprehensive example that shows how everything fits together.

Prerequisites:
- Python 3.9+
- neocore-sdk installed: pip install neocore-sdk
"""

import os
import sys
import subprocess
from pathlib import Path


def step_1_generate_keys():
    """Step 1: Generate Ed25519 key pair."""
    print("\n" + "=" * 70)
    print("[STEP 1] Generate Ed25519 Key Pair".center(70))
    print("=" * 70)

    key_dir = Path.home() / ".neocore"
    private_key = key_dir / "p_a1b2c3.pem"
    public_key = key_dir / "pub_a1b2c3.pem"

    if private_key.exists() and public_key.exists():
        print(f"\nKeys already exist at {key_dir}")
        print("  p_a1b2c3.pem: EXISTS")
        print("  pub_a1b2c3.pem: EXISTS")

        response = input("\nDo you want to regenerate keys? (y/N): ")
        if response.lower() != 'y':
            print("Using existing keys.")
            return True

    print("\nGenerating new key pair using CLI...")
    print(f"Command: neocore-keygen")

    try:
        result = subprocess.run(
            ["neocore-keygen", "--force"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("\nKeys generated successfully!")
            print(f"  Private key: {private_key}")
            print(f"  Public key: {public_key}")
            print("\nIMPORTANT: Keep p_a1b2c3.pem SECRET! Never share or commit to git.")
            return True
        else:
            print(f"\nError generating keys: {result.stderr}")
            return False

    except FileNotFoundError:
        print("\nError: 'neocore-keygen' command not found!")
        print("Make sure neocore-sdk is installed:")
        print("  pip install neocore-sdk")
        return False
    except Exception as e:
        print(f"\nError: {e}")
        return False


def step_2_register_key():
    """Step 2: Register public key with NeoCore API."""
    print("\n" + "=" * 70)
    print("[STEP 2] Register Public Key".center(70))
    print("=" * 70)

    print("\nTo register your public key, you need:")
    print("  1. A valid Firebase JWT token")
    print("  2. Network access to NeoCore API")

    print("\nRegistration options:")
    print("  A. Use the registration script: python examples/register_public_key.py")
    print("  B. Manual registration via API")
    print("  C. Skip (if already registered)")

    key_id = os.getenv("KEY_ID")
    if key_id:
        print(f"\nFound existing KEY_ID in environment: {key_id[:8]}...")
        response = input("Use this key_id? (Y/n): ")
        if response.lower() != 'n':
            return key_id

    response = input("\nEnter your registered key_id (or press Enter to skip): ")
    if response.strip():
        return response.strip()

    print("\nSkipping registration. You can register later.")
    print("See: examples/register_public_key.py")
    return None


def step_3_use_sdk(key_id):
    """Step 3: Use the SDK to make requests."""
    print("\n" + "=" * 70)
    print("[STEP 3] Using NeoCore SDK".center(70))
    print("=" * 70)

    if not key_id:
        print("\nSkipping SDK usage (no key_id provided)")
        print("Complete step 2 (registration) to use the SDK.")
        return

    from neocore_sdk import NeoCoreClient, KeyNotFoundError, APIConnectionError

    print(f"\nInitializing client with key_id: {key_id[:8]}...")

    try:
        client = NeoCoreClient(key_id=key_id)
        print("Client initialized successfully!")

    except KeyNotFoundError as e:
        print(f"\nError: {e}")
        print("Generate keys first: neocore-keygen")
        return
    except Exception as e:
        print(f"\nError initializing client: {e}")
        return

    # Example 1: GET request
    print("\n[Example 1] GET request - List users")
    try:
        response = client.get("/api/v1/users", params={"page": 1, "limit": 5})
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            users = response.json()
            print(f"  Retrieved {len(users)} users")
        else:
            print(f"  Response: {response.text}")
    except APIConnectionError as e:
        print(f"  Connection error: {e}")
    except Exception as e:
        print(f"  Error: {e}")

    # Example 2: POST request
    print("\n[Example 2] POST request - Create user")
    try:
        new_user = {
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "role": "developer"
        }
        response = client.post("/api/v1/users", data=new_user)
        print(f"  Status: {response.status_code}")

        if response.status_code in [200, 201]:
            print("  User created successfully!")
            if response.text:
                created = response.json()
                print(f"  User ID: {created.get('id', 'N/A')}")
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")

    # Example 3: PATCH request
    print("\n[Example 3] PATCH request - Update user")
    try:
        updates = {"role": "admin"}
        response = client.patch("/api/v1/users/123", data=updates)
        print(f"  Status: {response.status_code}")

        if response.status_code in [200, 204]:
            print("  User updated successfully!")
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")

    # Example 4: DELETE request
    print("\n[Example 4] DELETE request - Delete user")
    try:
        response = client.delete("/api/v1/users/123")
        print(f"  Status: {response.status_code}")

        if response.status_code in [200, 204]:
            print("  User deleted successfully!")
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\nSDK examples completed!")


def main():
    """Main workflow."""
    print("=" * 70)
    print("NeoCore SDK - Complete Workflow Example".center(70))
    print("=" * 70)

    print("\nThis example walks you through:")
    print("  1. Generating Ed25519 keys")
    print("  2. Registering your public key")
    print("  3. Using the SDK to make authenticated requests")

    # Step 1: Generate keys
    if not step_1_generate_keys():
        print("\nWorkflow stopped: Key generation failed")
        sys.exit(1)

    # Step 2: Register key
    key_id = step_2_register_key()

    # Step 3: Use SDK
    step_3_use_sdk(key_id)

    # Summary
    print("\n" + "=" * 70)
    print("Workflow Complete!".center(70))
    print("=" * 70)

    print("\nWhat you learned:")
    print("  - How to generate Ed25519 keys")
    print("  - How to register your public key")
    print("  - How to use NeoCoreClient for API requests")
    print("  - How to handle responses and errors")

    print("\nNext steps:")
    print("  - Explore other examples: examples/error_handling.py")
    print("  - Read the documentation: https://docs.neosapien.xyz")
    print("  - Build your application!")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nWorkflow cancelled by user.")
        sys.exit(0)
