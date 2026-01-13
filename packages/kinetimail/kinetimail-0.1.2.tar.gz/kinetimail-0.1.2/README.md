# kinetimail client

A Python client for interacting with the KinetiMail API service.

## Installation

```bash
pip install kinetimail
```

## Basic Usage

```python
from kinetimail import KinetiMail

# Setup client
client = KinetiMail(api_key="your_api_key")

# Create a new inbox
client.create_inbox(email_address="john-doe@free.kinetimail.com", name="John Doe")

# Send message
client.send_message(
    from_address="john-doe@free.kinetimail.com",
    to_address="your-address@example.com",
    subject=f'Hello!',
    body='Hey, how are you?'
)

# List messages
client.list_messages(email_address="john-doe@free.kinetimail.com")

# Read a specifc message
client.get_message(
    email_address="john-doe@free.kinetimail.com",
    message_id="<message_id>"
)
```

## Advanced Usage

```python
# Create a custom domain
client.create_domain(domain="yourdomain.com")

# Initiate verification of domain after DNS setup
client.verify_domain(domain="yourdomain.com")

# Create inbox on your domain after verification
client.create_inbox(email_address="sales@yourdomain.com", name="Sales Team")

# List all domains
client.list_domains()

# Get a domain
client.get_domain(domain="yourdomain.com")

# Delete a domain
client.delete_domain(domain="yourdomain.com")
```

## License

MIT License
