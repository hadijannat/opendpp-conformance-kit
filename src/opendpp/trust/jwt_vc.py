import base64
import json
from typing import Any, Optional

from joserfc import jwk, jwt

from opendpp.core.artifact import Artifact
from opendpp.core.report import ConformanceReport, Severity
from opendpp.trust.did import get_verification_key, resolve_did_web


def _decode_jwt_part(part: str) -> dict[str, Any]:
    """Decode a base64url-encoded JWT part (header or payload)."""
    # Add padding if needed
    padding = 4 - len(part) % 4
    if padding != 4:
        part += "=" * padding
    decoded = base64.urlsafe_b64decode(part)
    result: dict[str, Any] = json.loads(decoded)
    return result


def _peek_jwt(token: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Extract header and claims from a JWT without verification."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format: expected 3 parts")
    header = _decode_jwt_part(parts[0])
    claims = _decode_jwt_part(parts[1])
    return header, claims


def verify_vc_jwt(
    artifact: Artifact, report: ConformanceReport
) -> Optional[dict[str, Any]]:
    """Verifies a VC secured as a JWT (RFC 7519 / W3C VC JOSE)."""
    try:
        token = artifact.raw_bytes.decode("utf-8").strip()

        # 1. Peek at JWT to get header and claims without verification
        header, claims = _peek_jwt(token)
        kid = header.get("kid")

        # 2. Extract issuer from payload
        iss = claims.get("iss")
        if not iss:
            raise ValueError("Missing 'iss' claim in JWT")

        # 3. Resolve DID
        did_doc = resolve_did_web(iss)

        # 4. Get key
        vm = get_verification_key(did_doc, kid)
        public_key_jwk = vm.get("publicKeyJwk")
        if not public_key_jwk:
            raise ValueError("No publicKeyJwk found in verification method")
        public_key = jwk.import_key(public_key_jwk)

        # 5. Verify the JWT signature
        result = jwt.decode(token, public_key)

        report.add_finding(
            rule_id="TRUST-VC-JWT-01",
            severity=Severity.INFO,
            message=f"VC-JWT signature verified successfully for issuer {iss}",
            evidence={"artifact_hash": artifact.sha256, "issuer": iss},
        )

        return dict(result.claims)

    except Exception as e:
        report.add_finding(
            rule_id="TRUST-VC-JWT-ERR",
            severity=Severity.ERROR,
            message=f"VC-JWT verification failed: {str(e)}",
            evidence={"artifact_hash": artifact.sha256},
        )
        return None
