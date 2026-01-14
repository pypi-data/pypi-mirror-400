"""
Example: Wait for a new email (polling)

This is useful for E2E testing when you need to wait for
a verification email after triggering a signup or login flow.

Usage:
    python inbox_wait.py <email>

Example:
    python inbox_wait.py test@your-server.signinid.com
"""

import sys

from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".env.local", override=True)

from signinid import SigninID


def main():
    if len(sys.argv) < 2:
        print("Error: Email address is required.")
        print()
        print("Usage: python inbox_wait.py <email>")
        print("Example: python inbox_wait.py test@your-server.signinid.com")
        sys.exit(1)

    test_email = sys.argv[1]

    client = SigninID()

    print(f"Waiting for new email to: {test_email}")
    print("Timeout: 30 seconds")
    print("Polling...")

    # Wait for a new email (polls every 1 second)
    email = client.inbox.wait_for_new(
        to=test_email,
        timeout=30,  # 30 seconds
    )

    if email:
        print()
        print("=== New Email Received! ===")
        print("Email ID:", email.email_id)
        print("From:", email.from_address)
        print("Subject:", email.subject)
        print("Received:", email.received_at)

        if email.detected_otp:
            print()
            print("Detected OTP:", email.detected_otp)
            print("Use this OTP to complete verification in your test.")
    else:
        print()
        print("Timeout: No new email received within 30 seconds.")


if __name__ == "__main__":
    main()
