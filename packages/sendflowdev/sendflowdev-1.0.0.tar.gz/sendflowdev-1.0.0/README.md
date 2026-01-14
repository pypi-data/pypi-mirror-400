# sendflowdev

Official Python SDK for Sendflow - professional email delivery API.

## Installation

```bash
pip install sendflowdev
```

## Quick Start

```python
from sendflowdev import Sendflow

sendflow = Sendflow(api_key='your-api-key')

# Send an email
result = sendflow.emails.send(
    from_email='hello@yourdomain.com',
    to=['user@example.com'],
    subject='Welcome!',
    html='<h1>Hello World</h1>',
    text='Hello World'
)

print(f"Email sent: {result['id']}")
```

## Configuration

```python
sendflow = Sendflow(
    api_key='your-api-key',
    base_url='https://api.sendflow.dev/functions/v1',  # Optional: custom base URL
    timeout=30,                           # Optional: request timeout (seconds)
    max_retries=3,                        # Optional: max retry attempts
    retry_delay=1.0                       # Optional: delay between retries (seconds)
)
```

## API Reference

### Emails

```python
# Send an email
result = sendflow.emails.send(
    from_email='hello@yourdomain.com',
    to=['user@example.com'],
    subject='Hello',
    html='<p>HTML content</p>',
    text='Plain text content'
)

# Send using a saved template
result = sendflow.emails.send(
    from_email='hello@yourdomain.com',
    to=['user@example.com'],
    template_id='template-uuid-here',
    variables={
        'name': 'John Smith',
        'company': 'Acme Inc',
        'login_url': 'https://app.acme.com/login'
    }
)

# Template with subject override
result = sendflow.emails.send(
    from_email='hello@yourdomain.com',
    to=['user@example.com'],
    template_id='template-uuid-here',
    variables={'name': 'John'},
    subject='Custom Subject Override'
)

# Get email status
email = sendflow.emails.get('email-id')
print(f"Status: {email.status}")
```

### Inbound Emails

Receive and process incoming emails on your verified domains.

```python
# List inbound emails
response = sendflow.inbound_emails.list(
    domain_id='domain-id',  # Optional: filter by domain
    limit=20,
    offset=0
)
for email in response['emails']:
    print(f"From: {email['from_address']}")
    print(f"Subject: {email['subject']}")

# Get a specific inbound email with full content
email = sendflow.inbound_emails.get('inbound-email-id')
print(f"From: {email.from_address}")
print(f"Subject: {email.subject}")
print(f"Body: {email.text_content or email.html_content}")

# Download an attachment
attachment = sendflow.inbound_emails.get_attachment(
    'inbound-email-id',
    'attachment-id'
)
print(f"Download URL: {attachment.download_url}")
# URL expires in 1 hour
```

### Domains

```python
# List domains
domains = sendflow.domains.list()

# Get domain details
domain = sendflow.domains.get('domain-id')

# Add domain
new_domain = sendflow.domains.add('yourdomain.com')

# Verify domain
verified = sendflow.domains.verify('domain-id')
```

### Events

```python
# List all events
events = sendflow.events.list()

# Filter events
delivery_events = sendflow.events.list(
    event_type='delivery',
    limit=50
)
```

### Suppressions

```python
# List suppressions
suppressions = sendflow.suppressions.list()

# Add suppression
sendflow.suppressions.add('user@example.com', 'unsubscribe')

# Remove suppression
sendflow.suppressions.remove('user@example.com')
```

## Webhook Events

Subscribe to webhook events to receive real-time notifications:

```python
# Available events
events = [
    'email.delivered',
    'email.bounced',
    'email.complained',
    'email.opened',
    'email.clicked',
    'email.received',    # Inbound email received
    'domain.created',
    'domain.updated',
    'domain.deleted'
]
```

### Handling Inbound Email Webhooks

```python
# Flask webhook handler
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhooks/sendflow', methods=['POST'])
def handle_webhook():
    event = request.json
    
    if event['type'] == 'email.received':
        print(f"New inbound email from: {event['data']['from']}")
        print(f"Subject: {event['data']['subject']}")
        print(f"Has attachments: {event['data']['hasAttachments']}")
        
        # Fetch full email content if needed
        full_email = sendflow.inbound_emails.get(event['data']['id'])
    
    return 'OK', 200
```

## Error Handling

```python
from sendflowdev import SendflowError

try:
    sendflow.emails.send(
        from_email='hello@yourdomain.com',
        to=['invalid@domain'],
        subject='Test'
    )
except SendflowError as e:
    print(f"Error code: {e.code}")
    print(f"Error details: {e.details}")
    print(f"Status code: {e.status_code}")
```

## Data Classes

The SDK uses dataclasses for structured responses:

```python
from sendflowdev import Domain, Email, Event, Suppression, InboundEmail, InboundAttachment

# All API responses return typed objects
domain = sendflow.domains.get('domain-id')
print(domain.status)  # 'verified'
print(domain.state)   # 'healthy'

# Inbound email with attachments
email = sendflow.inbound_emails.get('email-id')
print(email.from_address)
print(email.subject)
if email.attachments:
    for att in email.attachments:
        print(f"Attachment: {att['filename']}")
```

## License

MIT
