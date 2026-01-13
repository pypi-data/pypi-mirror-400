## vestaboard-rw

Typed Python client for Vestaboard’s **Read / Write API** (and only the Read/Write API).

Links:
- [Read / Write API Introduction](https://docs.vestaboard.com/docs/read-write-api/introduction)
- [Authentication](https://docs.vestaboard.com/docs/read-write-api/authentication)
- [Endpoints](https://docs.vestaboard.com/docs/read-write-api/endpoints)

### Install

```bash
pip install vestaboard-rw
```

### Authentication

Enable the Read/Write API in the Vestaboard web app and copy your **Read / Write API key**
([docs](https://docs.vestaboard.com/docs/read-write-api/authentication)).

You can provide the key directly, or via environment variable:

- `VESTABOARD_READ_WRITE_API_KEY`: your key (sent as the `X-Vestaboard-Read-Write-Key`
  header)

### Quickstart

```python
from vestaboard import VestaboardClient

client = VestaboardClient(api_key="YOUR_READ_WRITE_API_KEY")

# Read current message
current = client.read_write.get_current_message()
layout_codes = current.current_message.layout_as_list()

# Send a text message
client.read_write.send_message(text="Hello World")

# Send a layout (validated as either 6x22 Flagship or 3x15 Note)
layout = [[0 for _ in range(22)] for _ in range(6)]
client.read_write.send_message(layout=layout)
```

### Rate limiting

Vestaboard notes that if you send more than **1 message every 15 seconds**, messages may
be dropped ([docs](https://docs.vestaboard.com/docs/read-write-api/endpoints)).

### Configuration

The underlying HTTP client supports timeouts and retries:

- `VESTABOARD_TIMEOUT_SECONDS` (float, default 10.0)
- `VESTABOARD_MAX_RETRIES` (int, default 3)
- `VESTABOARD_RETRY_BACKOFF_SECONDS` (float, default 0.5)

### Exceptions

All errors derive from `vestaboard.exceptions.ApiError` and include the HTTP status code
when available:

- `AuthenticationError` (401)
- `ValidationError` (400)
- `NotFoundError` (404)
- `RateLimitError` (429)
- `ServerError` (5xx)
- `NetworkError` (transport-level failures)

### Development

```bash
pip install -e ".[dev]"
pytest --cov=vestaboard
mypy vestaboard
flake8 vestaboard tests
```

