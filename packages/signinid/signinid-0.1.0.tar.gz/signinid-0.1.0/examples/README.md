# SigninID SDK Examples

Example projects demonstrating how to use the SigninID Python SDK.

## Prerequisites

1. Python 3.9 or higher
2. A SigninID account with an API key

## Setup

```bash
# Navigate to the basic example
cd examples/basic

# Install the SDK in development mode
pip install -e ../..

# Install example dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your API key
# SIGNINID_SECRET_KEY=sk_live_your_key_here
```

## Running Examples

### Get Latest Inbox Email

Basic usage showing how to retrieve the most recent email.

```bash
python inbox_latest.py
```

### Wait for New Email (Polling)

Useful for E2E testing - waits for a new email to arrive.

```bash
python inbox_wait.py test@your-server.signinid.com
```

### List Inbox Emails

Shows pagination and fetching multiple emails.

```bash
python inbox_list.py
```

### Get Latest Sent Email

View emails sent through your SMTP server.

```bash
python sent_latest.py
```

### Error Handling

Demonstrates handling different error types.

```bash
python error_handling.py
```

## Example Files

| File | Description |
|------|-------------|
| `inbox_latest.py` | Get the most recent inbox email |
| `inbox_wait.py` | Poll for new emails (E2E testing) |
| `inbox_list.py` | List and paginate through emails |
| `sent_latest.py` | Get the most recent sent email |
| `error_handling.py` | Handle SDK errors properly |

## Common Patterns

### E2E Test Flow

```python
from signinid import SigninID

client = SigninID()

# 1. Trigger signup in your app (sends verification email)
# await page.fill('[name="email"]', 'test@your-server.signinid.com')
# await page.click('button[type="submit"]')

# 2. Wait for the verification email
email = client.inbox.wait_for_new(
    to="test@your-server.signinid.com",
    timeout=30,
)

# 3. Use the OTP to complete verification
if email and email.detected_otp:
    # await page.fill('[name="otp"]', email.detected_otp)
    # await page.click('button[type="submit"]')
    pass
```

### Filtering Emails

```python
# Filter by sender
response = client.inbox.list(from_="noreply@myapp.com")

# Filter by subject
response = client.inbox.list(subject="verification")

# Filter by date range
from datetime import datetime
response = client.inbox.list(
    after=datetime(2024, 1, 1),
    before=datetime(2024, 12, 31),
)
```

### Async Usage

```python
import asyncio
from signinid import AsyncSigninID

async def main():
    async with AsyncSigninID() as client:
        email = await client.inbox.latest()
        if email:
            print(f"OTP: {email.detected_otp}")

asyncio.run(main())
```
