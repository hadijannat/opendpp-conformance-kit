# BatteryPass Profile

This profile targets BatteryPass aspect models (version 1.2.0) and wires in
upstream JSON Schema and OpenAPI artifacts for each aspect.

Included aspects:
- GeneralProductInformation
- PerformanceAndDurability
- Circularity
- MaterialComposition
- CarbonFootprintForBatteries
- SupplyChainDueDiligence
- Labeling

Artifacts:
- `schemas/*.json` JSON Schemas per aspect
- `openapi/*_openapi3_0.*` OpenAPI specs per aspect
- `contexts/*-ld.json` JSON-LD exports (SAMM)
- `contexts/*.ttl` RDF/SAMM aspect models
- `shapes/battery_pass_minimal.shapes.ttl` minimal SHACL constraints for AAS RDF

Test vectors:
- `testvectors/positive/*.json`
- `testvectors/positive/*.aas`
- `testvectors/positive/*.aasx`

See `NOTICE.md` for licensing and attribution details.
