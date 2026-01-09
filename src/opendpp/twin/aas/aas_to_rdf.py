from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, XSD
from opendpp.core.artifact import Artifact
from aas_core3.jsonization import dict_to_environment

AAS = Namespace("https://admin-shell.io/aas/3/0/")

def aas_to_rdf(artifact: Artifact) -> Graph:
    """Converts a subset of AAS environment to RDF for validation."""
    # Pragmatic approach: extract key IDs and Submodel structure
    env = dict_to_environment(json.loads(artifact.raw_bytes))
    g = Graph()
    g.bind("aas", AAS)
    
    for shell in env.asset_administration_shells:
        shell_uri = URIRef(f"shell:{shell.id}")
        g.add((shell_uri, RDF.type, AAS.AssetAdministrationShell))
        g.add((shell_uri, AAS.id, Literal(shell.id)))
        
    for submodel in env.submodels:
        sm_uri = URIRef(f"submodel:{submodel.id}")
        g.add((sm_uri, RDF.type, AAS.Submodel))
        g.add((sm_uri, AAS.id, Literal(submodel.id)))
        # Further mapping of SubmodelElements could go here
        
    return g
