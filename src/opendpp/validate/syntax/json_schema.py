import json
import jsonschema
from opendpp.core.artifact import Artifact
from opendpp.core.report import ConformanceReport, Severity


def validate_json_schema(
    artifact: Artifact, schema_artifact: Artifact, report: ConformanceReport
) -> None:
    """Validates an artifact against a JSON Schema."""
    try:
        data = json.loads(artifact.raw_bytes)
        schema = json.loads(schema_artifact.raw_bytes)

        validator = jsonschema.Draft7Validator(schema)
        errors = list(validator.iter_errors(data))

        for error in errors:
            location = getattr(error, "json_path", None)
            if not location:
                location = ".".join(str(p) for p in list(error.path)) or "$"
            report.add_finding(
                rule_id="JS-VAL-01",
                severity=Severity.ERROR,
                message=f"JSON Schema validation error: {error.message}",
                evidence={
                    "location": location,
                    "artifact_hash": artifact.sha256,
                    "schema_hash": schema_artifact.sha256,
                },
            )

    except Exception as e:
        report.add_finding(
            rule_id="JS-VAL-ERR",
            severity=Severity.ERROR,
            message=f"Failed to run JSON Schema validation: {str(e)}",
            evidence={"artifact_hash": artifact.sha256},
        )
