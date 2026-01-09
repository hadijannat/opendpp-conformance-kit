from pathlib import Path

from opendpp.core.engine import run_conformance_check


def test_battery_pass_profile_sample():
    sample_path = Path("profiles/battery-pass/testvectors/positive/GeneralProductInformation-payload.json")
    report = run_conformance_check(
        target=str(sample_path),
        profile_ref="battery-pass",
        report_artifacts_dir="/tmp/opendpp_battery_artifacts",
    )

    assert report.profile_id == "battery-pass"
    assert report.passed is True
