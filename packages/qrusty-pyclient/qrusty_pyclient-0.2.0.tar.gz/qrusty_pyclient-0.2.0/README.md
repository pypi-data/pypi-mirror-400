# qrusty_pyclient

A Python client wrapper for the qrusty API.

## Features

- Connect to a qrusty server
- Publish, consume, ack, and purge messages
- List and manage queues

## Installation

```bash
pip install qrusty_pyclient
```

## Usage

```python
from qrusty_pyclient import QrustyClient

client = QrustyClient(base_url="http://localhost:6784")
client.create_queue(name="orders", ordering="MaxFirst", allow_duplicates=True)
client.publish(queue="orders", priority=100, payload={"order_id": 123})
message = client.consume(queue="orders", consumer_id="worker-1")
if message is not None:
	client.ack(queue="orders", message_id=message["id"], consumer_id="worker-1")
```

## Development

Don't forget your `~/.pypirc` file if you intend to publish to PyPI.

## License

MIT
