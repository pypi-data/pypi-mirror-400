import click
import sys
from nomad_media_cli.helpers.utils import initialize_sdk

@click.command()
@click.pass_context
def live_channel_refresh(ctx):
    """Refresh live channels"""
    initialize_sdk(ctx)
    nomad_sdk = ctx.obj["nomad_sdk"]

    try:
        nomad_sdk.live_channel_refresh()
        click.echo("Live channels refreshed successfully.")

    except Exception as e:
        click.echo(json.dumps({"error": f"Error refreshing live channels: {e}"}))
        sys.exit(1)