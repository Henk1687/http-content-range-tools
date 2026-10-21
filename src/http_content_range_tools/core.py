# http-content-range-tools
"""Core parser for the HTTP Content-Range header.

The Content-Range header (RFC 7233 section 4.2) has two forms:

    Content-Range: <unit> <start>-<end>/<total>
    Content-Range: <unit> <start>-<end>/*
    Content-Range: <unit> */<total>       (unsatisfied-range)

Only the "bytes" unit is recognised here. Other units raise
InvalidContentRange rather than guessing, since this is a focused tool.
"""

from __future__ import annotations

import re
from typing import NamedTuple, Optional

__all__ = [
    "ContentRange",
    "ContentRangeError",
    "InvalidContentRange",
    "parse_content_range",
]


class ContentRangeError(ValueError):
    """Base class for Content-Range parse errors."""


class InvalidContentRange(ContentRangeError):
    """Raised when a header value cannot be parsed as a bytes content range."""


class ContentRange(NamedTuple):
    """Parsed representation of a Content-Range header.

    Fields:
        start:       First byte position (inclusive), or None for an
                     unsatisfied-range.
        end:         Last byte position (inclusive), or None for an
                     unsatisfied-range.
        total:       Total size in bytes, or None when unknown ("*").
        unit:        The unit string, always "bytes" for accepted values.
        unsatisfied: True if this is an unsatisfied-range response
                     (form ``bytes */<total>``).
    """

    start: Optional[int]
    end: Optional[int]
    total: Optional[int]
    unit: str
    unsatisfied: bool


# The grammar is small enough that a single anchored regex is clearer
# than a hand-rolled state machine and just as fast for header-length
# inputs. Named groups make the branch logic readable below.
_RANGE_RE = re.compile(
    r"bytes[ \t]+"
    r"(?:(?P<start>\d+)-(?P<end>\d+)/(?:(?P<total>\d+)|\*)"
    r"|\*/(?P<utotal>\d+))"
    r"[ \t]*$"
)


def parse_content_range(value: str) -> ContentRange:
    """Parse a Content-Range header value.

    Accepts the three bytes forms defined by RFC 7233:
    ``bytes <start>-<end>/<total>``, ``bytes <start>-<end>/*``, and
    ``bytes */<total>`` (unsatisfied-range). Returns a ContentRange.

    Raises InvalidContentRange for malformed values, non-bytes units, or
    invalid ranges (start > end).
    """
    if not isinstance(value, str):
        raise InvalidContentRange(
            f"Content-Range must be a string, got {type(value).__name__}"
        )

    match = _RANGE_RE.match(value)
    if match is None:
        raise InvalidContentRange(f"Invalid Content-Range header: {value!r}")

    start_s, end_s, total_s, utotal_s = match.group(
        "start", "end", "total", "utotal"
    )

    if utotal_s is not None:
        # Unsatisfied-range form: ``bytes */<total>``. The server cannot
        # or will not satisfy any byte range; only the total is meaningful.
        return ContentRange(
            start=None,
            end=None,
            total=int(utotal_s),
            unit="bytes",
            unsatisfied=True,
        )

    # Satisfied range. Validate the numeric relationship; RFC 7233 implies
    # start <= end, and rejecting otherwise prevents downstream surprises.
    start = int(start_s)
    end = int(end_s)
    if start > end:
        raise InvalidContentRange(
            f"Invalid Content-Range: start ({start}) > end ({end})"
        )

    return ContentRange(
        start=start,
        end=end,
        total=int(total_s) if total_s is not None else None,
        unit="bytes",
        unsatisfied=False,
    )
