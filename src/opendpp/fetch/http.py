from __future__ import annotations

from typing import Optional

import requests

from opendpp.core.artifact import Artifact, ArtifactType


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

        content_type = response.headers.get("Content-Type")
        artifact_type = ArtifactType.DPP_PAYLOAD
        if content_type:
            if "application/ld+json" in content_type:
                artifact_type = ArtifactType.DPP_PAYLOAD
            elif "application/json" in content_type:
                artifact_type = ArtifactType.DPP_PAYLOAD

        return Artifact.from_bytes(
            uri=response.url,
            content_type=content_type,
            artifact_type=artifact_type,
            raw_bytes=response.content or b"",
            metadata={"status_code": response.status_code, "headers": dict(response.headers)},
        )
