# http-content-range-tools

Parses HTTP `Content-Range` header values into `start`, `end`, and `total` fields, handling both normal byte ranges and the unsatisfied-range form.

## Usage

```python
from http_content_range_tools import (
    ContentRange,
    ContentRangeError,
    InvalidContentRange,
    parse_content_range,
)

result = parse_content_range("bytes 0-499/1000")
print(result.start)   # 0
print(result.end)     # 499
print(result.total)   # 1000
print(result.unsatisfied)  # False

# Unsatisfied-range form (server cannot satisfy any range):
result = parse_content_range("bytes */1000")
print(result.start)        # None
print(result.total)         # 1000
print(result.unsatisfied)   # True

# Unknown total:
result = parse_content_range("bytes 0-499/*")
print(result.total)  # None

# Malformed values raise InvalidContentRange:
try:
    parse_content_range("items 0-499/1000")
except InvalidContentRange as exc:
    print(exc)
```

## Why this exists

Reading a `Content-Range` header looks simple, but the RFC 7233 grammar has three distinct byte forms — `start-end/total`, `start-end/*`, and `*/total` — and conflating them produces subtle bugs. This library gives a single function that returns a structured result with explicit `None` markers for unknown or unsatisfied fields, so callers can branch on data rather than re-parsing strings.

The trade-off: only the `bytes` unit is accepted. Other units raise `InvalidContentRange` rather than being passed through or guessed at. If you need non-byte units, parse them yourself.

## Edge cases

The unsatisfied-range form (`bytes */1000`) sets `start` and `end` to `None` and `unsatisfied` to `True`. If your code assumes `start` is always an integer, you must check this flag first. A range where `start > end` is rejected as invalid.

Run tests with:

```
PYTHONPATH=src python -m unittest discover -s tests
```
