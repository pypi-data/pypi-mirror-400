"""
Comprehensive error handling examples for NeoCore Security SDK.

This example demonstrates:
1. Catching specific SDK exceptions
2. Handling HTTP status codes
3. Retry logic for transient failures
4. Production-ready error handling patterns

Prerequisites:
- Generate keys: neocore-keygen
- Set KEY_ID environment variable
"""

import os
import time
from neocore_sdk import (
    NeoCoreClient,
    # Base exceptions
    SecureSDKError,
    # Key errors
    KeyLoadError,
    KeyNotFoundError,
    # Signing errors
    SigningError,
    CanonicalizationError,
    # Network errors
    APIConnectionError,
)


def example_1_basic_exception_handling():
    """Example 1: Basic exception handling."""
    print("\n" + "=" * 70)
    print("[Example 1] Basic Exception Handling".center(70))
    print("=" * 70)

    key_id = os.getenv("KEY_ID", "demo-key-id")

    try:
        # Initialize client
        print("\nInitializing client...")
        client = NeoCoreClient(key_id=key_id)
        print("  Success!")

        # Make request
        print("\nMaking GET request...")
        response = client.get("/api/v1/users")
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"  Success: Retrieved {len(data)} users")
        else:
            print(f"  HTTP Error {response.status_code}: {response.text}")

    except KeyNotFoundError as e:
        print(f"\nKey Not Found Error: {e}")
        print("Solution: Run 'neocore-keygen' to generate keys")

    except KeyLoadError as e:
        print(f"\nKey Load Error: {e}")
        print("Solution: Check that your private key file exists and is readable")

    except APIConnectionError as e:
        print(f"\nAPI Connection Error: {e}")
        print("Solution: Check your network connection and API URL")

    except SigningError as e:
        print(f"\nSigning Error: {e}")
        print("Solution: Verify your private key is valid")

    except SecureSDKError as e:
        print(f"\nSDK Error: {e}")
        print("Solution: Check the error message above")

    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        print("Solution: Contact support with error details")


def example_2_http_status_code_handling():
    """Example 2: Handling specific HTTP status codes."""
    print("\n" + "=" * 70)
    print("[Example 2] HTTP Status Code Handling".center(70))
    print("=" * 70)

    key_id = os.getenv("KEY_ID", "demo-key-id")

    try:
        client = NeoCoreClient(key_id=key_id)

        print("\nMaking request that may return various status codes...")
        response = client.get("/api/v1/users/123")

        # Handle different status codes
        if response.status_code == 200:
            print("  200 OK: Request successful")
            data = response.json()
            print(f"  Data: {data}")

        elif response.status_code == 401:
            print("  401 Unauthorized: Invalid signature or key_id")
            print("  Action: Verify your key_id and private key")

        elif response.status_code == 403:
            print("  403 Forbidden: Insufficient permissions")
            print("  Action: Check your API access permissions")

        elif response.status_code == 404:
            print("  404 Not Found: Resource doesn't exist")
            print("  Action: Verify the endpoint path")

        elif response.status_code == 429:
            print("  429 Too Many Requests: Rate limit exceeded")
            print("  Action: Slow down your request rate")

        elif response.status_code >= 500:
            print(f"  {response.status_code} Server Error: API server issue")
            print("  Action: Retry after a delay")

        else:
            print(f"  {response.status_code}: {response.text}")

    except Exception as e:
        print(f"\nError: {e}")


