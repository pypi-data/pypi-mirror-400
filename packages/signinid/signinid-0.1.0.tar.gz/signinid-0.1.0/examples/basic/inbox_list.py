"""
Example: List inbox emails with pagination

Shows how to list email IDs and then fetch full details
for each email. Useful for browsing or processing multiple emails.

Usage:
    python inbox_list.py
"""

from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv(".env.local", override=True)

from signinid import SigninID


def main():
    client = SigninID()

    # List first 5 email IDs
    print("=== Fetching Inbox Emails ===")
    response = client.inbox.list(per_page=5)

    print(f"Found {response.pagination.returned} emails (has_more: {response.pagination.has_more})")
    print()

    # Fetch and display each email
    for email_id in response.data:
        email = client.inbox.get(email_id)

        from_display = (
            f"{email.from_name} <{email.from_address}>"
            if email.from_name
            else email.from_address
        )

        print(f"[{email.email_id[:8]}...] {email.subject}")
        print(f"  From: {from_display}")
        print(f"  To: {', '.join(email.to_addresses)}")
        print(f"  Received: {email.received_at}")
        if email.detected_otp:
            print(f"  OTP: {email.detected_otp}")
        print()

    # Show pagination info
    if response.pagination.has_more:
        print("---")
        print("More emails available. Use page parameter to fetch more:")
        print("  client.inbox.list(page=2, per_page=5)")


if __name__ == "__main__":
    main()
