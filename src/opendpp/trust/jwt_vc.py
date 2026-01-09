import json
from typing import Dict, Any, Optional
from joserfc.jwt import JWT
from joserfc.jwk import JWK
from opendpp.core.artifact import Artifact
from opendpp.core.report import ConformanceReport, Finding, Severity
from opendpp.trust.did import resolve_did_web, get_verification_key

def verify_vc_jwt(artifact: Artifact, report: ConformanceReport) -> Optional[Dict[str, Any]]:
    """Verifies a VC secured as a JWT (RFC 7519 / W3C VC JOSE)."""
    try:
        token = artifact.raw_bytes.decode("utf-8")
        
        # 1. Unpack JWT to get header (issuer DID)
        jwt = JWT()
        header = jwt.peek_header(token)
        kid = header.get("kid")
        
        # 2. Extract issuer from payload
        claims = jwt.peek_claims(token)
        iss = claims.get("iss")
        if not iss:
            raise ValueError("Missing 'iss' claim in JWT")
            
        # 3. Resolve DID
        did_doc = resolve_did_web(iss)
        
        # 4. Get key
        vm = get_verification_key(did_doc, kid)
        public_key = JWK.import_key(vm.get("publicKeyJwk"))
        
        # 5. Verify
        result = jwt.decode(token, public_key)
        
        report.add_finding(Finding(
            rule_id="TRUST-VC-JWT-01",
            severity=Severity.INFO,
            message=f"VC-JWT signature verified successfully for issuer {iss}",
            evidence_links=[artifact.sha256]
        ))
        
        return result.claims
        
    except Exception as e:
        report.add_finding(Finding(
            rule_id="TRUST-VC-JWT-ERR",
            severity=Severity.ERROR,
            message=f"VC-JWT verification failed: {str(e)}",
            evidence_links=[artifact.sha256]
        ))
        return None
