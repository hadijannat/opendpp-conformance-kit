import json
import jsonschema

from opendpp.core.artifact import Artifact
from opendpp.core.codec import decode_json_bytes
from opendpp.core.report import ConformanceReport, Severity


def validate_json_schema(
    artifact: Artifact,
    schema_artifact: Artifact,
    report: ConformanceReport,
    record: bool = True,
) -> list[dict[str, str]]:
    """Validates an artifact against a JSON Schema."""
    collected: list[dict[str, str]] = []
    try:
        data = json.loads(decode_json_bytes(artifact.raw_bytes))
        schema = json.loads(decode_json_bytes(schema_artifact.raw_bytes))

        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema)
        errors = list(validator.iter_errors(data))

        for error in errors:
            location = getattr(error, "json_path", None)
            if not location:
                location = ".".join(str(p) for p in list(error.path)) or "$"
            collected.append(
                {
                    "location": location,
                    "message": error.message,
                }
            )
            if record:
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
        if record:
            report.add_finding(
                rule_id="JS-VAL-ERR",
                severity=Severity.ERROR,
                message=f"Failed to run JSON Schema validation: {str(e)}",
                evidence={"artifact_hash": artifact.sha256},
            )
        collected.append({"location": "$", "message": str(e)})

    return collected
