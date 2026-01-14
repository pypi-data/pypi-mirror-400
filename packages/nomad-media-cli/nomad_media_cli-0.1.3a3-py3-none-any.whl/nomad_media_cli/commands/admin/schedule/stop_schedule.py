import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--schedule-id", required=True, help="The ID of the schedule to be stopped.")
@click.option("--force-stop", type=click.BOOL, help="Whether or not to force a stop.")
@click.pass_context
def stop_schedule(ctx, schedule_id, force_stop):
    """Stop schedule"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.stop_schedule(schedule_id, force_stop)
        click.echo("Schedule stopped successfully.")
        click.echo(result)

    except Exception as e:
        click.echo(json.dumps({"error": f"Error stopping schedule: {e}"}))
        sys.exit(1)