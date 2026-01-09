# BatteryPass Artifacts Notice

The BatteryPass artifacts in this profile are sourced from the public
BatteryPassDataModel repository:
- Repository: https://github.com/batterypass/BatteryPassDataModel
- Aspects (version 1.2.0):
  - GeneralProductInformation
  - PerformanceAndDurability
  - Circularity
  - MaterialComposition
  - CarbonFootprintForBatteries
  - SupplyChainDueDiligence
  - Labeling

Included files are used strictly as data-model artifacts for validation and
interoperability testing. Licensing and attribution are governed by the
notices embedded in the upstream files themselves, which reference
Creative Commons licenses (CC BY 4.0 and CC BY-NC 4.0).

Notes on local normalization:
- JSON and JSON-LD assets were converted to UTF-8 for tooling compatibility.
- `MaterialComposition-payload.json` had a trailing space removed from
  `batteryMaterialIdentifier` to satisfy the upstream schema.
