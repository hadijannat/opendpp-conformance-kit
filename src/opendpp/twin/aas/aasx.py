import json
import io
import zipfile
from typing import List, Optional
from aas_core3.jsonization import dict_to_environment
from opendpp.core.artifact import Artifact, ArtifactType

def parse_aas_json(artifact: Artifact):
    """Parses AAS JSON using aas-core-python."""
    if artifact.artifact_type != ArtifactType.AAS_PAYLOAD:
        raise ValueError("Artifact is not AAS JSON")
    
    data = json.loads(artifact.raw_bytes)
    environment = dict_to_environment(data)
    return environment

def extract_aasx(artifact: Artifact) -> List[Artifact]:
    """Extracts artifacts from an AASX package."""
    if artifact.artifact_type != ArtifactType.AASX_PACKAGE:
        raise ValueError("Artifact is not AASX")
    
    extracted_artifacts = []
    with zipfile.ZipFile(io.BytesIO(artifact.raw_bytes)) as z:
        for name in z.namelist():
            # IDTA Part 5: look for environment files (usually .json or .xml)
            if name.endswith((".json", ".xml", ".aasx")):
                content = z.read(name)
                # Map to specific artifact type
                atype = ArtifactType.AAS_PAYLOAD if name.endswith((".json", ".xml")) else ArtifactType.AASX_PACKAGE
                extracted_artifacts.append(Artifact(
                    uri=f"{artifact.uri}#{name}",
                    content_type="application/json" if name.endswith(".json") else "application/xml",
                    artifact_type=atype,
                    raw_bytes=content,
                    sha256="TODO", # compute hash
                    metadata={"filename": name}
                ))
    return extracted_artifacts
