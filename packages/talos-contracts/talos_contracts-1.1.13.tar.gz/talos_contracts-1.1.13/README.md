# Talos Contracts (Python)

Talos Protocol contracts - schemas, types, and helper functions for auditable AI agent security.

## Installation

```bash
pip install talos-contracts
```

## Features

- **Cursor derivation**: `derive_cursor(timestamp, event_id)` - Generate cursor from timestamp and event ID
- **Cursor decoding**: `decode_cursor(cursor)` - Parse cursor to extract timestamp and event ID
- **Base64url**: Strict base64url encoding/decoding (no padding)
- **UUIDv7 validation**: `is_uuid_v7(id)` - Validate UUIDv7 strings
- **Event ordering**: `ordering_compare(a, b)` - Compare events by (timestamp DESC, event_id DESC)

## Usage

```python
from talos_contracts import derive_cursor, decode_cursor, is_uuid_v7

# Derive a cursor
cursor = derive_cursor(1703721600, "0190a5e0-7c3a-7000-8000-000000000001")

# Decode a cursor
decoded = decode_cursor(cursor)
print(decoded)  # {"timestamp": 1703721600, "event_id": "0190a5e0-..."}

# Validate UUIDv7
is_valid = is_uuid_v7("0190a5e0-7c3a-7000-8000-000000000001")  # True
```

## License

MIT
