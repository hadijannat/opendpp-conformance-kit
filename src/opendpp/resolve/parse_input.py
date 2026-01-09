import re
from enum import Enum
from typing import Optional, Union, Tuple
from pathlib import Path

class InputType(str, Enum):
    URL = "url"
    DIGITAL_LINK = "digital_link"
    FILE_PATH = "file_path"
    DID = "did"
    UNKNOWN = "unknown"

def parse_input(input_str: str) -> Tuple[InputType, str]:
    """Recognizes the type of input and returns (type, canonical_form)."""
    input_str = input_str.strip()

    # Recognize GS1 Digital Link
    # Regex for plausibly a Digital Link (contains identifier keys like /01/, /21/, etc.)
    if re.search(r'/(01|21|10|11|17|240|414|417|422|8003|8004|8006|8010|8017|8018)/', input_str):
        return InputType.DIGITAL_LINK, input_str

    # Recognize URL
    if input_str.startswith(("http://", "https://")):
        return InputType.URL, input_str

    # Recognize DID
    if input_str.startswith("did:"):
        return InputType.DID, input_str

    # Recognize File Path
    if Path(input_str).exists() or input_str.endswith((".json", ".xml", ".aasx", ".ttl")):
        return InputType.FILE_PATH, str(Path(input_str).absolute())

    return InputType.UNKNOWN, input_str
