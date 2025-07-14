import typer
from qgjob.client import submit_job, get_status

VALID_TARGETS = ["emulator", "device", "browserstack"]

app = typer.Typer(help="Submit and monitor AppWright test jobs.\n\nExamples:\n  qgjob submit --org-id=qualgent --app-version-id=xyz123 --test=tests/onboarding.spec.js\n  qgjob status --job-id=abc456 --poll\n")

@app.command()
def submit(
    org_id: str = typer.Option(..., help="Organization ID"),
    app_version_id: str = typer.Option(..., help="App version identifier"),
    test: str = typer.Option(..., help="Path to the AppWright test script"),
    priority: int = typer.Option(5, help="Job priority (lower is higher)"),
    target: str = typer.Option("emulator", help="Target: emulator, device, browserstack"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON for CI parsing")
):
    """Submit a new test job."""
    if target not in VALID_TARGETS:
        typer.secho(f"Invalid target: {target}. Must be one of {', '.join(VALID_TARGETS)}.", fg=typer.colors.RED)
        raise typer.Exit(1)
    result = submit_job(org_id, app_version_id, test, priority, target)
    if isinstance(result, dict):
        if json_output:
            import json as _json
            typer.echo(_json.dumps(result))
        else:
            typer.secho(f"Job submitted! ID: {result.get('job_id')} | Status: {result.get('status')}", fg=typer.colors.GREEN)
            typer.echo(result.get('message', ''))
    else:
        typer.secho(result, fg=typer.colors.RED)
        raise typer.Exit(1)

@app.command()
def status(
    job_id: str = typer.Option(..., help="Job ID to check status for"),
    poll: bool = typer.Option(False, "--poll", help="Poll until job completes or fails"),
    json_output: bool = typer.Option(False, "--json", help="Output result as JSON for CI parsing")
):
    """Check the status of a job."""
    from time import sleep
    import sys

    while True:
        result = get_status(job_id)

        if isinstance(result, str):
            typer.secho(result, fg=typer.colors.RED)
            sys.exit(1)

        if json_output:
            import json as _json
            typer.echo(_json.dumps(result))
            if not poll or result["status"] in ("completed", "failed"):
                sys.exit(1 if result["status"] == "failed" else 0)
        else:
            typer.secho(f"Job {job_id} → {result['status']}", fg=typer.colors.BLUE if result['status'] == 'in_progress' else (typer.colors.GREEN if result['status'] == 'completed' else typer.colors.RED))

        if not poll or result["status"] in ("completed", "failed"):
            sys.exit(1 if result["status"] == "failed" else 0)

        sleep(3)
