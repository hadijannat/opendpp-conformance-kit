from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ArtifactType(str, Enum):
    DPP_PAYLOAD = "dpp_payload"
    AAS_PAYLOAD = "aas_payload"
    VC_JWT = "vc_jwt"
    OPENAPI_DOC = "openapi_doc"
    JSONLD_CONTEXT = "jsonld_context"
    RDF_GRAPH = "rdf_graph"
    AASX_PACKAGE = "aasx_package"

class Artifact(BaseModel):
    uri: str
    content_type: str
    artifact_type: ArtifactType
    raw_bytes: bytes
    sha256: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Profile(BaseModel):
    id: str
    version: str
    description: Optional[str] = None
    entrypoint_media_types: List[str] = Field(default_factory=list)
    artifacts: List[str] = Field(default_factory=list) # paths to schemas, shapes, etc.

class RunContext(BaseModel):
    profile: Profile
    trust_policy: Dict[str, Any] = Field(default_factory=dict)
    network_policy: Dict[str, Any] = Field(default_factory=dict)
    report_artifacts_dir: str = "report_artifacts"
