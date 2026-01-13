"""
Register your Ed25519 public key with the NeoCore API.

This example demonstrates:
1. Reading your public key from file
2. Getting Firebase JWT token (you need to implement your auth flow)
3. Registering the public key with NeoCore API
4. Saving the key_id for future SDK usage

Prerequisites:
- Generate keys: neocore-keygen
- Have Firebase authentication set up
- Get a valid Firebase JWT token

Environment Variables:
- FIREBASE_JWT: Your Firebase JWT token (required)
- PUBLIC_KEY_PATH: Path to public key (default: ~/.neocore/pub_a1b2c3.pem)
"""

import os
import uuid
import requests
from pathlib import Path


def get_public_key_path():
    """Get the path to the public key file."""
    custom_path = os.getenv("PUBLIC_KEY_PATH")
    if custom_path:
        return Path(custom_path)

    # Default location
    home = Path.home()
    return home / ".neocore" / "pub_a1b2c3.pem"


def read_public_key(key_path):
    """Read the public key from file."""
    if not key_path.exists():
        raise FileNotFoundError(f"Public key not found at: {key_path}")

    with open(key_path, "r") as f:
        return f.read()


def register_public_key(firebase_jwt, public_key_pem, api_url="https://api.neosapien.xyz"):
    """
    Register public key with NeoCore API.

    Args:
        firebase_jwt: Firebase JWT token for authentication
        public_key_pem: The public key in PEM format
        api_url: NeoCore API base URL

    Returns:
        tuple: (key_id, response_data)
    """
    # Generate unique key ID
    key_id = str(uuid.uuid4())

    # Prepare request
    endpoint = f"{api_url}/api/v1/dev-keys"
    headers = {
        "Authorization": f"Bearer {firebase_jwt}",
        "Content-Type": "application/json"
    }
    payload = {
        "key_id": key_id,
        "public_key_pem": public_key_pem
    }

    print(f"\nRegistering public key...")
    print(f"  Endpoint: {endpoint}")
    print(f"  Key ID: {key_id}")

    # Make request
    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code in [200, 201]:
        print(f"  Status: Success ({response.status_code})")
        return key_id, response.json()
    else:
        print(f"  Status: Failed ({response.status_code})")
        raise Exception(f"Registration failed: {response.text}")


def main():
    print("=" * 70)
    print("NeoCore SDK - Public Key Registration".center(70))
    print("=" * 70)

    # Step 1: Get Firebase JWT token
    print("\n[Step 1] Getting Firebase JWT token...")
    firebase_jwt = os.getenv("FIREBASE_JWT")

    if not firebase_jwt:
        print("\nError: FIREBASE_JWT environment variable not set!")
        print("\nTo get a Firebase JWT token:")
        print("  1. Implement your Firebase authentication flow")
        print("  2. Get the ID token from Firebase Auth")
        print("  3. Set it as environment variable:")
        print("     export FIREBASE_JWT='your-token-here'")
        print("\nExample Firebase authentication (pseudo-code):")
        print("  import firebase_admin")
        print("  # Initialize Firebase")
        print("  # Authenticate user")
        print("  # token = user.get_id_token()")
        return

    print(f"  Firebase JWT: {firebase_jwt[:20]}...")

    # Step 2: Read public key
    print("\n[Step 2] Reading public key...")
    try:
        public_key_path = get_public_key_path()
        print(f"  Key path: {public_key_path}")

        public_key_pem = read_public_key(public_key_path)
        print("  Public key loaded successfully!")

        # Display first few lines of the key
        key_lines = public_key_pem.strip().split('\n')
        print(f"  Key preview:")
        for line in key_lines[:3]:
            print(f"    {line}")
        if len(key_lines) > 3:
            print(f"    ... ({len(key_lines)} lines total)")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nGenerate keys first:")
        print("  neocore-keygen")
        return
    except Exception as e:
        print(f"\nError reading public key: {e}")
        return

    # Step 3: Register with API
    print("\n[Step 3] Registering with NeoCore API...")
    try:
        api_url = os.getenv("NEOCORE_API_URL", "https://api.neosapien.xyz")
        key_id, response_data = register_public_key(
            firebase_jwt=firebase_jwt,
            public_key_pem=public_key_pem,
            api_url=api_url
        )

        print("\n" + "=" * 70)
        print("SUCCESS! Public key registered".center(70))
        print("=" * 70)

        # Step 4: Save key_id for future use
        print(f"\nYour key_id: {key_id}")
        print("\nSave this key_id! You'll need it for all SDK requests.")
        print("\nRecommended: Add to your environment variables:")
        print(f"  export KEY_ID='{key_id}'")

        print("\nOr add to your .env file:")
        print(f"  KEY_ID={key_id}")

        print("\nNext steps:")
        print("  1. Save the key_id above")
        print("  2. Use it in your code:")
        print("     from neocore_sdk import NeoCoreClient")
        print(f"     client = NeoCoreClient(key_id='{key_id}')")
        print("     response = client.get('/api/v1/users')")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\nRegistration failed: {e}")
        print("\nPossible issues:")
        print("  - Invalid or expired Firebase JWT token")
        print("  - Network connection problems")
        print("  - API server is down")
        print("  - Invalid public key format")
        return


if __name__ == "__main__":
    main()
