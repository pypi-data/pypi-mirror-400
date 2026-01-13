from __future__ import annotations

from pathlib import Path

import click

from onecoder.diagnostics.env_scan import EnvDoctor, EnvFinding


@click.group()
def doctor():
    """Diagnostic tools for environment, ports, and gateways."""
    pass


@doctor.command(name="env")
@click.option("--json", "json_output", is_flag=True, help="Print JSON output.")
def doctor_env(json_output: bool):
    """Scan env files across components and flag mismatches."""
    runner = EnvDoctor()
    findings = runner.run()
    artifact_path = runner.write_artifact(findings)

    if json_output:
        click.echo(EnvDoctor.to_json(findings))
    else:
        _print_human(findings, artifact_path)

    if EnvDoctor.has_failures(findings):
        raise click.exceptions.Exit(1)


def _print_human(findings: list[EnvFinding], artifact_path: Path):
    click.echo("Environment diagnostics")
    for finding in findings:
        prefix = finding.status.upper()
        location = f" ({finding.file})" if finding.file else ""
        tt_hint = f" [see {finding.tt_id}]" if finding.tt_id else ""
        click.echo(f"- [{prefix}] {finding.component}::{finding.check}{location} - {finding.message}{tt_hint}")
    click.echo(f"\nSaved report to {artifact_path}")
