import base64
import json
from typing import Any, Dict, Optional

from joserfc import jwt
from joserfc import jwk

from opendpp.core.artifact import Artifact
from opendpp.core.report import ConformanceReport, Severity
from opendpp.trust.did import resolve_did_web, get_verification_key


def _b64url_decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def _peek_jwt_header_and_claims(token: str) -> tuple[dict[str, Any], dict[str, Any]]:
    parts = token.split(".")
    if len(parts) < 2:
        raise ValueError("Invalid JWT format")
    header = json.loads(_b64url_decode(parts[0]))
    claims = json.loads(_b64url_decode(parts[1]))
    return header, claims


def verify_vc_jwt(
    artifact: Artifact, report: ConformanceReport
) -> Optional[Dict[str, Any]]:
    """Verifies a VC secured as a JWT (RFC 7519 / W3C VC JOSE)."""
    try:
        token = artifact.raw_bytes.decode("utf-8")

        header, claims = _peek_jwt_header_and_claims(token)
        kid = header.get("kid")
        alg = header.get("alg")

        iss = claims.get("iss")
        if not iss:
            raise ValueError("Missing 'iss' claim in JWT")

        did_doc = resolve_did_web(iss)
        vm = get_verification_key(did_doc, kid)
        public_key_jwk = vm.get("publicKeyJwk")
        if not public_key_jwk:
            raise ValueError("No publicKeyJwk found in verification method")
        public_key = jwk.import_key(public_key_jwk)

        result = jwt.decode(token, public_key, algorithms=[alg] if alg else None)

        report.add_finding(
            rule_id="TRUST-VC-JWT-01",
            severity=Severity.INFO,
            message=f"VC-JWT signature verified successfully for issuer {iss}",
            evidence={"artifact_hash": artifact.sha256, "issuer": iss},
        )

        return result.claims

    except Exception as e:
        report.add_finding(
            rule_id="TRUST-VC-JWT-ERR",
            severity=Severity.ERROR,
            message=f"VC-JWT verification failed: {str(e)}",
            evidence={"artifact_hash": artifact.sha256},
        )
        return None
