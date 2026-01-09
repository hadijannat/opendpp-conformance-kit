from __future__ import annotations

import os
import re
from enum import Enum
from urllib.parse import ParseResult, urlparse


class InputType(str, Enum):
    URL = "url"
    DIGITAL_LINK = "digital_link"
    DID = "did"
    FILE = "file"


def _is_probable_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def _is_digital_link(parsed_url: ParseResult) -> bool:
    host = parsed_url.netloc.lower()
    if host.endswith("id.gs1.org"):
        return True

    # GS1 Digital Link commonly includes the GTIN (AI 01) path segment.
    if re.search(r"/01/\d{8,14}(?:/|$)", parsed_url.path):
        return True

    return False


def parse_input(raw: str) -> tuple[InputType, str]:
    """Determine the input type and return a canonical target string."""
    value = raw.strip()
    if value.lower().startswith("did:"):
        return InputType.DID, value

    if _is_probable_url(value):
        parsed = urlparse(value)
        if _is_digital_link(parsed):
            return InputType.DIGITAL_LINK, value
        return InputType.URL, value

    if value.startswith("file://"):
        path = value[7:]
        if os.path.exists(path):
            return InputType.FILE, path
        return InputType.FILE, path

    if os.path.exists(value):
        return InputType.FILE, value

    # Default to URL for unknown identifiers that may be resolvable.
    return InputType.URL, value
