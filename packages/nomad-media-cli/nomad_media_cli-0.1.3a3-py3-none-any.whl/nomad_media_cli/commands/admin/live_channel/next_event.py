import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-channel-id", required=True, help="The ID of the live channel.")
@click.pass_context
def next_event(ctx, live_channel_id):
    """Get next live channel event"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.next_event(live_channel_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting next live channel event: {e}"}))
        sys.exit(1)