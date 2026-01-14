"""
Example: Error handling

Shows how to handle different types of errors that
the SDK might throw.

Usage:
    python error_handling.py
"""

from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".env.local", override=True)

from signinid import (
    SigninID,
    SigninIDError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    TimeoutError,
    RateLimitError,
)


def demonstrate_auth_error():
    print("=== Authentication Error ===")
    try:
        # Using an invalid API key
        client = SigninID(secret_key="sk_live_invalid_key")
        client.inbox.latest()
    except AuthenticationError as error:
        print("Caught AuthenticationError:")
        print("  Message:", error.message)
    print()


def demonstrate_not_found_error():
    print("=== Not Found Error ===")
    try:
        client = SigninID()
        # Try to get a non-existent email
        client.inbox.get("00000000-0000-0000-0000-000000000000")
    except SigninIDError as error:
        print("Caught SigninIDError:")
        print("  Code:", error.code)
        print("  Message:", error.message)
        print("  Status:", error.status)
    print()


def demonstrate_error_types():
    print("=== Error Types Summary ===")
    print()
    print("SigninIDError       - Base class for all SDK errors")
    print("AuthenticationError - Invalid or missing API key (401)")
    print("ValidationError     - Invalid request parameters (400)")
    print("NetworkError        - Network connectivity issues")
    print("TimeoutError        - Request timeout exceeded")
    print("RateLimitError      - Too many requests (429)")
    print()
    print("All errors have: code, message, status properties")
    print("RateLimitError also has: retry_after (seconds to wait)")


def main():
    demonstrate_auth_error()
    demonstrate_not_found_error()
    demonstrate_error_types()


if __name__ == "__main__":
    main()
