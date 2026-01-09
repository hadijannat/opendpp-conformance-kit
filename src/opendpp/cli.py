import click
import json
import logging
from opendpp.core.report import ConformanceReport, Severity
from opendpp.resolve.parse_input import parse_input, InputType
from opendpp.fetch.http import HttpFetcher

@click.group()
def cli():
    """OpenDPP Conformance Kit CLI (dppctl)"""
    logging.basicConfig(level=logging.INFO)

@cli.command()
@click.argument('target')
@click.option('--profile', default='espr-core', help='Conformance profile to use.')
@click.option('--output', default='report.json', help='Output path for the report.')
def check(target, profile, output):
    """Runs a conformance check against a target (URL, DID, File)."""
    click.echo(f"Runing conformance check against: {target} using profile: {profile}")
    
    report = ConformanceReport(target=target, profile_id=profile, profile_version="1.0.0")
    
    try:
        # 1. Resolve and Fetch
        input_type, canonical_target = parse_input(target)
        click.echo(f"Input recognized as: {input_type}")
        
        if input_type == InputType.URL:
            fetcher = HttpFetcher()
            artifact = fetcher.fetch(canonical_target)
            click.echo(f"Fetched artifact: {artifact.artifact_type} ({artifact.sha256[:8]})")
            report.artifacts.append(artifact.uri) # Simplified for now
            
        # 2. Sequence of validations based on profile
        # (Orchestration logic goes here)
        
        report.finalize()
        
        with open(output, 'w') as f:
            f.write(report.model_dump_json(indent=2))
            
        click.echo(f"Report generated: {output}")
        if report.passed:
            click.echo(click.style("CONFORMANCE PASSED", fg="green"))
        else:
            click.echo(click.style("CONFORMANCE FAILED", fg="red"))
            
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
        raise click.Abort()

if __name__ == "__main__":
    cli()
