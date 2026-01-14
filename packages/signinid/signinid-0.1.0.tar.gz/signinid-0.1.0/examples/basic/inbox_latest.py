"""
Example: Get the latest inbox email

This is the simplest way to retrieve the most recent email
received in your SigninID inbox.

Usage:
    python inbox_latest.py
"""

from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".env.local", override=True)

from signinid import SigninID


def main():
    # Create client (reads SIGNINID_SECRET_KEY from environment)
    client = SigninID()

    # Get the latest inbox email
    email = client.inbox.latest()

    if email:
        print("=== Latest Inbox Email ===")
        print("Email ID:", email.email_id)
        print("From:", email.from_name or email.from_address)
        print("To:", ", ".join(email.to_addresses))
        print("Subject:", email.subject)
        print("Received:", email.received_at)
        print()

        # OTP detection - useful for verification emails
        if email.detected_otp:
            print("Detected OTP:", email.detected_otp)

        # Spam analysis
        print("Spam Score:", email.spam_score)
        print("Spam Verdict:", email.spam_verdict)

        # Email body preview
        if email.text_body:
            print()
            print("=== Body Preview ===")
            print(email.text_body[:200] + "...")
    else:
        print("No emails found in inbox.")


if __name__ == "__main__":
    main()
