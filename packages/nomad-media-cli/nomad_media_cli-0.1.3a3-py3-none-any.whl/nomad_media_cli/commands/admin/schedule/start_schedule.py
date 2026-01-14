import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule to be started.")
@click.option("--skip-cleanup-on-failure", type=click.BOOL, help="Whether or not to skip cleanup on failure.")
@click.pass_context
def start_schedule(ctx, schedule_id, skip_cleanup_on_failure):
    """Start schedule"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.start_schedule(schedule_id, skip_cleanup_on_failure)
        click.echo("Schedule started successfully.")
        click.echo(result)

    except Exception as e:
        click.echo(json.dumps({"error": f"Error starting schedule: {e}"}))
        sys.exit(1)