from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from joserfc import jwk, jwt

from opendpp.core.report import ConformanceReport


def _utc_now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _report_digest(report: ConformanceReport) -> str:
    payload = json.dumps(report.model_dump(), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def issue_vc_jwt(
    report: ConformanceReport,
    issuer: str,
    jwk_data: Dict[str, Any],
    alg: str = "ES256",
    kid: str | None = None,
) -> tuple[str, Dict[str, Any]]:
    key = jwk.import_key(jwk_data)
    if kid:
        key.kid = kid

    report_hash = _report_digest(report)

    vc = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "type": ["VerifiableCredential", "OpenDPPConformanceCredential"],
        "issuer": issuer,
        "issuanceDate": datetime.now(timezone.utc).isoformat(),
        "credentialSubject": {
            "id": report.target,
            "profile": {
                "id": report.profile_id,
                "version": report.profile_version,
            },
            "passed": report.passed,
            "reportHash": report_hash,
            "artifacts": [
                {
                    "sha256": artifact.sha256,
                    "uri": artifact.uri,
                    "type": artifact.artifact_type,
                }
                for artifact in report.artifacts
            ],
        },
    }

    claims = {
        "iss": issuer,
        "sub": report.target,
        "nbf": _utc_now_ts(),
        "vc": vc,
    }

    header = {"alg": alg}
    if key.kid:
        header["kid"] = key.kid

    token = jwt.encode(header, claims, key, algorithms=[alg])
    return token, vc


def load_jwk(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
