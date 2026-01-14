import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-channel-id", required=True, help="The ID of the live channel.")
@click.option("--wait-for-stop", type=click.BOOL, help="Indicates if the live channel should wait for stop.")
@click.pass_context
def stop_live_channel(ctx, live_channel_id, wait_for_stop):
    """Stop live channel"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.stop_live_channel(live_channel_id, wait_for_stop)
        click.echo("Live channel stopped successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error stopping live channel: {e}"}))
        sys.exit(1)