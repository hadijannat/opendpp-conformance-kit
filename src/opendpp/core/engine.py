from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Any, Iterable

from opendpp.core.artifact import Artifact, ArtifactType
from opendpp.core.report import ConformanceReport, Severity
from opendpp.fetch.http import HttpFetcher
from opendpp.policy.espr_core import PolicyEngine
from opendpp.profiles.loader import load_profile, resolve_artifact_paths
from opendpp.resolve.parse_input import InputType, parse_input
from opendpp.twin.aas.aas_to_rdf import aas_to_rdf
from opendpp.twin.aas.aasx import extract_aasx, parse_aas_json
from opendpp.validate.semantic.shacl import validate_shacl
from opendpp.validate.syntax.openapi_contract import validate_openapi_contract
from opendpp.validate.syntax.json_schema import validate_json_schema


def _looks_like_aas_json(data: dict[str, Any]) -> bool:
    return any(
        key in data
        for key in ["assetAdministrationShells", "submodels", "conceptDescriptions"]
    )


def _guess_content_type(path: Path) -> str | None:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed


def _artifact_type_from_path(path: Path, raw_bytes: bytes) -> ArtifactType:
    suffix = path.suffix.lower()
    if suffix == ".aasx":
        return ArtifactType.AASX_PACKAGE
    if suffix in {".ttl", ".nq", ".nt"}:
        return ArtifactType.RDF_GRAPH
    if suffix in {".xml"}:
        return ArtifactType.AAS_PAYLOAD
    if suffix in {".json", ".jsonld", ".json-ld"}:
        try:
            data = json.loads(raw_bytes)
            if isinstance(data, dict) and _looks_like_aas_json(data):
                return ArtifactType.AAS_PAYLOAD
        except Exception:
            pass
        return ArtifactType.DPP_PAYLOAD
    return ArtifactType.DPP_PAYLOAD


