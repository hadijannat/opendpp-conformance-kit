import json

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF

from aas_core3 import jsonization as aas_json

from opendpp.core.artifact import Artifact

AAS = Namespace("https://admin-shell.io/aas/3/0/")


def aas_to_rdf(artifact: Artifact) -> Graph:
    """Converts a subset of AAS environment to RDF for validation."""
    # Pragmatic approach: extract key IDs and Submodel structure
    env = aas_json.environment_from_jsonable(json.loads(artifact.raw_bytes))
    g = Graph()
    g.bind("aas", AAS)

    if env.asset_administration_shells:
        for shell in env.asset_administration_shells:
            if shell.id:
                shell_uri = URIRef(f"shell:{shell.id}")
                g.add((shell_uri, RDF.type, AAS.AssetAdministrationShell))
                g.add((shell_uri, AAS.id, Literal(shell.id)))

    if env.submodels:
        for submodel in env.submodels:
            if submodel.id:
                sm_uri = URIRef(f"submodel:{submodel.id}")
                g.add((sm_uri, RDF.type, AAS.Submodel))
                g.add((sm_uri, AAS.id, Literal(submodel.id)))
                # Further mapping of SubmodelElements could go here

    return g
