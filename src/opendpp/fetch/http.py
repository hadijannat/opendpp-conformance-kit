import requests
import hashlib
from typing import Optional, Dict, Any
from opendpp.core.artifact import Artifact, ArtifactType

class HttpFetcher:
    def __init__(self, timeout: int = 20, max_redirects: int = 5):
        self.session = requests.Session()
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session.max_redirects = max_redirects

    def fetch(self, url: str, headers: Optional[Dict[str, str]] = None) -> Artifact:
        """Fetches an artifact via HTTP with content negotiation."""
        default_headers = {
            "Accept": "application/ld+json, application/json, application/vc+json, text/turtle, */*"
        }
        if headers:
            default_headers.update(headers)

        response = self.session.get(url, headers=default_headers, timeout=self.timeout)
        response.raise_for_status()

        content = response.content
        sha256 = hashlib.sha256(content).hexdigest()
        
        content_type = response.headers.get("Content-Type", "").split(";")[0]
        
        # Determine artifact type from content type
        artifact_type = self._map_content_type(content_type, content)

        return Artifact(
            uri=url,
            content_type=content_type,
            artifact_type=artifact_type,
            raw_bytes=content,
            sha256=sha256,
            metadata={
                "headers": dict(response.headers),
                "final_url": response.url,
                "status_code": response.status_code
            }
        )

    def _map_content_type(self, content_type: str, content: bytes) -> ArtifactType:
        if "json" in content_type:
            # Check for @context to see if it's JSON-LD
            if b"@context" in content:
                return ArtifactType.JSONLD_CONTEXT if content_type == "application/ld+json" else ArtifactType.DPP_PAYLOAD
            return ArtifactType.DPP_PAYLOAD
        if "turtle" in content_type or "ntriples" in content_type:
            return ArtifactType.RDF_GRAPH
        if "xml" in content_type:
            return ArtifactType.AAS_PAYLOAD
        return ArtifactType.DPP_PAYLOAD
