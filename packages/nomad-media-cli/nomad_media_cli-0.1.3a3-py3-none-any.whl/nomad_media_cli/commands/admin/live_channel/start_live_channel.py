import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-channel-id", required=True, help="The ID of the live channel.")
@click.option("--wait-for-start", type=click.BOOL, help="Indicates if the live channel should wait for start.")
@click.pass_context
def start_live_channel(ctx, live_channel_id, wait_for_start):
    """Start live channel"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.start_live_channel(live_channel_id, wait_for_start)
        click.echo("Live channel started successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error starting live channel: {e}"}))
        sys.exit(1)