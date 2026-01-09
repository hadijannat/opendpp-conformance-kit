from pyshacl import validate
from rdflib import Graph
from opendpp.core.artifact import Artifact
from opendpp.core.report import ConformanceReport, Severity
from opendpp.normalize.jsonld import to_rdf_graph


def validate_shacl(
    artifact: Artifact, shapes_artifact: Artifact, report: ConformanceReport
) -> None:
    """Validates an RDF graph against SHACL shapes."""
    try:
        data_graph = to_rdf_graph(artifact)
        shapes_graph = Graph().parse(data=shapes_artifact.raw_bytes, format="turtle")

        conforms, results_graph, results_text = validate(
            data_graph,
            shacl_graph=shapes_graph,
            inference="rdfs",
            serialize_report_graph=True,
        )

        if not conforms:
            report.add_finding(
                rule_id="SHACL-VAL-01",
                severity=Severity.ERROR,
                message=f"SHACL validation failure: {results_text[:500]}...",
                evidence={
                    "artifact_hash": artifact.sha256,
                    "shapes_hash": shapes_artifact.sha256,
                },
            )

    except Exception as e:
        report.add_finding(
            rule_id="SHACL-VAL-ERR",
            severity=Severity.ERROR,
            message=f"Failed to run SHACL validation: {str(e)}",
            evidence={"artifact_hash": artifact.sha256},
        )
