"""
Example: Get the latest sent email

View emails that were sent through your SMTP server.
Useful for verifying that your application is sending
emails correctly.

Usage:
    python sent_latest.py
"""

from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".env.local", override=True)

from signinid import SigninID


def main():
    client = SigninID()

    # Get the latest sent email
    email = client.sent.latest()

    if email:
        print("=== Latest Sent Email ===")
        print("Email ID:", email.email_id)
        print("From:", email.from_name or email.from_address)
        print("To:", ", ".join(email.to_addresses))
        if email.cc_addresses:
            print("CC:", ", ".join(email.cc_addresses))
        if email.bcc_addresses:
            print("BCC:", ", ".join(email.bcc_addresses))
        print("Subject:", email.subject)
        print("Sent:", email.sent_at)
        print()

        # Spam analysis - check if your emails might be flagged as spam
        print("=== Spam Analysis ===")
        print("Spam Score:", email.spam_score)
        print("Spam Verdict:", email.spam_verdict)

        # OTP detection
        if email.detected_otp:
            print()
            print("Detected OTP:", email.detected_otp)

        # Email body preview
        if email.text_body:
            print()
            print("=== Body Preview ===")
            print(email.text_body[:200] + "...")
    else:
        print("No sent emails found.")


if __name__ == "__main__":
    main()
