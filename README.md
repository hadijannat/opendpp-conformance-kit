# OpenDPP Conformance Kit

A public, functional, audit-grade repository for OpenDPP conformance validation, supporting **Asset Administration Shell (AAS)** as a first-class input.

## Overview

The OpenDPP Conformance Kit provides tools to validate Digital Product Passports (DPP) against regulatory requirements (ESPR), sectoral standards (BatteryPass), and industrial digital twin models (AAS).

### Key Features

- **`dppctl` CLI**: A command-line harness for resolving and validating DPP artifacts.
- **Standards Aligned**: Inherently supports GS1 Digital Link, W3C Verifiable Credentials, SHACL, and IDTA AAS specifications.
- **Profile-Driven**: Flexible validation logic using "Profile Packs" (e.g., `espr-core`, `battery-pass`).
- **Audit-Grade**: Detailed conformance reports in JSON and HTML with evidence traceability.

## Getting Started

### Installation

```bash
pip install opendpp-conformance-kit
```

### Usage

```bash
dppctl check <url|qr|aasx> --profile espr-core
```

## Standards & References

- [ESPR (Ecodesign for Sustainable Products Regulation)](https://eur-lex.europa.eu/eli/reg/2024/1781/oj)
- [CIRPASS DPP Architecture](https://cirpassproject.eu/)
- [IDTA Asset Administration Shell (AAS)](https://industrialdigitaltwin.org/)
- [W3C Verifiable Credentials 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [GS1 Digital Link](https://www.gs1.org/standards/gs1-digital-link)

## License

Apache-2.0 - See [LICENSE](LICENSE) for details.
