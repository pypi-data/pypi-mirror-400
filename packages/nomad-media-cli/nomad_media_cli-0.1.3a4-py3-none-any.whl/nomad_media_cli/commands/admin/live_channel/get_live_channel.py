import click
import json
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-channel-id", required=True, help="The ID of the live channel.")
@click.pass_context
def get_live_channel(ctx, live_channel_id):
    """Get live channel"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        result = nomad_sdk.get_live_channel(live_channel_id)
        click.echo(json.dumps(result, indent=4))

    except Exception as e:
        click.echo(json.dumps({"error": f"Error getting live channel: {e}"}))
        sys.exit(1)