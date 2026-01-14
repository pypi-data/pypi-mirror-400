import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--event-id", required=True, help="The ID of the event to stop the live schedule of.")
@click.pass_context
def stop_live_schedule(ctx, event_id):
    """Stop live schedule of event"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.stop_live_schedule(event_id)
        click.echo("Live schedule stopped successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error stopping live schedule: {e}"}))
        sys.exit(1)