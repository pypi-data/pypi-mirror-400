# Sails Python SDK

Python client for the Sails Developer API.

## Install

```bash
pip install sails-sdk
```

## Usage

```python
from sails_sdk import SailsClient

client = SailsClient(api_key="sails_sk_...")

response = client.predict(
    image_url="https://example.com/shoe.jpg",
    description="Black Nike Air Max 90 on a white background",
    limit=10,
)

print(response["price_lower"], response["price_upper"])
```

By default the client targets `https://sails.live/api/v1`. Override it if needed:

```python
client = SailsClient(
    api_key="sails_sk_...",
    base_url="https://sails.live/api/v1",
)
```
