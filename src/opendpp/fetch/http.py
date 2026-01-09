from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class Artifact:
    uri: str
    content_type: Optional[str]
    sha256: str
    artifact_type: str


class HttpFetcher:
    def __init__(self, timeout: int = 15) -> None:
        self.timeout = timeout

    def fetch(self, url: str) -> Artifact:
        headers = {
            "Accept": "application/ld+json, application/json, */*;q=0.1",
            "User-Agent": "opendpp-conformance-kit/0.1",
        }
        response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
        response.raise_for_status()

        content = response.content or b""
        digest = hashlib.sha256(content).hexdigest()
        content_type = response.headers.get("Content-Type")
        artifact_type = "binary"
        if content_type:
            if "application/ld+json" in content_type:
                artifact_type = "jsonld"
            elif "application/json" in content_type:
                artifact_type = "json"

        return Artifact(
            uri=response.url,
            content_type=content_type,
            sha256=digest,
            artifact_type=artifact_type,
        )
