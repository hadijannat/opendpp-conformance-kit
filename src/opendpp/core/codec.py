from __future__ import annotations

from typing import Iterable


def decode_json_bytes(raw_bytes: bytes, encodings: Iterable[str] | None = None) -> str:
    """Decode JSON bytes, tolerating BOM and UTF-16 sources."""
    candidates = (
        list(encodings)
        if encodings
        else [
            "utf-8-sig",
            "utf-8",
            "utf-16",
            "utf-16le",
            "utf-16be",
        ]
    )
    last_error: UnicodeDecodeError | None = None
    for encoding in candidates:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
    if last_error:
        raise last_error
    return raw_bytes.decode("utf-8")
