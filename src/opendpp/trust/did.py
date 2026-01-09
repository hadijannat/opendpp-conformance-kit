from typing import Any, Optional

import requests


def resolve_did_web(did: str) -> dict[str, Any]:
    """Resolves did:web to a DID Document."""
    if not did.startswith("did:web:"):
        raise ValueError("Only did:web is supported in MVP")

    # did:web:example.com -> https://example.com/.well-known/did.json
    # did:web:example.com:path -> https://example.com/path/did.json
    parts = did.split(":")
    domain = parts[2]
    path = "/".join(parts[3:]) if len(parts) > 3 else ".well-known"

    url = f"https://{domain}/{path}/did.json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    did_doc: dict[str, Any] = response.json()
    return did_doc


def get_verification_key(
    did_doc: dict[str, Any], kid: Optional[str] = None
) -> dict[str, Any]:
    """Extracts a verification key from a DID Document."""
    methods: list[dict[str, Any]] = did_doc.get("verificationMethod", [])
    if not methods:
        raise ValueError("No verification methods found in DID Document")

    if kid:
        for m in methods:
            method_id = m.get("id", "")
            if method_id == kid or method_id.endswith(f"#{kid}"):
                return m

    # Return first method if no kid provided or not found
    return methods[0]
