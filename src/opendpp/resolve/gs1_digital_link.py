import re
from typing import Dict
from urllib.parse import urlparse, parse_qs

# Application Identifiers (AI) commonly used in Digital Link
# https://ref.gs1.org/standards/digital-link/uri-syntax/
AI_REGEX = {
    "gtin": r"^01$",
    "sscc": r"^00$",
    "cpv": r"^22$",
    "lot": r"^10$",
    "ser": r"^21$",
    "date": r"^17$",
}

def validate_digital_link(uri: str) -> bool:
    """Checks if a URI is plausibly a GS1 Digital Link."""
    # Simple check for path structure /(AI)/value
    path = urlparse(uri).path
    # This is a naive check; full validation would require AI table lookups
    return any(re.search(rf'/{ai}/', path) for ai in ["01", "21", "10", "17", "00"])

def parse_digital_link_attributes(uri: str) -> Dict[str, str]:
    """Extracts AI attributes from a Digital Link URI."""
    parsed = urlparse(uri)
    path_segments = parsed.path.strip("/").split("/")
    
    attributes = {}
    # Extract from path
    for i in range(0, len(path_segments) - 1, 2):
        ai = path_segments[i]
        value = path_segments[i+1]
        attributes[ai] = value
        
    # Extract from query params
    query_params = parse_qs(parsed.query)
    for k, v in query_params.items():
        if v:
            attributes[k] = v[0]
            
    return attributes
