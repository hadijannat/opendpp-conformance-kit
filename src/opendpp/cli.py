import json
import logging
from pathlib import Path

import click

from opendpp.core.engine import run_conformance_check
from opendpp.reporting.html import render_report_html
from opendpp.trust.issue import issue_vc_jwt, load_jwk
from opendpp.core.report import ConformanceReport


@click.group()
def cli():
    """OpenDPP Conformance Kit CLI (dppctl)"""
    logging.basicConfig(level=logging.INFO)


@cli.command()
@click.argument("target")
@click.option("--profile", default="espr-core", help="Conformance profile to use.")
@click.option("--output", default="report.json", help="Output path for JSON report.")
@click.option(
    "--html-output", default="report.html", help="Output path for HTML report."
)
@click.option(
    "--artifacts-dir",
    default="report_artifacts",
    help="Directory to store fetched artifacts.",
)
def check(target, profile, output, html_output, artifacts_dir):
    """Runs a conformance check against a target (URL, DID, File)."""
    click.echo(f"Running conformance check against: {target} using profile: {profile}")

    try:
        report = run_conformance_check(
            target=target, profile_ref=profile, report_artifacts_dir=artifacts_dir
        )

        Path(output).write_text(report.model_dump_json(indent=2), encoding="utf-8")
        click.echo(f"Report generated: {output}")

        if html_output:
            html = render_report_html(report)
            Path(html_output).write_text(html, encoding="utf-8")
            click.echo(f"HTML report generated: {html_output}")

        if report.passed:
            click.echo(click.style("CONFORMANCE PASSED", fg="green"))
        else:
            click.echo(click.style("CONFORMANCE FAILED", fg="red"))

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        raise click.Abort()


@cli.command("issue-attestation")
@click.option("--report", "report_path", required=True, help="Path to report.json.")
@click.option("--issuer", required=True, help="Issuer DID (did:web recommended).")
@click.option("--jwk", "jwk_path", required=True, help="Path to issuer private JWK.")
@click.option("--alg", default="ES256", help="Signing algorithm (default: ES256).")
@click.option("--kid", default=None, help="Override key id (kid) in JWT header.")
@click.option(
    "--output", default="conformance.vc.jwt", help="Output path for VC-JWT."
)
@click.option(
    "--decoded-output",
    default="conformance.vc.json",
    help="Output path for decoded VC JSON.",
)
def issue_attestation(report_path, issuer, jwk_path, alg, kid, output, decoded_output):
    """Issue a VC-JWT conformance attestation from a report.json."""
    try:
        report_json = Path(report_path).read_text(encoding="utf-8")
        report = ConformanceReport.model_validate_json(report_json)
        jwk_data = load_jwk(jwk_path)

        token, vc = issue_vc_jwt(
            report, issuer=issuer, jwk_data=jwk_data, alg=alg, kid=kid
        )
        Path(output).write_text(token, encoding="utf-8")

        decoded = {"vc": vc, "jwt": token}
        Path(decoded_output).write_text(
            json.dumps(decoded, indent=2), encoding="utf-8"
        )

        click.echo(f"VC-JWT written to: {output}")
        click.echo(f"Decoded JSON written to: {decoded_output}")
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        raise click.Abort()


if __name__ == "__main__":
    cli()
