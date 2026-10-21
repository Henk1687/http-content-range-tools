# http-content-range-tools
"""Parse HTTP Content-Range header values.

Exposes:
    ContentRange         -- namedtuple with start, end, total, unit, and
                            unsatisfied fields.
    ContentRangeError    -- base exception for parse failures.
    InvalidContentRange -- raised when the header is malformed.
    parse_content_range  -- parse a Content-Range header string.
"""

from http_content_range_tools.core import (
    ContentRange,
    ContentRangeError,
    InvalidContentRange,
    parse_content_range,
)

__all__ = [
    "ContentRange",
    "ContentRangeError",
    "InvalidContentRange",
    "parse_content_range",
]
