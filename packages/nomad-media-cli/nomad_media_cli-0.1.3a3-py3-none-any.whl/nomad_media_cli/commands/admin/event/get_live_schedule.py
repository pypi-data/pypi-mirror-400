import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--event-id", required=True, help="The ID of the event to get the live schedule of.")
@click.pass_context
def get_live_schedule(ctx, event_id):
    """Get live schedule of event"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_live_schedule(event_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting live schedule: {e}"}))
        sys.exit(1)