def example_3_retry_logic():
    """Example 3: Retry logic for transient failures."""
    print("\n" + "=" * 70)
    print("[Example 3] Retry Logic for Transient Failures".center(70))
    print("=" * 70)

    key_id = os.getenv("KEY_ID", "demo-key-id")

    def make_request_with_retry(client, endpoint, max_retries=3, backoff_seconds=1):
        """Make request with exponential backoff retry."""
        for attempt in range(max_retries):
            try:
                print(f"\n  Attempt {attempt + 1}/{max_retries}...")
                response = client.get(endpoint)

                # Retry on server errors (5xx) or rate limiting (429)
                if response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_retries - 1:
                        wait_time = backoff_seconds * (2 ** attempt)
                        print(f"  Status {response.status_code}: Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                # Success or non-retryable error
                return response

            except APIConnectionError as e:
                if attempt < max_retries - 1:
                    wait_time = backoff_seconds * (2 ** attempt)
                    print(f"  Connection error: Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise

        return response

    try:
        client = NeoCoreClient(key_id=key_id)

        print("\nMaking request with retry logic...")
        response = make_request_with_retry(
            client,
            "/api/v1/users",
            max_retries=3,
            backoff_seconds=1
        )

        print(f"\nFinal Status: {response.status_code}")

        if response.status_code == 200:
            print("Success!")
        else:
            print(f"Failed after retries: {response.text}")

    except Exception as e:
        print(f"\nError after all retries: {e}")


def example_4_production_ready_handler():
    """Example 4: Production-ready error handler."""
    print("\n" + "=" * 70)
    print("[Example 4] Production-Ready Error Handler".center(70))
    print("=" * 70)

    key_id = os.getenv("KEY_ID", "demo-key-id")

    def safe_api_call(client, method, endpoint, **kwargs):
        """
        Production-ready API call wrapper.

        Returns:
            tuple: (success: bool, data: dict or None, error: str or None)
        """
        try:
            # Make request
            if method.upper() == "GET":
                response = client.get(endpoint, **kwargs)
            elif method.upper() == "POST":
                response = client.post(endpoint, **kwargs)
            elif method.upper() == "PUT":
                response = client.put(endpoint, **kwargs)
            elif method.upper() == "PATCH":
                response = client.patch(endpoint, **kwargs)
            elif method.upper() == "DELETE":
                response = client.delete(endpoint, **kwargs)
            else:
                return False, None, f"Unsupported method: {method}"

            # Handle response
            if response.status_code in [200, 201]:
                data = response.json() if response.text else {}
                return True, data, None

            elif response.status_code == 204:
                return True, None, None

            elif response.status_code == 401:
                return False, None, "Authentication failed - check your key_id"

            elif response.status_code == 403:
                return False, None, "Permission denied"

            elif response.status_code == 404:
                return False, None, "Resource not found"

            elif response.status_code == 429:
                return False, None, "Rate limit exceeded - please slow down"

            elif response.status_code >= 500:
                return False, None, f"Server error ({response.status_code})"

            else:
                return False, None, f"HTTP {response.status_code}: {response.text}"

        except KeyNotFoundError:
            return False, None, "Private key not found - run 'neocore-keygen'"

        except KeyLoadError as e:
            return False, None, f"Failed to load private key: {e}"

        except APIConnectionError:
            return False, None, "Network connection failed"

        except SigningError:
            return False, None, "Failed to sign request - check your private key"

        except Exception as e:
            return False, None, f"Unexpected error: {e}"

    # Use the production-ready handler
    try:
        client = NeoCoreClient(key_id=key_id)

        # Example 1: GET request
        print("\nExample GET request:")
        success, data, error = safe_api_call(client, "GET", "/api/v1/users")

        if success:
            print(f"  Success! Data: {data}")
        else:
            print(f"  Failed: {error}")

        # Example 2: POST request
        print("\nExample POST request:")
        success, data, error = safe_api_call(
            client,
            "POST",
            "/api/v1/users",
            data={"name": "Bob", "email": "bob@example.com"}
        )

        if success:
            print(f"  Success! Created: {data}")
        else:
            print(f"  Failed: {error}")

    except Exception as e:
        print(f"\nCritical error: {e}")


def main():
    """Run all error handling examples."""
    print("=" * 70)
    print("NeoCore SDK - Error Handling Examples".center(70))
    print("=" * 70)

    print("\nThese examples demonstrate various error handling patterns.")

    key_id = os.getenv("KEY_ID")
    if not key_id:
        print("\nWARNING: KEY_ID environment variable not set")
        print("Some examples may fail. Set it with:")
        print("  export KEY_ID='your-key-id-here'")

    # Run examples
    example_1_basic_exception_handling()
    example_2_http_status_code_handling()
    example_3_retry_logic()
    example_4_production_ready_handler()

    # Summary
    print("\n" + "=" * 70)
    print("All Examples Completed!".center(70))
    print("=" * 70)

    print("\nKey Takeaways:")
    print("  1. Always catch specific exceptions (KeyNotFoundError, etc.)")
    print("  2. Handle HTTP status codes appropriately")
    print("  3. Implement retry logic for transient failures")
    print("  4. Use wrapper functions for production code")
    print("  5. Log errors for debugging")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
