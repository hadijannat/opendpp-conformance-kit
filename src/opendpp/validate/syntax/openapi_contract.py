from opendpp.core.artifact import Artifact
from opendpp.core.report import ConformanceReport, Severity


def validate_openapi_contract(
    artifact: Artifact, spec_artifact: Artifact, report: ConformanceReport
) -> None:
    """Placeholder for OpenAPI contract validation."""
    report.add_finding(
        rule_id="OPENAPI-SKIP",
        severity=Severity.WARNING,
        message="OpenAPI contract validation not implemented",
        evidence={"spec_hash": spec_artifact.sha256, "artifact_hash": artifact.sha256},
    )
