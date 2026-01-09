from opendpp.core.engine import run_conformance_check


def test_run_conformance_check_on_file(tmp_path):
    payload = '{"id": "example-1", "name": "Example"}'
    target = tmp_path / "dpp.json"
    target.write_text(payload, encoding="utf-8")

    report = run_conformance_check(
        target=str(target),
        profile_ref="espr-core",
        report_artifacts_dir=str(tmp_path / "artifacts"),
    )

    assert report.passed is True
    assert report.profile_id == "espr-core"
    assert len(report.artifacts) >= 1
    assert any(f.rule_id == "ESPR-01" for f in report.findings) is False