def _persist_artifact(artifact: Artifact, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    extension = ".bin"
    if artifact.content_type:
        if "json" in artifact.content_type:
            extension = ".json"
        elif "xml" in artifact.content_type:
            extension = ".xml"
        elif "turtle" in artifact.content_type:
            extension = ".ttl"
    path = output_dir / f"{artifact.sha256}{extension}"
    if not path.exists():
        path.write_bytes(artifact.raw_bytes)
    artifact.metadata["stored_path"] = str(path)


def _load_file_artifact(path: Path) -> Artifact:
    raw_bytes = path.read_bytes()
    content_type = _guess_content_type(path)
    artifact_type = _artifact_type_from_path(path, raw_bytes)
    return Artifact.from_bytes(
        uri=str(path),
        content_type=content_type,
        artifact_type=artifact_type,
        raw_bytes=raw_bytes,
    )


def _ingest_target(target: str) -> tuple[list[Artifact], str]:
    input_type, canonical = parse_input(target)
    artifacts: list[Artifact] = []

    if input_type in {InputType.URL, InputType.DIGITAL_LINK}:
        fetcher = HttpFetcher()
        artifacts.append(fetcher.fetch(canonical))
    elif input_type == InputType.FILE:
        artifacts.append(_load_file_artifact(Path(canonical)))
    else:
        raise ValueError(f"Unsupported input type: {input_type}")

    return artifacts, canonical


def _load_artifacts_from_paths(
    paths: Iterable[str], artifact_type: ArtifactType
) -> list[Artifact]:
    loaded: list[Artifact] = []
    for path in paths:
        raw_bytes = Path(path).read_bytes()
        content_type = _guess_content_type(Path(path))
        loaded.append(
            Artifact.from_bytes(
                uri=str(path),
                content_type=content_type,
                artifact_type=artifact_type,
                raw_bytes=raw_bytes,
            )
        )
    return loaded


def run_conformance_check(
    target: str,
    profile_ref: str,
    report_artifacts_dir: str = "report_artifacts",
) -> ConformanceReport:
    loaded_profile = resolve_artifact_paths(load_profile(profile_ref))
    manifest = loaded_profile.manifest

    report = ConformanceReport(
        target=target,
        profile_id=manifest.id,
        profile_version=manifest.version,
    )

    artifacts, canonical = _ingest_target(target)
    report.add_finding(
        rule_id="RESOLVE-INPUT",
        severity=Severity.INFO,
        message=f"Resolved input to {canonical}",
    )

    # Expand AASX packages
    expanded: list[Artifact] = []
    for artifact in artifacts:
        if artifact.artifact_type == ArtifactType.AASX_PACKAGE:
            expanded.extend(extract_aasx(artifact))
    artifacts.extend(expanded)

    output_dir = Path(report_artifacts_dir)
    for artifact in artifacts:
        _persist_artifact(artifact, output_dir)
        report.add_artifact(
            uri=artifact.uri,
            sha256=artifact.sha256,
            content_type=artifact.content_type,
            artifact_type=artifact.artifact_type.value,
            size=len(artifact.raw_bytes),
            metadata=artifact.metadata,
        )

    # AAS parse sanity checks
    for artifact in artifacts:
        if artifact.artifact_type == ArtifactType.AAS_PAYLOAD:
            if artifact.content_type and "json" not in artifact.content_type:
                report.add_finding(
                    rule_id="AAS-JSON-SKIP",
                    severity=Severity.WARNING,
                    message="Skipping AAS JSON parse for non-JSON payload",
                    evidence={"artifact_hash": artifact.sha256},
                )
                continue
            try:
                parse_aas_json(artifact)
                report.add_finding(
                    rule_id="AAS-JSON-01",
                    severity=Severity.INFO,
                    message="AAS JSON parsed successfully",
                    evidence={"artifact_hash": artifact.sha256},
                )
            except Exception as exc:
                report.add_finding(
                    rule_id="AAS-JSON-ERR",
                    severity=Severity.ERROR,
                    message=f"AAS JSON parsing failed: {str(exc)}",
                    evidence={"artifact_hash": artifact.sha256},
                )

    # JSON Schema validation
    schema_artifacts = _load_artifacts_from_paths(
        manifest.artifacts.schemas, ArtifactType.JSON_SCHEMA
    )
    for schema in schema_artifacts:
        for artifact in artifacts:
            if artifact.artifact_type == ArtifactType.DPP_PAYLOAD:
                validate_json_schema(artifact, schema, report)

    # OpenAPI validation (optional)
    openapi_artifacts = _load_artifacts_from_paths(
        manifest.artifacts.openapi, ArtifactType.OPENAPI_DOC
    )
    for spec in openapi_artifacts:
        for artifact in artifacts:
            if artifact.artifact_type == ArtifactType.DPP_PAYLOAD:
                validate_openapi_contract(artifact, spec, report)

    # SHACL validation
    shape_artifacts = _load_artifacts_from_paths(
        manifest.artifacts.shapes, ArtifactType.SHACL_SHAPES
    )
    for shape in shape_artifacts:
        for artifact in artifacts:
            if artifact.artifact_type == ArtifactType.DPP_PAYLOAD:
                validate_shacl(artifact, shape, report)
            elif artifact.artifact_type == ArtifactType.AAS_PAYLOAD:
                try:
                    graph = aas_to_rdf(artifact)
                    rdf_bytes = graph.serialize(format="turtle")
                    rdf_raw = (
                        rdf_bytes
                        if isinstance(rdf_bytes, bytes)
                        else rdf_bytes.encode("utf-8")
                    )
                    rdf_artifact = Artifact.from_bytes(
                        uri=f"{artifact.uri}#rdf",
                        content_type="text/turtle",
                        artifact_type=ArtifactType.RDF_GRAPH,
                        raw_bytes=rdf_raw,
                    )
                    _persist_artifact(rdf_artifact, output_dir)
                    report.add_artifact(
                        uri=rdf_artifact.uri,
                        sha256=rdf_artifact.sha256,
                        content_type=rdf_artifact.content_type,
                        artifact_type=rdf_artifact.artifact_type.value,
                        size=len(rdf_artifact.raw_bytes),
                        metadata=rdf_artifact.metadata,
                    )
                    validate_shacl(rdf_artifact, shape, report)
                except Exception as exc:
                    report.add_finding(
                        rule_id="AAS-RDF-ERR",
                        severity=Severity.ERROR,
                        message=f"Failed to convert AAS to RDF: {str(exc)}",
                        evidence={"artifact_hash": artifact.sha256},
                    )

    # Policy checks
    for rules_path in manifest.artifacts.rules:
        engine = PolicyEngine(rules_path)
        engine.run_checks(artifacts, report)

    report.finalize()
    return report
