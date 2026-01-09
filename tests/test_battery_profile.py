from pathlib import Path

import pytest

from opendpp.core.engine import run_conformance_check


PAYLOADS = sorted(
    Path("profiles/battery-pass/testvectors/positive").glob("*.json")
)


@pytest.mark.parametrize("payload_path", PAYLOADS)
def test_battery_pass_profile_samples(payload_path):
    report = run_conformance_check(
        target=str(payload_path),
        profile_ref="battery-pass",
        report_artifacts_dir="/tmp/opendpp_battery_artifacts",
    )

    assert report.profile_id == "battery-pass"
    assert report.passed is True
