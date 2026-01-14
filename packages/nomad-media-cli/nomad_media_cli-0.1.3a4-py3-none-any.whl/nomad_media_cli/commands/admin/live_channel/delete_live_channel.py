import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.option("--live-channel-id", required=True, help="The ID of the live channel.")
@click.option("--delete-inputs", required=True, type=click.BOOL, help="Indicates if the live channel inputs should be deleted.")
@click.pass_context
def delete_live_channel(ctx, live_channel_id, delete_inputs):
    """Delete live channel"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.delete_live_channel(live_channel_id, delete_inputs)
        click.echo("Live channel deleted successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error deleting live channel: {e}"}))
        sys.exit(1)