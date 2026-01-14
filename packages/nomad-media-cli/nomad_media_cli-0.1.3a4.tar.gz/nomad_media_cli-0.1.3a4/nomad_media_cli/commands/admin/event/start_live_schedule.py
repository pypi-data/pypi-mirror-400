import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--event-id", required=True, help="The ID of the event to start the live schedule of.")
@click.pass_context
def start_live_schedule(ctx, event_id):
    """Start live schedule of event"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.start_live_schedule(event_id)
        click.echo("Live schedule started successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error starting live schedule: {e}"}))
        sys.exit(1)