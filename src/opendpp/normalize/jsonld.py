import json
from pyld import jsonld
from rdflib import Graph
from opendpp.core.artifact import Artifact, ArtifactType

def expand_jsonld(artifact: Artifact) -> Dict[str, Any]:
    """Expands JSON-LD using pyld."""
    if artifact.artifact_type not in [ArtifactType.DPP_PAYLOAD, ArtifactType.JSONLD_CONTEXT]:
        raise ValueError("Artifact is not JSON-LD")
    
    data = json.loads(artifact.raw_bytes)
    expanded = jsonld.expand(data)
    return expanded

def to_rdf_graph(artifact: Artifact) -> Graph:
    """Converts artifact content to an RDFLib graph."""
    g = Graph()
    
    if artifact.artifact_type == ArtifactType.RDF_GRAPH:
        g.parse(data=artifact.raw_bytes, format=artifact.content_type)
    elif artifact.artifact_type == ArtifactType.DPP_PAYLOAD:
        # Try JSON-LD parsing via RDFLib
        g.parse(data=artifact.raw_bytes, format="json-ld")
    
    return g
