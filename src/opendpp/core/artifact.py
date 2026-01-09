from __future__ import annotations

import hashlib
from enum import Enum
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field

class ArtifactType(str, Enum):
    DPP_PAYLOAD = "dpp_payload"
    AAS_PAYLOAD = "aas_payload"
    VC_JWT = "vc_jwt"
    JSON_SCHEMA = "json_schema"
    OPENAPI_DOC = "openapi_doc"
    JSONLD_CONTEXT = "jsonld_context"
    RDF_GRAPH = "rdf_graph"
    SHACL_SHAPES = "shacl_shapes"
    AASX_PACKAGE = "aasx_package"

class Artifact(BaseModel):
    uri: str
    content_type: Optional[str]
    artifact_type: ArtifactType
    raw_bytes: bytes
    sha256: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_bytes(
        cls,
        *,
        uri: str,
        content_type: Optional[str],
        artifact_type: ArtifactType,
        raw_bytes: bytes,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Artifact":
        digest = hashlib.sha256(raw_bytes).hexdigest()
        return cls(
            uri=uri,
            content_type=content_type,
            artifact_type=artifact_type,
            raw_bytes=raw_bytes,
            sha256=digest,
            metadata=metadata or {},
        )

class ProfileArtifacts(BaseModel):
    schemas: List[str] = Field(default_factory=list)
    shapes: List[str] = Field(default_factory=list)
    openapi: List[str] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    contexts: List[str] = Field(default_factory=list)


class ProfileTrust(BaseModel):
    allowed_issuers: List[str] = Field(default_factory=list)
    vc_formats: List[str] = Field(default_factory=list)


class Profile(BaseModel):
    id: str
    version: str
    description: Optional[str] = None
    entrypoint_media_types: List[str] = Field(default_factory=list)
    artifacts: ProfileArtifacts = Field(default_factory=ProfileArtifacts)
    trust: ProfileTrust = Field(default_factory=ProfileTrust)

class RunContext(BaseModel):
    profile: Profile
    trust_policy: Dict[str, Any] = Field(default_factory=dict)
    network_policy: Dict[str, Any] = Field(default_factory=dict)
    report_artifacts_dir: str = "report_artifacts"
