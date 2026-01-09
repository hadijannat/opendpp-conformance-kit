from opendpp.resolve.parse_input import parse_input, InputType


def test_parse_input_url():
    itype, canonical = parse_input("https://example.com/dpp")
    assert itype == InputType.URL
    assert canonical == "https://example.com/dpp"


def test_parse_input_digital_link():
    itype, _ = parse_input("https://id.gs1.org/01/01234567890128/21/SER123")
    assert itype == InputType.DIGITAL_LINK


def test_parse_input_did():
    itype, _ = parse_input("did:web:example.com")
    assert itype == InputType.DID
