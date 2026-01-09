import json
import jsonschema
from typing import List, Optional
from opendpp.core.artifact import Artifact
from opendpp.core.report import ConformanceReport, Finding, Severity

def validate_json_schema(artifact: Artifact, schema_artifact: Artifact, report: ConformanceReport) -> None:
    """Validates an artifact against a JSON Schema."""
    try:
        data = json.loads(artifact.raw_bytes)
        schema = json.loads(schema_artifact.raw_bytes)
        
        validator = jsonschema.Draft7Validator(schema)
        errors = list(validator.iter_errors(data))
        
        for error in errors:
            report.add_finding(Finding(
                rule_id="JS-VAL-01",
                severity=Severity.ERROR,
                message=f"JSON Schema validation error: {error.message}",
                location=error.json_path,
                evidence_links=[artifact.sha256, schema_artifact.sha256]
            ))
            
    except Exception as e:
        report.add_finding(Finding(
            rule_id="JS-VAL-ERR",
            severity=Severity.CRITICAL,
            message=f"Failed to run JSON Schema validation: {str(e)}",
            evidence_links=[artifact.sha256]
        ))
