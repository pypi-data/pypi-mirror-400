import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-channel-id", required=True, help="The ID of the live channel.")
@click.pass_context
def start_output_tracking(ctx, live_channel_id):
    """Start output tracking for live channel"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.start_output_tracking(live_channel_id)
        click.echo("Output tracking started successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error starting output tracking: {e}"}))
        sys.exit(1)